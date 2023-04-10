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

from param_iterators.BinaryIter import BinaryIter
from param_iterators.ListIter import ListIter


class ParamFactory:
    """Iterates through all parameters specified in the TestConfig

    Protected Attributes:
        _argIters: Dict of args to iterators
        _constantArgs: Dict of args to value that don't iterate
        _triggerIter: iter to


    Methods:
        getNextParams(): iterates the parameters
        getParams(): Returns the current parameters
    """

    def __init__(self, testConfig):
        self._argIters = {}
        self._constantArgs = {}
        prevIter = []
        for arg in testConfig.arguments:
            if not arg.isConstant:
                if arg.isFlag:
                    self._argIters[arg.cmdLineOption] = BinaryIter(arg.cmdLineOption, prevIter)
                else:
                    self._argIters[arg.cmdLineOption] = ListIter(arg.values, arg.cmdLineOption, prevIter)
                prevIter = [self._argIters[arg.cmdLineOption]]
            else:
                if arg.isFlag:
                    self._constantArgs[arg.cmdLineOption] = ""
                else:
                    self._constantArgs[arg.cmdLineOption] = arg.values[0]
        if prevIter:
            self._triggerIter = prevIter[0]
        else:
            self._triggerIter = ListIter([], "Test Trigger")

    def getNextParams(self):
        """Increments the parameters and sets the curParams to the
        newly updated params
        """
        self._triggerIter.update()

    def getParams(self):
        """Returns the current set of parameters"""
        curArgs = self._constantArgs.copy()
        for arg, curIter in self._argIters.items():
            if isinstance(curIter, BinaryIter):
                if curIter.current():
                    curArgs[arg] = ""
            else:
                curArgs[arg] = curIter.current()
        return curArgs
