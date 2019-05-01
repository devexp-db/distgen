import distro
import subprocess


def detect_default_distro():
    os, version, name = distro.linux_distribution(full_distribution_name=True)
    os = os.lower()

    if os == 'fedora':
        if name.lower() == 'rawhide':
            version = 'rawhide'
    elif os in ['centos', 'rhel']:
        pass
    else:
        return None

    # Only RPM distros for now:
    cmd = ['rpm', '--eval', '%_arch']
    arch = subprocess.check_output(cmd).decode('ascii').strip()

    return '{0}-{1}-{2}.yaml'.format(os, version, arch)
