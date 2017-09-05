from setuptools import setup
from distgen.version import dg_version
from os import listdir, path

project = "distgen"
datadir = "share"
pkgdatadir = datadir + "/" + project
tpldir = pkgdatadir + "/templates"
distconfdir = pkgdatadir + "/distconf"

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
    author='praiskup@redhat.com',
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
)
