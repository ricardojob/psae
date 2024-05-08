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
# @click.option(
#     "--directory",
#     "-d",
#     help="The directory where the extracted Platform-Specific APIs will be stored."
#     "It is important to note that each directory stores a single project.", 
#     default = "data",
#     type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
# )
@click.argument(
    "repository",
    type=str,
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
# @click.option(
#     "--name",  "-n", help="Print name in console.", type=str,
# )
# def main(name, output):
def main(output, repository, commit, repository_name):
    # print('directory: ', directory)
    # extract = ExtractPlatformSpecific("")
    # extract.touch()
    
    # project = ProjectLocal(directory=repository)
    # project = ProjectRemote().clone(repository)
    project = Project.build(repository, repository_name, commit)
    logger.info(project)
    extract = ExtractPlatformSpecificDir(project)
    apis = extract.touch()
    logger.info(f"Collected: {len(apis)} Platform-Specific APIs.")
    report = Report.build(output)
    report.write(apis) 
    
    # extract = ExtractPlatformSpecificDir(directory)
    # apis = extract.touch()
    # csv = WriteCSV(output)
    # csv.write(apis) 
    # [print(f'{c.project_name}; hashs; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {c.is_test} ; {c.filename}') for c in apis]
    # return [print(f'{c}') for c in apis]
    
  
    
if __name__ == "__main__":
    main()
    

#  python3 psae/main.py ../study-docs/input/classes
#  python3 psae/main.py https://github.com/nvbn/thefuck