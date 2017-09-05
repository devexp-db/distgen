%global posttag %{?gitrev:.git%{gitrev}}
%global snapshot %{version}%{posttag}

Name:       distgen
Summary:    Templating system/generator for distributions
Version:    0.14%{posttag}
Release:    1%{?dist}
Group:      Applications/Communications
License:    GPLv2+
URL:        https://github.com/devexp-db/distgen
BuildArch:  noarch

%global both_requires python-jinja2, python-six, PyYAML

Requires:       python2
%if 0%{?rhel} == 7
BuildRequires: python-setuptools
%endif
BuildRequires:  python2-devel, %both_requires

Requires:       %both_requires

Source0: %{name}-%{version}.tar.gz

%description
Based on given template specification (configuration for template), template
file and preexisting distribution metadata generate output file.


%prep
%setup -q

%global pybin %{?!__python2:%{__python}}%{?__python2}
%global pylib %{?!python2_sitelib:%{python_sitelib}}%{?python2_sitelib}

%build
%{pybin} setup.py build


%install
%{pybin} setup.py install --root=%{buildroot}


%check
make check


%clean


%files
%{_bindir}/dg
%{pylib}/distgen
%{pylib}/%{name}-*.egg-info
%{_datadir}/%{name}


%changelog
* Tue Sep 05 2017 Pavel Raiskup <praiskup@redhat.com> - 0.14-1
- first stable release, thanks to Slavek

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
