import os
import re
import sys
import logging
import tempfile
import click

from extract import ExtractPlatformSpecific, ExtractPlatformSpecificDir, Report
from psae.projects import Project
# from .extract import WriteCSV

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(level=logging.INFO, filename='log.txt')
logger = logging.getLogger(__name__)

# See https://click.palletsprojects.com/en/8.1.x/documentation/#help-texts
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--output",
    "-o",
    help="The output CSV file where the usage of Platform-Specific APIs related to the repository will be stored. "
    "By default, the information will written to the standard output.",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
)

@click.option(
    "--commit",
    "-c",
    help="The commit reference (i.e., commit SHA or TAG) to be considered for the extraction."
    "It is important to note that each commit references a local project.", 
    type=str,
)
@click.option(
    "--repository-name",
    "-n",
    help="The name's project to be considered for the extraction."
    "It is important to note that the name references a local project.", 
    type=str,
)
@click.argument(
    "repository",
    type=str,
)
def main(output, repository, commit, repository_name):
    project = Project.build(repository, repository_name, commit)
    logger.info(project)
    extract = ExtractPlatformSpecificDir(project)
    apis = extract.touch()
    logger.info(f"Collected: {len(apis)} Platform-Specific APIs.")
    report = Report.build(output)
    report.write(apis) 

if __name__ == "__main__":
    main()
    

#  python3 psae/main.py tests/classes -n my/local --commit da39a3ee5e6b4b0d3255bfef95601890afd80709
#  python3 psae/main.py https://github.com/nvbn/thefuck -o output.csv 
