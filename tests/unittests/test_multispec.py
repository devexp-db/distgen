import os

import pytest
import yaml

from distgen.multispec import Multispec, MultispecError


here = os.path.dirname(__file__)
fixtures = os.path.join(here, 'fixtures')
ms_fixtures = os.path.join(fixtures, 'multispec')
simplest = {'version': '1',
            'specs': {'distroinfo': {'fedora': {'distros': ['fedora-26-x86_64']}}}
            }


class TestMultispec(object):
    @pytest.mark.parametrize('proj_dir, path', [
        (ms_fixtures, 'simplest.yaml'),
        (fixtures, os.path.join('multispec', 'simplest.yaml')),
    ])
    def test_from_path_ok(self, proj_dir, path):
        assert Multispec.from_path(proj_dir, path).raw_data == simplest

    def test_from_path_nok(self):
        with pytest.raises(SystemExit):
            Multispec.from_path('.', 'nope')

    def test_validate(self):
        with open(os.path.join(ms_fixtures, 'complex.yaml')) as f:
            Multispec(yaml.load(f, Loader=yaml.SafeLoader))._validate()

    def test_has_spec_group(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.has_spec_group('something_else')
        assert not ms.has_spec_group('nope')

    def test_get_spec_group(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.get_spec_group('version') == \
            {'2.2': {'version': '2.2'}, '2.4': {'version': '2.4'}}
        with pytest.raises(KeyError):
            ms.get_spec_group('nope')

    def test_has_spec_group_item(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.has_spec_group_item('something_else', 'foo')
        assert not ms.has_spec_group_item('something_else', 'nope')

    def test_get_spec_group_item(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.get_spec_group_item('something_else', 'foo') == {'spam': 'ham'}
        with pytest.raises(KeyError):
            ms.get_spec_group_item('something_else', 'nope')

    def test_get_all_combinations_simple(self):
        ms = Multispec.from_path(ms_fixtures, 'simplest.yaml')
        assert list(ms.get_all_combinations()) == [{'distro': 'fedora-26-x86_64.yaml'}]

    def test_get_all_combinations_complex(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        def comb_key(c):
            return (c['distro'], c['something_else'], c['version'])
        assert sorted(ms.get_all_combinations(), key=comb_key) == sorted([
            {'distro': 'centos-7-x86_64.yaml', 'something_else': 'bar', 'version': '2.2'},
            {'distro': 'centos-7-x86_64.yaml', 'something_else': 'bar', 'version': '2.4'},
            {'distro': 'centos-7-x86_64.yaml', 'something_else': 'foo', 'version': '2.2'},
            {'distro': 'centos-7-x86_64.yaml', 'something_else': 'foo', 'version': '2.4'},
            {'distro': 'centos-7-x86_64.yaml', 'something_else': 'baz', 'version': '2.2'},
            {'distro': 'centos-7-x86_64.yaml', 'something_else': 'baz', 'version': '2.4'},
            {'distro': 'fedora-26-x86_64.yaml', 'something_else': 'bar', 'version': '2.2'},
            {'distro': 'fedora-26-x86_64.yaml', 'something_else': 'bar', 'version': '2.4'},
            {'distro': 'fedora-26-x86_64.yaml', 'something_else': 'foo', 'version': '2.4'},
            {'distro': 'fedora-26-x86_64.yaml', 'something_else': 'baz', 'version': '2.2'},
            {'distro': 'fedora-26-x86_64.yaml', 'something_else': 'baz', 'version': '2.4'},
            {'distro': 'fedora-25-x86_64.yaml', 'something_else': 'bar', 'version': '2.2'},
            {'distro': 'fedora-25-x86_64.yaml', 'something_else': 'foo', 'version': '2.2'},
            {'distro': 'fedora-25-x86_64.yaml', 'something_else': 'foo', 'version': '2.4'},
            {'distro': 'fedora-25-x86_64.yaml', 'something_else': 'baz', 'version': '2.2'},
            {'distro': 'fedora-25-x86_64.yaml', 'something_else': 'baz', 'version': '2.4'},
        ], key=comb_key)

    def test_parse_selectors_ok(self):
        ms = Multispec.from_path(ms_fixtures, 'simplest.yaml')
        assert ms.parse_selectors(['foo=bar', 'spam=ham']) == {'foo': 'bar', 'spam': 'ham'}

    def test_parse_selectors_nok(self):
        ms = Multispec.from_path(ms_fixtures, 'simplest.yaml')
        with pytest.raises(MultispecError):
            ms.parse_selectors(['foo bar'])

    @pytest.mark.parametrize('node, distro, selectors, expected', [
        ('exclude', 'fedora-26-x86_64', ['version=2.2'], [True, False]),
        ('exclude', 'fedora-26-x86_64', ['version=2.4'], [False, False]),
        ('combination_extras', 'fedora-26-x86_64', ['version=2.4'],
         [{'name_label': "$FGC/$NAME",
           'base_version': 1}, False]),
        ('combination_extras', 'fedora-26-x86_64', ['version=2.2'],
         [False, False]),
        ('combination_extras', 'centos-7-x86_64', ['version=2.2'],
         [False, {'name_label': 'centos/SW-2.2-centos7'}]),
    ])
    def test_check_matrix_combinations(self, node, distro,
                                       selectors, expected):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        parsed_selectors = ms.parse_selectors(selectors)
        assert list(ms.check_matrix_combinations(node,
                                                 distro,
                                                 parsed_selectors)) == expected

    def test_distrofile2name(self):
        ms = Multispec.from_path(ms_fixtures, 'simplest.yaml')
        assert ms.distrofile2name('foo/bar/fedora-26-x86_64.yaml') == 'fedora-26-x86_64'

    def test_verify_selectors_ok(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.verify_selectors(['version=2.4', 'something_else=foo'],
                                   distro='fedora-26-x86_64') == (True, '')

    @pytest.mark.parametrize('selectors, distro, msg', [
        (['distroinfo=fedora'], 'fedora-26-x86_64', '"distroinfo" not allowed in selectors, it is '
         'chosen automatically based on distro'),
        (['version=2.2'], 'fedora-26-x86_64', '"something_else" selector must be present'),
        (['xxx=asd'], 'fedora-26-x86_64', '"xxx" not an entry in specs'),
        (['version=3.4'], 'fedora-26-x86_64', '"3.4" not an entry in specs.version'),
        (['version=2.2', 'something_else=foo'], 'fedora-26-x86_64', 'This combination is excluded '
         'in matrix section'),
        (['version=2.4', 'something_else=foo'], 'fedora-27-x86_64', '"fedora-27-x86_64" distro '
         'not found in any specs.distroinfo.*.distros section'),
    ])
    def test_verify_selectors_nok(self, selectors, distro, msg):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.verify_selectors(selectors, distro) == (False, msg)

    def test_select_data_ok(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        assert ms.select_data(['version=2.4', 'something_else=foo'], 'fedora-26-x86_64') == \
            {'authoritative_source_url': 'some.url.fedoraproject.org',
             'distro_specific_help': 'Some Fedora specific help',
             'spam': 'ham',
             'vendor': 'Fedora Project',
             'version': '2.4',
             'base_version': 1,
             'name_label': '$FGC/$NAME'}

    def test_select_data_nok(self):
        ms = Multispec.from_path(ms_fixtures, 'complex.yaml')
        with pytest.raises(MultispecError):
            ms.select_data(['version=2.4', 'something_else=foobar'], 'fedora-27-x86_64')
