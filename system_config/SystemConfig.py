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

import atexit
import os
import resource
import shutil
from datetime import datetime
from subprocess import PIPE, Popen
from time import sleep

from logger import logger
from mce_read.MceCheck import MCECheck
from mce_read.MsrRegister import MSRRegister
from system_config.cpuinfo import CpuInfo


class SystemConfig:
    """Contains information about the System and  Test Configuration

    Attributes:
        runDir: Directory where `list_core.sh` is located
        logDir: Directory containing all log files
        checkDMESG: Boolean to signify if DMESG is checked for MCEs
        testConfigs: List of TestConfig
        cpuInfo: CpuInfo containing information about the core configuration
        coreConfig: Configurations on how to allcoate the run of the tests on the CPU
        isConstantMceChecking: Boolean to determine if we should check for MCE after every command
        _mceChecker: reads msr registers to check for MCEs with the `check()` instance method

    Methods:
        clearMCEs(): Tells OS to flush MCEs
        checkMCEs()->[]: Check for MCEs and returns a list of all MCEs detected
    Protected Methods:
        _importSettings(configData)->None
        _importTests(configData)->None
        _importCoreConfig(configData)->None
        _checkRoot()->None
        _checkDependencies()->None
        _importConfig(configPath)->None
        _importJson(configPath)->dict
        _importYml(configPath)->dict
        _setCheckInterval()->None
        _setResourceLimits()->None
    """

    def __init__(
        self,
        config,
        runDir,
        logDir,
    ):
        """Saves config file in a structured way

        Handles all the different options in the command line, config file,
        and checks the system meets the requirements in order for the framework
        to correctly function

        Args:
            config: string of the location of the config YAML or JSON file
            runDir: string of directory containing `list_cores.sh`

        Raises:
            RuntimeError: An error has occurred reading the configuration
                or with the system configuration
        """

        self._checkDependencies()

        self.startTime = datetime.now()

        self.cpuInfo = CpuInfo()

        self.testConfigs = []

        self.runDir = runDir
        self.logDir = logDir

        self._setCheckInterval()
        atexit.register(self._setCheckInterval, 10000)

        self._importConfig(config)

        self._setupMCEDetection()

        # debug printing settings
        logger.debug("La Hacienda input variables:")
        logger.debug("Run Directory: {}".format(self.runDir))
        logger.debug("Start Time: {}".format(self.startTime))
        logger.debug("Log Directory: {}".format(self.logDir))

    def checkMCEs(self, force=False):
        if self.isConstantMceChecking or force:
            return self._mceChecker.check()
        else:
            return []

    def clearMCEs(self):
        """Tells the OS to read any MCE's and clear after reading.

        Changes check interval to 1, sleeps, then sets to 10000 to
        flush MCEs then prevent MCEs from being caught and cleared during execution
        Disclaimer: There is currently a kernel bug that makes the MCE dissapear,
        but this is a known issue and currently being worked.
        """
        logger.warning("Flushing MCEs. This will cause previous MCEs to show up in the OS's DMESG")
        logger.warning(
            "On earlier kernels, this does not function as intended and will cause the OS to `clear` the MCE without"
            " outputing to DMESG"
        )
        self._setCheckInterval(1)
        sleep(2)
        self._setCheckInterval()

    def _importSettings(self, configData):
        """Imports the tool level settings

        Args:
            configData: Dictionary from config file definied in README.md
        """
        # Log Directory
        if not self.logDir:
            self.logDir = configData["Log_Directory"]
        logger.set_log_dir(self.logDir)

        # Logging Level
        if "Log_Level" in configData:
            if configData["Log_Level"] == "Bare":
                logger.set_log_level(logger.BARE)
            elif configData["Log_Level"] == "All":
                logger.set_log_level(logger.ALL)
            elif configData["Log_Level"] == "Excess":
                logger.set_log_level(logger.EXCESS)
            elif configData["Log_Level"] == "Debug":
                logger.set_log_level(logger.DEBUG)
            else:
                logger.set_log_level(logger.DEBUG)
                logger.warning("Log level '{}' invalid".format(configData["Log_Level"]))
                logger.warning("Valid log levels are: Bare, All, Excess, or Debug")
                logger.warning("Setting Log Level to 'DEBUG'")
        else:
            # Default log level if not provied
            logger.set_log_level(logger.ALL)
            logger.warning("No log level specified in configuration or command line setting log level to default")

        logger.info("Set log level to: {}".format(logger.level))

        # Run Directory
        if not self.runDir:
            self.runDir = configData["Run_Directory"]

        if "Constant_MCE_Checking" in configData:
            self.isConstantMceChecking = configData["Constant_MCE_Checking"]
        else:
            # Default is to check after every command
            self.isConstantMceChecking = True

        if self.isConstantMceChecking:
            logger.warning(
                "Checking for MCE's after every command will result in MCE's being logged in the output for the failing"
                " command AND all commands after, because the MCE will not be cleared. The MCE is not cleared to allow"
                " the OS to catch the MCE"
            )

    def _importTests(self, configData):
        """Import and Test arguments in configuration file

        Takes the configuration file and verifies that is correctly formed

        Args:
            configData: Dictionary of the sturture of the configuration file

        Raises:
            RuntimeError: A unexpected configuration was specifed.
        """

        try:
            # General Test Data:
            if "Tests" in configData:
                for test in configData["Tests"]:
                    self.testConfigs.append(TestConfig(test))
            if len(self.testConfigs) == 0:
                raise RuntimeError("No tests found in configuration. See README for help.")
        except KeyError as e:
            logger.error("Failed to get required YAML Attribute: {}".format(e.args[0]))
            raise RuntimeError("Settings YAML file is incorrect")

    def _importCoreConfig(self, configData):
        """Imports all the core configuration"""
        try:
            coreConfig = configData["Core_Config"]
        except KeyError:
            logger.error("Missing 'Core_Config' option in configuration file.")
            raise RuntimeError("Incorrect configuration file. Please see 'README.md' for required format")
        self.coreConfig = CoreConfig(coreConfig, self.cpuInfo, self.runDir)

    def _checkRoot(self):
        # Check root user
        rootCmd = "whoami"
        p = Popen(rootCmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        if returncode != 0 or stdout.decode("utf-8").strip("\n") != "root":
            raise RuntimeError("You must execute the script as root to use MSR options, exiting...")

    def _checkDependencies(self):
        """Checks for recommended dependencies for La Hacienda

        Dependencies that are required will raise a RuntimeError others will log a warning

        Raises:
            RuntimeError: When a required dependency is not met
        """
        # Check EDAC module support
        edacCmd = "lsmod | grep -i -c edac"
        p = Popen(edacCmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        if (returncode != 0 or int(stdout.decode("utf-8")) == 0) and not os.path.isdir(
            "/sys/devices/system/edac/mc/mc0"
        ):
            raise RuntimeError("No kernel module found for edac (Error Detection and Correction) found, exiting...")

        # Virtual Address space randomization disabled
        vrandCmd = "cat /proc/sys/kernel/randomize_va_space"
        p = Popen(vrandCmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        if returncode != 0 or int(stdout.decode("utf-8")) != 0:
            logger.warning("/proc/sys/kernel/randomize_va_space not set to 0 (disabled)")

        # Check fatal signals enabled
        fatalSigCmd = "cat /proc/sys/kernel/print-fatal-signals"
        p = Popen(fatalSigCmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        if returncode != 0 or int(stdout.decode("utf-8").strip("\n")) != 1:
            logger.warning("/proc/sys/kernel/print-fatal-signals not set to 1 (enabled)")

        # Check NUMABALANCING
        numaCmd = "cat /proc/sys/kernel/numa_balancing"
        p = Popen(numaCmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        if returncode != 0 or int(stdout.decode("utf-8")) != 0:
            logger.warning("/proc/sys/kernel/numa_balancing not set to 0 (disabled)")

        # Check NUMACTL
        numaCtlCmd = "numactl -s"
        p = Popen(numaCtlCmd, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        returncode = p.returncode
        if returncode != 0:
            raise RuntimeError(
                "'numactl' is not in your $PATH variable. Please ensure 'numactl' is installed and in $PATH"
            )

    def _importConfig(self, configPath):
        """determinies what configuration input the user is using and calls the function
        to import that configuration as a dictionary

        Args:
            configPath: path to configuration file
        """
        configDict = {}
        if os.path.isfile(configPath):
            # Configuration is either yaml or json file
            fileExt = os.path.splitext(configPath)[1]
            if fileExt == ".json":
                configDict = self._importJson(configPath)
            elif fileExt == ".yaml" or fileExt == ".yml":
                configDict = self._importYml(configPath)
            else:
                raise RuntimeError(
                    "La Hacienda only supports YAML or JSON files, however filename is {}".format(configPath)
                )
        else:
            # Configuration is a JSON string
            import json

            try:
                configDict = json.loads(configPath)
            except json.JSONDecodeError as e:
                raise RuntimeError("Failed to load JSON settings string: {}, {}".format(configPath, e))

        # Import the settings:
        try:
            self._importSettings(configDict)
            self._importTests(configDict)
            self._importCoreConfig(configDict)
        except KeyError as e:
            raise RuntimeError(
                "Failed to import configuration file, please ensure you have specified all required Parameters in"
                " configuration file. {}".format(e)
            )

    def _importJson(self, configPath):
        """Imports JSON config file"""
        import json

        try:
            with open(configPath) as jsonFile:
                jsonData = json.load(jsonFile)
        except json.JSONDecodeError as e:
            raise RuntimeError("Failed to load JSON settings file: {}, {}".format(configPath, e))
        return jsonData

    def _importYml(self, ymlPath):
        """Imports YAML config file"""
        try:
            import yaml
        except ImportError:
            raise RuntimeError("Unable to import PyYAML. Please ensure you have installed PyYAML with pip")

        try:
            with open(ymlPath) as ymlFile:
                ymlData = yaml.safe_load(ymlFile)
        except yaml.YAMLError as e:
            raise RuntimeError("Failed to load YAML settings file: {}, {}".format(ymlPath, e))
        return ymlData

    def _setCheckInterval(self, intervalVal: int = 1000000):
        """
        Set machine check interval very high so it doesn't interfere with Tim's test catching MCEs
        """
        checkIntervalFile = "/sys/devices/system/machinecheck/machinecheck0/check_interval"
        with open(checkIntervalFile, "w") as mc:
            mc.write(str(intervalVal))

    def _setResourceLimits(self):
        """Sets resource limits

        unable to set LOCKS or NOFILE limits
        """
        limit = (resource.RLIM_INFINITY, resource.RLIM_INFINITY)
        resource.setrlimit(resource.RLIMIT_AS, limit)
        resource.setrlimit(resource.RLIMIT_CORE, limit)
        resource.setrlimit(resource.RLIMIT_CPU, limit)
        resource.setrlimit(resource.RLIMIT_DATA, limit)
        resource.setrlimit(resource.RLIMIT_FSIZE, limit)
        # resource.setrlimit(resource.RLIMIT_LOCKS, limit)
        resource.setrlimit(resource.RLIMIT_MEMLOCK, limit)
        resource.setrlimit(resource.RLIMIT_NPROC, limit)
        resource.setrlimit(resource.RLIMIT_RSS, limit)
        resource.setrlimit(resource.RLIMIT_SIGPENDING, limit)
        resource.setrlimit(resource.RLIMIT_STACK, limit)

        # flimit = (10000000, 10000000)
        # resource.setrlimit(resource.RLIMIT_NOFILE, flimit)

    def _setupMCEDetection(self):
        """Sets up the _mceChecker to check for MCEs after each command"""
        self._setResourceLimits()
        msrReg = MSRRegister(self.cpuInfo.num_logical_cores)
        self._mceChecker = MCECheck(msrReg)


class CoreConfig:
    """Contains the configuration where to run the tests.

    Attributes:
        sockets: list of values for sockets
        smt: list of values for SMT, valid values are boolean
        cores: list of values for Cores division to run each time.

        _listCoreFile: location of the list_cores.sh file

    Methods:
        _getCoreList(partition, threadList, sockets): returns the list of cores for the division

        _getItemAsList(item): options that can be either a boolean or list and converts it to the appropriate format
        _checkConfigIntegrity(): ensures that there are two sockets if two sockets are specified the Core_Config
    """

    def __init__(self, configDict, cpuInfo, runDir):
        """Checks vality of configDict from configDict

        Options looking for in configDict
            Sockets: (optional, defaults to all)
            SMT: bool
            All: bool
            Halfs: bool/list of ints
            Quarters: bool/list of ints
            CCDs: bool/list of ints
            Cores: bool/list of ints

        Args:
            configDict: Dictionary containing all required keys and values for the Core_Config
            cpuInfo: CPUInfo class containing CPU Topology
            runDir: directory containing list_cores.sh

        Raises:
            RuntimeError: if a configuration doesn't have the required keys or format
        """
        self.cpuInfo = cpuInfo

        # SMT
        try:
            self.smt = configDict["SMT"]
        except KeyError:
            raise RuntimeError("Incorrect config file format, 'SMT' requried to be specified in 'Core_Config'.")

        self._checkConfigIntegrity(configDict)

        self._listCoreFile = "{}/list_cores.sh".format(runDir)
        self.sockets = []
        if "Sockets" in configDict:
            sockets = self._getItemAsList(configDict["Sockets"])
            for s in sockets:
                if isinstance(s, list) and len(s) == 2:
                    # already vetted that sockets only contains the correct values
                    # in the _checkConfigIntegrity function
                    self.sockets.append("all")
                else:
                    self.sockets.append(str(s))
        else:
            logger.info("Sockets not specified in configuration file, setting to all")
            self.sockets = ["all"]

        self.cores = []
        coreDivisions = []
        threadlist = [0, 1] if self.smt else [0]

        if "All" in configDict and configDict["All"]:
            if not isinstance(configDict["All"], bool):
                raise RuntimeError(
                    "Unknown type for 'All' division in 'Cores_Config'. Only, boolean values are supported"
                )
            coreDivisions.append("all")
        if "Halfs" in configDict:
            if isinstance(configDict["Halfs"], bool) and configDict["Halfs"]:
                coreDivisions.append("half0")
                coreDivisions.append("half1")
            elif isinstance(configDict["Halfs"], list):
                for num in configDict["Halfs"]:
                    if num > 1 or num < 0:
                        raise RuntimeError(
                            "Invalid half specified '{}' in 'Core_Config'. There are only 2 halfs in a whole. Valid"
                            " values are (0,1)".format(num)
                        )
                    coreDivisions.append("half{}".format(num))
            else:
                raise RuntimeError(
                    "Unknown type for 'Halfs' division in 'Cores_Config'. Only, list and boolean values are supported"
                )
        if "Quarters" in configDict:
            if isinstance(configDict["Quarters"], bool) and configDict["Quarters"]:
                coreDivisions.append("quart0")
                coreDivisions.append("quart1")
                coreDivisions.append("quart2")
                coreDivisions.append("quart3")
            elif isinstance(configDict["Quarters"], list):
                for num in configDict["Quarters"]:
                    if num > 3 or num < 0:
                        raise RuntimeError(
                            "Invalid Quarter specified '{}' in 'Core_Config'. There are only 4 quarters in a whole"
                            .format(num)
                        )
                    coreDivisions.append("quart{}".format(num))
            else:
                raise RuntimeError(
                    "Unknown type for Quarters division in 'Cores_Config'. Only, list and boolean values are supported"
                )
        if "CCDs" in configDict:
            if isinstance(configDict["CCDs"], bool) and configDict["CCDs"]:
                for num in range(self.cpuInfo.ccds_per_socket):
                    coreDivisions.append(str(num))
            elif isinstance(configDict["CCDs"], list):
                for num in configDict["CCDs"]:
                    if num > self.cpuInfo.ccds_per_socket:
                        raise RuntimeError(
                            "Invalid CCD specified '{}' in 'Core_Config'. There are only {} CCDs in a socket".format(
                                num, self.cpuInfo.ccds_per_socket
                            )
                        )
                    coreDivisions.append(str(num))
            else:
                raise RuntimeError(
                    "Unknown type for 'CCDs' division in 'Cores_Config'. Only, list and boolean values are supported"
                )
        for socket in self.sockets:
            for corediv in coreDivisions:
                self.cores.append(self._getCoreList(corediv, threadlist, socket))

        if "Cores" in configDict:
            if isinstance(configDict["Cores"], bool) and configDict["Cores"]:
                for num in range(self.cpuInfo.num_logical_cores):
                    self.cores.append([str(num)])
            elif isinstance(configDict["Cores"], list):
                for core in configDict["Cores"]:
                    if core >= self.cpuInfo.num_logical_cores:
                        raise RuntimeError(
                            "Invalid Core specified '{}' in 'Core_Config'. There are only {} logical cores".format(
                                core, self.cpuInfo.num_logical_cores
                            )
                        )
                    self.cores.append([str(core)])

        if not self.cores and not self.coreDivisions:
            raise RuntimeError(
                "Incorrect configuration file format. It is required to specify at least one core division or core"
                " specified to run tests."
            )

    def _getItemAsList(self, item):
        if isinstance(item, bool):
            return [item]
        elif isinstance(item, list):
            return item
        else:
            raise RuntimeError("Incorrect 'Core_Config' format in configuration file.")

    def _getCoreList(self, partition, threadList, sockets):
        """Uses the CPUInfo topology to create a core list for given divisions

        Returns a list of cores
        Args:
            partition: str with options: all, half0, half1, quart0, quart1, quart2, quart3, 0, 1, 2, 3, 4, 5, 6...
                where the individual numbers are the CCD numbers.
            threadList: list of threads,
            sockets: string, either 0, 1 or all
        """
        coreList = ""
        if not os.path.isfile(self._listCoreFile):
            raise RuntimeError(
                "{} does not exist, please ensure you specified the correct Run_Directory.".format(self._listCoreFile)
            )
        for thread in threadList:
            cmd = (
                "{} {} ".format(self._listCoreFile, self.cpuInfo.cores_per_ccd)
                + "{} {} {} ".format(self.cpuInfo.ccds_per_socket, self.cpuInfo.num_sockets, partition)
                + "{} {}".format(thread, sockets)
            )
            p = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            returncode = p.returncode
            cmdOutput = stdout.decode("utf-8")
            if returncode != 0:
                raise RuntimeError("list cores command failed to execute. {}".format(stderr.decode("utf-8")))
            coreList += str(cmdOutput).strip("\n") + " "

        return coreList.split()

    def _checkConfigIntegrity(self, config):
        """Ensures that the 'Cores_Config' section matches the CPU Topology

        Checks if SMT is enabled, it's also enabled on the CPU
        Number of CCDs isn't more than the number of CCDs on the CPU
        Cores isn't more than the number of cores on the CPU
        Sockets is only 0, 1, or [0, 1]

        Args:
            config: the 'Cores_Config' option dictionary
        """

        if self.smt and not self.cpuInfo.is_smt_enabled:
            raise RuntimeError("Configuration File specifies use SMT, but the CPU doesn't have SMT enabled")

        # CCDs
        if "CCDs" in config:
            if isinstance(config["CCDs"], list):
                for ccd in config["CCDs"]:
                    if ccd >= self.cpuInfo.ccds_per_socket:
                        raise RuntimeError(
                            "Configuration File specifies CCD {}, but the CPU only has {}".format(
                                ccd, self.cpuInfo.ccds_per_socket
                            )
                        )
            elif not isinstance(config["CCDs"], bool):
                raise RuntimeError("'CCDs' configuration item can only be a list or boolean")
        # Cores
        if "Cores" in config:
            if isinstance(config["Cores"], list):
                for core in config["Cores"]:
                    if core >= self.cpuInfo.num_physical_cores:
                        raise RuntimeError(
                            "Configuration File specifies Core {}, but the CPU only has {}".format(
                                core, self.cpuInfo.num_physical_cores
                            )
                        )
            elif not isinstance(config["Cores"], bool):
                raise RuntimeError("Cores Configuration item can only be a list or boolean")

        # Sockets
        if "Sockets" in config:
            if not isinstance(config["Sockets"], list):
                raise RuntimeError("'Sockets' configuration item can only be a list")
            for s in config["Sockets"]:
                if isinstance(s, list):
                    if len(s) != 2 or 0 not in s or 1 not in s or self.cpuInfo.num_sockets != 2:
                        raise RuntimeError(
                            "The only valid options for 'Socket' configuration item are 0, 1, or [0,1] given a  2P"
                            f" system, '{s}' was provided in the configuration file."
                        )
                elif s + 1 > self.cpuInfo.num_sockets:
                    raise RuntimeError(
                        f"The configuration file specifies more sockets than are availble on the system. Socket {s} is"
                        f" specified, however the system only has {self.cpuInfo.num_sockets} active sockets"
                    )


class TestConfig:
    """Contains the configuration for each test

    Attributes:
        name: string that defines the name of the test
        binary: path to test binary
        arguments: list of TestConfigArguments for test to use
    """

    def __init__(self, config):
        """parses the config dictionary into a class object

        Args:
            config: config dictionary

        Raises:
            RuntimeException: When the test doesn't have the required format
        """
        try:
            self.name = config["Name"]
            self.binary = os.path.expandvars(config["Binary"])
            if not os.path.isfile(self.binary) and not shutil.which(self.binary):
                raise RuntimeError("Binary path '{}' specified for {} does not exist".format(self.binary, self.name))
            self.arguments = []
        except KeyError as e:
            raise RuntimeError("Configuration File's Test does not have expected values. {}".format(e))
        try:
            for arg in config["Args"]:
                self.arguments.append(TestArgConfig(arg))
        except KeyError:
            logger.warning(
                "There are no arguments for test '{}', ensure you don't require arguemnts for this binary".format(
                    self.name
                )
            )


class TestArgConfig:
    """Stores the arguments and values specified in the configuration file

    Attributes:
        cmdLineOption: string of the complete cmd line flag
            ex: `--run` or `-a
        values: list of possible values for the argument
        isConstant: boolean to determine if you want the argument to always show
            up in cmd line
        isFlag: boolean to determine if the argument is just a flag and
            no value associated with arg
    """

    def __init__(self, arg):
        """Parses the arg dictionary

        Args:
            name: string of name of arg specified in config file
            arg: the arg dictionary from the config file

        Raises:
            RuntimeError: if the arg dictionary is missing a key or malformed
        """

        self.name = list(arg.keys())[0]
        self.values = []
        argData = arg[self.name]
        try:
            self.isConstant = False if "Constant" not in argData else argData["Constant"]
            self.isFlag = False if "Flag" not in argData else argData["Flag"]
            self.cmdLineOption = argData["Option"]
            if not self.isFlag:
                self.values = argData["Values"]
        except KeyError as e:
            raise RuntimeError("Configuration File's Test Args does not have expected values. {}".format(e))
        # Check Types
        if not isinstance(self.values, list):
            raise TypeError("The 'Values' option is required to be a list, even for a constant argument.")

        # Ensure constant and flag contraints are valid
        if self.isConstant and len(self.values) > 1:
            raise RuntimeError(
                "Configuration File's Test Arg '{}' is incorrect. An argument cannot be constant and have multiple"
                " values. {}".format(self.name, self.values)
            )
        if self.isFlag and "Values" in argData and len(argData["Values"]) > 0:
            raise RuntimeError(
                "Configuration File's Test Arg '{}' is incorrect. An argument cannot be a flag and have values".format(
                    self.name
                )
            )
