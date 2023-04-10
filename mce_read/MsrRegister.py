# Copyright (C) 2023 Advanced Micro Devices, Inc
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the
# Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE X
# CONSORTIUM BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
# Except as contained in this notice, the name of Advanced Micro Devices, Inc shall not be used in advertising or
# otherwise to promote the sale, use or other dealings in this Software without prior written authorization from
# Advanced Micro Devices, Inc.
#
#
# Disclaimer
# The information presented in this document is for informational purposes only and may contain technical inaccuracies,
# omissions, and typographical errors. The information contained herein is subject to change and may be rendered
# inaccurate for many reasons, including but not limited to product and roadmap changes, component and motherboard
# version changes, new model and/or product releases, product differences between differing manufacturers, software
# changes, BIOS flashes, firmware upgrades, or the like. Any computer system has risks of security vulnerabilities that
# cannot be completely prevented or mitigated. AMD assumes no obligation to update or otherwise correct or revise this
# information. However, AMD reserves the right to revise this information and to make changes from time to time to the
# content hereof without obligation of AMD to notify any person of such revisions or changes.
#     THIS INFORMATION IS PROVIDED ‘AS IS.” AMD MAKES NO REPRESENTATIONS OR WARRANTIES WITH RESPECT TO THE CONTENTS
# HEREOF AND ASSUMES NO RESPONSIBILITY FOR ANY INACCURACIES, ERRORS, OR OMISSIONS THAT MAY APPEAR IN THIS INFORMATION.
# AMD SPECIFICALLY DISCLAIMS ANY IMPLIED WARRANTIES OF NON-INFRINGEMENT, MERCHANTABILITY, OR FITNESS FOR ANY PARTICULAR
# PURPOSE. IN NO EVENT WILL AMD BE LIABLE TO ANY PERSON FOR ANY RELIANCE, DIRECT, INDIRECT, SPECIAL, OR OTHER
# CONSEQUENTIAL DAMAGES ARISING FROM THE USE OF ANY INFORMATION CONTAINED HEREIN, EVEN IF AMD IS EXPRESSLY ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGES.
# AMD, the AMD Arrow logo, Open Field Health Check (OFHC) and combinations thereof are trademarks of Advanced Micro
# Devices, Inc. Other product names used in this publication are for identification purposes only and may be
# trademarks of their respective companies.
# © 2023 Advanced Micro Devices, Inc. All rights reserved.

import os
from ctypes import c_uint32, c_uint64, sizeof

from logger import logger


class PerCoreMSRRegister:
    def __init__(self, core_id):
        self.core_id = core_id
        msrFilename = "/dev/cpu/{}/msr".format(self.core_id)
        try:
            self._fd = os.open(msrFilename, (os.O_RDWR))
        except OSError as ex:
            raise RuntimeError("Failed to open MSR File for core {}. Message: {}".format(self.core_id, ex))

    def __del__(self):
        # close FD
        try:
            os.close(self._fd)
        except AttributeError:
            logger.warning(
                "Failed to close msr read/write file descriptors. Could be a result of failing to open File."
            )

    def getCoreId(self):
        return self.core_id

    def read(self, reg: c_uint32):
        if self._fd < 0:
            raise RuntimeError("MSR Regsiter: Does not have MSR file handle for cpu: {}.".format(self.core_id))
        try:
            data = os.pread(self._fd, sizeof(c_uint64), reg.value)
        except OSError as e:
            raise RuntimeError(
                "MSR Regsiter: Does not have MSR file handle for cpu: {}. Message: {}".format(self.core_id, e)
            )
        return data

    def write(self, reg: c_uint32, data: c_uint64):
        raise NotImplementedError("Write MSR Registers has not been successfully implemented")
        if self._fd < 0:
            raise RuntimeError("MSR Regsiter: Does not have MSR file handle for cpu: {}.".format(self.core_id))

        dataByteString = data.value.to_bytes(sizeof(data), "little")
        try:
            data = os.pwrite(self._fd, dataByteString, reg.value)
        except OSError as e:
            raise RuntimeError(
                "MSR Regsiter: Does not have MSR file handle for cpu: {}. Message: {}".format(self.core_id, e)
            )


class MSRRegister:
    def __init__(self, num_logical_cores):
        self.perCoreMsrRegister = [PerCoreMSRRegister(c) for c in range(num_logical_cores)]

    def read(self, reg: c_uint32, cpu: int):
        if cpu > len(self.perCoreMsrRegister):
            raise RuntimeError(
                "Invalid core id: {}. Only {} logical cores are present".format(cpu, len(self.perCoreMsrRegister))
            )
        return int.from_bytes(self.perCoreMsrRegister[cpu].read(reg), "little")

    def write(self, reg: c_uint32, data: c_uint64, cpu: int):
        if cpu > len(self.perCoreMsrRegister):
            raise RuntimeError(
                "Invalid core id: {}. Only {} logical cores are present".format(cpu, len(self.perCoreMsrRegister))
            )
        return self.perCoreMsrRegister[cpu].write(reg, data)
