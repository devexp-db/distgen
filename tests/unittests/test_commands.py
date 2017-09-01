import pytest

from distgen.commands import DnfPkgManager, YumPkgManager

class TestIndividualPkgManagers(object):
    def setup_method(self, method):
        class Config(object):
            def __init__(self, interactive, container=None):
                self.interactive = interactive
                self.container = container

        self.mgrs = {'yumi': YumPkgManager(Config(True)),
                     'yumni': YumPkgManager(Config(False)),
                     'dnfi': DnfPkgManager(Config(True)),
                     'dnfni': DnfPkgManager(Config(False)),
                     }

    @pytest.mark.parametrize('m, action, result', [
        ('yumi', 'install', 'yum install foo bar'),
        ('yumni', 'install', 'yum -y install foo bar'),
        ('yumi', 'reinstall', 'yum reinstall foo bar'),
        ('yumni', 'reinstall', 'yum -y reinstall foo bar'),
        ('yumi', 'remove', 'yum remove foo bar'),
        ('yumni', 'remove', 'yum -y remove foo bar'),
        ('yumi', 'update', 'yum update foo bar'),
        ('yumni', 'update', 'yum -y update foo bar'),
        ('dnfi', 'install', 'dnf install foo bar'),
        ('dnfni', 'install', 'dnf -y install foo bar'),
        ('dnfi', 'reinstall', 'dnf reinstall foo bar'),
        ('dnfni', 'reinstall', 'dnf -y reinstall foo bar'),
        ('dnfi', 'remove', 'dnf remove foo bar'),
        ('dnfni', 'remove', 'dnf -y remove foo bar'),
        ('dnfi', 'update', 'dnf update foo bar'),
        ('dnfni', 'update', 'dnf -y update foo bar'),
    ])
    def test_pkg_methods(self, m, action, result):
        assert getattr(self.mgrs[m], action)(['foo', 'bar']) == result

    @pytest.mark.parametrize('m, result', [
        ('yumi', 'yum update'),
        ('yumni', 'yum -y update'),
        ('dnfi', 'dnf update'),
        ('dnfni', 'dnf -y update'),
    ])
    def test_update_all(self, m, result):
        assert self.mgrs[m].update_all() == result

    @pytest.mark.parametrize('m, result', [
        ('yumi', 'yum clean all --enablerepo=\'*\''),
        ('yumni', 'yum -y clean all --enablerepo=\'*\''),
        ('dnfi', 'dnf clean all --enablerepo=\'*\''),
        ('dnfni', 'dnf -y clean all --enablerepo=\'*\''),
    ])
    def test_cleancache(self, m, result):
        assert self.mgrs[m].cleancache() == result
