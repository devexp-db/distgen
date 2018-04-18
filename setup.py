import sys

from setuptools import setup
from distgen.version import dg_version
from os import listdir, path, getcwd

project = "distgen"
datadir = "share"
pkgdatadir = datadir + "/" + project
tpldir = pkgdatadir + "/templates"
distconfdir = pkgdatadir + "/distconf"

from setuptools.command.build_py import build_py
from setuptools.command.install import install

try:
    sys.path = [path.join(getcwd(), 'build_manpages')] + sys.path
    from build_manpages.build_manpages import (
        build_manpages, get_build_py_cmd, get_install_cmd)
except:
    print("=======================================")
    print("Use 'git submodule update --init' first")
    print("=======================================")
    raise


def get_requirements():
    with open('requirements.txt') as f:
        return f.read().splitlines()


setup(
    name='distgen',
    version=dg_version,
    description='Templating system/generator for distributions',
    author='Pavel Raiskup (see AUTHORS)',
    author_email='praiskup@redhat.com',
    maintainer='Bohuslav Kabrda',
    maintainer_email='bkabrda@redhat.com',
    license='GPLv2+',
    url='https://github.com/devexp-db/distgen',
    platforms=['any'],
    packages=['distgen'],
    # this is bit impractical, but I see no better way to include subdirs properly
    package_data={'distgen':
                  ['distconf/*.yaml', 'distconf/**/*.yaml',
                   'templates/*.tpl', 'templates/**/*.tpl', 'templates/**/**/*.tpl']
                 },
    scripts=['bin/dg'],
    install_requires=get_requirements(),
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
)
