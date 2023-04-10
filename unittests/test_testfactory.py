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

from unittest import TestCase
from unittest.mock import MagicMock, NonCallableMagicMock, patch

from param_factories.ParamFactory import ParamFactory
from system_config.SystemConfig import CoreConfig, SystemConfig, TestConfig
from test_factories.TestFactory import TestFactory


@patch("test_factories.TestFactory.ParamFactory", autospec=True)
@patch("test_factories.TestFactory.Test", autospec=True)
class TestTestFactory(TestCase):
    def setUp(self):
        pass

    def testOneTestOneCoreConfig(self, testMock, paramFactoryMock):
        binaryPath = "/path/to/test/binary"
        testName = "test1"
        # Setup
        testConfigMock = NonCallableMagicMock(spec=TestConfig)
        testConfigMock.name = testName
        testConfigMock.binary = binaryPath

        coreConfigMock = NonCallableMagicMock(spec=CoreConfig)
        coreConfigMock.cores = [["0"]]

        sysConfigMock = NonCallableMagicMock(spec=[SystemConfig, "isConstantMceChecking", "checkMCEs"])
        sysConfigMock.checkMCEs = MagicMock()
        sysConfigMock.testConfigs = [testConfigMock]
        sysConfigMock.coreConfig = coreConfigMock

        params = [{"-a": "val1", "-b": ""}, {"-a": "va11"}, {"-a": "val2", "-b": ""}, {"-a": "val2"}]

        paramFactoryInstance = paramFactoryMock.return_value
        paramFactoryInstance.getParams.side_effect = params
        paramFactoryInstance.getNextParams.side_effect = [None, None, None, StopIteration]

        # Run
        testFactory = TestFactory(sysConfigMock)

        # Test
        testFactory.getNextTest()
        testMock.assert_called_with(params[0], binaryPath, 1, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params[1], binaryPath, 2, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params[2], binaryPath, 3, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params[3], binaryPath, 4, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        self.assertRaises(StopIteration, testFactory.getNextTest)

    def testOneTestMultipleCoreConfigs(self, testMock, paramFactoryMock):
        binaryPath = "/path/to/test/binary"
        testName = "test1"
        # Setup
        testConfigMock = NonCallableMagicMock(spec=TestConfig)
        testConfigMock.name = testName
        testConfigMock.binary = binaryPath

        coreConfigMock = NonCallableMagicMock(spec=CoreConfig)
        coreConfigMock.cores = [[str(x)] for x in range(4)]

        sysConfigMock = NonCallableMagicMock(spec=[SystemConfig, "isConstantMceChecking", "checkMCEs"])
        sysConfigMock.checkMCEs = MagicMock()
        sysConfigMock.testConfigs = [testConfigMock]
        sysConfigMock.coreConfig = coreConfigMock

        params = [{"-a": "val1", "-b": ""}, {"-a": "va11"}, {"-a": "val2", "-b": ""}, {"-a": "val2"}]

        paramFactoryInstance = paramFactoryMock.return_value
        paramFactoryInstance.getParams.side_effect = params
        paramFactoryInstance.getNextParams.side_effect = [None if i != 4 else StopIteration for i in range(5)]

        # Run
        testFactory = TestFactory(sysConfigMock)

        # Test
        testFactory.getNextTest()
        testMock.assert_called_with(params[0], binaryPath, 1, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params[1], binaryPath, 2, coreConfigMock.cores[1], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params[2], binaryPath, 3, coreConfigMock.cores[2], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params[3], binaryPath, 4, coreConfigMock.cores[3], sysConfigMock.checkMCEs)
        self.assertRaises(StopIteration, testFactory.getNextTest)

    def testTwoTest(self, testMock, paramFactoryMock):
        binaryPath1 = "/path/to/test1/binary"
        testName1 = "test1"
        binaryPath2 = "/path/to/test2/binary"
        testName2 = "test2"
        # Setup
        testConfig1 = NonCallableMagicMock(spec=TestConfig)
        testConfig1.name = testName1
        testConfig1.binary = binaryPath1

        testConfig2 = NonCallableMagicMock(spec=TestConfig)
        testConfig2.name = testName2
        testConfig2.binary = binaryPath2

        coreConfigMock = NonCallableMagicMock(spec=CoreConfig)
        coreConfigMock.cores = [[0]]

        sysConfigMock = NonCallableMagicMock(spec=[SystemConfig, "isConstantMceChecking", "checkMCEs"])
        sysConfigMock.checkMCEs = MagicMock()
        sysConfigMock.testConfigs = [testConfig1, testConfig2]
        sysConfigMock.coreConfig = coreConfigMock

        params1 = [{"-a": "val1", "-b": ""}, {"-a": "va11"}, {"-a": "val2", "-b": ""}, {"-a": "val2"}]
        params2 = [
            {"-a": "val1a", "-b": "no"},
            {"-a": "va11a"},
            {"-a": "val2a", "-b": "no"},
            {"-a": "val2a"},
        ]
        getNextParam1SideEffects = [None, None, None, StopIteration]
        getNextParam2SideEffects = [None, None, None, StopIteration]

        paramFactoryInstance1 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance1.getParams.side_effect = params1
        paramFactoryInstance1.getNextParams.side_effects = getNextParam1SideEffects
        paramFactoryInstance2 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance2.getParams.side_effect = params2
        paramFactoryInstance2.getNextParams.side_effects = getNextParam2SideEffects
        paramFactoryMock.side_effect = [paramFactoryInstance1, paramFactoryInstance2]

        # Run
        testFactory = TestFactory(sysConfigMock)

        # Test
        testFactory.getNextTest()
        testMock.assert_called_with(params1[0], binaryPath1, 1, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[0], binaryPath2, 2, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params1[1], binaryPath1, 3, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[1], binaryPath2, 4, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params1[2], binaryPath1, 5, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[2], binaryPath2, 6, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params1[3], binaryPath1, 7, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[3], binaryPath2, 8, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        self.assertRaises(StopIteration, testFactory.getNextTest)

    def testTwoTest_MulitpleCoreConfigs(self, testMock, paramFactoryMock):
        binaryPath1 = "/path/to/test1/binary"
        testName1 = "test1"
        binaryPath2 = "/path/to/test2/binary"
        testName2 = "test2"
        # Setup
        testConfig1 = NonCallableMagicMock(spec=TestConfig)
        testConfig1.name = testName1
        testConfig1.binary = binaryPath1

        testConfig2 = NonCallableMagicMock(spec=TestConfig)
        testConfig2.name = testName2
        testConfig2.binary = binaryPath2

        coreConfigMock = NonCallableMagicMock(spec=CoreConfig)
        coreConfigMock.cores = [[str(x)] for x in range(4)]

        sysConfigMock = NonCallableMagicMock(spec=[SystemConfig, "isConstantMceChecking", "checkMCEs"])
        sysConfigMock.checkMCEs = MagicMock()
        sysConfigMock.testConfigs = [testConfig1, testConfig2]
        sysConfigMock.coreConfig = coreConfigMock

        params1 = [{"-a": "val1", "-b": ""}, {"-a": "va11"}, {"-a": "val2", "-b": ""}, {"-a": "val2"}] * 4
        params2 = [
            {"-a": "val1a", "-b": "no"},
            {"-a": "va11a"},
            {"-a": "val2a", "-b": "no"},
            {"-a": "val2a"},
        ] * 4
        getNextParam1SideEffects = [None if i != 16 else StopIteration for i in range(17)]
        getNextParam2SideEffects = [None if i != 16 else StopIteration for i in range(17)]

        paramFactoryInstance1 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance1.getParams.side_effect = params1
        paramFactoryInstance1.getNextParams.side_effects = getNextParam1SideEffects

        paramFactoryInstance2 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance2.getParams.side_effect = params2
        paramFactoryInstance2.getNextParams.side_effects = getNextParam2SideEffects
        paramFactoryMock.side_effect = [paramFactoryInstance1, paramFactoryInstance2]

        # Run
        testFactory = TestFactory(sysConfigMock)

        # Test
        for i in range(16):
            testFactory.getNextTest()
            testMock.assert_called_with(
                params1[i], binaryPath1, 2 * i + 1, coreConfigMock.cores[i % 4], sysConfigMock.checkMCEs
            )
            testFactory.getNextTest()
            testMock.assert_called_with(
                params2[i], binaryPath2, 2 * i + 2, coreConfigMock.cores[i % 4], sysConfigMock.checkMCEs
            )
        self.assertRaises(StopIteration, testFactory.getNextTest)

    def testTwoTestDifferentSizesOfParams(self, testMock, paramFactoryMock):
        binaryPath1 = "/path/to/test1/binary"
        testName1 = "test1"
        binaryPath2 = "/path/to/test2/binary"
        testName2 = "test2"
        # Setup
        testConfig1 = NonCallableMagicMock(spec=TestConfig)
        testConfig1.name = testName1
        testConfig1.binary = binaryPath1

        testConfig2 = NonCallableMagicMock(spec=TestConfig)
        testConfig2.name = testName2
        testConfig2.binary = binaryPath2

        coreConfigMock = NonCallableMagicMock(spec=CoreConfig)
        coreConfigMock.cores = [["0"]]

        sysConfigMock = NonCallableMagicMock(spec=[SystemConfig, "isConstantMceChecking", "checkMCEs"])
        sysConfigMock.checkMCEs = MagicMock()
        sysConfigMock.testConfigs = [testConfig1, testConfig2]
        sysConfigMock.coreConfig = coreConfigMock

        params1 = [{"-a": "val1", "-b": ""}, {"-a": "va11"}]
        getNextParam1SideEffects = [None, StopIteration]
        params2 = [
            {"-a": "val1a", "-b": "no"},
            {"-a": "va11a"},
            {"-a": "val2a", "-b": "no"},
            {"-a": "val2a"},
        ]
        getNextParam2SideEffects = [None, None, None, StopIteration]

        paramFactoryInstance1 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance1.getParams.side_effect = params1
        paramFactoryInstance1.getNextParams.side_effect = getNextParam1SideEffects
        paramFactoryInstance2 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance2.getParams.side_effect = params2
        paramFactoryInstance2.getNextParams.side_effect = getNextParam2SideEffects
        paramFactoryMock.side_effect = [paramFactoryInstance1, paramFactoryInstance2]

        # Run
        testFactory = TestFactory(sysConfigMock)

        # Test
        testFactory.getNextTest()
        testMock.assert_called_with(params1[0], binaryPath1, 1, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[0], binaryPath2, 2, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params1[1], binaryPath1, 3, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[1], binaryPath2, 4, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[2], binaryPath2, 5, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        testFactory.getNextTest()
        testMock.assert_called_with(params2[3], binaryPath2, 6, coreConfigMock.cores[0], sysConfigMock.checkMCEs)
        self.assertRaises(StopIteration, testFactory.getNextTest)

    def testTwoTestDifferentSizesOfParams_MulitpleCoreConfig(self, testMock, paramFactoryMock):
        binaryPath1 = "/path/to/test1/binary"
        testName1 = "test1"
        binaryPath2 = "/path/to/test2/binary"
        testName2 = "test2"
        # Setup
        testConfig1 = NonCallableMagicMock(spec=TestConfig)
        testConfig1.name = testName1
        testConfig1.binary = binaryPath1

        testConfig2 = NonCallableMagicMock(spec=TestConfig)
        testConfig2.name = testName2
        testConfig2.binary = binaryPath2

        coreConfigMock = NonCallableMagicMock(spec=CoreConfig)
        coreConfigMock.cores = [[str(x)] for x in range(4)]

        sysConfigMock = NonCallableMagicMock(spec=[SystemConfig, "isConstantMceChecking", "checkMCEs"])
        sysConfigMock.checkMCEs = MagicMock()
        sysConfigMock.testConfigs = [testConfig1, testConfig2]
        sysConfigMock.coreConfig = coreConfigMock

        params1 = [{"-a": "val1", "-b": ""}] * 4 + [{"-a": "va11"}] * 4
        getNextParam1SideEffects = [None, StopIteration]  # for _ in range(1)]

        params2 = (
            ([{"-a": "val1a", "-b": "no"}] * 4)
            + ([{"-a": "va11a"}] * 4)
            + ([{"-a": "val2a", "-b": "no"}] * 4)
            + ([{"-a": "val2a"}] * 4)
        )
        getNextParam2SideEffects = [None if i < 3 else StopIteration for i in range(4)]

        paramFactoryInstance1 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance1.getParams.side_effect = params1
        paramFactoryInstance1.getNextParams.side_effect = getNextParam1SideEffects
        paramFactoryInstance2 = NonCallableMagicMock(spec=ParamFactory)
        paramFactoryInstance2.getParams.side_effect = params2
        paramFactoryInstance2.getNextParams.side_effect = getNextParam2SideEffects
        paramFactoryMock.side_effect = [paramFactoryInstance1, paramFactoryInstance2]

        # Run
        testFactory = TestFactory(sysConfigMock)

        # Test
        testNum = 0
        for i in range(max(len(params1), len(params2))):
            if i < len(params1):
                testNum += 1
                testFactory.getNextTest()
                testMock.assert_called_with(
                    params1[i], binaryPath1, testNum, coreConfigMock.cores[i % 4], sysConfigMock.checkMCEs
                )

            testNum += 1
            testFactory.getNextTest()
            testMock.assert_called_with(
                params2[i], binaryPath2, testNum, coreConfigMock.cores[i % 4], sysConfigMock.checkMCEs
            )
        self.assertRaises(StopIteration, testFactory.getNextTest)
