Builtins
========

distgen provides some builtins that might come convenient to you while
writing templates. Following is an overview and usage instructions
of these builtins.

Commands
--------

If you use one of the builtin :ref:`configs <configs>` of distgen or your
config contains ``package_installer.name`` that is known (currently
either ``yum`` or ``dnf``), the ``commands.pkginstaller`` will be
available. Here's a list of valuable attributes and functions that
become available with ``commands.pkginstaller``:

* ``commands.pkginstaller.binary`` - the name of the binary of the installer
* ``commands.pkginstaller.install(['foo', 'bar'])`` - install ``foo`` and
  ``bar`` packages
* ``commands.pkginstaller.reinstall(['foo', 'bar'])`` - reinstall ``foo``
  and ``bar`` packages
* ``commands.pkginstaller.remove(['foo', 'bar'])`` - remove ``foo`` and
  ``bar`` packages
* ``commands.pkginstaller.update(['foo', 'bar'])`` - update ``foo`` and
  ``bar`` packages
* ``commands.pkginstaller.update_all()`` - update all installed packages
* ``commands.pkginstaller.cleancache()`` - clean installer cache
