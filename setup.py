from distutils.core import setup
from distgen.version import dg_version

project = "distgen"
datadir = "share"
pkgdatadir = datadir + "/" + project
tpldir = pkgdatadir + "/templates"

setup(
    name='distgen',
    version=dg_version,
    description='Templating system/generator for distributions',
    author='praiskup@redhat.com',
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
    ],
    scripts=['bin/dg'],
)
