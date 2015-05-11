%global gitrev 97392
%global posttag git%{gitrev}
%global snapshot %{version}-%{posttag}

Name:       distgen
Summary:    Templating system/generator for distributions
Version:    0.1~dev
Release:    3.%{posttag}%{?dist}
Group:      Applications/Communications
License:    GPLv2+
URL:        https://github.com/devexp-db/distgen
BuildArch:  noarch

Requires:       python2
BuildRequires:  python2-devel
Requires:       PyYAML

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


%clean


%files
%{_bindir}/dg
%{pylib}/distgen
%{pylib}/%{name}-*.egg-info
%{_datadir}/%{name}


%changelog
* Mon May 11 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-3.git97392
- bump version (better example)

* Sun May 10 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-2.gitdefcd
- Add 'dg' option parser

* Sun May 10 2015 Pavel Raiskup <praiskup@redhat.com> - 0.1~dev-1.git64bbe
- Initial packaging
