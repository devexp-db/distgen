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
        self._version = None
        self._specgroups = {}
        self._matrix = {}
        self._process()

    def _process(self):
        # TODO: validate
        self._version = self.raw_data['version']
        self._specgroups = self.raw_data['specs']
        self._matrix = self.raw_data.get('matrix', {})  # optional

    def has_spec_group(self, group):
        return group in self._specgroups

    def get_spec_group(self, group):
        return copy.deepcopy(self._specgroups[group])

    def has_spec_group_item(self, group, item):
        return self.has_spec_group(group) and item in self.get_spec_group(group)

    def get_spec_group_item(self, group, item):
        return copy.deepcopy(self.get_spec_group(group)[item])

    def verify_selectors(self, selectors, distro):
        parsed_selectors = self.parse_selectors(selectors)
        distro = self.normalize_distro(distro)

        # first, verify that these selector values even exist in specs
        for selector_name, selector_val in parsed_selectors.items():
            if not self.has_spec_group(selector_name):
                return False, '"{0}" not an entry in specs'.format(selector_name)
            elif not self.has_spec_group_item(selector_name, selector_val):
                return False, '"{0}" not an entry in specs.{1}'.format(
                    selector_val, selector_name)

        # second, verify that the distro is allowed for given distroinfo
        distroinfo_spec = self.get_spec_group_item(DISTROINFO_GRP, parsed_selectors[DISTROINFO_GRP])
        if distro not in distroinfo_spec[DISTROINFO_GRP_DISTROS]:
            return False, '"{0}" not an allowed distro for "{1}" distroinfo'.format(
                distro, parsed_selectors['distroinfo'])

        # third, verify that these selector values are not excluded by matrix
        for excluded in self._matrix.get('excluded', []):
            exclude = True
            for k, v in excluded.items():
                if k == DISTROINFO_GRP_DISTROS and distro in v:
                    exclude = True
                elif k != DISTROINFO_GRP_DISTROS and parsed_selectors[k] == v:
                    exclude = True
            return False, 'This combination is excluded in matrix section'

        return True, ''

    def select_data(self, selectors, distro):
        allowed, reason = self.verify_selectors(selectors, distro)
        if not allowed:
            raise MultispecError(reason)

        parsed_selectors = self.parse_selectors(selectors)
        selected_data = {}

        for selector_name, selector_val in parsed_selectors.items():
            # we don't want the list of allowed distros to end up in spec
            spec_content = self.get_spec_group_item(selector_name, selector_val)
            if selector_name == DISTROINFO_GRP:
                spec_content.pop(DISTROINFO_GRP_DISTROS)
            selected_data = merge_yaml(selected_data, spec_content)

        return selected_data

    def parse_selectors(self, selectors):
        return dict([s.split('=') for s in selectors])

    def normalize_distro(self, distro):
        return os.path.splitext(os.path.basename(distro))[0]
