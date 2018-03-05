import os

from distgen.err import fatal


class PathManager(object):
    envvar = None

    def __init__(self, path, envvar=None, file_suffix=None):
        self.path = path
        self.envvar = envvar
        self.suffix = file_suffix

    def get_file(self, filename, prefered_path=None, fail=False,
                 file_desc="file"):

        if filename.startswith('/'):
            if os.path.isfile(filename):
                return filename
            else:
                return None

        path = self.get_path()
        if prefered_path:
            path = prefered_path + path

        for i in path:
            config_files = [os.path.join(i, filename)]
            if self.suffix:
                config_files.append(config_files[0] + self.suffix)
            for cf in config_files:
                if os.path.isfile(cf):
                    return cf

        if fail:
            fatal("can't find {0} '{1}'".format(file_desc, filename))

        return None

    def open_file(self, relative, prefered_path=None,
                  fail=False, file_desc="file"):

        filename = self.get_file(relative, prefered_path, fail=fail,
                                 file_desc=file_desc)
        if not filename:
            return None

        try:
            fd = open(filename)
        except IOError:
            if fail:
                fatal("can't open file {0}".format(relative))
            return None

        return fd

    def get_path(self):
        path = self.path
        if self.envvar and self.envvar in os.environ:
            env_path = os.environ[self.envvar].split(':')
            path = env_path + path

        return [os.getcwd()] + path
