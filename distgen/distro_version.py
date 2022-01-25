"""
Detect distribution we are running on.
"""

import subprocess
import distro as distro_module


def detect_default_distro():
    """
    Based on the current information from python-distro module, return the
    expected default distgen config.  Return None if distro can not be detected.
    """

    distro, version, name = distro_module.linux_distribution(full_distribution_name=True)

    if distro == 'Fedora Linux':
        distro = 'Fedora'

    distro = distro.lower()

    if distro == 'fedora':
        if name.lower() == 'rawhide':
            version = 'rawhide'
    elif distro in ['centos', 'rhel']:
        pass
    else:
        return None

    # Only RPM distros for now:
    cmd = ['rpm', '--eval', '%_arch']
    arch = subprocess.check_output(cmd).decode('ascii').strip()

    return '{0}-{1}-{2}.yaml'.format(distro, version, arch)
