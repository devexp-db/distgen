import os

import pytest
import six

from distgen.commands import CommandsConfig
from distgen.generator import Generator
from distgen.project import AbstractProject


here = os.path.dirname(__file__)
fixtures = os.path.join(here, 'fixtures', 'generator')
simple = os.path.join(fixtures, 'simple')


class TestGenerator(object):
    def setup_method(self, method):
        self.g = Generator()

    def test_load_project(self):
        self.g.load_project(simple)
        assert isinstance(self.g.project, AbstractProject)
        assert self.g.project.directory == simple
        assert hasattr(self.g.project, 'tplgen')

    @pytest.mark.parametrize('config, result', [
        ({'foo': 'bar'}, {'foo': 'bar'}),
        ({'foo': 'bar', 'baz': '$foo-asd'}, {'foo': 'bar', 'baz': 'bar-asd'}),
        ({'foo': 'bar', 'baz': '$foo-asd', 'x': 'x-$baz'},
         {'foo': 'bar', 'baz': 'bar-asd', 'x': 'x-bar-asd'}),
    ])
    def test_vars_fixed_point(self, config, result):
        self.g.vars_fixed_point(config)
        assert config == result

    @pytest.mark.parametrize('config, sysconfig, result', [
        ({'macros': {'x': '$y', 'y': 'z'}}, None, {'macros': {'x': 'z', 'y': 'z'}}),
        ({'macros': {'x': '$y'}}, {'macros': {'y': 'z'}}, {'macros': {'x': 'z'}}),
    ])
    def test_fill_variables(self, config, sysconfig, result):
        self.g.vars_fill_variables(config, sysconfig)
        assert config == result

    @pytest.mark.parametrize('template, max_passes, result', [
        (os.path.join(simple, 'Dockerfile'), 1,
         open(os.path.join(simple, 'expected_output')).read()),
        (os.path.join(simple, 'Dockerfile'), 10, # should be the same no matter how many passes
         open(os.path.join(simple, 'expected_output')).read()),
        ('{{ config.os.id }}', 1, 'fedora'),
        ("{{ '{{ config.os.id }}' }}", 1, '{{ config.os.id }}'),
        ("{{ '{{ config.os.id }}' }}", 3, 'fedora'),
    ])
    def test_render(self, template, max_passes, result):
        # TODO: more test cases for rendering
        self.g.load_project(simple)
        out = six.StringIO()
        self.g.render(
            [os.path.join(simple, 'common.yaml')],
            os.path.join(simple, 'complex.yaml'),
            ['version=2.4', 'something_else=foo'],
            template,
            'fedora-26-x86_64.yaml',
            CommandsConfig(),
            out,
            max_passes=max_passes,
        )

        if six.PY2:
            result = result.decode('utf-8')
        assert out.getvalue() == result
