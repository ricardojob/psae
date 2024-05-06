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
    "--name",  "-n", help="Print name in console.", type=str,
)
def main(name):
    print('Hello: ', name)

if __name__ == "__main__":
    main()
