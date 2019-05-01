import os
import sys
import pytest
from mock import patch

from distgen.distro_version import detect_default_distro


class TestDistroDetection(object):
    @pytest.mark.parametrize('arch', [b'x86_64', b'i386'])
    @pytest.mark.parametrize('distro, version, name, cversion', [
        ('fedora', 24, 'sth',            24),
        ('fedora', 25, 'sth',            25),
        ('fedora', 21, 'rawhide', 'rawhide'),
        ('rhel',    7, 'sth',             7),
    ])
    @patch('subprocess.check_output')
    @patch('distro.linux_distribution')
    def test_rpm(self, pdist, sp_co, distro, version, name, cversion, arch):
        sp_co.return_value = arch
        pdist.return_value = (distro, version, name)

        assert detect_default_distro() == '{0}-{1}-{2}.yaml'.format(
           distro, cversion, arch.decode('ascii')
        )


    @patch('distro.linux_distribution')
    def test_others(self, dist):
        dist.return_value = ('debian', 1, 'something')
        assert detect_default_distro() == None
