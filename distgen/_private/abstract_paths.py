"""
This file could theoretically be moved to some convenience lib
"""

import os

import importlib

GENERATED_MODULE = 'installed_paths'


def get_hacked_install():
    # time expensive, import on demand
    from setuptools.command.install import install

    class hacked_install(install):
        _paths = None

        def post_install(self):
            from distutils.util import byte_compile

            # racy, but setuptools/distutils do the same
            where = os.path.join(self.install_lib, *self._paths.install_dir)
            if not os.path.isdir(where):
                os.makedirs(where)

            raw_file = os.path.join(where, GENERATED_MODULE + ".py")
            with open(raw_file, 'w') as f:
                self._paths.write_paths(f, self.install_base)

            byte_compile([raw_file], force=self.force)

        def run(self):
            install.run(self)
            self.post_install()

    return hacked_install


class PathsAbstract(object):
    install_dir = None
    installed = False
    src_dir = None
    paths = None

    def get_installed_paths(self):
        try:
            module = '.'.join(self.install_dir + [GENERATED_MODULE])
            module = importlib.import_module(module)
            self.installed = True
            for key in self.paths:
                ipath = getattr(module, key)
                self.paths[key]['installed'] = ipath.split(':')
        except Exception:
            pass

    def __init__(self, dir_array):
        self.install_dir = dir_array
        self.get_installed_paths()

    def install_cls(self):
        # Time expensive, import on demand only for setup.py purposes.
        cls = get_hacked_install()
        cls._paths = self
        return cls

    def write_paths(self, fd, base):
        for key in self.paths:
            ipath = [os.path.join(base, d) for d in self.paths[key]['install']]
            ipath = ':'.join(ipath)
            fd.write('{0} = "{1}"\n'.format(key, ipath))

    def __getitem__(self, key):
        if self.installed:
            return self.paths[key]['installed']
        else:
            return [os.path.join(os.environ['SOURCEDIR'], d)
                    for d in self.paths[key]['source']]
