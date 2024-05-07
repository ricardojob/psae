import os
import re
import sys
import logging
import tempfile
import click

from extract import ExtractPlatformSpecific, ExtractPlatformSpecificDir, WriteCSV
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
@click.option(
    "--directory",
    "-d",
    help="The directory where the extracted GitHub Actions workflow files will be stored.",
    type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True),
)
# @click.option(
#     "--name",  "-n", help="Print name in console.", type=str,
# )
# def main(name, output):
def main(output, directory):
    # print('directory: ', directory)
    # extract = ExtractPlatformSpecific("")
    # extract.touch()
    extract = ExtractPlatformSpecificDir(directory)
    apis = extract.touch()
    # [print(f'{c.project_name}; hashs; {c.line}; {c.module}; {c.call_name}; {c.call_name_long}; {c.is_test} ; {c.filename}') for c in apis]
    # return [print(f'{c}') for c in apis]
    csv = WriteCSV(output)
    csv.write(apis) 
    
if __name__ == "__main__":
    main()