# MIT License
 
# Copyright (c) 2023 Advanced Micro Devices, Inc.
 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
 
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.




from ctypes import Structure, Union, c_uint, c_uint32, c_uint64

from mce_read.MsrRegister import MSRRegister
from system_config.cpuinfo import CpuInfo, GetSocketId


class GMCC_Data(Structure):
    _fields_ = [
        ("count", c_uint32, 8),
        ("McgCtlP", c_uint32, 1),
        ("reserved", c_uint64, 55),
    ]


class GMCC_RegisterData(Union):
    _fields_ = [
        ("data", GMCC_Data),
        ("raw", c_uint64),
    ]


class MSR_0179_GlobalMachineCheckCapabilities:
    def __init__(self):
        self.MSR_MCG_CAP = c_uint(0x179)
        self._register = GMCC_RegisterData()

    def read(self, msr: MSRRegister, core_id: int):
        self._register.raw = msr.read(self.MSR_MCG_CAP, core_id)

    def getRegister(self):
        return self._register.data


class GMCS_Data(Structure):
    _fields_ = [
        ("ripv", c_uint32, 1),
        ("eipv", c_uint32, 1),
        ("mcip", c_uint32, 1),
        ("reserved", c_uint64, 61),
    ]


class GMCS_Register(Union):
    _fields_ = [
        ("data", GMCS_Data),
        ("raw", c_uint64),
    ]


class MSR_017A_GlobalMachineCheckStatus:
    def __init__(self):
        self.MSR_MCG_CTL = c_uint(0x17A)
        self._register = GMCS_Register()

    def read(self, msr: MSRRegister, core_id):
        self._register.raw = msr.read(self.MSR_MCG_CTL, core_id)

    def getRegister(self):
        return self._register.data


class GMCERC_Data(Structure):
    _fields_ = [
        ("mc_n_en_core", c_uint32, 7),
        ("mc_n_en", c_uint64, 57),
    ]


class GMCERC_Register(Union):
    _fields_ = [
        ("data", GMCERC_Data),
        ("raw", c_uint64),
    ]


class MSR_017B_GlobalMachineCheckExceptionReportingControl:
    def __init__(self):
        self.MSR_MCG_CTL = 0x17B
        self._register = GMCERC_Register(self.Data())

    def read(self, msr: MSRRegister, core_id):
        self._register.raw = msr.read(self.MSR_MCG_CTL, core_id)

    def write(self, msr: MSRRegister, data: GMCERC_Data, core_id: int):
        self._register = data
        msr.write(self.MSR_MCG_CTL, self._regiser.raw, data, core_id)


class MCAStatusData(Structure):
    _fields_ = [
        ("error_code", c_uint32, 16),  # bit 0 - 15
        ("error_code_ext", c_uint32, 6),  # bit 16-21
        ("reserv22", c_uint32, 2),  # bit 22-23
        ("addr_lsb", c_uint32, 6),  # bit 24-29
        ("reserv30", c_uint32, 2),  # bit 30-31
        ("error_code_id", c_uint32, 6),  # bit 32-37
        ("reserv38", c_uint32, 2),  # bit 38-39
        ("scrub", c_uint32, 1),  # bit 40
        ("reserv41", c_uint32, 2),  # bit 41-42
        ("poison", c_uint32, 1),  # bit 43
        ("deferred", c_uint32, 1),  # bit 44
        ("uecc", c_uint32, 1),  # bit 45
        ("cecc", c_uint32, 1),  # bit 46
        ("reserv47", c_uint32, 5),  # bit 47-51
        ("transparent", c_uint32, 1),  # bit 52
        ("syndv", c_uint32, 1),  # bit 53
        ("reserv54", c_uint32, 1),  # bit 54
        ("tcc", c_uint32, 1),  # bit 56
        ("err_core_id_val", c_uint32, 1),  # bit 56
        ("pcc", c_uint32, 1),  # bit 57
        ("addrv", c_uint32, 1),  # bit 58
        ("miscv", c_uint32, 1),  # bit 59
        ("en", c_uint32, 1),  # bit 60
        ("uc", c_uint32, 1),  # bit 61
        ("overflow", c_uint32, 1),  # bit 62
        ("val", c_uint32, 1),  # bit 63
    ]


class MCAStatusRegister(Union):
    _fields_ = [("raw", c_uint64), ("data", MCAStatusData)]

    def __str__(self):
        (
            "error_code: {}; "
            + "error_code_ext: {}; "
            + "addr_lsb: {}; "
            + "err_code_id: {}; "
            + "reserv38: {}; "
            + "scrub: {}; "
            + "poison: {}; "
            + "deferred: {}; "
            + "uecc: {}; "
            + "cecc: {}; "
            + "transparent: {}; "
            + "syndv: {}; "
            + "tcc: {}; "
            + "err_core_id_val: {}; "
            + "pcc: {}; "
            + "addrv: {}; "
            + "miscv: {}; "
            + "en: {}; "
            + "uc: {}; "
            + "overflow: {}; "
            + "val: {}; "
        ).format(
            self.data.error_code,
            self.data.error_code_ext,
            self.data.addr_lsb,
            self.data.error_code_id,
            self.data.reserv38,
            self.data.scrub,
            self.data.poison,
            self.data.deferred,
            self.data.uecc,
            self.data.cecc,
            self.data.transparent,
            self.data.syndv,
            self.data.tcc,
            self.data.err_core_id_val,
            self.data.pcc,
            self.data.addrv,
            self.data.miscv,
            self.data.en,
            self.data.uc,
            self.data.overflow,
            self.data.val,
        )


class MCAAddressData(Structure):
    _fields_ = [
        ("error_addr", c_uint64, 57),  # bit 0-56
        ("reserved", c_uint32, 7),  # bit 57-63
    ]


class MCAAddressRegister(Union):
    _fields_ = [
        ("raw", c_uint64),
        ("data", MCAAddressData),
    ]


class MCADestat(Structure):
    _fields_ = [
        ("error_code", c_uint32, 16),  # bit 0-15
        ("error_code_ext", c_uint32, 6),  # bit 16-21
        ("reserv0", c_uint32, 2),  # bit 22-23
        ("addr_lsb", c_uint32, 6),  # bit 24-29
        ("reserv1", c_uint32, 14),  # bit 30-43
        ("deferred", c_uint32, 1),  # bit 44
        ("reserv2", c_uint32, 8),  # bit 45-52
        ("syndv", c_uint32, 1),  # bit 53
        ("reserv3", c_uint32, 4),  # bit 54-57
        ("addrv", c_uint32, 1),  # bit 58
        ("reserv4", c_uint32, 3),  # bit 59-61
        ("overflow", c_uint32, 1),  # bit 62
        ("val", c_uint32, 1),  # bit 63
    ]


class MCADestatRegister(Union):
    _fields_ = [
        ("raw", c_uint64),
        ("data", MCADestat),
    ]


class MCADummy(Structure):
    _fields_ = [("data_lo", c_uint32, 32), ("data_hi", c_uint32, 32)]


class MCADummyRegister(Union):
    _fields_ = [
        ("raw", c_uint64),
        ("data", MCADummy),
    ]


class MCABank:
    def __init__(self):
        self.core_id = 0
        self.bank_id = 0
        self.status = MCAStatusRegister()
        self.address = MCAAddressRegister()
        self.synd = MCADummyRegister()
        self.ipid = MCADummyRegister()
        self.misc0 = MCADummyRegister()
        self.destat = MCADestatRegister()
        self.deaddr = MCADummyRegister()

    def __str__(self):
        if self.status.data.val != 1:
            return ""

        msg = "MCE DETECTED [{}];".format("UNCORRECTED" if self.status.data.uc == 1 else "CORRECTED")
        msg += "CORE: {};".format(self.core_id)
        msg += "SOCKET: {};".format(GetSocketId(self.core_id))
        msg += "BANK: {};".format(self.bank_id)
        msg += "ERROR CODE EXT: {};".format(self.status.data.error_code_ext)
        msg += "STATUS: {};".format("UNCORRECTED" if self.status.data.uc == 1 else "CORRECTED")
        msg += "MCA_STATUS: {};".format(hex(self.status.raw))
        if self.status.data.addrv:
            msg += "MCA_ADDR: {};".format(hex(self.address.raw))
        if self.status.data.syndv:
            msg += "MCA_SYND: {};".format(hex(self.synd.raw))
        msg += "" + "MCA_IPID: {};".format(hex(self.ipid.raw))
        if self.status.data.miscv:
            msg += "MCA_MISC0: {};".format(hex(self.misc0.raw))
        if self.destat.data.val:
            msg += "MCA_DESTAT: {};".format(hex(self.destat.raw))
            msg += "MCA_DEADDR: {};".format(hex(self.deaddr.raw))
        msg += "STATUS DECODE: {}".format(str(self.status.raw))
        return msg


class MCECheck:
    def __init__(self, msrReg: MSRRegister):
        self.msr = msrReg

    def check(self):
        cpuInfo = CpuInfo()
        mceBankList = []
        for core_id in range(cpuInfo.num_logical_cores):
            # Read Global Machine Check Capabilities of each Core
            mc_capabilities = MSR_0179_GlobalMachineCheckCapabilities()
            mc_capabilities.read(self.msr, core_id)
            mc_cap_data = mc_capabilities.getRegister()
            if mc_cap_data.count == 0:
                raise RuntimeError("Error: Number of error reporting banks visible to core {} is 0.".format(core_id))

            class mca_bank_msr_regs(Structure):
                _fields_ = [
                    ("ctl", c_uint32),
                    ("status", c_uint32),
                    ("addr", c_uint32),
                    ("misc0", c_uint32),
                    ("config", c_uint32),
                    ("ipid", c_uint32),
                    ("synd", c_uint32),
                    ("destat", c_uint32),
                    ("deaddr", c_uint32),
                ]

                def __init__(self):
                    ctl = 0xC0002000
                    status = 0xC0002001
                    addr = 0xC0002002
                    misc0 = 0xC0002003
                    config = 0xC0002004
                    ipid = 0xC0002005
                    synd = 0xC0002006
                    destat = 0xC0002007
                    deaddr = 0xC0002008
                    super().__init__(ctl, status, addr, misc0, config, ipid, synd, destat, deaddr)

            reg = mca_bank_msr_regs()
            for bank_i in range(mc_cap_data.count):
                mca_bank = MCABank()
                mca_bank.core_id = core_id
                mca_bank.bank_id = bank_i
                mca_bank_status_msr_addr = c_uint(reg.status + bank_i * 16)

                mca_bank.status.raw = 0x0
                # Step0: Read MCA Status
                mca_bank.status.raw = self.msr.read(mca_bank_status_msr_addr, core_id)

                if mca_bank.status.data.val == 1:
                    # Step 1: Check for valid MISC0
                    if mca_bank.status.data.miscv:
                        mca_bank_misc0_msr_addr = c_uint32(reg.misc0 + bank_i * 16)
                        mca_bank.misc0.raw = self.msr.read(mca_bank_misc0_msr_addr, core_id)

                    # Step 2: Check for valid Addr
                    if mca_bank.status.data.addrv:
                        mca_bank_addr_msr_addr = c_uint32(reg.addr + bank_i * 16)
                        mca_bank.address.raw = self.msr.read(mca_bank_addr_msr_addr, core_id)

                    # Step 3: Check for valid Synd
                    if mca_bank.status.data.syndv:
                        mca_bank_synd_msr_addr = c_uint32(reg.synd + bank_i * 16)
                        mca_bank.synd.raw = self.msr.read(mca_bank_synd_msr_addr, core_id)

                    # Step 4: Check for valid Ipid
                    mca_bank_ipid_msr_addr = c_uint32(reg.ipid + bank_i * 16)
                    mca_bank.ipid.raw = self.msr.read(mca_bank_ipid_msr_addr, core_id)

                    # Step 5: Check for valid Destat
                    mca_bank_destat_msr_addr = c_uint32(reg.destat + bank_i * 16)
                    mca_bank.destat.raw = self.msr.read(mca_bank_destat_msr_addr, core_id)

                    # Step 6: Check for valid Deaddr
                    mca_bank_deaddr_msr_addr = c_uint32(reg.deaddr + bank_i * 16)
                    mca_bank.deaddr.raw = self.msr.read(mca_bank_deaddr_msr_addr, core_id)
                    mceBankList.append(mca_bank)
        return mceBankList
