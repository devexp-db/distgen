import os

import pytest

from distgen.pathmanager import PathManager


this = os.path.abspath(__file__)
this_fn = os.path.basename(this)
here = os.path.dirname(this)
doesnt_exist = this + '.hahahaha'
open_file_type = type(open(this))


class TestPathmanager(object):
    def test_get_path(self):
        pm = PathManager(['some', 'path'])
        assert pm.get_path() == [os.getcwd()] + ['some', 'path']

        pm = PathManager(['some', 'path'], 'SOME_PATH_VAR')
        os.environ['SOME_PATH_VAR'] = 'foo:bar'
        assert pm.get_path() == [os.getcwd()] + ['foo', 'bar', 'some', 'path']

    def test_get_file_abspath(self):
        pm = PathManager([])
        assert pm.get_file(this) == this
        assert pm.get_file(doesnt_exist) is None

    @pytest.mark.parametrize('path, prefered_path, fail, retval', [
        ([], None, False, None),
        ([here], None, False, this),
        (['some/other/path', here], None, False, this),
        (['some/other/path'], [here], False, this),
        ([], None, True, SystemExit(1)),
    ])
    def test_get_file_relpath(self, path, prefered_path, fail, retval):
        pm = PathManager(path)
        if isinstance(retval, SystemExit):
            with pytest.raises(SystemExit) as e:
                pm.get_file(this_fn, prefered_path=prefered_path, fail=fail)
            assert e.value.code == retval.code
        else:
            assert pm.get_file(this_fn, prefered_path=prefered_path, fail=fail) == retval

    @pytest.mark.parametrize('path, prefered_path, fail, retval', [
        ([], None, False, type(None)),
        ([here], None, False, open_file_type),
        (['some/other/path', here], None, False, open_file_type),
        (['some/other/path'], [here], False, open_file_type),
        ([], None, True, SystemExit(1)),
    ])
    def test_get_file_relpath(self, path, prefered_path, fail, retval):
        pm = PathManager(path)
        if isinstance(retval, SystemExit):
            with pytest.raises(SystemExit) as e:
                pm.open_file(this_fn, prefered_path=prefered_path, fail=fail)
            assert e.value.code == retval.code
        else:
            assert isinstance(pm.open_file(this_fn, prefered_path=prefered_path, fail=fail),
                              retval)
