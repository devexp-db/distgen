Distribution oriented templating system
=======================================

[![Copr package](https://copr.fedorainfracloud.org/coprs/praiskup/distgen/package/distgen/status_image/last_build.png)](https://copr.fedorainfracloud.org/coprs/praiskup/distgen/)
[![Fedora package](https://img.shields.io/fedora/v/distgen)](https://packages.fedoraproject.org/pkgs/distgen/distgen/)
[![Coverage Status](https://coveralls.io/repos/github/devexp-db/distgen/badge.svg)](https://coveralls.io/github/devexp-db/distgen)
[![Documentation Status](https://readthedocs.org/projects/distgen/badge/?version=latest)](https://distgen.readthedocs.io)

The problem this project tries to mitigate is "portable" scripting for variety
of operating systems (currently Linux distributions only) in the wild.  While
writing an "universal" script, one needs to take into account small or bigger
differences among operating systems (like package installation tools, versions
of utilities, expected directories for binaries, libraries, etc.).

The *distgen* project is thus something like database of OS differences together
with convenience tool-set that allows you to instantiate valid script for
particular distribution.  The concept is to have *template* file (mostly raw
jinja2 template) together with "declarative" *spec* file (YAML file) that
fulfils the needs of particular template.

You can find distgen documentation at http://distgen.readthedocs.io.

Download/Installation
---------------------

Stable releases of distgen are available as RPMs in Fedora and EPEL
repositories, and in [pypi](https://pypi.python.org/pypi/distgen):

  ```
  $ sudo dnf install distgen

  $ pip install distgen
  ````

Development (git snapshot) RPMs are automatically built in [Fedora
Copr](https://copr.fedoraproject.org/coprs/praiskup/distgen).

You can also run development version directly from `git`, simply use the `dg`
shell wrapper available in this git root directory.

Example with Dockerfile
-----------------------

Typical example is the need to instantiate working **FOO** package oriented
**Dockerfile**s for all supported **Fedora/RHEL** versions.

To achieve that goal with distgen, you need to write something like
`docker.tpl` template and `FOO.yaml` spec file.  If the system-default
`docker.tpl` template is good enough, its enough to write proper spec file:

1. create `FOO.yaml` spec:

   ```
   $ cat FOO.yaml
   maintainer: John Doe <jdoe@example.com>
   parts:
     pkginstall:
       data:
         - type: pkg
           action: install
           packages:
             - vim
     footer:
       cmd: ["vim"]
   ```

2. Run `dg` tool to generate **Fedora 22** Dockerfile:

   ```
   $ dg --template docker.tpl \
        --spec FOO.yaml \
        --distro fedora-22-x86_64.yaml \
   > Dockerfile
   $ cat Dockerfile
   FROM index.docker.io/fedora:22
   MAINTAINER John Doe <jdoe@example.com>

   ENV container="docker"

   RUN dnf -y --setopt=tsflags=nodocs install vim \
       && dnf -y --setopt=tsflags=nodocs clean all --enablerepo='*'

   CMD ["vim"]
   ```

3. Run `dg` tool again to generate **RHEL 7** dockerfile:

    ```
    $ dg --template docker.tpl \
         --spec FOO.yaml \
         --distro rhel-7-x86_64.yaml \
    > Dockerfile
    $ cat Dockerfile
    FROM registry.access.redhat.com/rhel7
    MAINTAINER John Doe <jdoe@example.com>

    ENV container="docker"

    RUN yum -y --setopt=tsflags=nodocs install vim \
        && yum -y --setopt=tsflags=nodocs clean all --enablerepo='*'

    CMD ["vim"]
    ```
