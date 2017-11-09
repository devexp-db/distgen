import os

import pytest
import six

from distgen.commands import CommandsConfig
from distgen.generator import Generator
from distgen.project import AbstractProject


here = os.path.dirname(__file__)
fixtures = os.path.join(here, 'fixtures', 'generator')
simple = os.path.join(fixtures, 'simple')
simple_wp = os.path.join(fixtures, 'simple_with_projectfile')


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

    @pytest.mark.parametrize('project, result', [
        ('projectfile', 'bar'),
    ])
    def test_load_project(self, project, result):
        self.g.load_project(os.path.join(fixtures, project))
        self.g.project.inst_init(None, None, None)
        self.g.project.inst_finish(None, None, None, None)
        assert self.g.project.foo == 'bar'

    @pytest.mark.parametrize('project, template, max_passes, result', [
        (simple, os.path.join(simple, 'Dockerfile'), 2,
         open(os.path.join(simple, 'expected_output'), 'rb').read()),
        (simple, os.path.join(simple, 'Dockerfile'), 10, # should be the same no matter how many passes
         open(os.path.join(simple, 'expected_output'), 'rb').read()),
        (simple, '{{ config.os.id }}', 2, b'fedora'),
        (simple_wp, os.path.join(simple_wp, 'Dockerfile'), 10,
         open(os.path.join(simple_wp, 'expected_output'), 'rb').read()),
    ])
    def test_render(self, project, template, max_passes, result):
        # TODO: more test cases for rendering
        self.g.load_project(project)
        out = six.BytesIO()
        self.g.render(
            [os.path.join(project, 'common.yaml')],
            os.path.join(project, 'complex.yaml'),
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
