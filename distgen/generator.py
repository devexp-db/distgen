from __future__ import print_function

import os
import imp
import jinja2
from err import fatal
from distgen.pathmanager import PathManager
from distgen.config import load_config
from distgen.project import AbstractProject


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
        self.project.tplgen = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.pm_tpl.get_path()),
        )

        self.project.initialize()


    def render(self, specfile, template, config, output=None):
        config_path = [self.project.directory] + self.pm_cfg.get_path()
        sysconfig = load_config(config_path, config)

        init_data = self.project.inst_init(specfile, template, sysconfig)

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

        try:
            spec = yaml.load(
                open(self.pm_spc.get_file(
                    specfile,
                    [self.project.directory],
                    fail=True,
                ))
            )
        except yaml.YAMLError, exc:
            fatal("Error in spec file: {0}".format(exc))

        self.project.inst_finish(specfile, template, spec)

        try:
            tpl = self.project.tplgen.get_template(template)
        except jinja2.exceptions.TemplateNotFound as err:
            fatal("Can not find template {0}".format(err))

        print(tpl.render(
            config=sysconfig,
            dirs=sysconfig["dirs"],
            container={'name': 'docker'},
            spec=spec,
            project=self.project,
        ))
