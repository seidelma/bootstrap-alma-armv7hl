Name:           python-systemd
Version:        234
Release:        18%{?dist}
Summary:        Python module wrapping systemd functionality

License:        LGPLv2+
URL:            https://github.com/systemd/python-systemd
Source0:        https://github.com/systemd/python-systemd/archive/v%{version}.tar.gz#/%{name}-%{version}.tar.gz

Patch0001:      0001-journal-avoid-warning-about-deprecated-constant.patch
Patch0002:      0002-reader-make-PY_SSIZE_T_CLEAN.patch
Patch0003:      0003-test-make-sure-NOTIFY_SOCKET-is-unset-in-test.patch

BuildRequires: make
BuildRequires:  gcc
BuildRequires:  systemd-devel
BuildRequires:  python3-devel
BuildRequires:  python3-sphinx
BuildRequires:  web-assets-devel
BuildRequires:  python3-pytest

%global _description %{expand:
Python module for native access to the systemd facilities.
Functionality includes sending of structured messages to the journal
and reading journal files, querying machine and boot identifiers and a
lists of message identifiers provided by systemd. Other functionality
provided by libsystemd is also wrapped.}

%description %_description

%package -n python3-systemd
Summary:        %{summary}

%{?python_provide:%python_provide python3-systemd}
Provides:       systemd-python3 = %{version}-%{release}
Provides:       systemd-python3%{?_isa} = %{version}-%{release}
Obsoletes:      systemd-python3 < 230
Recommends:	%{name}-doc

%description -n python3-systemd %_description

%package doc
Summary:        HTML documentation for %{name}
Requires:       js-jquery

%description doc
%{summary}.

%prep
%autosetup -p1
sed -i 's/py\.test/pytest/' Makefile

%build
make PYTHON=%{__python3} build
#make PYTHON=%{__python3} SPHINX_BUILD=sphinx-build-3 sphinx-html
#rm -r build/html/.buildinfo build/html/.doctrees

%install
%make_install PYTHON=%{__python3}
mkdir -p %{buildroot}%{_pkgdocdir}
#cp -rv build/html %{buildroot}%{_pkgdocdir}/
#ln -vsf %{_jsdir}/jquery/latest/jquery.min.js %{buildroot}%{_pkgdocdir}/html/_static/jquery.js
cp -p README.md NEWS %{buildroot}%{_pkgdocdir}/

%check
# if the socket is not there, skip doc tests
test -f /run/systemd/journal/stdout || \
     sed -i 's/--doctest[^ ]*//g' pytest.ini
make PYTHON=%{__python3} check

%files -n python3-systemd
%license LICENSE.txt
%doc %{_pkgdocdir}
%exclude %{_pkgdocdir}/html
%{python3_sitearch}/systemd/
%{python3_sitearch}/systemd_python*.egg-info

%files doc
#%doc %{_pkgdocdir}/html

%changelog
* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 234-18
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 234-17
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 234-16
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Thu Nov 12 2020 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-15
- Fix build with new mock (#1793022) and python 3.10 (#1891786)

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 234-14
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sat May 23 2020 Miro Hrončok <mhroncok@redhat.com> - 234-13
- Rebuilt for Python 3.9

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 234-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Sep 08 2019 Miro Hrončok <mhroncok@redhat.com> - 234-11
- Subpackage python2-systemd has been removed
  See https://fedoraproject.org/wiki/Changes/Mass_Python_2_Package_Removal

* Fri Aug 16 2019 Miro Hrončok <mhroncok@redhat.com> - 234-10
- Rebuilt for Python 3.8

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 234-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 234-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 234-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Jun 15 2018 Miro Hrončok <mhroncok@redhat.com> - 234-6
- Rebuilt for Python 3.7

* Fri Feb 09 2018 Fedora Release Engineering <releng@fedoraproject.org> - 234-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Nov  1 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-4
- Use separate license and documentation directories

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 234-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 234-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sun Mar 26 2017 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 234-1
- Update to latest version

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 232-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Dec 13 2016 Stratakis Charalampos <cstratak@redhat.com> - 232-2
- Rebuild for Python 3.6

* Thu Sep 22 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 232-1
- Update to latest version

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 231-6
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 231-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sun Jan 24 2016 Zbigniew Jędrzejewski-Szmek <zbyszek@bupkis> - 231-4
- Bugfixes for seek_monotonic and Python 2 compat

* Sun Nov 15 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 231-3
- Split out doc subpackage (#1242619)
- Do not allow installation of python-systemd in different versions

* Sat Nov 07 2015 Robert Kuska <rkuska@redhat.com> - 231-2
- Rebuilt for Python3.5 rebuild

* Tue Oct 27 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@laptop> - 231-1
- Update to latest version

* Mon Jul  6 2015 Zbigniew Jędrzejewski-Szmek <zbyszek@laptop> - 230-1
- Initial packaging
