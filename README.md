Distribution oriented templating system
=======================================

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

Download/Installation
---------------------

Stable releases of distgen are available (for Red Hat distributions) in
[Copr](https://copr.fedoraproject.org/coprs/praiskup/distgen).

You can also run development version directly from `git`, simply use the `dg`
shell wrapper available in git root directory.

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

Multispec and Rendering Matrix
==============================

When using distgen, you'll often find yourself needing to build multiple
variations of the image. For example, you might want to build an image
based on 3 different distributions and do so for 2 different versions
of that software. To make that easy, distgen provides a feature called
"multispec". An example multispec file follows:

    ```
    version: 1
    
    specs:
      distroinfo:
        fedora:
          distros:
            - fedora-26-x86_64
            - fedora-25-x86_64
          vendor: "Fedora Project"
        centos:
          distros:
            - centos-7-x86_64
          vendor: "CentOS"
      version:
        "2.2":
          version: 2.2
        "2.4":
          version: 2.4
    
    matrix:
      exclude:
        - distroinfo: fedora
          distros:
            - fedora-26-x86_64
          version: 2.2
    ```

A multispec has 3 attributes (see below for the explanation of mechanics
behind this file):

* `version` (mandatory) - The version of the multispec file, currently there's
  only version `1`.
* `specs` (mandatory) - contains list of *groups* (`distroinfo` and `version`
  in the example above). Each *group* contains named specs - these are exactly
  like the specs that you would otherwise write into separate files and pass
  to distgen via `--spec`.

  * The `distroinfo` *group* is mandatory and each of its members *must*
    contain the `distros` list. These are names of the distro configs
    shipped with distgen.

* `matrix` (optional) - currently, this attribute can only contain the
  `exclude` member. When used, the `exclude` attribute contains a list
  of combinations excluded from the matrix.

How multispec works:

Let's consider the example above. We could use it like this:

    ```
    $ dg --template docker.tpl \
         --spec FOO.yaml \
         --multispec MULTISPEC.yaml \
         --multispec-selector version=2.4 \
         --distro fedora-26-x86_64.yaml \
    > Dockerfile
    ```

On calling this command, distgen will:

* Take values from `FOO.yaml` for base of the result values used for
  rendering the template.
* It will then add values from `MULTISPEC.yaml`:

  * The `--distro fedora-26-x86_64` argument will automatically select
    the `distroinfo.fedora` section of multispec and add it to result
    values.
  * The `--multispec-selector version=2.4` will make the `version."2.4"`
    section of multispec added to the result values.

* Render the template providing the result of operations above accessible
  under `spec.*` values.

Some notes on usage:

* There can be as many *groups* as you want, not just `distroinfo` and
  `version`. This also means that you need to use `--multispec-selector`
  multiple times on commandline.
* The `--multispec-selector` must be used for all groups except `distroinfo`.
  A proper section to be used from `distroinfo` is implicitly specified
  by passing the `--distro` argument.
* Only a combination of specs belonging to *groups* can be used when using
  multispec. In the example above, you can't use fedora-22\_i686, since
  it's not listed in any `distroinfo` section.
* Combinations explicitly listed in `matrix.exclude` cannot be used.

Multispec mainly solves two problems:

* With multispec, you don't have to write multiple simple specs (e.g. in this
  case, you'd have to write a separate spec for version 2.2 and for version
  2.4, each of which would contain only the `version` attribute).
* Multispec specifies combinations (== matrix) of individual specs, that are
  supposed to be used to render the Dockerfile.
