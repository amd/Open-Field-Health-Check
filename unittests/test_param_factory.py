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
from unittest.mock import NonCallableMagicMock

from param_factories.ParamFactory import ParamFactory
from system_config.SystemConfig import TestArgConfig, TestConfig


class TestParamFactory(TestCase):
    def setUp(self):
        pass

    def testConstantParam(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        constArg = NonCallableMagicMock(spec=TestArgConfig)
        constArg.isFlag = False
        constArg.isConstant = True
        constArg.cmdLineOption = "-a"
        constArg.values = ["value_a"]
        testConfig.arguments = [constArg]

        # Run
        factory = ParamFactory(testConfig)
        params = factory.getParams()

        # Test Results
        self.assertEqual(params, {"-a": "value_a"})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testConstantFlagParam(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        constFlagArg = NonCallableMagicMock(spec=TestArgConfig)
        constFlagArg.isFlag = True
        constFlagArg.isConstant = True
        constFlagArg.cmdLineOption = "-b"
        testConfig.arguments = [constFlagArg]

        # Run
        factory = ParamFactory(testConfig)
        params = factory.getParams()

        # Test Results
        self.assertEqual(params, {"-b": ""})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testFlagParam(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        flagArg = NonCallableMagicMock(spec=TestArgConfig)
        flagArg.isFlag = True
        flagArg.isConstant = False
        flagArg.cmdLineOption = "-b"
        testConfig.arguments = [flagArg]

        # Run
        factory = ParamFactory(testConfig)
        params = []
        # True case
        params.append(factory.getParams())
        # False case
        factory.getNextParams()
        params.append(factory.getParams())

        # Test Results
        self.assertEqual(params[0], {"-b": ""})
        self.assertEqual(params[1], {})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testListParam(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        listArg = NonCallableMagicMock(spec=TestArgConfig)
        listArg.isFlag = False
        listArg.isConstant = False
        listArg.cmdLineOption = "-a"
        listArg.values = ["val1", "val2", "val3"]
        testConfig.arguments = [listArg]

        # Run
        factory = ParamFactory(testConfig)
        params = []
        # val1
        params.append(factory.getParams())
        # val2
        factory.getNextParams()
        params.append(factory.getParams())
        # val3
        factory.getNextParams()
        params.append(factory.getParams())

        # Test Results
        self.assertEqual(params[0], {"-a": "val1"})
        self.assertEqual(params[1], {"-a": "val2"})
        self.assertEqual(params[2], {"-a": "val3"})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testNoParam(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        testConfig.arguments = []

        # Run
        factory = ParamFactory(testConfig)
        params = factory.getParams()

        # Test Results
        self.assertEqual(params, {})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testFlagAndListParams(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        # list
        listArg = NonCallableMagicMock(spec=TestArgConfig)
        listArg.isFlag = False
        listArg.isConstant = False
        listArg.cmdLineOption = "-a"
        listArg.values = ["val1", "val2", "val3"]

        # flag
        flagArg = NonCallableMagicMock(spec=TestArgConfig)
        flagArg.isFlag = True
        flagArg.isConstant = False
        flagArg.cmdLineOption = "-b"

        testConfig.arguments = [listArg, flagArg]

        # Run
        factory = ParamFactory(testConfig)
        params = []
        # val1
        params.append(factory.getParams())
        # val2
        factory.getNextParams()
        params.append(factory.getParams())
        # val3
        factory.getNextParams()
        params.append(factory.getParams())
        # val4
        factory.getNextParams()
        params.append(factory.getParams())
        # val5
        factory.getNextParams()
        params.append(factory.getParams())
        # val6
        factory.getNextParams()
        params.append(factory.getParams())

        # Test Results
        self.assertEqual(params[0], {"-a": "val1", "-b": ""})
        self.assertEqual(params[1], {"-a": "val1"})
        self.assertEqual(params[2], {"-a": "val2", "-b": ""})
        self.assertEqual(params[3], {"-a": "val2"})
        self.assertEqual(params[4], {"-a": "val3", "-b": ""})
        self.assertEqual(params[5], {"-a": "val3"})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testConstantFlagAndListParams(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        # list
        listArg = NonCallableMagicMock(spec=TestArgConfig)
        listArg.isFlag = False
        listArg.isConstant = False
        listArg.cmdLineOption = "-a"
        listArg.values = ["val1", "val2", "val3"]

        # flag
        flagArg = NonCallableMagicMock(spec=TestArgConfig)
        flagArg.isFlag = True
        flagArg.isConstant = True
        flagArg.cmdLineOption = "-b"

        testConfig.arguments = [listArg, flagArg]

        # Run
        factory = ParamFactory(testConfig)
        params = []
        # val1
        params.append(factory.getParams())
        # val2
        factory.getNextParams()
        params.append(factory.getParams())
        # val3
        factory.getNextParams()
        params.append(factory.getParams())

        # Test Results
        self.assertEqual(params[0], {"-a": "val1", "-b": ""})
        self.assertEqual(params[1], {"-a": "val2", "-b": ""})
        self.assertEqual(params[2], {"-a": "val3", "-b": ""})
        self.assertRaises(StopIteration, factory.getNextParams)

    def testThreeListParams(self):
        # Setup
        testConfig = NonCallableMagicMock(spec=TestConfig)
        # list 1
        listArg1 = NonCallableMagicMock(spec=TestArgConfig)
        listArg1.isFlag = False
        listArg1.isConstant = False
        listArg1.cmdLineOption = "-a"
        listArg1.values = ["val1", "val2"]
        # list 2
        listArg2 = NonCallableMagicMock(spec=TestArgConfig)
        listArg2.isFlag = False
        listArg2.isConstant = False
        listArg2.cmdLineOption = "-b"
        listArg2.values = ["val3", "val4"]
        # list 3
        listArg3 = NonCallableMagicMock(spec=TestArgConfig)
        listArg3.isFlag = False
        listArg3.isConstant = False
        listArg3.cmdLineOption = "--last"
        listArg3.values = ["val5", "val6"]

        testConfig.arguments = [listArg1, listArg2, listArg3]

        # Run
        factory = ParamFactory(testConfig)
        params = []
        # val1
        params.append(factory.getParams())
        # val2
        factory.getNextParams()
        params.append(factory.getParams())
        # val3
        factory.getNextParams()
        params.append(factory.getParams())
        # val4
        factory.getNextParams()
        params.append(factory.getParams())
        # val5
        factory.getNextParams()
        params.append(factory.getParams())
        # val6
        factory.getNextParams()
        params.append(factory.getParams())
        # val7
        factory.getNextParams()
        params.append(factory.getParams())
        # val8
        factory.getNextParams()
        params.append(factory.getParams())

        # Test Results
        self.assertEqual(params[0], {"-a": "val1", "-b": "val3", "--last": "val5"})
        self.assertEqual(params[1], {"-a": "val1", "-b": "val3", "--last": "val6"})
        self.assertEqual(params[2], {"-a": "val1", "-b": "val4", "--last": "val5"})
        self.assertEqual(params[3], {"-a": "val1", "-b": "val4", "--last": "val6"})
        self.assertEqual(params[4], {"-a": "val2", "-b": "val3", "--last": "val5"})
        self.assertEqual(params[5], {"-a": "val2", "-b": "val3", "--last": "val6"})
        self.assertEqual(params[6], {"-a": "val2", "-b": "val4", "--last": "val5"})
        self.assertEqual(params[7], {"-a": "val2", "-b": "val4", "--last": "val6"})
        self.assertRaises(StopIteration, factory.getNextParams)
