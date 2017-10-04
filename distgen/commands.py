"""
This file contains helper classes for jinja templating system, because its much
more comfortable and secure to write command-class, than implement that
completely in template.
"""


class Command(object):
    interactive = False

    def __init__(self, config):
        self.config = config

    def is_interactive(self, opts=None):
        i = self.config.interactive
        if opts and 'interactive' in opts:
            i = opts['interactive']
        return i

    def in_container(self, opts=None):
        return self.config.container


class AbstractPkgManger(Command):
    pass


class YumPkgManager(AbstractPkgManger):
    binary = "yum"

    def _base_command(self, opts):
        base = self.binary + " -y"
        if self.is_interactive(opts):
            base = self.binary

        docs = True
        if self.in_container(opts):
            docs = False

        if opts and 'docs' in opts:
            docs = opts['docs']

        docs_string = ""
        if not docs:
            docs_string = " --setopt=tsflags=nodocs"

        return base + docs_string

    def action(self, action, pkgs, options):
        return "{0} {1} {2}".format(
            self._base_command(options),
            action,
            " ".join(pkgs),
        ).strip()

    def install(self, pkgs, options=None):
        return self.action("install", pkgs, options)

    def reinstall(self, pkgs, options=None):
        return self.action("reinstall", pkgs, options)

    def remove(self, pkgs, options=None):
        return self.action("remove", pkgs, options)

    def update(self, pkgs, options=None):
        return self.action("update", pkgs, options)

    def update_all(self, options=None):
        return self.action("update", [], options)

    def cleancache(self, options=None):
        return self._base_command(options) + " clean all --enablerepo='*'"


class DnfPkgManager(YumPkgManager):
    binary = "dnf"


class CommandsConfig(object):
    interactive = False
    container = False


class Commands(object):
    def __init__(self, command_config, system_config):
        self.commands_config = command_config
        self.system_config = system_config

        pkginstid = system_config['package_installer']['name']
        if "yum" == pkginstid:
            self.pkginstaller = YumPkgManager(command_config)
        elif "dnf" == pkginstid:
            self.pkginstaller = DnfPkgManager(command_config)
