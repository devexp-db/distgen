import pytest

from distgen.err import fatal


class TestFatal(object):
    def test_fatal(self, capsys):
        with pytest.raises(SystemExit) as e:
            fatal('Message')
        assert capsys.readouterr()[1] == 'CRITICAL:root:Message\n'
        assert e.value.code == 1
