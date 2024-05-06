import os
import re
import sys
import logging
import tempfile
import click
from extract import WriteCSV
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
#     "--name",  "-n", help="Print name in console.", type=str,
# )
# def main(name, output):
def main(output):
    # print('Hello: ', name)
    # print(f'Output: {output}.csv')
    csv = WriteCSV(output)
    csv.write("a;b;c;") 
    # if output:
    #     csv.write_to_file("a;b;c;")    
    # else:
    #     csv.write_to_stdo("stdo::print")

if __name__ == "__main__":
    main()