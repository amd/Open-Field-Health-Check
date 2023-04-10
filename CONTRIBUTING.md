## Contributing to OFHC

### Introduction
Welcome to the Open Field Health Check (OFHC) respository. The purpose of this repository is to provide a deterministic approach to running AMD devices tests.

### Prerequisites
Please install all prerequisites listed in the README prior to commencing development. Ensure that you have a local system with an AMD device to execute the suite and additionally test any new code that is developed. For Python dependencies it is recommended to setup a Python virtual environment to track them via [venv](https://docs.python.org/3/library/venv.html)

Ensure that your development system meets the minimum CPU family requirements so that the scripts run as intended and expected test functionality is retained.

This repository supports a minimum HW generations of AMD EPYC CPU Family 25. 

### Contributing Guidelines
Please do not open issues for general support questions as we want to keep this GitHub repository for bug reports and feature requests.
Please utilize the Github Issues section to create a new post to describe a new feature proposal after reading through prior posts to identify duplicate feature requests. This will help us manage our backlog and ensure that we aren't duplicating work in different instances.

#### Style Guide
All commits must pass Flake8 guidelines. Code styling is enforced via [Black](https://github.com/psf/black)

#### Pre-commit Hooks
This repository is configured with pre-commit hooks to check for PEP8 compliance, code formatting and spacing guidelines. Please see the 'ofhc/pre-commit-hooks.yaml' file for additional details.

For a tutorial on how to setup your own pre-commit hooks, please see this [link](https://pre-commit.com/)

### Recommended Workflow

#### Forking
If you are posting a pull request for the first time, you should fork the La Hacienda repository by clicking the Fork button in the top right corner of the GitHub page, and the forked repositories will appear under your GitHub profile.

#### Testing and Code Coverage
In addition to the pre-commit hooks, please ensure that any new code is tested independently on AMD hardware prior to generating a pull-request. 

#### Creating a pull-request
Before submitting a pull request make sure you have validated the following:

1. Check the Version and Branching section before commiting a change through PR.

2. All the individual commits in the PR should be signed off.

3. Make sure the PR does not have any merge conflicts. If there are any conflicts please resolve them before opening the PR up for review.

4. Ensure the linting and testing checks pass once you raise the PR. Unless the lint is passing the PR cannot be merged. You will be able to see the results of the workflows. In case it is failing, you can use it to debug further.

#### Certificate of Origin

In order to get a clear contribution chain of trust we use the [signed-off-by
language](https://01.org/community/signed-process) used by the Linux kernel
project

#### Feature Requests and Bug Reports

If you've thought of an innovative test approach, we want to hear about it. We are always looking to improve this repository, and we'd like to hear yours thoughts about it and track feature requests (examples) using GitHub, so please feel free to open an issue which describes the feature you would like to see, why you need it, and how it should work. If you would like to contribute code towards building it, you might consider a feature proposal instead. A feature proposal is the first step to helping the community better understand what you are planning to contribute, why it should be built, and collaborate on ensuring you have all the data points you need for implementation.

#### Issue tracking

If you have a problem, please let us know. Review the list of 'Issues' associated with this repository to see if similar problem or request is already documented.

If the issue already exists, review it for completeness and provide any
additional insight. If the issue is not documented, file one uder 'Issues'. When reporting
multiple issues, use one report for each problem observed -- it makes it much
easier to track them.

### Community
[https://community.amd.com/](https://community.amd.com/)



