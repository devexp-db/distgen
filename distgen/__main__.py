#!/bin/python

"""Main entrypoint for distgen. This module handles CLI interface"""

from __future__ import print_function

import os
import sys
import tempfile
import shutil

import logging

from distgen.cli_parser import parser

from distgen.generator import Generator
from distgen.commands import CommandsConfig
from distgen.multispec import Multispec
from distgen.distro_version import detect_default_distro
from distgen.err import fatal

logging.basicConfig(format='dg: %(levelname)-8s: %(message)s')

def print_multispec_combinations(args):
    ms = Multispec.from_path(args.projectdir, args.multispec)
    for c in ms.get_all_combinations():
        to_print = ['--distro {0}'.format(c.pop('distro'))]
        [to_print.append('--multispec-selector {0}={1}'.format(k, v)) for k, v in c.items()]
        print(' '.join(to_print))


def render_template(args):
    temp_filename = False
    output = sys.stdout.buffer
    try:
        if args.output:
            _, temp_filename = tempfile.mkstemp(prefix="distgen-")
            output = open(temp_filename, 'wb')
    except:
        fatal("can't create temporary file for '{0}'".format(args.output))

    cmd_cfg = CommandsConfig()
    cmd_cfg.container = args.container

    explicit_macros = {}
    if args.macro:
        for i in args.macro:
            key, value = i.split(' ', 1)
            explicit_macros[key] = value

    if args.template == '-':
        args.template = "/proc/self/fd/0"

    global_jinja_args = None
    if not args.keep_block_whitespaces:
        global_jinja_args = {
            'trim_blocks': True,
            'lstrip_blocks': True,
        }

    generator = Generator(global_jinja_args=global_jinja_args)
    generator.load_project(args.projectdir)

    distro = args.distro
    if not distro:
        distro = detect_default_distro()
    if not distro:
        fatal("distribution not detected, use --distro option")

    generator.render(
        args.spec,
        args.multispec,
        args.multispec_selector,
        args.template,
        distro,
        cmd_cfg,
        output,
        args.macros_from,
        explicit_macros,
        args.max_passes,
    )

    if temp_filename:
        try:
            output.close()
            shutil.move(temp_filename, args.output)
            # there's no way in Python to get umask without setting it
            # to some value, therefore we have to get while setting
            # to 0 and then re-set to original value
            umask = os.umask(0)
            os.umask(umask)
            os.chmod(args.output, 0o666 &~umask)
        except:
            fatal("can't move '{0}' into '{1}'".format(temp_filename, args.output))


def main():
    args = parser.parse_args()
    if args.multispec_combinations:
        print_multispec_combinations(args)
    else:
        render_template(args)


if __name__ == "__main__":
    main()
