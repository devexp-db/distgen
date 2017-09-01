import os

from distgen.config import merge_yaml, load_config


class TestMergeYaml(object):
    def test_non_overlapping(self):
        a = {'a': 1, 'aa': 2}
        b = {'b': 3, 'bb': 4}
        assert merge_yaml(a, b) == {'a': 1, 'aa': 2, 'b': 3, 'bb': 4}

    def test_overlapping(self):
        a = {'a': 1, 'aa': 2, 'c': 111}
        b = {'b': 3, 'bb': 4, 'c': 112}
        assert merge_yaml(a, b) == {'a': 1, 'aa': 2, 'c': 112, 'b': 3, 'bb': 4}

    def test_nested(self):
        a = {'a': {'b': 'c', 'd': 'e'}}
        b = {'a': {'b': 'x', 'f': 'g'}}
        assert merge_yaml(a, b) == {'a': {'b': 'x', 'd': 'e', 'f': 'g'}}


class TestLoadConfig(object):
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', 'load_config')

    def test_simple(self):
        assert load_config([self.p], 'simple.yaml') == {'foo': 'bar', 'ham': {'and': 'spam'}}

    def test_recursive(self):
        assert load_config([self.p], 'level3.yaml') == \
            {'extends': 'level2.yaml', 'foo': 'override', 'ham': {'and': 'spam', 'or': 'eggs'}}
