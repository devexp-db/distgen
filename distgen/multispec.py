import copy
import itertools
import os

import yaml

from distgen.config import merge_yaml
from distgen.pathmanager import PathManager


DISTROINFO_GRP = 'distroinfo'
DISTROINFO_GRP_DISTROS = 'distros'


class MultispecError(Exception):
    def __init__(self, cause):
        self.cause = cause

    def __str__(self):
        return self.cause


class Multispec(object):
    def __init__(self, data):
        self.raw_data = data
        self._validate()
        self._version = None
        self._specgroups = {}
        self._matrix = {}
        self._process()

    @classmethod
    def from_path(cls, project_dir, path):
        pm = PathManager([])
        fd = pm.open_file(path, [project_dir], fail=True)
        data = yaml.load(fd, Loader=yaml.SafeLoader)
        return cls(data)

    def _process(self):
        self._version = int(self.raw_data['version'])
        self._specgroups = self.raw_data['specs']
        self._matrix = self.raw_data.get('matrix', {})  # optional

    def _validation_err(self, err):
        raise MultispecError('Multispec validation error: ' + err)

    def _validate(self):
        # TODO: perhaps use jsonschema or something similar?
        if not isinstance(self.raw_data, dict):
            self._validation_err('multispec must be a mapping, is "{0}"'.
                                 format(type(self.raw_data)))
        self._validate_version(self.raw_data.get('version', None))
        self._validate_specs(self.raw_data.get('specs', None))
        self._validate_matrix(self.raw_data.get('matrix', {}))

    def _validate_version(self, version):
        try:
            v = int(version)
        except TypeError:
            self._validation_err(
                'version must be int or string convertable '
                'to string, is "{0}"'.format(version))
        if v != 1:
            self._validation_err(
                'only version "1" is recognized by this distgen version')

    def _validate_specs(self, specs):
        if not isinstance(specs, dict):
            self._validation_err(
                '"specs" must be a mapping, is "{0}"'.format(type(specs)))

        for k, v in specs.items():
            self._validate_spec_group(k, v)

        if 'distroinfo' not in specs:
            self._validation_err('"distroinfo" must be in "specs"')

    def _validate_spec_group(self, name, spec_group):
        if not isinstance(spec_group, dict):
            self._validation_err(
                'a spec group "{0}" must be a mapping, is "{1}"'.
                format(name, type(spec_group)))
        for k, v in spec_group.items():
            self._validate_single_spec(name, k, v)

    def _validate_single_spec(self, groupname, specname, spec):
        if not isinstance(spec, dict):
            self._validation_err('a spec "{0}" must be a mapping, is "{1}"'.
                                 format(specname, type(spec)))

        if groupname == 'distroinfo':
            if 'distros' not in spec:
                self._validation_err(
                    '"distroinfo" spec "{0}" must contain "distros" list'.
                    format(specname))
            self._validate_distros(spec['distros'])

    def _validate_distros(self, distros):
        if not isinstance(distros, list):
            self._validation_err(
                '"distros" entry must be a list, is "{0}"'.
                format(type(distros)))

    def _validate_matrix(self, matrix):
        if not isinstance(matrix, dict):
            self._validation_err(
                'matrix must be a mapping, is "{0}"'.format(type(matrix)))

        self._validate_matrix_node('exclude', matrix)
        self._validate_matrix_node('combination_extras', matrix)

    def _validate_matrix_node(self, node_name, matrix):
        node = matrix.get(node_name, [])
        if not isinstance(node, list):
            self._validation_err(
                'matrix.{0} must be a list, is "{1}"'.
                format(node_name, type(node)))

        for e in node:
            self._validate_single_matrix_item(e, node_name)

    def _validate_single_matrix_item(self, item, name):
        if not isinstance(item, dict):
            self._validation_err(
                'each matrix node item must be a mapping, not "{0}"'.
                format(type(item)))

        if 'distroinfo' in item:
            self._validation_err(
                'a matrix.{0} member must not contain "distroinfo", '
                'use "distro" list instead'.format(name))

        if 'distros' in item and not isinstance(item['distros'], list):
            self._validation_err(
                'matrix.{0}.*.distros must be a list, found "{1}"'.
                format(name, type(item['distros'])))

    def has_spec_group(self, group):
        return group in self._specgroups

    def get_spec_group(self, group):
        return copy.deepcopy(self._specgroups[group])

    def get_distroinfos_by_distro(self, distro):
        distroinfos = []

        for di in self.get_spec_group(DISTROINFO_GRP):
            item = self.get_spec_group_item(DISTROINFO_GRP, di)
            if distro in item[DISTROINFO_GRP_DISTROS]:
                distroinfos.append(item)

        return distroinfos

    def has_spec_group_item(self, group, item):
        return (self.has_spec_group(group)
                and item in self.get_spec_group(group))

    def get_spec_group_item(self, group, item):
        return copy.deepcopy(self.get_spec_group(group)[item])

    def get_all_combinations(self):
        distros = set()

        for _, spec_vals in self.get_spec_group(DISTROINFO_GRP).items():
            distros.update(spec_vals[DISTROINFO_GRP_DISTROS])

        values = [[{'group': 'distro', 'value': d + '.yaml'} for d in distros]]
        for grp_name, grp_vals in self._specgroups.items():
            if grp_name != DISTROINFO_GRP:
                values.append([{
                    'group': grp_name, 'value': v} for v in grp_vals.keys()
                ])

        for combination in itertools.product(*values):
            selector_dict = {p['group']: p['value'] for p in combination}
            as_selectors = ['{0}={1}'.format(k, v)
                            for k, v in selector_dict.items() if k != 'distro']
            if self.verify_selectors(
                    as_selectors,
                    self.distrofile2name(selector_dict['distro']))[0]:
                yield selector_dict

    def check_matrix_combinations(self, node, distro, parsed_selectors):

        def process_combinations(data, distro, parsed_selectors):
            for k, v in data.items():
                if k == DISTROINFO_GRP_DISTROS and distro not in v:
                    return False
                elif (k != DISTROINFO_GRP_DISTROS and k in parsed_selectors
                      and parsed_selectors[k] != v):
                    return False
            return data.get('data', True)

        for data in self._matrix.get(node, []):
            yield process_combinations(data, distro, parsed_selectors)

    def verify_selectors(self, selectors, distro):
        parsed_selectors = self.parse_selectors(selectors)

        if DISTROINFO_GRP in parsed_selectors.keys():
            return (
                False,
                ('"{0}" not allowed in selectors, it is chosen '
                 'automatically based on distro'.format(DISTROINFO_GRP)))

        # first, verify that these selector values even exist in specs
        for selector_name, selector_val in parsed_selectors.items():
            if not self.has_spec_group(selector_name):
                return (
                    False,
                    '"{0}" not an entry in specs'.format(selector_name)
                )
            elif not self.has_spec_group_item(selector_name, selector_val):
                return (
                    False,
                    '"{0}" not an entry in specs.{1}'.format(
                        selector_val, selector_name)
                )

        for selector_name in self.raw_data['specs'].keys():
            if (selector_name != DISTROINFO_GRP
                    and selector_name not in parsed_selectors):
                return (
                    False,
                    '"{0}" selector must be present'.format(selector_name)
                )

        # second, verify that these selector values are not excluded by matrix
        if any([v for v in self.check_matrix_combinations('exclude',
                                                          distro,
                                                          parsed_selectors)]):
            return False, 'This combination is excluded in matrix section'

        # third, make sure we have a distroinfo section that contains
        # passed distro
        if not self.get_distroinfos_by_distro(distro):
            msg = (
                '"{0}" distro not found in any '
                'specs.distroinfo.*.distros section'.format(distro)
            )
            return (False, msg)

        return True, ''

    def select_data(self, selectors, distrofile):
        distro = self.distrofile2name(distrofile)
        allowed, reason = self.verify_selectors(selectors, distro)
        if not allowed:
            raise MultispecError(reason)

        parsed_selectors = self.parse_selectors(selectors)
        selected_data = {}

        for selector_name, selector_val in parsed_selectors.items():
            spec_content = self.get_spec_group_item(
                selector_name, selector_val)
            selected_data = merge_yaml(selected_data, spec_content)

        for di in self.get_distroinfos_by_distro(distro):
            # we don't want the list of allowed distros to end up in spec
            di = copy.deepcopy(di)
            di.pop(DISTROINFO_GRP_DISTROS)
            selected_data = merge_yaml(selected_data, di)

        for extras in self.check_matrix_combinations('combination_extras',
                                                     distro,
                                                     parsed_selectors):
            if extras:
                selected_data = merge_yaml(selected_data, extras)

        return selected_data

    def parse_selectors(self, selectors):
        res = []
        for selector in selectors:
            if selector.count('=') != 1:
                raise MultispecError(
                    'selector "{0}" does not contain exactly one "="'.
                    format(selector))
            else:
                res.append(selector.split('='))
        return dict(res)

    def distrofile2name(self, distro):
        return os.path.splitext(os.path.basename(distro))[0]
