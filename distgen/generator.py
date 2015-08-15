from __future__ import print_function

import os, sys
import imp
import jinja2
from err import fatal
from distgen.pathmanager import PathManager
from distgen.config import load_config
from distgen.project import AbstractProject
from distgen.commands import Commands, CommandsConfig


class Generator(object):
    project = None

    pm_cfg = None
    pm_tpl = None
    pm_spc = None


    def __init__(self):
        self.pm_cfg = PathManager(
            # TODO: Is there better way to reuse configured directories
            # from setup.py in python?
            ["/usr/share/distgen/distconf"],
            envvar="DG_DISTCONFDIR"
        )

        self.pm_tpl = PathManager(
            ['/usr/share/distgen/templates'],
            envvar="DG_TPLDIR"
        )

        self.pm_spc = PathManager([])


    def _load_class_from_file(self, filename, classname):
        mod_name, file_ext = os.path.splitext(os.path.split(filename)[-1])
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filename)
        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filename)

        if hasattr(py_mod, classname):
            return getattr(py_mod, classname)()
        else:
            return None


    def load_project(self, project):
        project_file = project + "/project.py"

        if os.path.isfile(project_file):
            self.project = self._load_class_from_file(project_file, "Project")
        else:
            self.project = AbstractProject()
        self.project.directory = project

        def absolute_load(name):
            """
            In our templating system, we care about filenames specified by
            absolute path, which is not truth for default FileSystemLoader.
            """
            if name.startswith('/'):
                try:
                    with file(name) as f:
                        return f.read().decode('utf-8')
                except:
                    pass
            raise jinja2.TemplateNotFound()

        loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(self.pm_tpl.get_path()),
            jinja2.FunctionLoader(absolute_load),
        ])

        self.project.tplgen = jinja2.Environment(loader=loader)

        self.project.abstract_initialize()


    def vars_fixed_point(self, config):
        """ substitute variables in paths """
        dirs = config['dirs']

        dirs['name'] = self.project.name

        keys = dirs.keys()

        something_changed = True
        while something_changed:
            something_changed = False

            for i in keys:
                for j in keys:
                    if j == i:
                        continue
                    replaced = dirs[i].replace("$" + j, dirs[j])
                    if replaced != dirs[i]:
                        something_changed = True
                        dirs[i] = replaced

        dirs.pop('name')


    def render(self, specfile, template, config, output=sys.stdout):
        config_path = [self.project.directory] + self.pm_cfg.get_path()
        sysconfig = load_config(config_path, config)

        self.project.abstract_setup_vars(sysconfig)

        init_data = self.project.inst_init(specfile, template, sysconfig)

        self.vars_fixed_point(sysconfig)

        # NOTE: This is soo ugly, sorry for that, in future we need to modify
        # PyYAML to let us specify callbacks, somehow.  But for now, import
        # yaml right here to be able to add the constructors/representers
        # "locally".
        import yaml

        def _eval_node(loader, node):
            return str(eval(str(loader.construct_scalar(node)), {
                'init': init_data,
                'config': sysconfig,
                'dirs': sysconfig['dirs']
            }))

        yaml.add_constructor(u'!eval', _eval_node)

        spec = {}
        if specfile:
            specfd = self.pm_spc.open_file(
                specfile,
                [self.project.directory],
                fail=True,
            )
            if not specfd:
                fatal("Spec file {0} not found".format(specfile))

            try:
                spec = yaml.load(specfd)
            except yaml.YAMLError, exc:
                fatal("Error in spec file: {0}".format(exc))

        self.project.inst_finish(specfile, template, sysconfig, spec)

        try:
            tpl = self.project.tplgen.get_template(template)
        except jinja2.exceptions.TemplateNotFound as err:
            fatal("Can not find template {0}".format(err))

        cmd_cfg = CommandsConfig()
        # TODO: used only "docker" for now as nothing else is needed ATM
        cmd_cfg.container = "docker"

        output.write(tpl.render(
            config=sysconfig,
            dirs=sysconfig["dirs"],
            container={'name': 'docker'},
            spec=spec,
            project=self.project,
            commands=Commands(cmd_cfg, sysconfig)
        ) + "\n")
