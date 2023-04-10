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

import unittest
from subprocess import PIPE
from unittest.mock import MagicMock, call, patch

from tests.Test import Test


@patch("tests.Test.Popen", autospec=True)
@patch("tests.Test.logger", autospec=True)
class TestTestExecution(unittest.TestCase):
    def setUp(self):
        # Setup test parameters
        params = {
            "-a": "",
            "-b": "value1",
        }
        execLoc = "/path/to/exec"
        testNum = 19

        cores = [x for x in range(6)]

        self.checkMCEMock = MagicMock()
        self.checkMCEMock.return_value = []
        # Run item under test
        self.test = Test(params, execLoc, testNum, cores, self.checkMCEMock)

    def _getACFDetailString(self, core):
        return (
            "Test number {} on core {} return a non-zero exit code: 1, stdout: Failure occurred, stderr: This is the"
            " failure details".format(self.test._testNum, core)
        )

    def _getACFTuple(self, core):
        return (core, "Failure occurred", "This is the failure details", 1)

    def testCmdLineBuilding(self, poolMock, loggerMock):
        # Test results
        self.assertEqual(self.test._cmdLine, "/path/to/exec -a  -b value1")

    @patch("tests.Test.Pool", autospec=True)
    def testCmdExecZeroExit(self, poolMock, loggerMock, popenMock):
        # Setup
        poolMock.return_value.__enter__.return_value.starmap.return_value = [
            (core, "", "", 0) for core in self.test._cores
        ]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = True

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertTrue(testPassed)

    @patch("tests.Test.Pool", autospec=True)
    def testCmdExecNonZeroExit(self, poolMock, loggerMock, popenMock):
        # Setup
        poolMock.return_value.__enter__.return_value.starmap.return_value = [
            (core, "", "", 0) if core != 2 else self._getACFTuple(core) for core in self.test._cores
        ]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = True

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            True,
            [2],
            False,
            self.test._uptime,
            self._getACFDetailString(2),
            "",
        )

    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsPass64Core(self, poolMock, loggerMock, popenMock):
        self.test._cores = [i for i in range(64)]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [
            (core, "", "", 0) for core in self.test._cores
        ]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = True

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertTrue(testPassed)

    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsPass1Core(self, poolMock, loggerMock, popenMock):
        # Setup
        self.test._cores = [i for i in range(1)]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [
            (core, "", "", 0) for core in self.test._cores
        ]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = True

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertTrue(testPassed)

    # ACF Fails
    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsACF64Core(self, poolMock, loggerMock, popenMock):
        # Setup
        self.test._cores = [i for i in range(64)]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [
            (core, "", "", 0) if core != 33 else self._getACFTuple(core) for core in self.test._cores
        ]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0

        loggerMock.level.__ge__.return_value = True

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            True,
            [33],
            False,
            self.test._uptime,
            self._getACFDetailString(33),
            "",
        )

    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsACF1Core(self, poolMock, loggerMock, popenMock):
        self.test._cores = ["0"]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [self._getACFTuple(0)]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = False

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            True,
            [0],
            False,
            self.test._uptime,
            self._getACFDetailString(0),
            "",
        )

    # MCE Fails
    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsMCE64Core(self, poolMock, loggerMock, popenMock):
        # Setup
        self.test._cores = [i for i in range(64)]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [
            (core, "", "", 0) for core in self.test._cores
        ]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0

        loggerMock.level.__ge__.return_value = True

        self.checkMCEMock.return_value = ["This is MCE"]

        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            False,
            [],
            True,
            self.test._uptime,
            "",
            "This is MCE",
        )

    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsMCE1Core(self, poolMock, loggerMock, popenMock):
        self.test._cores = ["0"]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [(0, "", "", 0)]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = False

        self.checkMCEMock.return_value = ["This is MCE"]
        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            False,
            [],
            True,
            self.test._uptime,
            "",
            "This is MCE",
        )

    # More than one MCE
    @patch("tests.Test.Pool", autospec=True)
    def testTestResults2MCEs1Core(self, poolMock, loggerMock, popenMock):
        self.test._cores = ["0"]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [(0, "", "", 0)]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = False

        self.checkMCEMock.return_value = ["This is MCE1", "This is MCE2"]
        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            False,
            [],
            True,
            self.test._uptime,
            "",
            "This is MCE1;;This is MCE2",
        )

    # MCE & ACF
    @patch("tests.Test.Pool", autospec=True)
    def testTestResultsMCE_ACF1Core(self, poolMock, loggerMock, popenMock):
        self.test._cores = ["0"]
        poolMock.return_value.__enter__.return_value.starmap.return_value = [self._getACFTuple(0)]
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0
        loggerMock.level.__ge__.return_value = False

        self.checkMCEMock.return_value = ["This is MCE1", "This is MCE2"]
        # Run
        testPassed = self.test.execute()

        # Check Results
        self.assertFalse(testPassed)
        loggerMock.results.assert_called_with(
            self.test._testNum,
            self.test._cmdLine,
            self.test._cores,
            True,
            [0],
            True,
            self.test._uptime,
            self._getACFDetailString(0),
            "This is MCE1;;This is MCE2",
        )

    def testCallPopenWithNumactl(self, loggerMock, popenMock):
        # Setup
        popenMock.return_value.communicate.return_value = (b"", b"")
        popenMock.return_value.returncode = 0

        cmds = [
            call("numactl --physcpubind={} {}".format(core, self.test._cmdLine), shell=True, stdout=PIPE, stderr=PIPE)
            for core in self.test._cores
        ]
        loggerMock.level.__ge__.return_value = False

        # Run

        from multiprocessing.pool import Pool

        with patch.object(Pool, "starmap", new=lambda p, f, args: [f(cmd, core) for cmd, core in args]):
            self.test.execute()

        # Check Results
        popenMock.assert_has_calls(cmds, any_order=True)
