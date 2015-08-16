from __future__ import print_function

import os, sys
import imp
import jinja2
from err import fatal
from distgen.pathmanager import PathManager
from distgen.config import load_config, merge_yaml
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


    def load_project(self, project):
        self.project = self._load_project_from_dir(project)
        if not self.project:
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


    @staticmethod
    def _load_python_file(filename):
        """ load compiled python source """
        mod_name, file_ext = os.path.splitext(os.path.split(filename)[-1])
        if file_ext.lower() == '.py':
            py_mod = imp.load_source(mod_name, filename)
        elif file_ext.lower() == '.pyc':
            py_mod = imp.load_compiled(mod_name, filename)

        return py_mod


    def _load_obj_from_file(self, filename, objname):
        py_mod = self._load_python_file(filename)

        if hasattr(py_mod, objname):
            return getattr(py_mod, objname)
        else:
            return None


    def _load_obj_from_projdir(self, projectdir, objname):
        """ given project directory, load possibly existing project.py """
        project_file = projectdir + "/project.py"

        if os.path.isfile(project_file):
            return self._load_obj_from_file(project_file, objname)
        else:
            return None


    def _load_project_from_dir(self, projectdir):
        """ given project directory, load possibly existing project.py """
        projclass = self._load_obj_from_projdir(projectdir, "Project")
        if not projclass:
            return None
        return projclass()


    def load_config_from_project(self, directory):
        """
        read the project.py file for (dirs only) variables
        """
        config = self._load_obj_from_projdir(directory, 'config')
        if config:
            return config
        return {}


    @staticmethod
    def vars_fixed_point(config):
        """ substitute variables in paths """

        keys = config.keys()

        something_changed = True
        while something_changed:
            something_changed = False

            for i in keys:
                for j in keys:
                    if j == i:
                        continue
                    replaced = config[i].replace("$" + j, config[j])
                    if replaced != config[i]:
                        something_changed = True
                        config[i] = replaced


    def vars_fill_variables(self, config, sysconfig=None):
        if not 'dirs' in config:
            return

        dirs = config['dirs']

        additional_dirs = {}
        if sysconfig and 'dirs' in sysconfig:
            additional_dirs = sysconfig['dirs']

        merged = merge_yaml(additional_dirs, dirs)
        if 'name' in config:
            merged['name'] = config['name']
        else:
            merged['name'] = 'unknown-pkg'
        self.vars_fixed_point(merged)

        config['dirs'] = {x: merged[x] for x in dirs.keys()}


    def render(self, specfile, template, config, output=sys.stdout,
               confdirs=None):
        """ render single template """
        config_path = [self.project.directory] + self.pm_cfg.get_path()
        sysconfig = load_config(config_path, config)

        if not confdirs:
            confdirs = []
        for i in confdirs + [self.project.directory]:
            additional_vars = self.load_config_from_project(i)
            self.vars_fill_variables(additional_vars, sysconfig)
            # filter only interresting variables
            interresting_parts = ['dirs']
            additional_vars = {x: additional_vars[x] \
                    for x in interresting_parts if x in additional_vars}
            sysconfig = merge_yaml(sysconfig, additional_vars)

        self.project.abstract_setup_vars(sysconfig)

        init_data = self.project.inst_init(specfile, template, sysconfig)

        projcfg = self.load_config_from_project(self.project.directory)
        if projcfg and 'name' in projcfg:
            sysconfig['name'] = projcfg['name']
        self.vars_fill_variables(sysconfig)

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
