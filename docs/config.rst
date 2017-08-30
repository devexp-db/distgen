.. _configs:

Configs in distgen
==================

distgen provides lots of useful predefined values that you can use
in your templates. These are called *configs* or *distros*. When executing
distgen from commandline, you can use ``--distro <file>`` to select desired
config. You can either select a config that's shipped with distgen or you
can create and pass your own config.

You can browse through configs shipped with your distgen version in the
``/usr/share/distgen/distconf`` directory.

Builtin Configs
---------------

Following is a list of values that configs shipped with distgen provide.
Each item in the list contains a value example for ``centos-7-x86_64`` config.

* ``config.os.arch`` (e.g. ``x86_64``) - Architecture of the selected distro
* ``config.os.id`` (e.g. ``centos``) - Id of this distro inside distgen
* ``config.os.name`` (e.g. ``CentOS Linux``) - A verbose name of the distro
* ``config.os.version`` (e.g. ``7``) - Version of the distro
* ``config.docker.from`` (e.g. ``centos:7``) - Name (and possibly a tag) of the
  base image with this distro
* ``config.docker.registry`` (e.g. ``index.docker.io``) - Name of the registry
  where image specified by ``docker.from`` can be obtained
* ``macros`` - Macros provide paths to some useful directories of given distro;
  for more information on "why and how", see
  :ref:`macros documentation section <macros>`. Complete list of macros follows:

  * ``macros.bindir`` (e.g. ``/usr/bin``)
  * ``macros.datadir`` (e.g. ``/usr/share``)
  * ``macros.docdir`` (e.g. ``/usr/share/doc``)
  * ``macros.libdir`` (e.g. ``/usr/lib64``)
  * ``macros.libexecdir`` (e.g. ``/usr/libexec``)
  * ``macros.pkgdatadir`` - this will expand to ``/usr/share/$name``, if
    ``name`` is defined in the config - this is not true for default configs
  * ``macros.pkgdocdir`` - this will expand to ``/usr/share/doc/$name``, if
    ``name`` is defined in the config - this is not true for default configs
  * ``macros.prefix`` (e.g. ``/usr``)
  * ``macros.sbindir`` (e.g. ``/usr/sbin``)
  * ``macros.sysconfdir`` (e.g. ``/etc``)
  * ``macros.unitdir`` (e.g. ``/usr/lib/systemd/system``)
  * ``macros.userunitdir`` (e.g. ``/usr/lib/systemd/user``)

* ``config.package_installer.name`` (e.g. ``yum``) - name of the command that invokes
  distro package installer

Using Config Values in Templates
--------------------------------

Usage of config values in templates is simple. Here's a very simple example::

   FROM {{ config.docker.from }}

   COPY script.sh {{ macros.bindir }}

Creating Your Own Config
------------------------

When creating your own config, you don't need to specify any of these values,
a config can contain any values you want. In that case however, your
template must only use the values that your config has.
