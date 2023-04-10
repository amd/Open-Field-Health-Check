#!/usr/bin/env python3

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

import argparse
import time

from logger import logger
from system_config.SystemConfig import SystemConfig


def checkMces(config, description):
    mces = config.checkMCEs(force=True)
    if mces:
        logger.warning("Post-Test check detected MCE. Check log for details")
        for mce in mces:
            logger.results(description, "", [], False, [], True, "", "", str(mce))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("settings_file")
    parser.add_argument("--run_dir", type=str)
    parser.add_argument("--log_dir", type=str)
    args = parser.parse_args()

    try:
        config = SystemConfig(
            args.settings_file,
            args.run_dir,
            args.log_dir,
        )
    except RuntimeError as ex:
        print("Failed to detect the configuration needed to run La Hacienda")
        print(ex)
        exit(1)

    # Clear MCE's before running any tests
    checkMces(config, "PRETEST Detection")
    config.clearMCEs()
    # Importing this after setting the logging level
    from test_factories.TestFactory import TestFactory

    testFactory = TestFactory(config)

    startTime = time.perf_counter()
    while True:
        try:
            test = testFactory.getNextTest()
        except StopIteration:
            checkMces(config, "POSTTEST Detection")
            logger.info("Finished executing all tests")
            exit(0)
        if not test.execute():
            logger.warning("Test Failed, see logs for details")
