### Availability and Usage of Platform-Specific APIs: A First Empirical Study
O **objetivo** seria propor uma abordagem para identificar as OS-specific API, no código de teste: 
- os-specific-api: são apis que, por construção, estão limitadas a determinados sistemas operacionais.
- *statements* e *code blocks* que podem estar dependentes do sistema operacional;

[![Tests](https://github.com/ricardojob/psae/actions/workflows/tests.yaml/badge.svg)](https://github.com/ricardojob/psae/actions/workflows/tests.yaml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/psae)](https://pypi.org/project/psae/)

# PSAE

An automated tool for extracting Platform-Specific API from Git repositories written in Python. 
The `psae` (**P**latform-**S**pecific **A**PI **E**xtract) is primarily designed to be used as a command-line tool. 
With `psae`, you can easily extract information about the Platform-Specific APIs and their usages from the Git repository.
The set of Platform-Specific APIs are saved in a given directory along with relevant metadata in a given CSV file.

## Install

The easiest way to install `psae` is to install from Pypi

```
pip install psae
```

Alternatively, you can install from `test environment`
```
pip install --index-url https://test.pypi.org/simple/ --no-deps psae
```

You may wish to use this tool in a virtual environment. You can use the following commands.

```
virtualenv psae_venv
source psae_venv/bin/activate
pip install psae
```

## Usage

## Examples

## License