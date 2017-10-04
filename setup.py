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


def dynamic_data_files():
    dynamic_list = []
    for dcdir in ["distconf", "distconf/lib"]:
        dcfiles = ["{0}/{1}".format(dcdir, f)
                   for f in listdir(dcdir)]
        dcfiles = [f for f in dcfiles if path.isfile(f)]
        dynamic_list.append((pkgdatadir + "/" + dcdir, dcfiles))

    return dynamic_list


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
    data_files=[
        (tpldir + '/container/docker', [
            'templates/container/docker/parts.tpl',
        ]),
        (tpldir, [
            'templates/docker.tpl',
            'templates/makefile-macros.tpl',
            'templates/README',
            'templates/general.tpl',
        ]),
    ] + dynamic_data_files(),
    scripts=['bin/dg'],
    install_requires=get_requirements(),
    cmdclass={
        'build_manpages': build_manpages,
        'build_py': get_build_py_cmd(build_py),
        'install': get_install_cmd(install),
    },
)
