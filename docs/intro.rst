Introduction to distgen
=======================

`Distgen <https://github.com/devexp-db/distgen/>`_ is a distribution-oriented
templating system.

The problem this project tries to mitigate is "portable" scripting for variety
of operating systems (currently Linux distributions only) in the wild.  While
writing a "universal" script, one needs to take into account small or bigger
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
`Copr <https://copr.fedoraproject.org/coprs/praiskup/distgen>`_.

You can also run development version directly from
`Github <https://github.com/devexp-db/distgen/>`_, simply use the
``dg`` shell wrapper available in git root directory. In order to use
distgen from git checkout, you'll need to install dependencies manually.
You can do that e.g. using pip: ``pip install --user -r requirements.txt``.

Simple Example with Dockerfile
------------------------------

Typical example is the need to instantiate working Dockerfile for list
of supported **Fedora/CentOS** versions.

1. Create ``common.yaml`` spec::

     # This file provides basic values that are the same for all various rendering combinations
     name: myawesomeimage
     description: "This is a simple container that just tells you how awesome it is. That's it."

2. Create ``multispec.yaml`` spec::

     # This file specifies rendering "matrix" - the different combinations of values
     # that the templates can be rendered for
     version: 1

     # "specs" contains named "spec groups"
     specs:
       # "distroinfo" is a mandatory "spec group"
       # - each of its members must contain "distros" list
       # - it can also contain any extra values
       distroinfo:
         fedora:
           distros:
             - fedora-26-x86_64
             - fedora-25-x86_64
           vendor: "Fedora Project"
           authoritative_source_url: "some.url.fedoraproject.org"
           distro_specific_help: "Some Fedora specific help"
         centos:
           distros:
             - centos-7-x86_64
           vendor: "CentOS"
           authoritative_source_url: "some.url.centos.org"
           distro_specific_help: "Some CentOS specific help"
       # apart from "distroinfo", you can specify as many arbitrary spec groups as you want
       # - any of the members of these spec groups can contain arbitrary values
       version:
         "2.2":
           version: "2.2"
         "2.4":
           version: "2.4"

3. Create a ``Dockerfile.template`` template

  .. code-block:: dockerfile

     # "config.*" values usually come from distribution configs shipped with distgen;
     # the config is specified by "--distro" argument to "dg" on command line
     FROM {{ config.docker.from }}
     
     LABEL MAINTAINER ...
     
     ENV NAME=mycontainer VERSION=0 RELEASE=1 ARCH=x86_64
     
     # "spec.*" values are result of merging any specs passed by "--spec" to "dg"
     # and values selected from multispec file (if used) - see below
     LABEL summary="A container that tells you how awesome it is." \
           com.redhat.component="$NAME" \
           version="$VERSION" \
           release="$RELEASE.$DISTTAG" \
           architecture="$ARCH" \
           usage="docker run -p 9000:9000 mycontainer" \
           help="Runs mycontainer, which listens on port 9000 and tells you how awesome it is. No dependencies." \
           description="{{ spec.description }}" \
           vendor="{{ spec.vendor }}" \
           org.fedoraproject.component="postfix" \
           authoritative-source-url="{{ spec.authoritative_source_url }}" \
           io.k8s.description="{{ spec.description }}" \
           io.k8s.display-name="Awesome container with SW version {{ spec.software_version }}" \
           io.openshift.expose-services="9000:http" \
           io.openshift.tags="some,tags"
     
     EXPOSE 9000
     
     # We don't actually use the "software_version" here, but we could,
     #  e.g. to install a module with that ncat version
     RUN {{ commands.pkginstaller.install(['nmap-ncat']) }} && \
         {{ commands.pkginstaller.cleancache() }}
     
     RUN echo '#!/bin/bash' > /usr/bin/script.sh && \
         echo "exec nc -kl 9000 -c 'echo -e \"HTTP/1.1 200 OK\n\";echo \"I am awesome\"'" >> /usr/bin/script.sh && \
         chmod +x /usr/bin/script.sh
     
     CMD ["/usr/bin/script.sh"]


4. Run the ``dg`` tool to generate a **Fedora 26** Dockerfile with software
   version **2.4**::

     # when using "--multispec", "--multispec-selector" must be used for all
     # spec groups except "distroinfo"
     $ dg --template Dockerfile.template \
          --spec common.yaml \
          --multispec multispec.yaml \
          --multispec-selector version=2.4 \
          --distro fedora-26-x86_64.yaml \
     > Dockerfile

5. Run the ``dg`` tool again to generate a **CentOS 7** dockerfile with software
   version **2.2**::

     $ dg --template Dockerfile.template \
          --spec common.yaml \
          --multispec multispec.yaml \
          --multispec-selector version=2.2 \
          --distro centos-7-x86_64.yaml \
     > Dockerfile

There are more nuances and features of distgen that you can utilize,
all of them are documented in the following sections of this documentation.
