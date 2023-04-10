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

from logger import logger
from param_factories.ParamFactory import ParamFactory
from param_iterators.ListIter import ListIter
from tests.Test import Test


class TestFactory:
    """Keeps track of ochestraiting the order of tests and serving up the next tests with parameters

    Protected Attributes:
        _testIter: ListIter that keeps track of what test to execute next
        _testFactoryDict: Tuple of execLocation and ParamIter, keeps track
            of all the test's ParamIters to iterate through all different
            parameters of each test
        _testCounter: int current test number
        _coreIter: core iterator that give the current core set to run on
        _checkMCEs: reference to SystemConfig checkMCEs method

    Methods:
        getNextTest: returns the next test to execute

    """

    def __init__(self, sysConfig):
        """inits the test dictionary

        Args:
            sysConfig: SystemConfig object with tests and configuration
        """
        self.__initTestDict(sysConfig)
        self._testCounter = 0
        self._coreIter = ListIter(items=sysConfig.coreConfig.cores, name="DivisionIter")
        self._testIter = ListIter(
            items=list(self._testFactoryDict.keys()), name="TestIter", subscribers=[self._coreIter]
        )
        self._checkMCEs = sysConfig.checkMCEs

    def __initTestDict(self, sysConfig):
        self._testFactoryDict = {}
        for testConfig in sysConfig.testConfigs:
            self._testFactoryDict[testConfig.name] = (testConfig.binary, ParamFactory(testConfig))
        logger.info(
            "TestFactoryDict has been initialized with the following tests: {}".format(self._testFactoryDict.keys())
        )

    def getNextTest(self):
        """Returns the next test to execute

        Raises:
            StopIteration: Raises when there are no more test to execute
            RuntimeError: Raises when a test is not supported
        """
        self._testCounter += 1
        useNextParams = False
        # The first test, we don't need to update the test
        if self._testCounter != 1:
            try:
                self._testIter.update()
                logger.debug("{}: Current test: {}".format(__name__, self._testIter.current()))
            except StopIteration:
                logger.debug("{}: Get next parameters".format(__name__))
                useNextParams = True

        if useNextParams:
            self._testIter.resetCount(resetSubs=True)
            removeTests = []
            for testName in self._testFactoryDict.keys():
                try:
                    self._testFactoryDict[testName][1].getNextParams()
                except StopIteration:
                    # Once test is finished iterating over all possible
                    # commands, remove the test from Test Iter
                    removeTests.append(testName)
                    logger.debug("{}: Remove test {}".format(__name__, removeTests))

            if len(removeTests) == len(self._testFactoryDict):
                raise StopIteration

            if len(removeTests) > 0:
                for test in removeTests:
                    del self._testFactoryDict[test]
                self._testIter = ListIter(
                    items=list(self._testFactoryDict.keys()),
                    name="Updated TestIter",
                    subscribers=self._testIter.subscribers,
                )

        testExecLoc, curTestFactory = self._testFactoryDict[self._testIter.current()]
        params = curTestFactory.getParams()

        test = Test(params, testExecLoc, self._testCounter, self._coreIter.current(), self._checkMCEs)
        return test
