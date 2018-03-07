%global postrel dev1
%global posttag %{?gitrev:.git%{gitrev}}
%global snapshot %{version}%{posttag}

%global pybin %{?fedora:%{__python3}}%{!?fedora:%{__python}}
%global pylib %{?fedora:%{python3_sitelib}}%{!?fedora:%{python_sitelib}}
%global pypkg %{?fedora:python3}%{!?fedora:python}

Name:       distgen
Summary:    Templating system/generator for distributions
Version:    1.0%{?postrel:.%{postrel}%{posttag}}
Release:    1%{?dist}
Group:      Applications/Communications
License:    GPLv2+
URL:        https://github.com/devexp-db/distgen
BuildArch:  noarch

%global both_requires %{pypkg}-jinja2, %{pypkg}-six, %{?fedora:%{pypkg}-}PyYAML

Requires:      %both_requires
BuildRequires: %{pypkg}-setuptools %{pypkg}-devel %{?fedora:%{pypkg}-}pytest %{pypkg}-flake8 %both_requires
BuildRequires: %{pypkg}-pytest-catchlog

%if 0%{?postrel:1}
Source0:       %{name}-%{version}.tar.gz
%else
Source0:       https://pypi.python.org/packages/85/67/c5eda06be88a44767ce75acda4f301f5cf210de335be2276f70e198a71d2/%{name}-%{version}.tar.gz
%endif

%description
Based on given template specification (configuration for template), template
file and preexisting distribution metadata generate output file.


%prep
%setup -q


%build
%{pybin} setup.py build


%install
%{pybin} setup.py install --root=%{buildroot}


%check
make PYTHON=%{pybin} check


%files
%license LICENSE
%doc AUTHORS NEWS
%doc docs/
%{_bindir}/dg
%{pylib}/distgen
%{pylib}/%{name}-*.egg-info
%{_datadir}/%{name}
%{_mandir}/man1/*


%changelog
* Wed Mar 07 2018 Pavel Raiskup <praiskup@redhat.com> - 1.0.dev1-1
- bump v1.0

* Tue Oct 17 2017 Slavek Kabrda <bkabrda@redhat.com> - 0.18.dev1-1
- update to 0.18.dev1

* Tue Sep 26 2017 Pavel Raiskup <praiskup@redhat.com> - 0.17.dev1-2
- package manual page and AUTHORS file

* Mon Sep 18 2017 Slavek Kabrda <bkabrda@redhat.com> - 0.17.dev1-1
- update to 0.17.dev1

* Wed Sep 13 2017 Slavek Kabrda <bkabrda@redhat.com> - 0.16.dev1-1
- update to 0.16.dev1

* Wed Sep 06 2017 Slavek Kabrda <bkabrda@redhat.com> - 0.15.dev1-1
- spec cleanup
- update to 0.15.dev1

* Fri Aug 18 2017 Pavel Raiskup <praiskup@redhat.com> - 0.13.dev1-1
- fix build on RHEL7

* Fri Aug 18 2017 Slavek Kabrda <bkabrda@redhat.com> - 0.12.dev1-1
- new release scheme

* Tue Aug 15 2017 Pavel Raiskup <praiskup@redhat.com> - 0.11~dev-1
- multiple --spec options

* Mon Aug 14 2017 Pavel Raiskup <praiskup@redhat.com> - 0.10~dev-1
- rebase

* Thu May 19 2016 Pavel Raiskup <praiskup@redhat.com> - 0.9~dev-1
- rebase

* Sat Feb 06 2016 Pavel Raiskup <praiskup@redhat.com> - 0.8~dev-1
- rebase

* Wed Jan 27 2016 Pavel Raiskup <praiskup@redhat.com> - 0.7~dev-1
- rebase

* Fri Nov 20 2015 Pavel Raiskup <praiskup@redhat.com> - 0.6~dev-1
- rebase

* Mon Oct 26 2015 Pavel Raiskup <praiskup@redhat.com> - 0.5~dev-1
- rebase

* Thu Sep 10 2015 Pavel Raiskup <praiskup@redhat.com> - 0.4~dev-1.git33125
- rebase

* Tue Sep 01 2015 Pavel Raiskup <praiskup@redhat.com> - 0.3~dev-1.git76d41
- rebase

* Wed May 20 2015 Pavel Raiskup <praiskup@redhat.com> - 0.2~dev-1.git32635
- new release, enable testsuite

* Mon May 11 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-4.gitf6fc9
- fixes to allow build of PostgreSQL Docker image correctly

* Mon May 11 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-3.git97392
- bump version (better example)

* Sun May 10 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-2.gitdefcd
- Add 'dg' option parser

* Sun May 10 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-1.git64bbe
- Initial packaging
