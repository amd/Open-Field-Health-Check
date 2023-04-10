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

from param_iterators.BinaryIter import BinaryIter
from param_iterators.ListIter import ListIter
from param_iterators.ParamIter import ParamIter


class TestParamIter(TestCase):
    def setUp(self):
        pass

    def testListUpdateIter(self):
        # Setup
        vals = [x for x in range(5)]
        listIter = ListIter(vals, "testing list iter")

        # Run
        # only iterate to n-1 because the update at n will cause StopIteration
        for expected in vals[:-1]:
            self.assertEqual(listIter.current(), expected)
            listIter.update()

        self.assertEqual(listIter.current(), vals[-1])
        self.assertRaises(StopIteration, listIter.update)

    def testBinaryUpdateIter(self):
        # Setup
        binIter = BinaryIter("testing bin iter")
        # Run
        results = []
        results.append(binIter.current())
        binIter.update()
        results.append(binIter.current())
        # Test Results
        self.assertRaises(StopIteration, binIter.update)
        self.assertEqual(len(results), 2)
        self.assertTrue(True in results)
        self.assertTrue(False in results)

    def testParamIterUpdateWithSubscriber(self):
        # Setup
        mockIter = NonCallableMagicMock(spec=ParamIter)
        paramIter = ListIter([0], "single param iter", subscribers=[mockIter])

        # Run
        paramIter.update()

        # Check Results
        mockIter.update.assert_called_once()

    def testParamIterResetWithSubscriber(self):
        # Setup
        mockIter = NonCallableMagicMock(spec=ParamIter)
        paramIter = ListIter([0], "single param iter", subscribers=[mockIter])

        # Run
        paramIter.resetCount()

        # Check Results
        mockIter.resetCount.assert_not_called()

    def testParamIterResetWithSubscriber_resetSubs(self):
        # Setup
        mockIter = NonCallableMagicMock(spec=ParamIter)
        paramIter = ListIter([0], "single param iter", subscribers=[mockIter])

        # Run
        paramIter.resetCount(resetSubs=True)

        # Check Results
        mockIter.resetCount.assert_called_once()
