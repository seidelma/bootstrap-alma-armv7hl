Name:           libpsl
Version:        0.21.1
Release:        5%{?dist}
Summary:        C library for the Publix Suffix List
License:        MIT
URL:            https://rockdaboot.github.io/libpsl
Source0:        https://github.com/rockdaboot/libpsl/releases/download/%{version}/libpsl-%{version}.tar.gz
BuildRequires:  gcc
BuildRequires:  gettext-devel
BuildRequires:  glib2-devel
BuildRequires:  gtk-doc
BuildRequires:  libicu-devel
BuildRequires:  libidn2-devel
BuildRequires:  libunistring-devel
BuildRequires:  libxslt
BuildRequires:  make
BuildRequires:  publicsuffix-list
BuildRequires:  python3-devel
Requires:       publicsuffix-list-dafsa

%description
libpsl is a C library to handle the Public Suffix List. A "public suffix" is a
domain name under which Internet users can directly register own names.

Browsers and other web clients can use it to

- Avoid privacy-leaking "supercookies";
- Avoid privacy-leaking "super domain" certificates;
- Domain highlighting parts of the domain in a user interface;
- Sorting domain lists by site;

Libpsl...

- has built-in PSL data for fast access;
- allows to load PSL data from files;
- checks if a given domain is a "public suffix";
- provides immediate cookie domain verification;
- finds the longest public part of a given domain;
- finds the shortest private part of a given domain;
- works with international domains (UTF-8 and IDNA2008 Punycode);
- is thread-safe;
- handles IDNA2008 UTS#46;

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       publicsuffix-list

%description    devel
This package contains libraries and header files for
developing applications that use %{name}.

%package -n     psl
Summary:        Commandline utility to explore the Public Suffix List

%description -n psl
This package contains a commandline utility to explore the Public Suffix List,
for example it checks if domains are public suffixes, checks if cookie-domain
is acceptable for domains and so on.

%package -n     psl-make-dafsa
Summary:        Compiles the Public Suffix List into DAFSA form

%description -n psl-make-dafsa
This script produces C/C++ code or an architecture-independent binary object
which represents a Deterministic Acyclic Finite State Automaton (DAFSA)
from a plain text Public Suffix List.


%prep
%autosetup -p1
rm -frv list
ln -sv %{_datadir}/publicsuffix list
sed -i -e "1s|#!.*|#!%{__python3}|" src/psl-make-dafsa

%build
# Tarballs from github have 2 versions, one is raw files from repo, and
# the other one from CDN contains pre-generated autotools files.
# But makefile hack is not upstreamed yet so we continue reconfiguring these.
# [ -f configure ] || autoreconf -fiv
# autoreconf -fiv

# libicu does allow support for a newer IDN specification (IDN 2008) than
# libidn 1.x (IDN 2003). However, libpsl mostly relies on an internally
# compiled list, which is generated at buildtime and the testsuite thereof
# requires either libidn or libicu only at buildtime; the runtime
# requirement is only for loading external lists, which IIUC neither curl
# nor wget support. libidn2 supports IDN 2008 as well, and is *much* smaller
# than libicu.
#
# curl (as of 7.51.0-1.fc25) and wget (as of 1.19-1.fc26) now depend on libidn2.
# Therefore, we use libidn2 at runtime to help minimize core dependencies.
%configure --disable-silent-rules \
           --disable-static       \
           --enable-man           \
           --enable-builtin=libicu \
           --enable-runtime=libidn2 \
           --with-psl-distfile=%{_datadir}/publicsuffix/public_suffix_list.dafsa  \
           --with-psl-file=%{_datadir}/publicsuffix/effective_tld_names.dat       \
           --with-psl-testfile=%{_datadir}/publicsuffix/test_psl.txt

# avoid using rpath
sed -i libtool \
    -e 's|^\(runpath_var=\).*$|\1|' \
    -e 's|^\(hardcode_libdir_flag_spec=\).*$|\1|'

%make_build

%install
%make_install

# the script is noinst but the manpage is installed
install -m0755 src/psl-make-dafsa %{buildroot}%{_bindir}/

find %{buildroot} -name '*.la' -delete -print

%check
make check || cat tests/test-suite.log

%ldconfig_scriptlets

%files
%license COPYING
%{_libdir}/libpsl.so.5
%{_libdir}/libpsl.so.5.*

%files devel
%doc AUTHORS NEWS
%{_datadir}/gtk-doc/html/libpsl/
%{_includedir}/libpsl.h
%{_libdir}/libpsl.so
%{_libdir}/pkgconfig/libpsl.pc
#%{_mandir}/man3/libpsl.3*

%files -n psl
%doc AUTHORS NEWS
%license COPYING
%{_bindir}/psl
%{_mandir}/man1/psl.1*

%files -n psl-make-dafsa
%license COPYING
%{_bindir}/psl-make-dafsa
%{_mandir}/man1/psl-make-dafsa.1*

%changelog
* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 0.21.1-5
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.21.1-4
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.21.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.21.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 20 2020 Kamil Dudka <kdudka@redhat.com> - 0.21.1-1
- update to 0.21.1 (#1858489)

* Thu Jan 30 2020 Kamil Dudka <kdudka@redhat.com> - 0.21.0-4
- fix unnecessary build failure due to missing tree_index.sgml in gtk-doc output

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.21.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.21.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Apr 17 2019 Kamil Dudka <kdudka@redhat.com> - 0.21.0-1
- update to 0.21.0 (#1700444)

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.20.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Fri Jul 27 2018 Kamil Dudka <kdudka@redhat.com> - 0.20.2-5
- avoid using rpath in the psl executable (#1533448)

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.20.2-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 0.20.2-3
- Rebuilt for Python 3.7

* Tue May 22 2018 Yaakov Selkowitz <yselkowi@redhat.com> - 0.20.2-2
- Rebuilt for publicsuffix-list 20180514

* Tue May 01 2018 Yaakov Selkowitz <yselkowi@redhat.com> - 0.20.2-1
- Update to 0.20.2 (#1572887)

* Wed Feb 28 2018 Yaakov Selkowitz <yselkowi@redhat.com> - 0.20.1-1
- Update to 0.20.1 (#1548604)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.19.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.19.1-2
- Switch to %%ldconfig_scriptlets

* Tue Nov 14 2017 Yaakov Selkowitz <yselkowi@redhat.com> - 0.19.1-1
- new version (#1511463)

* Fri Aug 11 2017 Yaakov Selkowitz <yselkowi@redhat.com> - 0.18.0-1
- new version (#1473465)

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.17.0-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.17.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.17.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Jan 17 2017 Yaakov Selkowitz <yselkowi@redhat.com> - 0.17.0-1
- new version (#1413791)

* Thu Jan  5 2017 Yaakov Selkowitz <yselkowi@redhat.com> - 0.16.1-1
- new version (#1403620)

* Tue Nov 15 2016 Yaakov Selkowitz <yselkowi@redhat.com> - 0.15.0-1
- new version (#1394761)

* Fri Nov 04 2016 Yaakov Selkowitz <yselkowi@redhat.com> - 0.14.0-2
- Switch to libidn2 at runtime
- Rebuilt with publicsuffix-list-20161028

* Mon Aug 15 2016 Yaakov Selkowitz <yselkowi@redhat.com> - 0.14.0-1
- new version (#1361781)

* Thu Mar 31 2016 Yaakov Selkowitz <yselkowi@redhat.com> - 0.13.0-1
- new version (#1313825)
- Use libidn at runtime, libicu only at buildtime (#1305701)

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 22 2016 Christopher Meng <rpm@cicku.me> - 0.12.0-1
- Update to 0.12.0

* Wed Oct 28 2015 David Tardon <dtardon@redhat.com> - 0.7.0-7
- rebuild for ICU 56.1

* Tue Aug 04 2015 Christopher Meng <rpm@cicku.me> - 0.7.0-6
- Rebuild for publicsuffix-list-20150731

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Feb 28 2015 Christopher Meng <rpm@cicku.me> - 0.7.0-4
- Rebuild for publicsuffix-list-20150226

* Fri Feb 20 2015 Christopher Meng <rpm@cicku.me> - 0.7.0-3
- Rebuild for publicsuffix-list-20150217

* Sun Feb 15 2015 Christopher Meng <rpm@cicku.me> - 0.7.0-2
- Correct the dependency

* Mon Feb 02 2015 Christopher Meng <rpm@cicku.me> - 0.7.0-1
- Update to 0.7.0

* Mon Jan 26 2015 David Tardon <dtardon@redhat.com> - 0.6.2-2
- rebuild for ICU 54.1

* Thu Nov 20 2014 Christopher Meng <rpm@cicku.me> - 0.6.2-1
- Update to 0.6.2

* Tue Aug 26 2014 David Tardon <dtardon@redhat.com> - 0.5.1-3
- rebuild for ICU 53.1

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.5.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Aug 04 2014 Christopher Meng <rpm@cicku.me> - 0.5.1-1
- Update to 0.5.1
- Drop patch merged upstream

* Sat Aug 02 2014 Christopher Meng <rpm@cicku.me> - 0.5.0-3
- Add a patch from Jakub Čajka to complete the tests on non-x86 arch.

* Thu Jul 24 2014 Christopher Meng <rpm@cicku.me> - 0.5.0-2
- Drop useless test data
- Add missing gettext-devel
- psl is now separately packaged recommended by the upstream

* Fri Jul 04 2014 Christopher Meng <rpm@cicku.me> - 0.5.0-1
- Update to 0.5.0

* Tue Jul 01 2014 Christopher Meng <rpm@cicku.me> - 0.4.0-1
- Update to 0.4.0

* Tue Apr 08 2014 Christopher Meng <rpm@cicku.me> - 0.2-1
- Initial Package.
