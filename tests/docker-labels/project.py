config = {
    'macros': {
        # Directory under which 'atomic CMD' will mount Host's '/' directory
        # into (privileged) container.
        'atomic_hostdir': '/host',

        # Basic "privileged" docker command
        'atomic_docker_pcmd':
            "docker run -t -i --rm --privileged -u 0:0 "  + \
            "-v /:$atomic_hostdir --net=host --ipc=host --pid=host " + \
            "-e HOST=$atomic_hostdir " + \
            '-e LOGDIR=/var/log/"\\${NAME}" ' + \
            '-e DATADIR=/var/lib/"\\${NAME}" ' + \
            '-e CONFDIR=/etc/"\\${NAME}" ' + \
            '-e IMAGE="\\${IMAGE}" -e NAME="\\${NAME}" ' + \
            '-e OPT1 -e OPT2 -e OPT3 ' + \
            '\\${OPT2} \\${IMAGE}',

        # Atomic commands, should be redefined in dependant project.
        'atomic_install': '$atomic_docker_pcmd install',
        'atomic_uninstall': '$atomic_docker_pcmd install',
    }
}
