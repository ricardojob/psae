[![Tests](https://github.com/ricardojob/PSASpotter/actions/workflows/tests.yaml/badge.svg)](https://github.com/ricardojob/PSASpotter/actions/workflows/tests.yaml)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/psaspotter)](https://pypi.org/project/psaspotter/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7025599.svg)](https://doi.org/10.5281/zenodo.14029218)
[![License](https://img.shields.io/badge/License-MIT-blue)](LICENSE.txt)

<!-- ![Maven](https://github.com/VariantSync/SyncStudy/actions/workflows/maven.yml/badge.svg) -->
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7025599.svg)](https://doi.org/10.5281/zenodo.14029218)
[![Documentation](https://img.shields.io/badge/Documentation-read%20here-blue)][documentation]
[![Requirements](https://img.shields.io/badge/System%20Requirements-read%20here-blue)](INSTALL.md)
[![Install](https://img.shields.io/badge/Installation%20Instructions-read%20here-blue)](INSTALL.md)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue)](LICENSE) -->

# PSASpotter

An automated tool for extracting Platform-Specific API from Git repositories written in Python. 
The `psaspotter` (**P**latform-**S**pecific **A**PI Spotter) is primarily designed to be used as a command-line tool. 
With `psaspotter`, you can easily extract information about the Platform-Specific APIs and their usages from the Git repository or directory (only python files are analyzed).
The set of Platform-Specific APIs are saved in a given CSV file.

PSASpotter is an AST-based tool that detects API usage at the function/method level. 
Given a Git project, PSASpotter analyzes all Python files and exports details of platform-specific API usage. 
Specifically, for each usage, PSASpotter reports information about the analyzed project (name and commit), the used API (name and availability), and the usage location (filename, line, and GitHub link). 
In addition, PSASpotter also reports whether the usage happens within defensive code.

## Install

The easiest way to install `psaspotter` is to install from Pypi

```
pip install psaspotter
```

Alternatively, you can install from `test environment`
```
pip install --index-url https://test.pypi.org/simple/ --no-deps psaspotter
```

You may wish to use this tool in a virtual environment. You can use the following commands.

```
virtualenv psaspotter_venv
source psaspotter_venv/bin/activate
pip install psaspotter
```

## Quick examples

As an example, the following command extracts every platform-specific APIs from the directory `repository_local`. 
It also saves various information (line, module, filename ...) in `output.csv`. 
Additionally, we can provide information about the project present in the directory provided. 
For this, the parameters `-n` and `-c` can be added to inform the name (`my/local`) and last commit (`da39a3ee5e6b4b0d3255bfef95601890afd80709`) of the project. 
This information will be available in the output file.

```bash
psaspotter repository_local -o output.csv -n my/local --commit da39a3ee5e6b4b0d3255bfef95601890afd80709 
```

Note that the repository does not have to be already cloned, the tool also can fetch it. 
For example, the GitHub repository `https://github.com/ricardojob/PSASpotter` will be fetched, saved under the `data/PSASpotter` directory.
Note that, by default all projects are cloned to the `data` directory.

```bash
psaspotter https://github.com/ricardojob/PSASpotter -o output.csv
```

## Usage

After installation, the `psaspotter` command-line tool should be available in your shell. 
Otherwise, please replace `psaspotter` by `python -m psaspotter`. 
The explanations in the following stays valid in both cases.

We can use PSASpotter to extract information about the usage of platform-specific in a Git repository:


```bash
psaspotter <git_repo> -o <output_file.csv>
```

The first parameter is the Git repository to be analyzed. 
The parameter `-o` represents the name of the CSV output file.

You can use `psaspotter` with the following arguments:

```
  -o,                     Output CSV file.
  -c,                     Commit or tag to be analyzed.
  -p,                     Platform-specific API category.
```

The CSV file given to `-o` (or that will be written to the standard output by default) will contain the following columns:
- `project_name`: Respository name
- `project_commit`: Analyzed commit
- `api_name`: Name of the used platform-specific API
- `api_availability`: Availability of the used platform-specific API
- `usage_filename`: Filename using the platform-specific API
- `usage_line`: Filename line using the platform-specific API
- `usage_github_link`: Github link to the filename and line
- `defensive_code`: Check if the API is used within defensive code

## Tool demonstration

The following video presents a demonstration scenario of the tool: [video](https://youtu.be/).

## License

Distributed under [MIT License](https://github.com/ricardojob/PSASpotter/blob/main/LICENSE.txt).

## Acknowledgements

The structure of this project was heavily inspired by the [gigawork](https://github.com/cardoeng/gigawork) and [spotflow](https://github.com/andrehora/spotflow) projects.
