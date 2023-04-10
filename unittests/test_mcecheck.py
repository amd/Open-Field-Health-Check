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

from ctypes import c_uint64
from unittest import TestCase
from unittest.mock import NonCallableMagicMock, patch

from mce_read.MceCheck import GMCC_RegisterData, MCECheck
from mce_read.MsrRegister import MSRRegister


@patch("mce_read.MceCheck.CpuInfo", autospec=True)
@patch("mce_read.MceCheck.MSR_0179_GlobalMachineCheckCapabilities", autospec=True)
class TestMCECheck(TestCase):
    def setUp(self):
        self.msrReg = NonCallableMagicMock(spec=MSRRegister)
        self.mceCheck = MCECheck(self.msrReg)

        # Base Register Addresses
        self.statusAddr = 0xC0002001
        self.addrAddr = 0xC0002002
        self.misc0Addr = 0xC0002003
        self.configAddr = 0xC0002004
        self.ipidAddr = 0xC0002005
        self.synd = 0xC0002006
        self.destatAddr = 0xC0002007
        self.deaddrAddr = 0xC0002008

    def testInit(self, mcCapMock, cpuInfoMock):
        self.assertEqual(self.mceCheck.msr, self.msrReg)

    def testCheckNoMCEs(self, mcCapMock, cpuInfoMock):
        # Setup
        cpuInfoMock.return_value.num_logical_cores = 1

        gmccRegData = NonCallableMagicMock(spec=GMCC_RegisterData)
        numOfBanks = 5
        gmccRegData.count = numOfBanks
        mcCapMock.return_value.getRegister.return_value = gmccRegData

        self.msrReg.read.return_value = c_uint64(0x0)

        # Run
        mces = self.mceCheck.check()

        # Test
        self.assertEqual(len(mces), 0)
        self.msrReg.read.assert_called()

    def testCheck1MCEs(self, mcCapMock, cpuInfoMock):
        # TODO test reading each MCA Info Register
        # Setup
        cpuInfoMock.return_value.num_logical_cores = 128

        gmccRegData = NonCallableMagicMock(spec=GMCC_RegisterData)
        numOfBanks = 1
        gmccRegData.count = numOfBanks
        mcCapMock.return_value.getRegister.return_value = gmccRegData

        def getMsrSideEffect(addr, coreId):
            if coreId != 0:
                return c_uint64(0x0)
            else:
                return c_uint64(0x8000000000000000)

        self.msrReg.read.side_effect = getMsrSideEffect

        # Run
        mces = self.mceCheck.check()

        # Test
        self.assertEqual(len(mces), 1)

    def testCheckMoreMCEs(self, mcCapMock, cpuInfoMock):
        # Setup
        cpuInfoMock.return_value.num_logical_cores = 5
        gmccRegData = NonCallableMagicMock(spec=GMCC_RegisterData)
        numOfBanks = 5
        gmccRegData.count = numOfBanks
        mcCapMock.return_value.getRegister.return_value = gmccRegData

        def getMsrSideEffect(addr, coreId):
            if coreId != 4:
                return c_uint64(0x0)
            else:
                return c_uint64(0x8000000000000000)

        self.msrReg.read.side_effect = getMsrSideEffect

        # Run
        mces = self.mceCheck.check()

        # Test
        self.assertEqual(len(mces), 5)

    def testCheckBankNotCompatable(self, mcCapMock, cpuInfoMock):
        # Setup
        cpuInfoMock.return_value.num_logical_cores = 5

        gmccRegData = NonCallableMagicMock(spec=GMCC_RegisterData)
        gmccRegData.count = 0
        mcCapMock.return_value.getRegister.return_value = gmccRegData

        # Run & Test
        self.assertRaises(RuntimeError, self.mceCheck.check)
