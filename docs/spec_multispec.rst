Specs and Multispecs
====================

There are two ways in which the distgen command obtains values for template
rendering: :ref:`config <configs>` and specs. These two differ in their purpose.
While config values should provide template-agnostic values (e.g. facts about
a Linux distro), specs provide template-specific values (e.g. information about
version of software being built into a Docker image).

Spec values can be provided either through spec files or through multispec
files.

Specs
-----

Specs are simple key-value files that you can use in your templates.
You pass them to the ``dg`` command via ``--spec <file>`` (can be
specified multiple times).

Example spec::

   version: 2.4

Example template::

   This is documentation for version {{ spec.version }} of some software.

By using specs with different ``version`` in the example above, you could
render the template for various software versions. While this is ok for
simpler usecases, it might become impractical on bigger scale: imagine
you want to render a Dockerfile for an image, that will be based on several
different distributions and contain a combination of several versions
of 2 different packages. This would mean you'd need lots of small spec
files, each with couple of lines and you'd need to manually select and
pass them to the ``dg`` command. This is why the *multispec* mechanism
was added to distgen.

Multispecs
----------

Multispec is a file that solves two problems:

* Merges several different smaller spec files into a single file for better
  readability and convenience.
* Puts smaller specs in logical groups and defines a "matrix" - a list of all
  combinations of distro config and other features to render templates for.

Here's an example multispec file::

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
   
   # in the "matrix" section, you can define an action that is
   # applied only to specified distro and version combinations
   matrix:
     exclude:
       - distros:
           - fedora-26-x86_64
         version: "2.2"

     combination_extras:
       - distros:
           - centos-7-x86_64
         version: "2.4"
         data:
           extra_pkgs: ['foo', 'bar']

A multispec has 3 attributes (see below for the explanation of mechanics
behind this file):

* ``version`` (mandatory) - The version of the multispec file, currently there's
  only version ``1``.
* ``specs`` (mandatory) - contains list of *groups* (``distroinfo`` and
  ``version`` in the example above). Each *group* contains named specs -
  these are exactly like the specs that you would otherwise write into
  separate files and pass to distgen via ``--spec``.

  * The ``distroinfo`` *group* is mandatory and each of its members *must*
    contain the ``distros`` list. These are names of the distro configs
    shipped with distgen.
  * The ``specs`` *groups* implicitly define a rendering matrix, which
    is the cartesian product of all *groups* except ``distroinfo``. The
    ``distroinfo`` *group* is an exception, as its members ``distros`` list
    are used in the cartesian product.

* ``matrix`` (optional) - currently, this attribute can only contain three
  members.

  * The ``exclude`` attribute contains a list of combinations excluded
    from the matrix. The ``distroinfo`` members must be referred to via
    ``distro`` list.

  * The ``include`` attribute contains a list of combinations included
    from the matrix. The ``distroinfo`` members must be referred to via
    ``distro`` list.
  
  ``exclude`` and ``include`` are mutually exclusive.

  * The ``combination_extras`` member contains a list of combinations and
    extras, mapping of key-value pairs, which are only added to this combination
    and can be used in your templates.

Hence the above example produces a following rendering matrix:

* ``distroinfo: fedora`` (for ``fedora-25-x86_64`` distro), ``version: "2.2"``
* ``distroinfo: fedora`` (for ``fedora-25-x86_64`` distro), ``version: "2.4"``
* ``distroinfo: fedora`` (for ``fedora-26-x86_64`` distro), ``version: "2.4"``
* ``distroinfo: centos`` (for ``centos-7-x86_64`` distro), ``version: "2.2"``
* ``distroinfo: centos`` (for ``centos-7-x86_64`` distro), ``version: "2.4"``

Note that ``version: "2.2"`` is excluded for ``fedora-26-x86_64``.

Using Multispecs
^^^^^^^^^^^^^^^^

Let's consider the example above. We could use it like this::

   $ dg --template docker.tpl \
        --spec common.yaml \
        --multispec multispec.yaml \
        --multispec-selector version=2.4 \
        --distro fedora-26-x86_64.yaml \
   > Dockerfile

On calling this command, distgen will:

* Take values from ``common.yaml`` for base of the result values used for
  rendering the template.
* It will then add values from ``multispec.yaml``:

  * The ``--distro fedora-26-x86_64`` argument will automatically select
    the ``distroinfo.fedora`` section of multispec and add it to result
    values.
  * The ``--multispec-selector version=2.4`` will make the ``version."2.4"``
    section of multispec added to the result values.

* Render the template providing the result of operations above accessible
  under ``spec.*`` values.

Notes on Multispec Usage
^^^^^^^^^^^^^^^^^^^^^^^^

* There can be as many *groups* as you want, not just ``distroinfo`` and
  ``version``. This also means that you need to use ``--multispec-selector``
  multiple times on commandline.
* The ``--multispec-selector`` must be used for all groups except ``distroinfo``.
  A proper section to be used from ``distroinfo`` is implicitly specified
  by passing the ``--distro`` argument.
* Only a combination of specs belonging to *groups* can be used when using
  multispec. In the example above, you can't use fedora-22\_i686, since
  it's not listed in any ``distroinfo`` section.
* Combinations explicitly listed in ``matrix.exclude`` cannot be used.
* You can use ``dg --multispec <path> --multispec-combinations`` to print
  out all available combinations of distros and selectors based on the
  given multispec file.

Combining Specs and Multispecs
------------------------------

As shown in the example above, it is perfectly possible to combine specs
and multispec. In this case, the specs will be used as a base and values
from multispec will be added on top of that (overwriting values if their
names conflict).
