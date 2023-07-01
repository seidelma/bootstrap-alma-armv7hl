
# run internal testsuite?
# fakechroot is severely broken beyond fedora 33, disable...
%if 0%{?fedora} > 33 || 0%{?rhel} > 8
%bcond_with check
%else
%bcond_without check
%endif

# build against xz?
%bcond_without xz
# build with plugins?
%bcond_without plugins
# build with libarchive? (needed for rpm2archive)
%bcond_without libarchive
# build with libimaevm.so
%bcond_without libimaevm
# build with zstd support?
%bcond_without zstd
# build with ndb backend?
%bcond_without ndb
# build with sqlite support?
%bcond_without sqlite
# build with bdb support?
%bcond_with bdb
# build with internal Berkeley DB?
%bcond_with int_bdb
# build with bdb_ro support?
%bcond_without bdb_ro

%define rpmhome /usr/lib/rpm

%global rpmver 4.16.1.3
#global snapver rc1
%global rel 19
%global sover 9

%global srcver %{rpmver}%{?snapver:-%{snapver}}
%global srcdir %{?snapver:testing}%{!?snapver:rpm-%(echo %{rpmver} | cut -d'.' -f1-2).x}

%if %{with bdb}
%define bdbver 5.3.15

# Build-dependency on systemd for the sake of one macro would be a bit much...
%{!?_tmpfilesdir:%global _tmpfilesdir /usr/lib/tmpfiles.d}
%endif

Summary: The RPM package management system
Name: rpm
Version: %{rpmver}
Release: %{?snapver:0.%{snapver}.}%{rel}%{?dist}
Url: http://www.rpm.org/
Source0: http://ftp.rpm.org/releases/%{srcdir}/rpm-%{srcver}.tar.bz2
%if %{with bdb} && %{with int_bdb}
Source1: db-%{bdbver}.tar.gz
%endif

Source10: rpmdb-rebuild.service

# Disable autoconf config.site processing (#962837)
Patch1: rpm-4.15.x-siteconfig.patch
# In current Fedora, man-pages pkg owns all the localized man directories
Patch3: rpm-4.9.90-no-man-dirs.patch
# Temporary band-aid for rpm2cpio whining on payload size mismatch (#1142949)
Patch5: rpm-4.12.0-rpm2cpio-hack.patch
# https://github.com/rpm-software-management/rpm/pull/473
Patch6: 0001-find-debuginfo.sh-decompress-DWARF-compressed-ELF-se.patch
Patch7: 0001-Issue-deprecation-warning-when-creating-BDB-database.patch

# Patches already upstream:
Patch100: rpm-4.16.1.3-imp-covscan-fixes.patch
Patch101: rpm-4.16.1.3-rpmsign-support-EdDSA-sig.patch
Patch102: rpm-4.16.1.3-add-fapolicyd-plugin.patch
Patch103: rpm-4.16.1.3-unblock-signals-in-forked-scriptlets.patch
Patch104: rpm-4.16.1.3-support-bdb-hash-v8.patch
Patch105: rpm-4.16.1.3-ELF-files-strip-when-debuginfo-disabled.patch
Patch106: rpm-4.16.1.3-unbreak-checking-of-installed-rich-deps.patch
Patch107: rpm-4.16.1.3-fix-IMA-sig-len-assumed-const.patch
Patch108: rpm-4.16.1.3-validate-and-require-subkey-binding-sigs.patch
Patch109: rpm-4.16.1.3-bump-rpmdb-cookie-hash-to-SHA256-for-FIPS.patch
Patch110: rpm-4.16.1.3-add-path-query-option.patch
Patch111: rpm-4.16.1.3-skip-recorded-symlinks-in-setperms.patch
Patch112: rpm-4.16.1.3-fix-regression-reading-rpm-v3-pkgs.patch
Patch113: rpm-4.16.1.3-fix-spurious-transfiletriggerpostun-execution.patch
Patch114: rpm-4.16.1.3-Make-rpm2cpio.sh-more-robust.patch
Patch115: rpm-4.16.1.3-fapolicyd-make-write-nonblocking.patch

# These are not yet upstream
Patch906: rpm-4.7.1-geode-i686.patch
# Probably to be upstreamed in slightly different form
Patch907: rpm-4.15.x-ldflags.patch
Patch908: 0001-Give-warning-on-not-supported-hash-for-RSA-keys.patch

# Not yet (all) upstream, debugedit DWARF5
# https://code.wildebeest.org/git/user/mjw/rpm/log/?h=gcc-dwarf5-4.16.1.2
Patch911: 0001-NFC-debugedit-Protect-macro-arguments-by-parentheses.patch
Patch912: 0002-NFC-debugedit-Move-code-from-edit_dwarf2-to-edit_inf.patch
Patch913: 0003-debugedit-Fix-missing-relocation-of-.debug_types-sec.patch
Patch914: 0004-NFC-debugedit-Move-code-to-separate-functions.patch
Patch915: 0005-debugedit-Implement-DWARF-5-unit-header-and-new-form.patch
Patch916: 0006-debugedit-Handle-DWARF-5-debug_line-and-debug_line_s.patch

# Downstream-only patches
Patch1000: rpm-4.16.1.3-hashtab-use-after-free-fix.patch
Patch1001: rpm-4.16.1.3-find_debuginfo_vendor_opts.patch

# Partially GPL/LGPL dual-licensed and some bits with BSD
# SourceLicense: (GPLv2+ and LGPLv2+ with exceptions) and BSD
License: GPLv2+

Requires: coreutils
Requires: popt%{_isa} >= 1.10.2.1
Requires: curl
Obsoletes: python2-rpm < %{version}-%{release}

%if %{with bdb} && %{without int_bdb}
BuildRequires: libdb-devel
%endif

%if %{with check}
BuildRequires: fakechroot gnupg2
%endif

# XXX generally assumed to be installed but make it explicit as rpm
# is a bit special...
BuildRequires: redhat-rpm-config >= 94
BuildRequires: systemd-rpm-macros
BuildRequires: gcc make
BuildRequires: gawk
BuildRequires: elfutils-devel >= 0.112
BuildRequires: elfutils-libelf-devel
BuildRequires: readline-devel zlib-devel
BuildRequires: openssl-devel
# The popt version here just documents an older known-good version
BuildRequires: popt-devel >= 1.10.2
BuildRequires: file-devel
BuildRequires: gettext-devel
BuildRequires: ncurses-devel
BuildRequires: bzip2-devel >= 0.9.0c-2
BuildRequires: lua-devel >= 5.1
BuildRequires: libcap-devel
BuildRequires: libacl-devel
%if %{with xz}
BuildRequires: xz-devel >= 4.999.8
%endif
%if %{with libarchive}
BuildRequires: libarchive-devel
%endif
%if %{with zstd}
BuildRequires: libzstd-devel
%endif
%if %{with sqlite}
BuildRequires: sqlite-devel
%endif
# Couple of patches change makefiles so, require for now...
BuildRequires: automake libtool

%if %{with plugins}
BuildRequires: libselinux-devel
BuildRequires: dbus-devel
BuildRequires: audit-libs-devel
%endif

%if %{with libimaevm}
BuildRequires: ima-evm-utils-devel >= 1.0
%endif

%description
The RPM Package Manager (RPM) is a powerful command line driven
package management system capable of installing, uninstalling,
verifying, querying, and updating software packages. Each software
package consists of an archive of files along with information about
the package like its version, a description, etc.

%package libs
Summary:  Libraries for manipulating RPM packages
License: GPLv2+ and LGPLv2+ with exceptions
Requires: %{name} = %{version}-%{release}

%description libs
This package contains the RPM shared libraries.

%package build-libs
Summary:  Libraries for building RPM packages
License: GPLv2+ and LGPLv2+ with exceptions
Requires: rpm-libs%{_isa} = %{version}-%{release}

%description build-libs
This package contains the RPM shared libraries for building packages.

%package sign-libs
Summary:  Libraries for signing RPM packages
License: GPLv2+ and LGPLv2+ with exceptions
Requires: rpm-libs%{_isa} = %{version}-%{release}
Requires: %{_bindir}/gpg2

%description sign-libs
This package contains the RPM shared libraries for signing packages.

%package devel
Summary:  Development files for manipulating RPM packages
License: GPLv2+ and LGPLv2+ with exceptions
Requires: %{name} = %{version}-%{release}
Requires: %{name}-libs%{_isa} = %{version}-%{release}
Requires: %{name}-build-libs%{_isa} = %{version}-%{release}
Requires: %{name}-sign-libs%{_isa} = %{version}-%{release}
Requires: popt-devel%{_isa}

%description devel
This package contains the RPM C library and header files. These
development files will simplify the process of writing programs that
manipulate RPM packages and databases. These files are intended to
simplify the process of creating graphical package managers or any
other tools that need an intimate knowledge of RPM packages in order
to function.

This package should be installed if you want to develop programs that
will manipulate RPM packages and databases.

%package build
Summary: Scripts and executable programs used to build packages
Requires: rpm = %{version}-%{release}
Requires: elfutils >= 0.128 binutils
Requires: findutils sed grep gawk diffutils file patch >= 2.5
Requires: tar unzip gzip bzip2 cpio xz
%if %{with zstd}
Requires: zstd
%endif
Requires: pkgconfig >= 1:0.24
Requires: /usr/bin/gdb-add-index
# https://fedoraproject.org/wiki/Changes/Minimal_GDB_in_buildroot
Suggests: gdb-minimal
# Technically rpmbuild doesn't require any external configuration, but
# creating distro-compatible packages does. To make the common case
# "just work" while allowing for alternatives, depend on a virtual
# provide, typically coming from redhat-rpm-config.
Requires: system-rpm-config

%description build
The rpm-build package contains the scripts and executable programs
that are used to build packages using the RPM Package Manager.

%package sign
Summary: Package signing support
Requires: rpm-sign-libs%{_isa} = %{version}-%{release}

%description sign
This package contains support for digitally signing RPM packages.

%package -n python3-%{name}
Summary: Python 3 bindings for apps which will manipulate RPM packages
BuildRequires: python3-devel
%{?python_provide:%python_provide python3-%{name}}
Requires: %{name}-libs%{?_isa} = %{version}-%{release}
Provides: %{name}-python3 = %{version}-%{release}
Obsoletes: %{name}-python3 < %{version}-%{release}
Obsoletes: platform-python-%{name} < %{version}-%{release}

%description -n python3-%{name}
The python3-rpm package contains a module that permits applications
written in the Python programming language to use the interface
supplied by RPM Package Manager libraries.

This package should be installed if you want to develop Python 3
programs that will manipulate RPM packages and databases.

%package apidocs
Summary: API documentation for RPM libraries
BuildArch: noarch

%description apidocs
This package contains API documentation for developing applications
that will manipulate RPM packages and databases.

%package cron
Summary: Create daily logs of installed packages.
BuildArch: noarch
Requires: crontabs logrotate rpm = %{version}-%{release}

%description cron
This package contains a cron job which creates daily logs of installed
packages on a system.

%if %{with plugins}
%package plugin-selinux
Summary: Rpm plugin for SELinux functionality
Requires: rpm-libs%{_isa} = %{version}-%{release}
Requires: selinux-policy-base

%description plugin-selinux
%{summary}.

%package plugin-syslog
Summary: Rpm plugin for syslog functionality
Requires: rpm-libs%{_isa} = %{version}-%{release}

%description plugin-syslog
%{summary}.

%package plugin-systemd-inhibit
Summary: Rpm plugin for systemd inhibit functionality
Requires: rpm-libs%{_isa} = %{version}-%{release}

%description plugin-systemd-inhibit
This plugin blocks systemd from entering idle, sleep or shutdown while an rpm
transaction is running using the systemd-inhibit mechanism.

%package plugin-ima
Summary: Rpm plugin ima file signatures
Requires: rpm-libs%{_isa} = %{version}-%{release}

%description plugin-ima
%{summary}.

%package plugin-fapolicyd
Summary: Rpm plugin for fapolicyd functionality
Requires: rpm-libs%{_isa} = %{version}-%{release}
Provides: fapolicyd-plugin
Obsoletes: fapolicyd-dnf-plugin

%description plugin-fapolicyd
%{summary}.

%package plugin-prioreset
Summary: Rpm plugin for resetting scriptlet priorities for SysV init
Requires: rpm-libs%{_isa} = %{version}-%{release}

%description plugin-prioreset
%{summary}.

Useful on legacy SysV init systems if you run rpm transactions with
nice/ionice priorities. Should not be used on systemd systems.

%package plugin-audit
Summary: Rpm plugin for logging audit events on package operations
Requires: rpm-libs%{_isa} = %{version}-%{release}

%description plugin-audit
%{summary}.

# with plugins
%endif

%prep
%autosetup -n rpm-%{srcver} %{?with_int_bdb:-a 1} -p1

%if %{with bdb} && %{with int_bdb}
ln -s db-%{bdbver} db
%endif

# switch to sqlite db by default, including during build-time tests
%if %{with sqlite}
sed -i -e "/_db_backend/ s/ bdb/ sqlite/g" macros.in
%endif

%build
%set_build_flags

autoreconf -i -f

# Hardening hack taken from macro %%configure defined in redhat-rpm-config
for i in $(find . -name ltmain.sh) ; do
     %{__sed} -i.backup -e 's~compiler_flags=$~compiler_flags="%{_hardened_ldflags}"~' $i
done;

# Using configure macro has some unwanted side-effects on rpm platform
# setup, use the old-fashioned way for now only defining minimal paths.
./configure \
    --prefix=%{_usr} \
    --sysconfdir=%{_sysconfdir} \
    --localstatedir=%{_var} \
    --sharedstatedir=%{_var}/lib \
    --libdir=%{_libdir} \
    --build=%{_target_platform} \
    --host=%{_target_platform} \
    --with-vendor=redhat \
    --enable-bdb=%{?with_bdb:yes}%{!?with_bdb:no} \
    %{!?with_int_bdb: --with-external-db} \
    %{!?with_plugins: --disable-plugins} \
    --with-lua \
    --with-selinux \
    --with-cap \
    --with-acl \
    %{?with_ndb: --enable-ndb} \
    %{!?with_libarchive: --without-archive} \
    %{?with_libimaevm: --with-imaevm} \
    %{?with_zstd: --enable-zstd} \
    %{?with_sqlite: --enable-sqlite} \
    %{?with_bdb_ro: --enable-bdb-ro} \
    --with-fapolicyd \
    --enable-python \
    --with-crypto=openssl

%make_build

pushd python
%py3_build
popd

%install
%make_install

# We need to build with --enable-python for the self-test suite, but we
# actually package the bindings built with setup.py (#531543#c26)
pushd python
%py3_install
popd

mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -m 644 %{SOURCE10} $RPM_BUILD_ROOT/%{_unitdir}

# Save list of packages through cron
mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.daily
install -m 755 scripts/rpm.daily ${RPM_BUILD_ROOT}%{_sysconfdir}/cron.daily/rpm

mkdir -p ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d
install -m 644 scripts/rpm.log ${RPM_BUILD_ROOT}%{_sysconfdir}/logrotate.d/rpm

%if %{with bdb}
mkdir -p ${RPM_BUILD_ROOT}%{_tmpfilesdir}
echo "r /var/lib/rpm/__db.*" > ${RPM_BUILD_ROOT}%{_tmpfilesdir}/rpm.conf
%endif

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/rpm
mkdir -p $RPM_BUILD_ROOT%{rpmhome}/macros.d
mkdir -p $RPM_BUILD_ROOT/var/lib/rpm

# init an empty database for %ghost'ing for all supported backends
for be in %{?with_ndb:ndb} %{?with_sqlite:sqlite} %{?with_bdb:bdb}; do
    ./rpmdb --define "_db_backend ${be}" --dbpath=${PWD}/${be} --initdb
    cp -va ${be}/. $RPM_BUILD_ROOT/var/lib/rpm/
done

%find_lang rpm

find $RPM_BUILD_ROOT -name "*.la"|xargs rm -f

# These live in perl-generators and python-rpm-generators now
rm -f $RPM_BUILD_ROOT/%{rpmhome}/{perldeps.pl,perl.*,pythond*}
rm -f $RPM_BUILD_ROOT/%{_fileattrsdir}/{perl*,python*}
rm -rf $RPM_BUILD_ROOT/var/tmp

%if %{with check}
%check
make check TESTSUITEFLAGS=-j%{_smp_build_ncpus} || (cat tests/rpmtests.log; exit 1)
# rpm >= 4.16.0 testsuite leaves a read-only tree behind, clean it up
make clean
%endif

# Handle rpmdb rebuild service on erasure of old to avoid ordering issues
# https://pagure.io/fesco/issue/2382
%triggerun -- rpm < 4.15.90-0.git14971.10
if [ -x /usr/bin/systemctl ]; then
    systemctl --no-reload preset rpmdb-rebuild ||:
fi

%posttrans
if [ -f /var/lib/rpm/Packages ]; then
    touch /var/lib/rpm/.rebuilddb
fi

%files -f rpm.lang
%license COPYING
%doc CREDITS doc/manual/[a-z]*

%if %{with bdb}
%{_tmpfilesdir}/rpm.conf
%endif

%{_unitdir}/rpmdb-rebuild.service

%dir %{_sysconfdir}/rpm

%attr(0755, root, root) %dir /var/lib/rpm
%attr(0644, root, root) %ghost %config(missingok,noreplace) /var/lib/rpm/*
%attr(0644, root, root) %ghost /var/lib/rpm/.*.lock

%{_bindir}/rpm
%if %{with libarchive}
%{_bindir}/rpm2archive
%endif
%{_bindir}/rpm2cpio
%{_bindir}/rpmdb
%{_bindir}/rpmkeys
%{_bindir}/rpmquery
%{_bindir}/rpmverify

%{_mandir}/man8/rpm.8*
%{_mandir}/man8/rpmdb.8*
%{_mandir}/man8/rpmkeys.8*
%if %{with libarchive}
%{_mandir}/man8/rpm2archive.8*
%endif
%{_mandir}/man8/rpm2cpio.8*
%{_mandir}/man8/rpm-misc.8*
%{_mandir}/man8/rpm-plugins.8*

# XXX this places translated manuals to wrong package wrt eg rpmbuild
%lang(fr) %{_mandir}/fr/man[18]/*.[18]*
%lang(ko) %{_mandir}/ko/man[18]/*.[18]*
%lang(ja) %{_mandir}/ja/man[18]/*.[18]*
%lang(pl) %{_mandir}/pl/man[18]/*.[18]*
%lang(ru) %{_mandir}/ru/man[18]/*.[18]*
%lang(sk) %{_mandir}/sk/man[18]/*.[18]*

%attr(0755, root, root) %dir %{rpmhome}
%{rpmhome}/macros
%{rpmhome}/macros.d
%{rpmhome}/lua
%{rpmhome}/rpmpopt*
%{rpmhome}/rpmrc

%{rpmhome}/rpmdb_*
%{rpmhome}/rpm.daily
%{rpmhome}/rpm.log
%{rpmhome}/rpm.supp
%{rpmhome}/rpm2cpio.sh
%{rpmhome}/tgpg

%{rpmhome}/platform

%dir %{rpmhome}/fileattrs

%files libs
%{_libdir}/librpmio.so.%{sover}
%{_libdir}/librpm.so.%{sover}
%{_libdir}/librpmio.so.%{sover}.*
%{_libdir}/librpm.so.%{sover}.*
%if %{with plugins}
%dir %{_libdir}/rpm-plugins

%files plugin-syslog
%{_libdir}/rpm-plugins/syslog.so
%{_mandir}/man8/rpm-plugin-syslog.8*

%files plugin-selinux
%{_libdir}/rpm-plugins/selinux.so
%{_mandir}/man8/rpm-plugin-selinux.8*

%files plugin-systemd-inhibit
%{_libdir}/rpm-plugins/systemd_inhibit.so
%{_mandir}/man8/rpm-plugin-systemd-inhibit.8*

%files plugin-ima
%{_libdir}/rpm-plugins/ima.so
%{_mandir}/man8/rpm-plugin-ima.8*

%files plugin-fapolicyd
%{_libdir}/rpm-plugins/fapolicyd.so
%{_mandir}/man8/rpm-plugin-fapolicyd.8*

%files plugin-prioreset
%{_libdir}/rpm-plugins/prioreset.so
%{_mandir}/man8/rpm-plugin-prioreset.8*

%files plugin-audit
%{_libdir}/rpm-plugins/audit.so
%{_mandir}/man8/rpm-plugin-audit.8*
# with plugins
%endif

%files build-libs
%{_libdir}/librpmbuild.so.%{sover}
%{_libdir}/librpmbuild.so.%{sover}.*

%files sign-libs
%{_libdir}/librpmsign.so.%{sover}
%{_libdir}/librpmsign.so.%{sover}.*

%files build
%{_bindir}/rpmbuild
%{_bindir}/gendiff
%{_bindir}/rpmspec

%{_mandir}/man1/gendiff.1*
%{_mandir}/man8/rpmbuild.8*
%{_mandir}/man8/rpmdeps.8*
%{_mandir}/man8/rpmspec.8*

%{rpmhome}/brp-*
%{rpmhome}/check-*
%{rpmhome}/debugedit
%{rpmhome}/sepdebugcrcfix
%{rpmhome}/find-debuginfo.sh
%{rpmhome}/find-lang.sh
%{rpmhome}/*provides*
%{rpmhome}/*requires*
%{rpmhome}/*deps*
%{rpmhome}/*.prov
%{rpmhome}/*.req
%{rpmhome}/mkinstalldirs
%{rpmhome}/fileattrs/*

%files sign
%{_bindir}/rpmsign
%{_mandir}/man8/rpmsign.8*

%files -n python3-%{name}
%{python3_sitearch}/rpm/
%{python3_sitearch}/rpm-%{rpmver}*.egg-info

%files devel
%{_mandir}/man8/rpmgraph.8*
%{_bindir}/rpmgraph
%{_libdir}/librp*[a-z].so
%{_libdir}/pkgconfig/rpm.pc
%{_includedir}/rpm/

%files cron
%{_sysconfdir}/cron.daily/rpm
%config(noreplace) %{_sysconfdir}/logrotate.d/rpm

%files apidocs
%license COPYING
%doc doc/librpm/html/*

%changelog
* Fri Oct 21 2022 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-19
- Bump release for rebuild

* Fri Sep 23 2022 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-18
- Make write() nonblocking in fapolicyd plugin (#2111251)

* Wed Aug 03 2022 Florian Festi <ffesti@redhat.com> - 4.16.1.3-17
- Make rpm2cpio.sh more robust (#1983015)

* Thu Jun 30 2022 Nick Clifton  <nickc@redhat.com> - 4.16.1.3-15
- Pass _find_debuginfo_vendor_opts to the find-debuginfo script.  (#2099617)

* Tue Jun 28 2022 Florian Festi <ffesti@redhat.com> - 4.16.1.3-14
- Warning for failed key import (#2069877)

* Tue Apr 05 2022 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-12
- Fix minor ABI regression in rpmcli.h (#2037352)

* Mon Feb 14 2022 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-11
- Fix IMA signature lengths assumed constant, take III (#2018937)
- Fix regression reading rpm v3 and other rare packages (#2037186)
- Fix spurious %transfiletriggerpostun execution (#2023692)

* Mon Jan 31 2022 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-10
- Address covscan issues in binding sigs validation patch (#1943724)
- Bump hash for rpmdb cookie to SHA256 for FIPS (#2048455)
- Add --path query option (#2037352)
- Skip recorded symlinks in --setperms (#2025906)

* Mon Dec 13 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-9
- Fix IMA signature lengths assumed constant, take II (#2018937)

* Thu Dec 09 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-8
- Support hash v8 databases from BDB < 4.6 (#1965147)
- Ensure ELF files get stripped when debuginfo is disabled (#1999009)
- Actually honor libarchive bcond at configure time (#1999012)
- Unbreak checking of installed rich dependencies (#2015407)
- Rebuild against soname bump in ima-evm-utils (#2026079)
- Fix IMA signature lengths assumed constant (#2018937)
- Validate and require subkey binding sigs on PGP pubkeys (#1943724)
- Fixes CVE-2021-3521

* Thu Aug 19 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-7
- Unblock signals in forked scriptlets (#1991667)

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 4.16.1.3-6.1
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jul 28 2021 Florian Weimer <fweimer@redhat.com> - 4.16.1.3-6
- Rebuild to pick up OpenSSL 3.0 Beta ABI (#1984097)

* Fri Jul 23 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-5
- Rebuild for gating.yaml

* Thu Jul 22 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-4
- Add support for EdDSA signatures to rpmsign (#1962234)
- Add fapolicyd plugin (#1942549)

* Mon Jul 12 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-3
- Release bump for a rebuild

* Tue Jun 29 2021 Michal Domonkos <mdomonko@redhat.com> - 4.16.1.3-2
- Address important covscan issues (#1938861)

* Tue Jun 15 2021 Mohan Boddu <mboddu@redhat.com> - 4.16.1.3-1.2
- Rebuilt for RHEL 9 BETA for openssl 3.0. Related: rhbz#1971065

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 4.16.1.3-1.1
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Mon Mar 22 2021 Panu Matilainen <pmatilai@redhat.com> - 4.16.1.3-1
- Rebase to rpm 4.16.1.3 (https://rpm.org/wiki/Releases/4.16.1.3)

* Wed Feb 03 2021 Panu Matilainen <pmatilai@redhat.com> - 4.16.1.2-6
- Drop support for read-write Berkeley DB format (#1787311)

* Wed Feb 03 2021 Panu Matilainen <pmatilai@redhat.com> - 4.16.1.2-5
- Make with/without bdb build option actually work
- Clean up unpackaged /var/tmp from the build root

* Wed Jan 27 2021 Fedora Release Engineering <releng@fedoraproject.org> - 4.16.1.2-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 22 2021 Mark Wielaard <mjw@fedoraproject.org> - 4.16.1.2-4
- Fix edit_attributes_str_comp_dir in Patch916 (#1919107)

* Tue Jan 19 2021 Jeff Law <law@redhat.com> - 4.16.1.2-3
- Fix typo in test for F33 or newer

* Tue Jan 19 2021 Mark Wielaard <mjw@fedoraproject.org> - 4.16.1.2-2
- Add debugedit DWARF5 support

* Wed Dec 16 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.1.2-1
- Rebase to rpm 4.16.1.2 (http://rpm.org/wiki/Releases/4.16.1.2)
- Add a spec safeguard for accidental soname bumps

* Wed Dec 16 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.1.1-1
- Rebase to rpm 4.16.1.1 (http://rpm.org/wiki/Releases/4.16.1.1)

* Thu Dec 10 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.1-1
- Rebase to rpm 4.16.1 (http://rpm.org/wiki/Releases/4.16.1)

* Mon Nov 30 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-5
- Only disable test-suite where it's actually broken

* Mon Nov 30 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-4
- Fix BDB crashing on failed open attempts (#1902395, #1898299, #1900407)
- Fix unnecessary double failure on lazy keyring open

* Wed Oct 28 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-3
- Issue deprecation warning when creating BDB databases (#1787311)
- Temporarily disable test-suite due to massive fakechroot breakage

* Mon Oct 05 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-2
- Clean up after test-suite which leaves a read-only tree behind

* Wed Sep 30 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-1
- Rebase to 4.16.0 final (https://rpm.org/wiki/Releases/4.16.0)

* Mon Aug 31 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-0.rc1.1
- Rebase to 4.16.0-rc1
- Run test-suite in parallel

* Sat Aug 01 2020 Fedora Release Engineering <releng@fedoraproject.org> - 4.16.0-0.beta3.2.3
- Second attempt - Rebuilt for
  https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jul 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 4.16.0-0.beta3.2.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Sun Jul 26 2020 Peter Robinson <pbrobinson@fedoraproject.org> - 4.16.0-0.beta3.2.1
- rebuild for ima-evm-utils 1.3

* Mon Jun 29 2020 Tom Callaway <spot@fedoraproject.org> - 4.16.0-0.beta3.2
- rebuild for lua 5.4

* Wed Jun 24 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-0.beta3.1
- Rebase to beta3

* Wed Jun 10 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-0.beta1.4
- Fix prefix search on sqlite backend (many file triggers not running)

* Mon Jun 8 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-0.beta1.3
- Unbreak metainfo() provide generation

* Wed Jun 3 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-0.beta1.2
- Don't auto-enable _flush_io on non-rotational media, it's too costly

* Mon Jun 1 2020 Panu Matilainen <pmatilai@redhat.com> - 4.16.0-0.beta1.1
- Rebase to rpm 4.16.0-beta1

* Fri May 22 2020 Miro Hrončok <mhroncok@redhat.com> - 4.15.90-0.git14971.12.1
- Rebuilt for Python 3.9

* Tue May 12 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.12
- Fix segfault when trying to use unknown database backend

* Thu May 7 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.11
- Flag BDB databases for rebuild on next reboot whenever rpm is updated
- Switch default database to sqlite (#1818910)

* Mon May 4 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.10
- Handle rpmdb-rebuild service enablement for upgrades

* Thu Apr 23 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.9
- Fix questionable uses of %%{name} and %%{version} in the spec

* Wed Apr 22 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.8
- Fix regression(s) on build dependency resolution

* Wed Apr 22 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.7
- Add rpmdb-rebuild systemd service

* Fri Apr 17 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.6
- Warn on undefined macros in buildtree setup macros (#1820349)

* Thu Apr 09 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.5
- Fix regression causing all ELF files classified as OCaml

* Mon Apr 06 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.4
- Fix invalid path passed to parametric macro generators

* Thu Apr 02 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.3
- Fix db lock files not getting packaged

* Tue Mar 31 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.2
- Move bdb specific systemd-tmpfiles cleanup crutch behind the bdb bcond

* Tue Mar 31 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.90-0.git14971.1
- Rebase to rpm 4.16 alpha (https://rpm.org/wiki/Releases/4.16.0)
- Add bconds for and enable sqlite, ndb and bdb_ro database backends
- Add bcond for disabling bdb backend
- Drop lmdb bcond, the backend was removed upstream
- Ensure all database backend files are owned
- Fix external environment causing test-suite failures in spec build
- Re-enable hard test-suite failures again

* Thu Jan 30 2020 Fedora Release Engineering <releng@fedoraproject.org> - 4.15.1-2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Jan 9 2020 Panu Matilainen <pmatilai@redhat.com> - 4.15.1-2
- Obsolete python2-rpm to fix upgrade path (#1775113)

* Mon Nov 18 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.1-1
- Rebase to 4.15.1 (https://rpm.org/wiki/Releases/4.15.1)

* Thu Nov 14 2019 Adam Williamson <awilliam@redhat.com> - 4.15.0-7
- Really revert armv8 detection improvements (patch was not applied in -6)

* Wed Oct 23 2019 Peter Robinson <pbrobinson@fedoraproject.org> 4.15.0-6
- Revert armv8 detection improvements

* Mon Oct 21 2019 Stephen Gallagher <sgallagh@redhat.com> - 4.15.0-5
- Revert aliasing arm64 to aarch64
- Resolves: rhbz#1763831

* Fri Oct 18 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-4
- Revert problematic sub-variants of armv8 (#1691430)

* Thu Oct 17 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-3
- Drop python2 bindings for good (#1761211)

* Tue Oct 15 2019 Adam Williamson <awilliam@redhat.com> - 4.15.0-2
- Revert systemd inhibit plugin's calling of dbus_shutdown (#1750575)

* Thu Sep 26 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-1
- Update to 4.15.0 final (https://rpm.org/wiki/Releases/4.15.0)

* Wed Aug 28 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-0.rc1.1
- Update to 4.15.0-rc1

* Tue Aug 27 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-0.beta.6
- Fix some issues in the thread cap logic

* Mon Aug 26 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-0.beta.5
- Re-enable test-suite, temporarily disabled during alpha troubleshooting

* Fri Aug 23 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-0.beta.4
- Cap number of threads on 32bit platforms (#1729382)
- Drop %%_lto_cflags macro (reverted upstream)

* Fri Aug 23 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-0.beta.3
- Restore strict order of build scriptlet stdout/stderr output

* Thu Aug 15 2019 Miro Hrončok <mhroncok@redhat.com> - 4.15.0-0.beta.2.3
- Rebuilt for Python 3.8

* Wed Jul 31 2019 Miro Hrončok <mhroncok@redhat.com> - 4.15.0-0.beta.2.2
- Rebuilt for libimaevm.so.1

* Fri Jul 26 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.15.0-0.beta.2.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Sat Jul 20 18:30:10 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.15.0-0.beta.2
- Backport patch to not set RPMTAG_BUILDTIME to SOURCE_DATE_EPOCH

* Thu Jun 27 2019 Panu Matilainen <pmatilai@redhat.com> - 4.15.0-0.beta.1
- Rebase to 4.15.0 beta

* Thu Jun 20 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.90-0.git14653.18
- Fix excessive TLS use, part II (#1722181)

* Thu Jun 20 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.90-0.git14653.17
- Fix excessive TLS use (#1722181)

* Wed Jun 19 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.90-0.git14653.16
- Drop buildarch again now that python_provide no longer needs it (#1720139)

* Fri Jun 14 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.90-0.git14653.15
- Temporarily re-enable buildarch macro for python_provide macro use (#1720139)

* Thu Jun 13 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.90-0.git14653.14
- Don't fail build trying to kill a non-existent process (#1720143)

* Tue Jun 11 14:59:16 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.90-0.git14653.13
- Fix build of binary packages in parallel

* Tue Jun 11 00:08:50 CEST 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.90-0.git14653.10
- Revert generation of binary packages in parallel

* Mon Jun 10 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.90-0.git14653.1
- Update to 4.15.0 alpha

* Mon Jun 10 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-14
- Drop support for sanitizer build, it never really worked anyway
- Drop leftover build-dependency on binutils-devel
- Truncate changelog to rpm 4.14.x (last two years)

* Mon Jun 10 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-13
- Drop support for Fedora < 28 builds
- Drop leftover BDB-related compiler flag foo

* Fri Jun 07 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-12
- Use pre-determined buildhost in test-suite to avoid DNS usage
- Drop obsolete specspo and gpg2 related patches

* Fri Jun 07 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.2.1-11
- Use py2/3 macros for building and installing the bindings

* Tue May 21 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-10
- Support build-id generation from compressed ELF files (#1650072)

* Fri May 03 2019 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.2.1-9
- Suggest gdb-minimal

* Thu Apr 25 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-8
- Replace deprecated __global_ldflags uses with build_ldflags macro

* Thu Apr 11 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-7
- Fix excessive reference counting on faked string .decode()

* Wed Apr 10 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-6
- Unbreak Python 3 API by returning string data as surrogate-escaped utf-8
  string objects instead of bytes (#1693751)
- As a temporary crutch,  monkey-patch a .decode() method to returned strings
  to give users time to migrate from the long-standing broken behavior

* Wed Apr 10 2019 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-5
- Generate minidebug for PIE executables on file >= 5.33 too
- Backport find-debuginfo --g-libs option for glibc's benefit (#1661512)

* Sat Feb 02 2019 Fedora Release Engineering <releng@fedoraproject.org> - 4.14.2.1-4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Wed Dec 19 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-4
- Backport the new modularity label tag (#1650286)

* Mon Nov 19 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-3
- Take prefix into account when compressing man pages etc for Flatpak builds

* Wed Oct 24 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-2
- Selinux plugin requires a base policy to work (#1641631)

* Mon Oct 22 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2.1-1
- Rebase to rpm 4.14.2.1 (http://rpm.org/wiki/Releases/4.14.2.1)

* Wed Oct 17 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.2-9
- Push name/epoch/version/release macro before invoking depgens

* Tue Oct 16 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.2-8
- Resurrect long since broken Lua library path

* Fri Oct 12 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-7
- Actually fail build on test-suite failures again
- Invoke python2 explicitly from test-suite to unbreak build, part II

* Thu Oct 11 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-6
- Drop duplicate BDB buildrequire
- Drop nowadays unnecessary BDB macro foo
- Drop nowadays unnecessary manual libcap dependency

* Thu Oct 11 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-5
- Own all rpmdb files and ensure the list remains up to date
- Drop redundant verify exclusions on rpmdb ghosts
- Fix build when systemd is not installed (duh)

* Thu Oct 11 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-4
- Erm, really use the macro for tmpfiles.d path
- Erm, don't nuke buildroot at beginning of %%install
- Use modern build/install helper macros

* Thu Oct 11 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-3
- Eh, selinux plugin dependency condition was upside down (#1493267)
- Drop no longer necessary condition over imaevm name
- Drop no longer necessary obsolete on compat-librpm3

* Thu Oct 11 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-2
- Fix ancient Python GIL locking bug (#1632488)
- Use the appropriate macro for tmpfiles.d now that one exists

* Tue Aug 21 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-1
- Update to rpm 4.14.2 final (http://rpm.org/wiki/Releases/4.14.2)

* Mon Aug 13 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-0.rc2.2
- Move python-macro-helper to main package where the macros are (#1577860)

* Wed Aug 08 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-0.rc2.1
- Update to rpm 4.14.2-rc2

* Sat Jul 21 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.2-0.rc1.2
- Decompress DWARF compressed ELF sections

* Sat Jul 14 2018 Fedora Release Engineering <releng@fedoraproject.org> - 4.14.2-0.rc1.1.2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Mon Jul 02 2018 Miro Hrončok <mhroncok@redhat.com> - 4.14.2-0.rc1.1.1
- Rebuilt for Python 3.7

* Fri Jun 29 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.2-0.rc1.1
- Update to rpm 4.14.2-rc1
- Patching test-suite for python2 too painful, just sed it instead
- Fix premature version increment from previous changelog entries, oops

* Fri Jun 29 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-13
- Ehm, need to patch the autogenerated rpmtests script too for python2
- Ehm, it's ldconfig_scriptlets not scripts
- Drop the non-working python envvar magic from obsoleted change

* Fri Jun 29 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-12
- Invoke python2 explicitly from test-suite to unbreak build

* Fri Jun 29 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-11
- Remove direct ldconfig calls, use compat macros instead

* Fri Jun 15 2018 Miro Hrončok <mhroncok@redhat.com> - 4.14.1-10.1
- Rebuilt for Python 3.7

* Mon May 28 2018 Miro Hrončok <mhroncok@redhat.com> - 4.14.1-10
- Backport upstream solution to make brp-python-bytecompile automagic part opt-outable
  https://fedoraproject.org/wiki/Changes/No_more_automagic_Python_bytecompilation

* Tue May 22 2018 Mark Wielaard <mjw@fedoraproject.org> - 4.14.1-9
- find-debuginfo.sh: Handle application/x-pie-executable (#1581224)

* Tue Feb 20 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.1-8
- Split rpm-build-libs to one more subpackage rpm-sign-libs

* Mon Feb 19 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-7
- Explicitly BuildRequire gcc and make

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.1-6.1
- Escape macros in %%changelog

* Wed Jan 31 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-6
- Avoid unnecessary macro helper dependency on /usr/bin/python (#1538657)
- Fix release of previous changelog entry

* Tue Jan 30 2018 Tomas Orsava <torsava@redhat.com> - 4.14.1-5
- Add envvar that will be present during RPM build,
  Part of a Fedora Change for F28: "Avoid /usr/bin/python in RPM build"
  https://fedoraproject.org/wiki/Changes/Avoid_usr_bin_python_in_RPM_Build

* Tue Jan 30 2018 Petr Viktorin <pviktori@redhat.com> - 4.14.1-4
- Skip automatic Python byte-compilation if *.py files are not present

* Thu Jan 25 2018 Florian Weimer <fweimer@redhat.com> - 4.14.1-3
- Rebuild to work around gcc bug leading to librpm miscompilation (#1538648)

* Thu Jan 18 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-2
- Avoid nuking the new python-macro-helper along with dep generators (#1535692)

* Tue Jan 16 2018 Panu Matilainen <pmatilai@redhat.com> - 4.14.1-1
- Rebase to rpm 4.14.1 (http://rpm.org/wiki/Releases/4.14.1)

* Tue Nov 07 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.0-5
- Fix typo in Obsoletes

* Mon Nov 06 2017 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 4.14.0-4
- Remove platform-python bits

* Thu Oct 26 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-3
- Move selinux plugin dependency to selinux-policy in Fedora >= 28 (#1493267)

* Thu Oct 12 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-2
- Dump out test-suite log in case of failures again
- Don't assume per-user groups in test-suite

* Thu Oct 12 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-1
- Rebase to rpm 4.14.0 final (http://rpm.org/wiki/Releases/4.14.0)

* Tue Oct 10 2017 Troy Dawson <tdawson@redhat.com> - 4.14.0-0.rc2.6
- Cleanup spec file conditionals

* Tue Oct 03 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc2.5
- Add build conditionals for zstd and lmdb support
- Enable zstd support

* Tue Oct 03 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc2.4
- Spec cleanups

* Fri Sep 29 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc2.3
- BuildRequire gnupg2 for the testsuite

* Fri Sep 29 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc2.2
- ima-evm-utils only has a -devel package in fedora >= 28

* Thu Sep 28 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc2.1
- Rebase to rpm 4.14.0-rc2 (http://rpm.org/wiki/Releases/4.14.0)

* Mon Sep 18 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc1.3
- Fix Ftell() past 2GB on 32bit architectures (#1492587)

* Thu Sep 07 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc1.2
- Actually honor with/without libimaevm option
- ima-evm-utils-devel >= 1.0 is required for rpm >= 4.14.0

* Wed Sep 06 2017 Panu Matilainen <pmatilai@redhat.com> - 4.14.0-0.rc1.1
- Rebase to rpm 4.14.0-rc1 (http://rpm.org/wiki/Releases/4.14.0)
- Re-enable SHA256 header digest generation (see #1480407)

* Mon Aug 28 2017 Panu Matilainen <pmatilai@redhat.com> - 4.13.90-0.git14000.8
- Band-aid for DB_VERSION_MISMATCH errors on glibc updates (#1465809)

* Thu Aug 24 2017 Panu Matilainen <pmatilai@redhat.com> - 4.13.90-0.git14000.7
- Remove ugly kludges from posttrans script, BDB handles this now

* Fri Aug 18 2017 Panu Matilainen <pmatilai@redhat.com> - 4.13.90-0.git14000.6
- Silence harmless but bogus error message on noarch packages (#1482144)

* Thu Aug 17 2017 Miro Hrončok <mhroncok@redhat.com> - 4.13.90-0.git14002.5
- Build with platform_python

* Mon Aug 14 2017 Miro Hrončok <mhroncok@redhat.com> - 4.13.90-0.git14000.4
- Add platform-python bytecompilation patch: platform-python-bytecompile.patch
- Add platform python deps generator patch: platform-python-abi.patch
- Add a platform-python subpackage and remove system python related declarations
- Build rpm without platform_python for bytecompilation
  (https://fedoraproject.org/wiki/Changes/Platform_Python_Stack)

* Mon Aug 14 2017 Panu Matilainen <pmatilai@redhat.com> - 4.13.90-0.git14000.3
- Disable macro argument quoting as a band-aid to #1481025

* Fri Aug 11 2017 Panu Matilainen <pmatilai@redhat.com> - 4.13.90-0.git14000.2
- Disable SHA256 header-only digest generation temporarily (#1480407)

* Thu Aug 10 2017 Panu Matilainen <pmatilai@redhat.com> - 4.13.90-0.git14000.1
- Rebase to rpm 4.13.90 aka 4.14.0-alpha (#1474836)

