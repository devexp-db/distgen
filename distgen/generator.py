import os
import sys
import imp
import jinja2
import functools

from distgen.err import fatal
from distgen.pathmanager import PathManager
from distgen.config import load_config, merge_yaml
from distgen.project import AbstractProject
from distgen.commands import Commands
from distgen.multispec import Multispec, MultispecError


class Generator(object):
    project = None

    pm_cfg = None
    pm_tpl = None
    pm_spc = None

    def __init__(self, global_jinja_args=None):
        here = os.path.dirname(os.path.abspath(__file__))
        self.pm_cfg = PathManager(
            [os.path.join(here, "distconf"),
             os.path.join(sys.prefix, "share", "distgen", "distconf")],
            envvar="DG_DISTCONFDIR"
        )

        self.pm_tpl = PathManager(
            [os.path.join(here, "templates"),
             os.path.join(sys.prefix, "share", "distgen", "templates")],
            envvar="DG_TPLDIR"
        )

        self.pm_spc = PathManager([])
        self.jinjaenv_args = {'keep_trailing_newline': True}

        if global_jinja_args:
            self.jinjaenv_args.update(global_jinja_args)

    def load_project(self, project):
        self.project = self._load_project_from_dir(project)
        if not self.project:
            self.project = AbstractProject()
        self.project.directory = project

        def file_load(name):
            """
            The default FileSystemLoader doesn't load files specified
            by absolute paths or paths that include '..' - therefore
            we provide a custom fallback function that handles this.
            """
            name = os.path.abspath(name)
            try:
                with open(name, 'rb') as f:
                    return f.read().decode('utf-8')
            except Exception:
                raise jinja2.TemplateNotFound(name)

        def string_load(name):
            """
            Allow specifying a string instead of template to be able
            to return expanded config/specs/...
            """
            if name.startswith(('{{', '{%')):
                return name
            raise jinja2.TemplateNotFound(name)

        loader = jinja2.ChoiceLoader([
            jinja2.FileSystemLoader(self.pm_tpl.get_path()),
            jinja2.FunctionLoader(string_load),
            jinja2.FunctionLoader(file_load),
        ])

        self.project.tplgen = jinja2.Environment(
            loader=loader,
            **self.jinjaenv_args
        )

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
        project_file = os.path.join(projectdir, "project.py")

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
        read the project.py file for macros
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
        if 'macros' not in config:
            return

        macros = config['macros']

        additional_macros = {}
        if sysconfig and 'macros' in sysconfig:
            additional_macros = sysconfig['macros']

        merged = merge_yaml(additional_macros, macros)
        if 'name' in config:
            merged['name'] = config['name']
        else:
            merged['name'] = 'unknown-pkg'
        self.vars_fixed_point(merged)

        config['macros'] = {x: merged[x] for x in macros.keys()}

    def _rerender_spec(self, s, **kwargs):
        changed = False

        if isinstance(s, dict):
            for k, v in s.items():
                _changed, s[k] = self._rerender_spec(v, **kwargs)
                changed |= _changed
        elif isinstance(s, list):
            for i in range(0, len(s)):
                _changed, s[i] = self._rerender_spec(s[i], **kwargs)
                changed |= _changed
        elif isinstance(s, str):
            new_spec = jinja2.Template(s).render(**kwargs)
            changed = s != new_spec
            s = new_spec
        else:
            pass  # int, float, perhaps something else?

        return changed, s

    def _recursive_render_spec(self, s, max_passes=25, **kwargs):
        for i in range(0, max_passes):

            changed, s = self._rerender_spec(s, **kwargs)

            if not changed:
                break
            elif i == max_passes - 1:
                fatal(
                    'Maximum number of rendering passes reached '
                    'but spec still changing')

        return s

    def _enhanced_yaml_module(self, sysconfig):

        # NOTE: This is soo ugly, sorry for that, in future we need to modify
        # PyYAML to let us specify callbacks, somehow.  But for now, import
        # yaml right here (local import) to be able to add the
        # constructors/representers **only** locally (don't modify global
        # context).
        def _eval_node(loader, node):
            return str(eval(str(loader.construct_scalar(node)), {
                'project': self.project,
                'config': sysconfig,
                'macros': sysconfig['macros'],
            }))

        import yaml
        try:
            yaml.add_constructor(u'!eval', _eval_node, yaml.FullLoader)
            yaml.dg_load = functools.partial(yaml.load, Loader=yaml.FullLoader)
        except AttributeError:
            # Older versions of PyYAML don't have yaml.FullLoader, remove this
            # once we don't have to deal with those.
            yaml.add_constructor(u'!eval', _eval_node)
            yaml.dg_load = yaml.load

        return yaml

    def render(self, specfiles, multispec, multispec_selectors, template,
               config, cmd_cfg, output, confdirs=None,
               explicit_macros={}, max_passes=1):
        """ render single template """
        config_path = [self.project.directory] + self.pm_cfg.get_path()
        sysconfig = load_config(config_path, config)

        if not confdirs:
            confdirs = []
        for i in confdirs + [self.project.directory]:
            additional_vars = self.load_config_from_project(i)
            self.vars_fill_variables(additional_vars, sysconfig)
            # filter only interresting variables
            interresting_parts = ['macros']
            additional_vars = {
                x: additional_vars[x] for x in
                interresting_parts if x in additional_vars}
            sysconfig = merge_yaml(sysconfig, additional_vars)

        self.project.abstract_setup_vars(sysconfig)

        self.project.inst_init(specfiles, template, sysconfig)

        projcfg = self.load_config_from_project(self.project.directory)
        if projcfg and 'name' in projcfg:
            sysconfig['name'] = projcfg['name']
        self.vars_fill_variables(sysconfig)

        explicit_macros = {'macros': explicit_macros}
        self.vars_fill_variables(explicit_macros, sysconfig)
        sysconfig = merge_yaml(sysconfig, explicit_macros)

        yaml = self._enhanced_yaml_module(sysconfig)

        spec = {}
        for specfile in specfiles or []:
            specfd = self.pm_spc.open_file(
                specfile,
                [self.project.directory],
                fail=True,
            )
            if not specfd:
                fatal("Spec file {0} not found".format(specfile))

            try:
                specdata = yaml.dg_load(specfd)
                spec = merge_yaml(spec, specdata)
            except yaml.YAMLError as exc:
                fatal("Error in spec file: {0}".format(exc))
        if multispec:
            try:
                mltspc = Multispec.from_path(self.project.directory, multispec)
                spec = merge_yaml(
                    spec, mltspc.select_data(multispec_selectors, config))
            except yaml.YAMLError as exc:
                fatal("Error in multispec file: {0}".format(exc))
            except MultispecError as exc:
                fatal(str(exc))

        try:
            tpl = self.project.tplgen.get_template(template)
        except jinja2.exceptions.TemplateNotFound as err:
            fatal("Can not find template {0}".format(err))

        self.project.inst_finish(specfiles, template, sysconfig, spec)

        rendering_kwargs = {
            'config': sysconfig,
            'macros': sysconfig['macros'],
            'm': sysconfig['macros'],
            'container': {'name': 'docker'},
            'spec': spec,
            'project': self.project,
            'commands': Commands(cmd_cfg, sysconfig),
            'env': os.environ,
        }

        self._recursive_render_spec(
            spec,
            max_passes=max_passes,
            **rendering_kwargs
        )

        output.write(tpl.render(**rendering_kwargs).encode('utf-8'))
