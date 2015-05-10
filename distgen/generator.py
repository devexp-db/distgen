import os
import imp
from jinja2 import Environment, FileSystemLoader
from pathmanager import PathManager
from config import load_config


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
        self.project = self._load_class_from_file(project_file, "Project")
        self.project.directory = project
        self.project.tplgen = Environment(
            loader=FileSystemLoader(self.pm_tpl.get_path()),
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

        spec = yaml.load(
            open(self.pm_spc.get_file(specfile, [self.project.directory]))
        )

        self.project.inst_finish(specfile, template, spec)

        tpl = self.project.tplgen.get_template(template)
        print tpl.render(
            config=sysconfig,
            dirs=sysconfig["dirs"],
            container={'name': 'docker'},
            spec=spec,
            project=self.project,
        )
