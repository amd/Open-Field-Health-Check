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

import logging
import os
from logging.handlers import RotatingFileHandler


class logger:
    """Logger singleton that takes care of logging the results, warnings, and errors to the appropriate locations

    Attributes:
        level: an integer representation of the log level to log
        log_dir: the directory to output all the log files

        BARE: No warnings, info, or debug messages. Only output file
        ALL: Output file and logs warnings to stream
        EXCESS: Output file and logs info to stream
        DEBUG: Output file and logs debug messages to debug file

    Static Methods:
        log_level_help_str(): returns a string that defines the differt log levels

    Class Methods:
        set_log_level(int): sets log level
        set_log_dir(str): sets the log directory and creates it if it doesn't exist

        debug(msg): log a debugging message
        info(msg): log an info message
        warning(msg): log a warning message
        error(msg): log an error message
        critical(msg): log a critical message
        results(cls,cmdNum,cmdLine,cores,isACF,acfFailingcores,isMCE,sysUptime,acfDetails,mceDetails):
            log a test result to the results file

        cmd(cmdNum, cmdLine, sysUptime): log a command to the pending command file before running the test


    Protected Methods:
        _set_stream_handler()
        _get_debug_file_handler()
        _set_results_logger()
        _get_results_handler()
        _set_cmd_logger()
        _get_cmd_handler()
    """

    level = 10
    # TODO: make these read only
    BARE = 0
    ALL = 10
    EXCESS = 20
    DEBUG = 30

    log_dir = "logs"

    __results_logger = None
    __cmd_logger = None
    __logger = None

    @classmethod
    def set_log_level(cls, logLevel: int):
        """Set the log level
        Log Levels:
            0: bare minimum, only output file
            10: output file and warning messages
            20: output file, warning, and info messages
            30: all messages, debug messages output to a debug log file
        """
        cls.level = logLevel
        cls._check_log_dir()
        cls.__logger = logging.getLogger(__name__)
        cls.__logger.setLevel(logging.DEBUG)
        cls.__logger.addHandler(cls._get_debug_file_handler())
        cls.__logger.addHandler(cls._get_stream_handler())

    @classmethod
    def _check_log_dir(cls):
        if not os.path.exists(cls.log_dir):
            os.makedirs(cls.log_dir)

    @staticmethod
    def log_level_help_str():
        retStr = (
            "Log Levels:\n"
            "0: bare minimum, only output file\n"
            "10: output file and warning messages\n"
            "20: output file, warning, and info messages\n"
            "30: all messages, debug messages output to a debug log file\n"
        )
        return retStr

    @classmethod
    def cmd(cls, cmdNum, cmdLine, cores, sysUptime=""):
        if not cls.__cmd_logger:
            cls._set_cmd_logger()
        coreStr = ",".join(cores)
        cls.__cmd_logger.info('"{}","{}","{}","{}"'.format(sysUptime, cmdNum, cmdLine, coreStr))

    @classmethod
    def results(
        cls,
        cmdNum,
        cmdLine,
        cores,
        isACF,
        acfFailingcores,
        isMCE,
        sysUptime="",
        acfDetails="",
        mceDetails="",
    ):
        if not cls.__results_logger:
            cls._set_results_logger()
        coreStr = ",".join(cores)
        cls.__results_logger.info(
            '"{}","{}","{}","{}","{}","{}","{}","{}","{}"'.format(
                sysUptime,
                cmdNum,
                cmdLine,
                coreStr,
                isACF,
                acfFailingcores,
                acfDetails,
                isMCE,
                mceDetails,
            )
        )

    @classmethod
    def debug(cls, msg):
        if cls.level >= cls.DEBUG:
            cls.__logger.debug(msg)

    @classmethod
    def info(cls, msg):
        if cls.level >= cls.EXCESS:
            cls.__logger.info(msg)

    @classmethod
    def warning(cls, msg):
        if cls.level >= cls.ALL:
            cls.__logger.warning(msg)

    @classmethod
    def error(cls, msg):
        cls.__logger.error(msg)

    @classmethod
    def critical(cls, msg):
        cls.__logger.error(msg)

    @classmethod
    def set_log_dir(cls, logDir: str):
        cls.log_dir = logDir
        cls._check_log_dir()

    @classmethod
    def _get_debug_file_handler(cls):
        if cls.level < cls.DEBUG:
            return logging.NullHandler()
        else:
            file_handler = logging.FileHandler("{}/debug.log".format(cls.log_dir))
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
            return file_handler

    @classmethod
    def _get_stream_handler(cls):
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        handler.setLevel(logging.WARNING)
        return handler

    @classmethod
    def _get_results_handler(cls):
        file_handler = logging.FileHandler("{}/cmd_results_list.log.csv".format(cls.log_dir))
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter('"%(asctime)s",%(message)s'))
        return file_handler

    @classmethod
    def _set_results_logger(cls):
        if cls.__results_logger is None:
            cls._check_log_dir()
            cls.__results_logger = logging.getLogger(__name__ + "results")
            cls.__results_logger.setLevel(logging.INFO)
            cls.__results_logger.addHandler(cls._get_results_handler())
            cls.__results_logger.info(
                "System Uptime,Command Number,Command Line,Cores Ran,ACF,ACF Failing Cores,ACF Details,MCE,MCE Failing"
                " Cores,MCE Details"
            )

    @classmethod
    def _get_cmd_handler(cls):
        file_handler = RotatingFileHandler("{}/cur_cmd".format(cls.log_dir), mode="w", maxBytes=10, backupCount=1)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(asctime)s,%(message)s"))
        return file_handler

    @classmethod
    def _set_cmd_logger(cls):
        if cls.__cmd_logger is None:
            cls._check_log_dir()
            cls.__cmd_logger = logging.getLogger(__name__ + "cmd")
            cls.__cmd_logger.setLevel(logging.INFO)
            cls.__cmd_logger.addHandler(cls._get_cmd_handler())
            cls.__cmd_logger.info("System Uptime,Command Number,Command Line,Cores")
