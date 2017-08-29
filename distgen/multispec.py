import copy
import os

from distgen.config import merge_yaml


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

    def _process(self):
        self._version = int(self.raw_data['version'])
        self._specgroups = self.raw_data['specs']
        self._matrix = self.raw_data.get('matrix', {})  # optional

    def _validation_err(self, err):
        raise MultispecError('Multispec validation error: ' + err)

    def _validate(self):
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
            self._validation_err('version must be int or string convertable to string, is "{0}"'.
                                 format(version))
        if v != 1:
            self._validation_err('only version "1" is recognized by this distgen version')

    def _validate_specs(self, specs):
        if not isinstance(specs, dict):
            self._validation_err('"specs" must be a mapping, is "{0}"'.format(type(specs)))

        for k, v in specs.items():
            self._validate_spec_group(k, v)

        if 'distroinfo' not in specs:
            self._validation_err('"distroinfo" must be in "specs"')

    def _validate_spec_group(self, name, spec_group):
        if not isinstance(spec_group, dict):
            self._validation_err('a spec group "{0}" must be a mapping, is "{1}"'.
                                 format(name, type(spec_group)))
        for k, v in spec_group.items():
            self._validate_single_spec(name, k, v)

    def _validate_single_spec(self, groupname, specname, spec):
        if not isinstance(spec, dict):
            self._validation_err('a spec "{0}" must be a mapping, is "{1}"'.
                                 format(specname, type(spec)))

        if groupname == 'distroinfo':
            if 'distros' not in spec:
                self._validation_err('"distroinfo" spec "{0}" must contain "distros" list'.
                                    format(specname))
            self._validate_distros(spec['distros'])

    def _validate_distros(self, distros):
        if not isinstance(distros, list):
            self._validation_err('"distros" entry must be a list, is "{0}"'.format(type(distros)))

    def _validate_matrix(self, matrix):
        if not isinstance(matrix, dict):
            self._validation_err('matrix must be a mapping, is "{0}"'.format(type(matrix)))

        self._validate_excludes(matrix.get('exclude', []))

    def _validate_excludes(self, excludes):
        if not isinstance(excludes, list):
            self._validation_err('matrix.exclude must be a list, is "{0}"'.format(type(excludes)))

        for e in excludes:
            self._validate_single_exclude(e)

    def _validate_single_exclude(self, exclude):
        if not isinstance(exclude, dict):
            self._validation_err('each exclude must be a mapping, not "{0}"'.format(type(exclude)))
        if 'distros' in exclude and not isinstance(exclude['distros'], list):
            self._validation_err('matrix.exclude.*.distros must be a list, found "{0}"'.
                                 format(type(exclude['distros'])))

    def has_spec_group(self, group):
        return group in self._specgroups

    def get_spec_group(self, group):
        return copy.deepcopy(self._specgroups[group])

    def get_distroinfos_by_distro(self, distro):
        distro = self.normalize_distro(distro)
        distroinfos = []

        for di in self.get_spec_group(DISTROINFO_GRP):
            item = self.get_spec_group_item(DISTROINFO_GRP, di)
            if distro in item[DISTROINFO_GRP_DISTROS]:
                distroinfos.append(item)

        return distroinfos

    def has_spec_group_item(self, group, item):
        return self.has_spec_group(group) and item in self.get_spec_group(group)

    def get_spec_group_item(self, group, item):
        return copy.deepcopy(self.get_spec_group(group)[item])

    def verify_selectors(self, selectors, distro):
        parsed_selectors = self.parse_selectors(selectors)
        distro = self.normalize_distro(distro)

        if DISTROINFO_GRP in parsed_selectors.keys():
            return False, \
                '"{0}" not allowed in selectors, it is chosen automatically based on distro'.\
                format(DISTROINFO_GRP)

        # first, verify that these selector values even exist in specs
        for selector_name, selector_val in parsed_selectors.items():
            if not self.has_spec_group(selector_name):
                return False, '"{0}" not an entry in specs'.format(selector_name)
            elif not self.has_spec_group_item(selector_name, selector_val):
                return False, '"{0}" not an entry in specs.{1}'.format(
                    selector_val, selector_name)

        # second, verify that these selector values are not excluded by matrix
        for excluded in self._matrix.get('excluded', []):
            exclude = True
            for k, v in excluded.items():
                if k == DISTROINFO_GRP_DISTROS and distro in v:
                    exclude = True
                elif k != DISTROINFO_GRP_DISTROS and parsed_selectors[k] == v:
                    exclude = True
            return False, 'This combination is excluded in matrix section'

        # third, make sure we have a distroinfo section that contains passed distro
        if not self.get_distroinfos_by_distro(distro):
            return False, '"{0}" distro not found in any specs.distroinfo.*.distros section'

        return True, ''

    def select_data(self, selectors, distro):
        allowed, reason = self.verify_selectors(selectors, distro)
        if not allowed:
            raise MultispecError(reason)

        parsed_selectors = self.parse_selectors(selectors)
        selected_data = {}

        for selector_name, selector_val in parsed_selectors.items():
            spec_content = self.get_spec_group_item(selector_name, selector_val)
            selected_data = merge_yaml(selected_data, spec_content)

        for di in self.get_distroinfos_by_distro(distro):
            # we don't want the list of allowed distros to end up in spec
            di = copy.deepcopy(di)
            di.pop(DISTROINFO_GRP_DISTROS)
            selected_data = merge_yaml(selected_data, di)

        return selected_data

    def parse_selectors(self, selectors):
        return dict([s.split('=') for s in selectors])

    def normalize_distro(self, distro):
        return os.path.splitext(os.path.basename(distro))[0]
