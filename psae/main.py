import os
import re
import sys
import logging
import tempfile
import click

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# See https://click.palletsprojects.com/en/8.1.x/documentation/#help-texts
CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}

@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--output",
    "-o",
    help="TThe output CSV file where the usage of Platform-Specific APIs related to the repository will be stored. "
    "By default, the information will written to the standard output.",
    type=click.Path(exists=False, file_okay=True, dir_okay=False, writable=True),
)
@click.option(
    "--name",  "-n", help="Print name in console.", type=str,
)
def main(name, output):
    print('Hello: ', name)
    print(f'Output: {output}.csv')

if __name__ == "__main__":
    main()
    
# The output CSV file where the usage of APIs related to the repository will be stored.
# The output CSV file where information related to the dataset will be stored.