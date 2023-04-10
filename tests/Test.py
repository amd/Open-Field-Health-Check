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

from multiprocessing import Pool
from subprocess import PIPE, Popen

from logger import logger


def execTestOnCore(cmdLine, core):
    """Execute Test on one core
    Top level function for Pickability
    """
    cmdLine = "numactl --physcpubind={} {}".format(core, cmdLine)
    p = Popen(cmdLine, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    return core, stdout.decode("utf-8"), stderr.decode("utf-8"), p.returncode


class Test:
    """Takes care of pretest setup execution of the test, and posttest clean-up and MCE logging

    Protected Attributes:
        _testNum: int: Test number being executed in La Hacienda run
        _cmdLine: str: The command line without numactl
        _cores: list[int]: set of all the cores to execute commandline on
        _uptime: str: system uptime
        _checkMCEs: reference to SystemConfig's checkMCE method

    Methods:
        execute()->bool: returns boolean representing if the test passed.
            this will run _pretest setup and _posttest teardown. If you extend
            the test class you can inherit these methods to provide more setup or teardown

    Protected Methods:
        _buildCmdLine(execLoc, paramDict, coreGroup)->None:
        _posttest(stdout, stderr, returncode)->bool: Returns if the test passed. Logs the output. Any aditional cleanup
        _pretest()->None: logs the command line being executed
        _checkTestResults()->bool:
    """

    def __init__(self, paramDict, execLoc, testNum, coreGroup, checkMCEs):
        """
        Args:
            paramDict: A dictionary containing all params and their values
            execLoc: the location of the executable
            logHeading: The heading to put into the log file
            testNumber: The number of the test in the run
            coreGroup: List of cores to run the test on simultaniously
        """
        self._testNum = testNum
        self._cores = coreGroup
        self._buildCmdLine(execLoc, paramDict)
        self._uptime = ""
        self._checkMCEs = checkMCEs

    def execute(self):
        """Run pretest setup, executes test, and posttest detection and cleanup"""

        self._pretest()

        with Pool(len(self._cores)) as pool:
            res = pool.starmap(execTestOnCore, [(self._cmdLine, str(c)) for c in self._cores])

        return self._posttest(res)

    def _pretest(self):
        """Run any pretest setup and logging"""
        if logger.level >= logger.EXCESS:
            # log cmd number
            logger.debug("Command Number: {}".format(self._testNum))

            # log time
            timeCmd = "cat /proc/uptime"
            p = Popen(timeCmd, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            output = stdout.decode("utf-8")
            self._uptime = output.split(" ")[0]
        logger.cmd(
            self._testNum,
            self._cmdLine,
            self._cores,
            self._uptime,
        )

    def _posttest(self, results):
        """Logs output and any cleanup needed"""
        failingACFCores = []
        acfDetails = []
        for core, stdout, stderr, returncode in results:
            logger.debug(
                "CMD#: {}, CORE: {}, STDOUT: {}, STDERR: {}, RETURNCODE: {}".format(
                    self._testNum, core, stdout, stderr, returncode
                )
            )
            if returncode != 0:
                details = "Test number {} on core {} return a non-zero exit code: {}, stdout: {}, stderr: {}".format(
                    self._testNum, core, returncode, stdout, stderr
                )
                logger.error(details)
                acfDetails.append(details)
                failingACFCores.append(core)

        mces = self._checkMCEs()

        isACF = bool(failingACFCores)
        logger.results(
            self._testNum,
            self._cmdLine,
            self._cores,
            isACF,
            failingACFCores,
            bool(mces),
            self._uptime,
            ";".join(acfDetails),
            ";;".join([str(m) for m in mces]),
        )

        return (not isACF) and (not mces)

    def _buildCmdLine(self, execLoc, params):
        """Is call from the init fuction and sets the command line
        of this test to the cmdLine variable
        """
        self._cmdLine = execLoc
        for arg, value in params.items():
            self._cmdLine += " {} {}".format(arg, value)
