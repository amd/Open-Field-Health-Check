# Open Source Field Health Checks (OFHC)

## Requirements
- **Python 3.8 or greater**
- AMD EPYC CPU Family 25
- EDAC kernel MCA module
- numactl
- root permissions
- Linux
- bare metal non-virtualized environment
- PyYaml[^1]
  
[^1]: Only applies if you are using a YAML configuration file.  

## What is OFHC run script  
OFHC run script is a test orchestration framework. You can give OFHC a configuration file with the tests to run and it'll run them  in the desired sequence and log pass/fail information on each test. OFHC handles test execution on the desired cores of the CPU and checking for MCEs to make the process simpler for CPU test writers.


## How to run
`python ./run.py {config_file} [--run-dir {run_dir} --log-dir {log_dir}]`  

*Required*  
`config_file`: The file to take the configuration from.  

*Optional*   
The optional fields are also available to set in the [Configuration File](#configuration-file-format). If you provide the command line arguments and they are provided in the configuration file, the command line arguments will take priority.  
`run_dir`: Points to root directory of the OFHC source files.  
`log_dir`: Points to a new or existing directory where all log files will be output.


## Configuration File Format

*The following section shows the configuration in a `YAML` format, however OFHC also support `JSON`.  
All keys are case sensitive, so ensure you have the correct case for all configuration keys.*  

**Tool Level Settings**
```yaml
Log_Level: All 
Log_Directory: logs
Run_Directory: .
Constant_MCE_Checking: false
```
- `Log_Level`: See section [Logging](#logging) for details.
- `Log_Directory`: Points to a new or existing directory where all log files will be output.
- `Run_Directory`: Points to root directory of the OFHC source files.
- `Constant_MCE_Checking`: When `true`, OFHC will check for a MCE after test execution. This helps user understand exactly which test caused an MCE, but also involves more overhead. Also, since OFHC only clears MCE's before beginning a test suite run, the log will show MCE's for the test that generated the MCE and all subsequent tests.  When `false` is specified, OFHC will check before and after the test suite is ran instead of after every test.

**Test Configuration**

```yaml
Tests:
- Name: Example Test
  Binary: ./example_test
  Args:
    - arg1: ...
```

- `Name`: Used for debugging and descriptive configuration file only. 
- `Binary`: path to any executable or an executable in your path.
- `Args`: List of arguments to provide to the binary. See below for how to define the arguments.

**Test Argument Settings**

```yaml
Tests:
- Name: Example Test
  Binary: ./example_test
  Args:
    - arg1:
        Option: "-a1"
        Values:
          - abc
    - arg2:
        Option: "-a2"
        Values:
          - 25
          - 50
          - 75
    - arg3:
        Option: "-a3"
        Values: [1]
    - Tox:
        Option: "-tox"
        Values:
            - 90
    - arg4:
        Option: "-a4"
        Flag: true
        Constant: true
    - arg5:
        Option: "-a5"
        Values:
            - 0
            - 1
    - arg6:
        Option: "-a6"
        Flag: true
```

- Ordinary Arguments: An example of an ordinary argument is `arg1`, `arg2`, and `arg5`. These arguments consist of two separate keys, the first `Option`, which is the way that you specify an argument for your test in command line. The `Values` key requires a list for it's values and each item in the list represents a value for the argument. For example for `arg1` would be run on Example Test like this: `./example_test -a1 abc`.
- Flags: These arguments are just a command line argument without a value. Examples are `arg4` and `arg6`. A flag argument without the `Constant` will run one time with the flag and one time without. If `Constant` is true on the flag then it will only run with the flag. For example flag `arg4` on the Example Test command line would be `./example_test -a4`.
- Constant Arguments: If the `Constant` key on an argument is not specified, the default is `false`. An argument can only be constant if it is a flag, or if it only contains one item in the `Values` list.

**Core Level Settings**  


```yaml
Core_Config:
    Sockets:
        - 0
    SMT: True
    All: True
    Halfs: True
    Quarters: True
    CCDs: True
    Cores: True
```

- Sockets: list of sockets. Can either be 0, 1, or all, so for example if the list was `[0,1,all]` The test suite would first run on socket 0, then then socket 1, then all sockets together. (optional, defaults to all)  
- SMT: bool. When `true` the test suite will run on thread 0 and thread 1 together, if `false` will only run on thread 0.   

*Each of the following core divisions default to `false` if they are not specifed in the configruation.*  

- All: bool. When `true`, the suite will run on all cores together. `false` means it will skip running on all cores.   

*For the following, core divisions, the configuration file can specify either a boolean or a list of integers. When boolean is specified as true, this will result in the test suite running on all the possible subdivisions one at a time. For example, when `Halfs: true` is specified, the test suite will first run on all cores in half 0, then all cores in half 1. When an integer is speificed, it will only run on the specified subdivisions. For example, when `CCDs: [0,2,7]` is specified, the suite will only run on CCD0, CCD2, then CCD7.*

- Halfs: bool/list of ints.  
- Quarters: bool/list of ints.  
- CCDs: bool/list of ints.  
- Cores: bool/list of ints. *Cores specify logical cores*  


## Logging
If the there already exists a log file in the `log_dir` the most recent run will appended to existing log file.

### Files in Log Directory
- `cmd_results_list.log.csv`: A CSV file containing pass/fail results and details for all tests run in the suite.
- `cur_cmd`: The current test being executed. This file is created before running the test so that if the test execution stops due to unexpected reasons, this file will reflect the failing test.
- `cur_cmd.1`: This is the previous test before the current failing test.
- `debug.log`: This is a file containing debugging information. It is only being created if `Log_Level: Debug`.

### Log Levels

- `Bare`: No warnings, info, or debug messages are output. Only output file(`cmd_results_list.log.csv`), current test file(`cur_cmd`), and previous test (`cur_cmd.1`).
- `All`: `Bare` plus logs warnings to stream.
- `Excess`: `All` plus captures system uptime in output file.
- `Debug`: `Excess` plus creates a Debug file with all messages.

*Logging uptime in output only occurs when log level is set when log level is `EXCESS` or higher.*  

# User Defined Test Executable 
## Requirements
It is expected that the test binaries will check for fails. When the executable detects a fail, it should return a non-zero exit code and provide any relevant details in STDOUT and STDERR.
The executable should not control core affinity or any type of threading, the framework is expected to takes care of this.  

## Arguments
The arguments should be compatible with the specifications in the configuration file.

## Output
On success, should use return code 0. On failure, use non-zero return code and output any details in STDOUT and STDERR.

# Checking for MCE & Fails

## MCEs
Default to checking MCE after every test, to reduce overhead of OFHC, you can disable this by setting `Constant_MCE_Checking` to `false` in the configuration file. All details of the MCE is logged to the log file. Basic information is decoded and provided in a transparent way, however for extended debug, extra decoding of the MCEs maybe required. For this, contact a representative at AMD for OFHC.

## Fails
User defined test is responsible for this. See [User Defined Test Executable](#user-defined-test-executable) for details.

# Try it out with Example Stress Test
An example of a standard CPU stress test is [System Stability Tester](https://systester.sourceforge.net/), or `Systester`.

## Systester Configurations
Included are `$OFHC_ROOT/config_files/systester-config.yml` and `$OFHC_ROOT/config_files/systester-config.json`.[^2]
These configuration files give an example of the different argument types and how to specify them as specifically applies to `Systester`.

[^2]: `$OFHC_ROOT` is defined to be the root directory of this repository.

## Running SysTester
To run this example test, download the [binaries](https://systester.sourceforge.net/downloads.php), extract, and
set the environment variable `SYSTESTER_DIR`. Alternatively, you could modify the configuration files to point to where the
extracted binaries are located.
After the previous step you can simply run `python run.py config_files/systester-config.json` to begin the test.
All log files will be in the `logs` directory.


# Future Developments
- Test Randomization
- Test Power Events
- Update Core Configuration to support custom core groupings
