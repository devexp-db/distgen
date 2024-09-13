"""Module providing an ArgumentParser object to be used by CLI interface."""

from argparse import ArgumentParser, RawDescriptionHelpFormatter

from importlib.metadata import version, PackageNotFoundError

try:
    VERSION = version("distgen")
except PackageNotFoundError:
    # package is not installed, due to this file being used by manpage generator
    # we have to check for this, we do not need valid version during manpage
    # generation, but it will crash
    VERSION = 0

DESCRIPTION = \
    """
Generate script using predefined metadata about distribution and
templates.

As an example of 'dg' usage, to generate _Dockerfile_ for Fedora
21 64-bit system, you may use command(s):

$ cd project/directory
$ dg --spec      docker-data.yaml      \\
--template  docker.tpl
    """

parser = ArgumentParser(
    prog='dg',
    description=DESCRIPTION,
    formatter_class=RawDescriptionHelpFormatter,
)

# Solely for the purpose of manpage generator
parser.man_short_description = "templating system/generator for distributions"

parser.add_argument(
    '--version',
    action='version',
    version=f"dg (distgen) {VERSION}"
)

parser.add_argument(
    '--projectdir',
    metavar='PROJECTDIR',
    type=str,
    help='Directory with project (defaults to CWD)',
    default="."
)

parser.add_argument(
    '--distro',
    metavar='DIST',
    type=str,
    help='Use DIST distribution configuration.  Either that DIST.yaml needs '
         'to exist in the distgen installation, or it can be any file '
         'within PROJECTDIR (relative or absolute file name).',
)

parser.add_argument(
    '--multispec',
    metavar='MULTISPEC',
    type=str,
    help='Use MULTISPEC yaml file to fill the TEMPLATE file',
)

parser.add_argument(
    '--multispec-selector',
    metavar='MULTISPEC_SELECTOR',
    type=str,
    help='Selectors for the multispec file',
    action='append',
    default=[],
)

parser.add_argument(
    '--spec',
    metavar='SPEC',
    type=str,
    help='Use SPEC yaml file to fill the TEMPLATE file',
    action='append',
)

parser.add_argument(
    '--output',
    metavar='OUTPUT',
    type=str,
    help='Write result to OUTPUT file instead of stdout',
)

parser.add_argument(
    '--macros-from',
    metavar='PROJECTDIR',
    type=str,
    action='append',
    help='Load variables from PROJECTDIR',
)

parser.add_argument(
    '--container',
    metavar='CONTAINER_TYPE',
    type=str,
    help='Container type, e.g. \'docker\'',
    default=False,
)

parser.add_argument(
    '--macro',
    metavar='MACRO',
    type=str,
    action='append',
    help='Define distgen\'s macro',
)

parser.add_argument(
    '--max-passes',
    metavar='PASSES',
    type=int,
    default=32,
    help='Maximum number of rendering passes, defaults to 32',
)

parser.add_argument(
    '--keep-block-whitespaces',
    help="Disable the jinja2 trim_blocks and lstrip_blocks options",
    action="store_true",
)

tpl_or_combinations = parser.add_mutually_exclusive_group(required=True)

tpl_or_combinations.add_argument(
    '--template',
    metavar='TEMPLATE',
    type=str,
    help='Use TEMPLATE file, e.g. docker.tpl or a template string, '
    'e.g. "{{ config.docker.from }}"'
)

tpl_or_combinations.add_argument(
    '--multispec-combinations',
    action='store_true',
    help='Print available multispec combinations',
)
