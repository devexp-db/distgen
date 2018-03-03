import pytest
import logging

from distgen.err import fatal


class TestFatal(object):
    def test_fatal(self, capsys, caplog):
        with pytest.raises(SystemExit) as e:
            fatal('Message')
        assert caplog.record_tuples == [('root', logging.CRITICAL, 'Message')]
        assert e.value.code == 1
