from distutils.core import setup
from distgen.version import dg_version

project = "distgen"
datadir = "share"
pkgdatadir = datadir + "/" + project
tpldir = pkgdatadir + "/templates"

distconfdir = pkgdatadir + "/distconf"

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
        (distconfdir, [
            'distconf/fedora-20-i686.yaml',
            'distconf/fedora-20-x86_64.yaml',
            'distconf/fedora-21-i686.yaml',
            'distconf/fedora-21-x86_64.yaml',
            'distconf/fedora-22-i686.yaml',
            'distconf/fedora-22-x86_64.yaml',
            'distconf/fedora-23-i686.yaml',
            'distconf/fedora-23-x86_64.yaml',
            'distconf/rhel-7-x86_64.yaml',
        ]),
        (distconfdir + "/lib", [
            'distconf/lib/fedora.yaml',
            'distconf/lib/general.yaml',
            'distconf/lib/rhel.yaml',
            'distconf/lib/rpmsystems.yaml',
        ]),
    ],
    scripts=['bin/dg'],
)
