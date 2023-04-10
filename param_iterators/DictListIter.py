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
from param_iterators.ParamIter import ParamIter


class DictListIter(ParamIter):
    def __init__(self, valDict, name, subscribers=[]):
        logger.debug(f"Initializing {name} with {valDict}")
        self.count = 0
        self.valDict = valDict
        self.name = name
        self.maxCount = 0
        for key, val in valDict.items():
            self.maxCount += len(val)
        super().__init__(subscribers)

    def __iter__(self):
        return self

    def resetCount(self, resetSubs=False):
        self.count = 0
        super().resetCount(resetSubs)

    def current(self):
        logger.debug(f"Getting current {self.name} with count {self.count} max count: {self.maxCount}")
        if self.count >= self.maxCount:
            raise StopIteration

        keyLen = len(self.valDict.keys())
        key = [*self.valDict][self.count % keyLen]

        valOptLen = len(self.valDict[key])
        valOptIndex = int(self.count / keyLen) % valOptLen

        return key, self.valDict[key][valOptIndex]

    def __str__(self):
        return f"{self.name} {self.valDict}"
