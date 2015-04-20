import os


class PathManager(object):
    envvar = None

    def __init__(self, path, envvar=None):
        self.path = path
        self.envvar = envvar


    def get_file(self, relative, prefered_path=None):
        path = self.path
        if prefered_path:
            path = prefered_path + path

        if self.envvar:
            env_path = os.environ[self.envvar].split(':')
            path = env_path + path

        for i in path:
            config_file = i + "/" + relative
            if os.path.isfile(config_file):
                return config_file

        return None


    def get_path(self):
        return self.path
