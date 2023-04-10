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

import os
import sys
from io import open


def GetSocketId(cpu_id: int):
    f = "/sys/devices/system/cpu/cpu{}/topology/physical_package_id".format(cpu_id)
    if not os.path.isfile(f):
        raise RuntimeError(
            "Failed to get socket id for cpu core {}. Please ensure you are root and valid core id.".format(cpu_id)
        )

    try:
        with open(f, "r") as ppFile:
            pId = ppFile.read(1)
    except OSError:
        raise RuntimeError(
            "Failed to get socket id for cpu core {}. Please ensure you are root and valid core id.".format(cpu_id)
        )

    pId = int(pId.strip("\n"))
    return pId


class CpuInfo:
    """Contains info about the core configuration of the CPU

    Attributes:
        is_smt_enabled: boolean for multithreading
        num_logical_cores: integer representing total number of logical cores
        num_physical_cores: integer representing the total number of physical cores
        cores_per_ccd: integer representing the total number of cores in each CCD
        ccds_per_socket: integer representing number of CCDs in each socket
        num_sockets: integer representing the number of populated sockets


    """

    def __init__(self):
        self.file_name = "/proc/cpuinfo"
        self.topology = {}
        self.is_smt_enabled = False
        self.num_logical_cores = 0
        self.ccds_per_socket = 0
        self.num_sockets = 0
        self.num_physical_cores = 0
        self.Enumerate()
        self.cores_per_ccd = int(self.num_physical_cores / (self.ccds_per_socket * self.num_sockets))

    def Enumerate(self):
        self.cpuinfo = {}
        ccds = {}
        try:
            f = open(self.file_name, encoding="utf-8")
            core_id = 0
            for line in f:
                x = [x.strip() for x in line.split(":")]
                if len(x) == 2:
                    if x[0] == "processor":
                        core_id = x[1]
                        self.cpuinfo[int(core_id)] = {}
                    self.cpuinfo[int(core_id)][x[0]] = x[1]
        except OSError:
            print("Could not open/read file:{}".format(self.file_name))
            sys.exit()
        finally:
            f.close()

        for key, value in self.cpuinfo.items():
            if int(value["physical id"]) not in self.topology:
                self.topology[int(value["physical id"])] = {}
            self.topology[int(value["physical id"])][int(key)] = value

        if len(self.topology[0]) != int(self.topology[0][0]["cpu cores"]):
            self.is_smt_enabled = True
        else:
            self.is_smt_enabled = False

        self.num_logical_cores = len(self.cpuinfo)
        self.num_physical_cores = int(len(self.cpuinfo) / (2 if self.is_smt_enabled else 1))
        self.num_sockets = len(self.topology)
        v1 = int(self.cpuinfo[0]["apicid"])
        v2 = int(self.cpuinfo[1]["apicid"])
        div_fact = v2 - v1
        for key, value in self.cpuinfo.items():
            apicid = int(value["apicid"])
            if self.is_smt_enabled:
                apicid = (apicid >> 4) & 0x1F
            else:
                if int(value["cpu family"]) == 25 and int(value["model"]) >= 1:
                    apicid = (apicid >> (1 + div_fact)) & 0x1F
                else:
                    apicid = (apicid >> 3) & 0x1F
            ccds[apicid] = 1
        self.ccds_per_socket = int(len(ccds) / self.num_sockets)
