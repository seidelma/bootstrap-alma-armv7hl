%global libmodulemd_version 2.3.0

%define __cmake_in_source_build 1

%global bash_completion %{_datadir}/bash-completion/completions/*

%if 0%{?rhel} && ( 0%{?rhel} <= 7 || 0%{?rhel} >= 9 )
%bcond_with drpm
%else
%bcond_without drpm
%endif

%if 0%{?rhel}
%bcond_with zchunk
%else
%bcond_without zchunk
%endif

%if 0%{?rhel} && 0%{?rhel} < 8
%bcond_with libmodulemd
%else
%bcond_without libmodulemd
%endif

Summary:        Creates a common metadata repository
Name:           createrepo_c
Version:        0.17.7
Release:        4%{?dist}
License:        GPLv2+
URL:            https://github.com/rpm-software-management/createrepo_c
Source0:        %{url}/archive/%{version}/%{name}-%{version}.tar.gz
Patch1:         0001-Default---keep-all-metadata-to-TRUE-and-add---discard-additional-metadata.patch
Patch2:         0002-Revert-added-API-for-parsing-main-metadata-together-RhBug2062299.patch

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  bzip2-devel
BuildRequires:  doxygen
BuildRequires:  file-devel
BuildRequires:  glib2-devel >= 2.22.0
BuildRequires:  libcurl-devel
BuildRequires:  libxml2-devel
BuildRequires:  openssl-devel
BuildRequires:  rpm-devel >= 4.8.0-28
BuildRequires:  sqlite-devel
BuildRequires:  xz
BuildRequires:  xz-devel
BuildRequires:  zlib-devel
%if %{with zchunk}
BuildRequires:  pkgconfig(zck) >= 0.9.11
BuildRequires:  zchunk
%endif
%if %{with libmodulemd}
BuildRequires:  pkgconfig(modulemd-2.0) >= %{libmodulemd_version}
BuildRequires:  libmodulemd
Requires:       libmodulemd%{?_isa} >= %{libmodulemd_version}
%endif
Requires:       %{name}-libs =  %{version}-%{release}
BuildRequires:  bash-completion
Requires: rpm >= 4.9.0
%if %{with drpm}
BuildRequires:  drpm-devel >= 0.4.0
%endif

%if 0%{?fedora} || 0%{?rhel} > 7
Obsoletes:      createrepo < 0.11.0
Provides:       createrepo = %{version}-%{release}
%endif

%description
C implementation of Createrepo.
A set of utilities (createrepo_c, mergerepo_c, modifyrepo_c)
for generating a common metadata repository from a directory of
rpm packages and maintaining it.

%package libs
Summary:    Library for repodata manipulation

%description libs
Libraries for applications using the createrepo_c library
for easy manipulation with a repodata.

%package devel
Summary:    Library for repodata manipulation
Requires:   %{name}-libs%{?_isa} = %{version}-%{release}

%description devel
This package contains the createrepo_c C library and header files.
These development files are for easy manipulation with a repodata.

%package -n python3-%{name}
Summary:        Python 3 bindings for the createrepo_c library
%{?python_provide:%python_provide python3-%{name}}
BuildRequires:  python3-devel
BuildRequires:  python3-sphinx
Requires:       %{name}-libs = %{version}-%{release}

%description -n python3-%{name}
Python 3 bindings for the createrepo_c library.

%prep
%autosetup -p1

mkdir build-py3

%build
# Build createrepo_c with Pyhon 3
pushd build-py3
  %cmake .. \
      -DWITH_ZCHUNK=%{?with_zchunk:ON}%{!?with_zchunk:OFF} \
      -DWITH_LIBMODULEMD=%{?with_libmodulemd:ON}%{!?with_libmodulemd:OFF} \
      -DENABLE_DRPM=%{?with_drpm:ON}%{!?with_drpm:OFF}
  make %{?_smp_mflags} RPM_OPT_FLAGS="%{optflags}"
  # Build C documentation
  make doc-c
popd

%check
# Run Python 3 tests
pushd build-py3
  # Compile C tests
  make tests

  # Run Python 3 tests
  make ARGS="-V" test
popd

%install
pushd build-py3
  # Install createrepo_c with Python 3
  make install DESTDIR=%{buildroot}
popd

%if 0%{?fedora} || 0%{?rhel} > 7
ln -sr %{buildroot}%{_bindir}/createrepo_c %{buildroot}%{_bindir}/createrepo
ln -sr %{buildroot}%{_bindir}/mergerepo_c %{buildroot}%{_bindir}/mergerepo
ln -sr %{buildroot}%{_bindir}/modifyrepo_c %{buildroot}%{_bindir}/modifyrepo
%endif

%if 0%{?rhel} && 0%{?rhel} <= 7
%post libs -p /sbin/ldconfig
%postun libs -p /sbin/ldconfig
%else
%ldconfig_scriptlets libs
%endif

%files
%doc README.md
%{_mandir}/man8/createrepo_c.8*
%{_mandir}/man8/mergerepo_c.8*
%{_mandir}/man8/modifyrepo_c.8*
%{_mandir}/man8/sqliterepo_c.8*
%{bash_completion}
%{_bindir}/createrepo_c
%{_bindir}/mergerepo_c
%{_bindir}/modifyrepo_c
%{_bindir}/sqliterepo_c

%if 0%{?fedora} || 0%{?rhel} > 7
%{_bindir}/createrepo
%{_bindir}/mergerepo
%{_bindir}/modifyrepo
%endif

%files libs
%license COPYING
%{_libdir}/lib%{name}.so.*

%files devel
%doc build-py3/doc/html
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/%{name}.pc
%{_includedir}/%{name}/

%files -n python3-%{name}
%{python3_sitearch}/%{name}/
%{python3_sitearch}/%{name}-%{version}-py%{python3_version}.egg-info

%changelog
* Tue Mar 15 2022 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.7-4
- Reference correct bug (RhBug:2062301)

* Fri Mar 11 2022 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.7-3
- Revert addition of new API for parsing main metadata together (RhBug:2062299)

* Wed Feb 16 2022 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.7-2
- Switch default of --keep-all-metadata to TRUE and add --discard-additional-metadata (RhBug:2055032)

* Mon Oct 25 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.7-1
- Update to 0.17.7
- Remove insecure hashes SHA-1 and MD5 from the default build (RhBug:1935486)
- Fix error when updating repo with removed modules metadata
- Exit with status code 1 when loading of repo's metadata fails
- Fix memory leaks (RhBug:1998426)
- Fix valgrind warnings caused by subprocess calls

* Mon Aug 16 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.2-5
- Fix issues detected by static analyzers

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 0.17.2-4
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jul 27 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.2-3
- Fix spec conditional to enable libmodulemd in RHEL >= 8 (RhBug:1816753) 

* Wed Jun 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.17.2-2
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Mon Apr 26 2021 Pavla Kratochvilova <pkratoch@redhat.com> - 0.17.2-1
- Update to 0.17.2
- Fix Python deprecation (PY_SSIZE_T_CLEAN) (RhBug:1891785)
- Revert back to old c API for destination file of cr_compress_file_with_stat and cr_compress_file to prevent a memory leak
- Never leave behind .repodata lock on exit (RhBug:1906831)
- Disable drpm for RHEL >= 9 (RhBug:1914828)
- Setting updated/issued_date to None doesn't produce garbage values (RhBug:1921715)
- Allow taking __repr__ (__str__) of closed xmlfile and sqlite (RhBug:1913465)

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 0.16.2-3
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.16.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Nov 23 2020 Nicola Sella <nsella@redhat.com> - 0.16.2-1
- Fix various memory leaks
- Add a new function to replace PyObject_ToStrOrNull()

* Tue Oct 06 2020 Nicola Sella <nsella@redhat.com> - 0.16.1
- Update to 0.16.1
- Add the section number to the manual pages
- Parse xml snippet in smaller parts (RhBug:1859689)
- Add module metadata support to createrepo_c (RhBug:1795936)

* Fri Aug 07 2020 Nicola Sella <nsella@redhat.com> - 0.15.11-4
- spec: Fix building with new cmake macros

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.15.11-3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.15.11-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jun 02 2020 Ales Matej <amatej@redhat.com> - 0.15.11-1
- Update to 0.15.11
- Switch updateinfo to explicitly include bool values (RhBug:1772466)
- Enhance error handling when locating repositories (RhBug:1762697)
- Make documentation for --update-md-path more specific
- Clean up temporary .repodata on sigint
- Add relogin_suggested to updatecollectionpackage (Rhbug:1779751)
- Support issued date in epoch format in Python API (RhBug:1779751)
- Allow parsing of xml repodata from string (RhBug: 1804308)
- Remove expat xml library in favor of libxml2
- Copy updateCollectionModule on assignment to prevent bogus data (RhBug:1821781)
- Add --arch-expand option to mergerepo_c

* Sun May 24 2020 Miro Hrončok <mhroncok@redhat.com> - 0.15.5-3
- Rebuilt for Python 3.9

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.15.5-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Wed Jan 08 2020 Pavel Raiskup <praiskup@redhat.com> - 0.15.5-1
- update to upstream 0.15.5 release, per
  https://github.com/rpm-software-management/createrepo_c/compare/0.15.4...0.15.5
- new option --recycle-pkglist for --update mode
- a bit more optimal --update caching

* Wed Dec 11 2019 Mohan Boddu <mboddu@bhujji.com> - 0.15.4-1
- Update to upstream 0.15.4 release

* Tue Sep 17 2019 Ales Matej <amatej@redhat.com> - 0.15.1-1
- Update to 0.15.1
- Allow pip to see installation of python3-createrepo_c
- Imporove documentation
- Switch off timestamping of documentation to avoid file conflics for createrepo_c-devel i686/x86_64 parallel installation
- Remove dependency on deltarpm in favour of drpm

* Sat Aug 17 2019 Miro Hrončok <mhroncok@redhat.com> - 0.14.2-3
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.14.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu Jun 27 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.14.2-1
- Update to 0.14.2
- Obsolete createrepo on all Fedoras again (RhBug:1702771)
- Fix issue with createrepo_c hanging at the end (RhBug:1714666)
- Don't include packages with forbidden control chars in repodata

* Mon Jun 10 22:13:18 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.14.1-4
- Rebuild for RPM 4.15

* Mon Jun 10 15:42:00 CET 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.14.1-3
- Rebuild for RPM 4.15

* Tue May 28 2019 Stephen Gallagher <sgallagh@redhat.com> - 0.14.1-2
- Depend on the appropriate minimum version of libmodulemd

* Fri May 24 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.14.1-1
- Update to 0.14.1
- Add --pkgorigins mode for Koji
- Correct pkg count in headers if there were invalid pkgs (RhBug:1596211)
- Prevent exiting with 0 if errors occur while finalizing repodata.

* Mon May 20 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.13.2-2
- Backport patch to fix crash when dumping updateinfo and module is ommited (RhBug:1707981)

* Tue May 07 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.13.2-1
- Update to 0.13.2
- Add support for reading and merging module metadata
- Add support for modular errata (RhBug:1656584)
- Update --keep-all-metadata to keep all additional metadata, not just updateinfo and groupfile (RhBug:1639287)
- mergerepo_c: Add support for --koji simple mode
- Fix generating corrupted sqlite files (RhBug: 1696808)
- modifyrepo_c: Prevent doubling of compression suffix (test.gz.gz)
- Do not obsolete createrepo on Fedora < 31

* Mon Mar 11 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.12.2-1
- Update to 0.12.2
- mergerepo_c: check if nevra is NULL and warn user about src.rpm naming
- Consistently produce valid URLs by prepending protocol. (RhBug:1632121)

* Wed Feb 13 2019 Pavla Kratochvilova <pkratoch@redhat.com> - 0.12.1-1
- Update to 0.12.1-1
- Include file timestamp in repomd.xml to allow reproducing exact metadata as produced in the past
- Enhance support of zchunk

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.12.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Dec 12 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.12.0-1
- Update to 0.12.0
- Support of zchunk

* Mon Nov 26 2018 Miro Hrončok <mhroncok@redhat.com> - 0.11.1-2
- Drop Python 2 subpackage on Fedora 30 (#1651182)

* Tue Jul 31 2018 Daniel Mach <dmach@redhat.com> - 0.11.1-1
- [spec] Fix ldconfig for rhel <= 7
- Fix "CR_DELTA_RPM_SUPPORT" redefined warnings
- Set to build against Python 3 by default
- Update README
- Add mergerepo_c --repo-prefix-search and --repo-prefix-replace.
- Fix missing packages in mergerepo_c in case multiple VR exists for single pkg in repo.

* Wed Jul 25 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.11.0-4
- Backport patch for multiple packages with same name for mergerepo_c

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.11.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 0.11.0-2
- Rebuilt for Python 3.7

* Wed Jun 27 2018 Marek Blaha <mblaha@redhat.com> - 0.11.0-1
- Update to 0.11.0

* Mon Jun 18 2018 Miro Hrončok <mhroncok@redhat.com> - 0.10.0-21
- Rebuilt for Python 3.7

* Wed May 16 2018 Jaroslav Mracek <jmracek@redhat.com> - 0.10.0-20
- Obsolete and provide createrepo

* Fri Mar 16 2018 Miro Hrončok <mhroncok@redhat.com> - 0.10.0-19
- Conditionalize the Python 2 subpackage
- Don't build the Python 2 subpackage on EL > 7

* Wed Feb 07 2018 Iryna Shcherbina <ishcherb@redhat.com> - 0.10.0-18
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.0-17
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Feb 03 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 0.10.0-16
- Switch to %%ldconfig_scriptlets

* Fri Dec 22 2017 Patrick Uiterwijk <puiterwijk@redhat.com> - 0.10.0-15
- Backport PR#64 and #66

* Fri Aug 11 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.10.0-14
- Rebuilt after RPM update (№ 3)

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.10.0-13
- Rebuilt for RPM soname bump

* Thu Aug 10 2017 Igor Gnatenko <ignatenko@redhat.com> - 0.10.0-12
- Rebuilt for RPM soname bump

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.0-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Mon Feb 13 2017 Pavel Raiskup <praiskup@redhat.com> - 0.10.0-9
- backport patches for double-free in --ignore-lock (rhbz#1355720)

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.0-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Dec 13 2016 Stratakis Charalampos <cstratak@redhat.com> - 0.10.0-7
- Rebuild for Python 3.6

* Tue Jul 19 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.10.0-6
- https://fedoraproject.org/wiki/Changes/Automatic_Provides_for_Python_RPM_Packages

* Tue Apr 12 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.10.0-5
- Make drpm builds conditional

* Sun Apr 10 2016 Igor Gnatenko <ignatenko@redhat.com> - 0.10.0-4
- Don't own python3_sitearch dir in python3 subpkg
- Use %%license macro
- Follow modern packaging guidelines
- Cleanups in spec file
- Follow packaging guidelines about SourceURL
- Fix license

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.10.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jan 8 2016 Orion Poplawski <orion@cora.nwra.com> - 0.10.0-2
- Remove comments causing trouble with post/postun scriptlets

* Tue Jan   5 2016 Tomas Mlcoch <tmlcoch at redhat.com> - 0.10.0-1
- Python 3 support (made by Ralph Bean)
- Modify gen_rst.py to indicate --sqliterepo is an option too (Neal Gompa)
- Do not compress manpages at generation time (Neal Gompa)

* Tue Oct  20 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.9.1-1
- Fix double free during parsing broken XML metadata (Issue #33)
- Tests: Add acceptance test for --general-compress-type option
- Fix 'CR_CW_UNKNOWN_COMPRESSION cannot be used' error
- Refactoring: Fix compiler warnings
- Add --general-compress-type option (RhBug 1253850)
- Enable drpm support when drpm library is detected on system (RhBug: 1261031) (Issue #37)
- fix traceback on non-complete datetime information (Jarek Polok)
- parsehdr: Skip broken dependency with bad (non-numerical) epoch and print warning about that
  (https://lists.fedoraproject.org/pipermail/devel/2015-August/213882.html)
- misc: cr_str_to_evr(): Return NULL instead of "0" for bad (non-numerical) epoch
- updateinfo: Fix a typo in the package release attribute (Luke Macken)
- CMake: Don't require CXX compiler
- Tests for different checksum type for RPMs and repodata files (#31)
- Support different checksum type for RPMs and repodata files (#31)

* Tue Jul   7 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.9.0-2
- Add drpm as a BuildRequire

* Thu May  28 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.9.0-1
- mergerepo_c: Prepend protocol (file://) for URLs in pkgorigins (if --koji is used)
- Update bash completion
- doc: Update manpages
- mergerepo: Fix NVR merging method
- mergerepo: Fix behavior of --all param
- createrepo: Add --cut-dirs and --location-prefix options
- misc: Add cr_cut_dirs()
- mergerepo: Use better version comparison algorithm
- utils: Port cr_cmp_version_str() to rpm's algorithm (rpmvercmp)
- misc: Rename elements in cr_Version structure
- mergerepo: Fix version-release comparison for packages when --all is used
- mergerepo: Show warnings if some groupfile cannot be automatically used
- mergerepo: Exit with error code when a groupfile cannot be copied

* Fri May  15 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.8.3-1
- mergerepo: Do not prepend file:// if protocol is already specified

* Thu May  14 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.8.2-1
- doc: Add man pages for sqliterepo and update manpages for other tools
- mergerepo: Work only with noarch packages if --koji is used and
  no archlist is specified
- mergerepo: Use file:// protocol in local baseurl
- mergerepo: Do not include baseurl for first repo if --koji is specified (RhBug: 1220082)
- mergerepo_c: Support multilib arch for --koji repos
- mergerepo_c: Refactoring
- Print debug message with version in each tool when --verbose is used
- modifyrepo: Don't override file with itself (RhBug: 1215229)

* Wed May   6 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.8.1-1
- Fix bash completion for RHEL 6

* Tue May   5 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.8.0-1
- New tool Sqliterepo_c - It generates sqlite databases into repos
  where the sqlite is missing.
- Internal refactoring and code cleanup

* Fri Feb  20 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.7-1
- Proper directory for temporary files when --local-sqlite is used (Issue #12)
- Bring bash completion install dir and filenames up to date with current bash-completion

* Thu Jan   8 2015 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.6-1
- Python: Add __contains__ method to Repomd() class

* Sun Dec  28 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.5-1
- Python repomd: Support for iteration and indexing by type - e.g. record = repomd['primary']
- Show warning if an XML parser probably parsed a bad type of medata (New XML parser warning type CR_XML_WARNING_BADMDTYPE)
- drpm library: Explicitly try to locate libdrpm.so.0
- deltarpms: Don't show options for delta rpms if support is not available

* Tue Nov  11 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.4-1
- createrepo_c, mergerepo_c: Follow redirs by default while downloading remote repos
- mergerepo_c: Fix segfault when a package without sourcerpm is part of metadata and --koji option is used

* Mon Nov  10 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.3-1
- xml_parser: Add file path into error messages
- Refactor: Replace g_error() with g_critical() (RhBug: 1162102)

* Thu Nov  06 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.2-1
- createrepo_c: New option --local-sqlite

* Fri Oct  31 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.1-1
- Mergerepo: Fix mergerepo
- Mergerepo: Add some debugging of metadata read.

* Mon Oct  20 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.7.0-1
- deltarpms: Update module to work with current version of drpm
- mergerepo_c: Add --omit-baseurl option
- craterepo_c: Gen empty repo if empty pkglist is used
- Docs: Output python docs to separate directory
- Several small fixes

* Tue Aug  12 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.6.1-1
- updateinfo: Use Python datetime objects in python bindings

* Tue Aug   5 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.6.0-1
- Support for updateinfo.xml manipulation (including Python bindings)

* Fri Jul  18 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.5.0-1
- Experimental delta rpm (DRPM) support (Disabled in Fedora build).

* Thu Jun  26 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.4.1-1
- Initialize threads correctly on old versions of GLib2 (RhBug: 1108787)
- Do not print log domain (get rid off C_CREATEREPOLIB prefix in log messages)
- Implements support for --cachedir
- New option --retain-old-md-by-age
- Few small API changes

* Tue May   6 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.4.0-1
- Change default behavior of repodata files handling. (RhBug: 1094539)
  See: https://github.com/Tojaj/createrepo_c/wiki/New-File-Handling
  By default, createrepo leaves old groupfiles (comps files)
  in the repodata/ directory during update.
  Createrepo_c did the same thing but the version 0.4.0 changes this behaviour.

* Thu Apr  10 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.3.1-2
- Support for weak and rich dependecies

* Mon Mar  10 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.3.0-1
- Relevant only for developers using createrepo_c library: New approach for
  metadata loading in case of internal high-level parser functions (see commit
  messages for more information: d6ed327595, 0b0e75203e, ad1e8450f5)
- Support for changelog limit value == -1 (include all changelogs)
- Update debug compilation flags
- Update man pages (Add synompsis with usage)
- Update usage examples in help

* Thu Feb  20 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.2.2-1
- Temporary remove deltarepo subpackages
- cmake: Do not install deltarepo stuff yet
- helper: Removed cr_remove_metadata() and cr_get_list_of_md_locations()
- Add module helpers
- Sanitize strings before writting them to XML or sqlitedb (ISSUE #3)

* Mon Jan  27 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.2.1-3
- New expert option: --ignore-lock

* Mon Jan  20 2014 Tomas Mlcoch <tmlcoch at redhat.com> - 0.2.1-2
- More effort to avoid residual .repodata/ directory on error
- Add deltarepo and python-deltarepo subpackages
- Add modifyrepo_c
- Add documentation for python bindings
- Refactored code & a lot of little bug fixes

* Wed Aug  14 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.2.1-1
- checksum: Set SHA to be the same as SHA1 (For compatibility with original
  Createrepo)

* Mon Aug   5 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.2.0-1
- Speedup (More parallelization)
- Changed C API
- Add python bindings
- A lot of bugfixes
- Add new make targets: tests (make tests - builds c tests) and test
  (make test - runs c and python test suits).
- Changed interface of most of C modules - Better error reporting
  (Add GError ** param).
- Experimental Python bindings (Beware: The interface is not final yet!).
- package: Add cr_package_copy method.
- sqlite: Do not recreate tables and triggers while opening existing db.
- mergerepo_c: Implicitly use --all with --koji.
- Man page update.

* Thu Apr  11 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.17-3
- mergerepo_c: Add --simple-md-filenames and --unique-md-filenames
options. (RhBug: 950994)
- mergerepo_c: Always include noarch while mimic koji
mergerepos. (RhBug: 950991)
- Rename cr_package_parser_shutdown to cr_package_parser_cleanup()
- cr_db_info_update is now safe from sqlinjection.

* Mon Mar  25 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.17-1
- Fix double free() when old metadata parsing failed. (related to RhBug: 920795)
- Convert all strings to UTF-8 while dumping XML. (related RhBug: 920795)

* Mon Mar  11 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.16-2
- Remove creation of own empty rpm keyring for a transaction set.
This is not necessary since rpm-4.8.0-28 (rpm commit
cad147070e5513312d851f44998012e8f0cdf1e3). Moreover, own rpm keyring
causes a race condition in threads (causing double free()) which use
rpmReadPackageFile() called from cr_package_from_rpm().

* Thu Mar  07 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.16-1
- Fix usage of rpm keyring (RhBug:918645)
- More generic interface of repomd module
- Code refactoring
- Add some usage examples into the doxygen documentation and .h files
- Rename version constants in version.h
- New function cr_package_nevra (returns package nevra string)

* Mon Feb  11 2013 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.15-1
- Fix bug in final move from .repodata/ -> repodata/
- Fix warnings from RPM library. RPM library is thread-unsafe. This
includes also reading headers. Use of empty keyring for rpm transaction
should work around the problem.

* Tue Nov  27 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.14-1
- Fix filelists database generation (use '.' instead of '' for current dir)

* Tue Nov  20 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.13-1
- Fix race-condition during task buffering in createrepo_c

* Tue Nov  20 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.12-2
- Fix removing old repomd.xml while --update

* Thu Nov  15 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.12-1
- Fix bug in sqlite filelists database
- Fix memory leak

* Fri Nov  09 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.11-1
- Deterministic output! Packages in output repodata are now sorted
by ASCII value
- Support for Koji mergerepos behaviour in mergerepo_c
(new --koji, --groupfile and --blocked params)
- Better atomicity while finall move .repodata/ -> repodata/
- Repomd module supports pkgorigins record
- Some new functions in misc module
- Small changes in library interface

* Wed Oct  03 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.10-1
- Another memory usage optimalization

* Mon Sep  03 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.9-1
- Some changes in library interface
- Memory usage optimalization
- Fix a segfault and a race condition
- New cmd options: --read-pkgs-list and --retain-old-md param
- Few other bugfixes

* Wed Aug  15 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.8-1
- New interface of repomd module
- New cmd options: --repo --revision --distro --content --basedir
- New createrepo_c specific cmd option --keep-all-metadata
- Few bugfixes

* Thu Jul  26 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.7-1
- SQLite support
- Bash completion
- createrepo_c support for --compress-type param
- Improved logging
- Subpackages -devel and -libsi
- Relicensed to GPLv2
- Doxygen documentation in devel package
- README update

* Mon Jun  11 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.5-1
- Support for .xz compression
- Unversioned .so excluded from installation

* Mon Jun   4 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.4-1
- New mergerepo params: --all, --noarch-repo and --method
- Fix segfault when more than one --excludes param used

* Mon May  28 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.3-1
- Set RelWithDebInfo as default cmake build type

* Wed May  23 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.2-1
- Add version.h header file

* Wed May  23 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.1-1
- Add license

* Wed May  9 2012 Tomas Mlcoch <tmlcoch at redhat.com> - 0.1.0-1
- First public release
