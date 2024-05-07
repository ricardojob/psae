import os
import re
import sys
import logging
import tempfile
import click

from extract import ExtractPlatformSpecific, ExtractPlatformSpecificDir, WriteCSV
from project_config import ProjectLocal, ProjectRemote, Project
# from .extract import WriteCSV

logging.basicConfig(level=logging.INFO)
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
# @click.option(
#     "--name",  "-n", help="Print name in console.", type=str,
# )
# def main(name, output):
def main(output, repository):
    # print('directory: ', directory)
    # extract = ExtractPlatformSpecific("")
    # extract.touch()
    
    # tmp_directory = None  # the temporary directory if one is created
    # repo = None  # the repository

    # # clone the repository if it does not exist
    # try:
    #     if not os.path.exists(repository):
    #         if not save_repository:
    #             tmp_directory = tempfile.TemporaryDirectory(dir=".")
    #             save_repository = tmp_directory.name
    #         repo = clone_repository(repository, save_repository)
    #     else:
    #         repo = read_repository(repository)
    # except (git.exc.GitCommandError, ValueError) as exception:
    #     logger.error("Could not read repository at '%s'", repository)
    #     logger.debug(exception)
    #     sys.exit(1)
    
    
    # project = ProjectLocal(directory=repository)
    # project = ProjectRemote().clone(repository)
    project = Project.build(repository)
    print(project)
    extract = ExtractPlatformSpecificDir(project)
    apis = extract.touch()
    print(f"length: {len(apis)}")
    # csv = WriteCSV(output)
    # csv.write(apis) 
    
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