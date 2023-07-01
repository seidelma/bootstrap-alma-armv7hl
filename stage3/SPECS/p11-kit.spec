# This spec file has been automatically updated
Version:	0.24.1
Release: 2%{?dist}
Name:           p11-kit
Summary:        Library for loading and sharing PKCS#11 modules

License:        BSD
URL:            http://p11-glue.freedesktop.org/p11-kit.html
Source0:        https://github.com/p11-glue/p11-kit/releases/download/%{version}/p11-kit-%{version}.tar.xz
Source1:        https://github.com/p11-glue/p11-kit/releases/download/%{version}/p11-kit-%{version}.tar.xz.sig
Source2:        gpgkey-462225C3B46F34879FC8496CD605848ED7E69871.gpg
Source3:        trust-extract-compat
Source4:        p11-kit-client.service

BuildRequires:  gcc
BuildRequires:  libtasn1-devel >= 2.3
BuildRequires:  libffi-devel
BuildRequires:  gettext
BuildRequires:  meson
#BuildRequires:  gtk-doc
BuildRequires:  systemd-devel
BuildRequires:  bash-completion
# Work around for https://bugzilla.redhat.com/show_bug.cgi?id=1497147
# Remove this once it is fixed
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  gnupg2
BuildRequires:  /usr/bin/xsltproc

%description
p11-kit provides a way to load and enumerate PKCS#11 modules, as well
as a standard configuration setup for installing PKCS#11 modules in
such a way that they're discoverable.


%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.


%package trust
Summary:            System trust module from %{name}
Requires:           %{name}%{?_isa} = %{version}-%{release}
Requires(post):     %{_sbindir}/update-alternatives
Requires(postun):   %{_sbindir}/update-alternatives
Conflicts:          nss < 3.14.3-9

%description trust
The %{name}-trust package contains a system trust PKCS#11 module which
contains certificate anchors and blocklists.


%package server
Summary:        Server and client commands for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description server
The %{name}-server package contains command line tools that enable to
export PKCS#11 modules through a Unix domain socket.  Note that this
feature is still experimental.


# solution taken from icedtea-web.spec
%define multilib_arches ppc64 sparc64 x86_64 ppc64le
%ifarch %{multilib_arches}
%define alt_ckbi  libnssckbi.so.%{_arch}
%else
%define alt_ckbi  libnssckbi.so
%endif


%prep
gpgv2 --keyring %{SOURCE2} %{SOURCE1} %{SOURCE0}

%autosetup -p1

%build
# These paths are the source paths that  come from the plan here:
# https://fedoraproject.org/wiki/Features/SharedSystemCertificates:SubTasks
%meson -Dtrust_paths=%{_sysconfdir}/pki/ca-trust/source:%{_datadir}/pki/ca-trust-source
%meson_build

%install
%meson_install
mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/pkcs11/modules
install -p -m 755 %{SOURCE3} $RPM_BUILD_ROOT%{_libexecdir}/p11-kit/
# Install the example conf with %%doc instead
mkdir -p $RPM_BUILD_ROOT%{_docdir}/%{name}
mv $RPM_BUILD_ROOT%{_sysconfdir}/pkcs11/pkcs11.conf.example $RPM_BUILD_ROOT%{_docdir}/%{name}/pkcs11.conf.example
mkdir -p $RPM_BUILD_ROOT%{_userunitdir}
install -p -m 644 %{SOURCE4} $RPM_BUILD_ROOT%{_userunitdir}
%find_lang %{name}

%check
%meson_test


%post trust
%{_sbindir}/update-alternatives --install %{_libdir}/libnssckbi.so \
        %{alt_ckbi} %{_libdir}/pkcs11/p11-kit-trust.so 30

%postun trust
if [ $1 -eq 0 ] ; then
        # package removal
        %{_sbindir}/update-alternatives --remove %{alt_ckbi} %{_libdir}/pkcs11/p11-kit-trust.so
fi


%files -f %{name}.lang
%{!?_licensedir:%global license %%doc}
%license COPYING
%doc AUTHORS NEWS README
%{_docdir}/%{name}/pkcs11.conf.example
%dir %{_sysconfdir}/pkcs11
%dir %{_sysconfdir}/pkcs11/modules
%dir %{_datadir}/p11-kit
%dir %{_datadir}/p11-kit/modules
%dir %{_libexecdir}/p11-kit
%{_bindir}/p11-kit
%{_libdir}/libp11-kit.so.*
%{_libdir}/p11-kit-proxy.so
%{_libexecdir}/p11-kit/p11-kit-remote
#%{_mandir}/man1/trust.1.gz
#%{_mandir}/man8/p11-kit.8.gz
#%{_mandir}/man5/pkcs11.conf.5.gz
%{_datadir}/bash-completion/completions/p11-kit

%files devel
%{_includedir}/p11-kit-1/
%{_libdir}/libp11-kit.so
%{_libdir}/pkgconfig/p11-kit-1.pc
#%doc %{_datadir}/gtk-doc/

%files trust
%{_bindir}/trust
%dir %{_libdir}/pkcs11
%ghost %{_libdir}/libnssckbi.so
%{_libdir}/pkcs11/p11-kit-trust.so
%{_datadir}/p11-kit/modules/p11-kit-trust.module
%{_libexecdir}/p11-kit/trust-extract-compat
%{_datadir}/bash-completion/completions/trust

%files server
%{_libdir}/pkcs11/p11-kit-client.so
%{_userunitdir}/p11-kit-client.service
%{_libexecdir}/p11-kit/p11-kit-server
%{_userunitdir}/p11-kit-server.service
%{_userunitdir}/p11-kit-server.socket


%changelog
* Tue Feb  1 2022 Daiki Ueno <dueno@redhat.com> - 0.24.1-2
- Replace "black list" with "blocklist" in -trust subpackage description (#2026457)

* Mon Jan 17 2022 Packit Service <user-cont-team+packit-service@redhat.com> - 0.24.1-1
- Release 0.24.1 (Daiki Ueno)
- common: Support copying attribute array recursively (Daiki Ueno)
- common: Add assert_ptr_cmp (Daiki Ueno)
- gtkdoc: remove dependencies on custom target files (Eli Schwartz)
- doc: Replace occurrence of black list with blocklist (Daiki Ueno)
- build: Suppress cppcheck false-positive on array bounds (Daiki Ueno)
- ci: Use Docker image from the same repository (Daiki Ueno)
- ci: Integrate Docker image building to GitHub workflow (Daiki Ueno)
- rpc: Fallback to version 0 if server does not support negotiation (Daiki Ueno)
- build: Port e850e03be65ed573d0b69ee0408e776c08fad8a3 to meson (Daiki Ueno)
- Link libp11-kit so that it cannot unload (Emmanuel Dreyfus)
- trust: Use dngettext for plurals (Daiki Ueno)
- rpc: Support protocol version negotiation (Daiki Ueno)
- rpc: Separate authentication step from transaction (Daiki Ueno)
- Meson: p11_system_config_modules instead of p11_package_config_modules (Issam E. Maghni)
- shell: test -a|o is not POSIX (Issam E. Maghni)
- Meson: Add libtasn1 to trust programs (Issam E. Maghni)
- meson: optionalise glib's development files for gtk_doc (Đoàn Trần Công Danh)

* Wed Aug 18 2021 DJ Delorie <dj@redhat.com> - 0.24.0-4
- Rebuilt for libffi 3.4.2 SONAME transition.
  Related: rhbz#1891914

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 0.24.0-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Tue Jul 13 2021 Daiki Ueno <dueno@redhat.com> - 0.24.0-2
- Rebuild with newer GCC to fix annocheck failures

* Thu Jun 03 2021 Packit Service <user-cont-team+packit-service@redhat.com> - 0.24.0-1
- common: Only check strndup behavior when replacement is used (Daiki Ueno)
- Release 0.24.0 (Daiki Ueno)
- Release 0.23.22 (Daiki Ueno)
- rpc: Tighten attribute array check with manual enumeration (Daiki Ueno)
- Check for SUN_LEN and provide fallback (Claes Nästén)
- Do not define _XOPEN_SOURCE in compat.c on Solaris (Claes Nästén)
- make autogen.sh a bit more portable (Claes Nästén)
- rpc-server: Disable parsing CKF_ARRAY_ATTRIBUTE (Daiki Ueno)
- Update README.md (Daiki Ueno)
- README.md: Suggest using only meson sub-commands instead of ninja (Daiki Ueno)
- p11-kit: Add missing <limits.h> include for SIZE_MAX (Daiki Ueno)
- packit: drop synced_files (Tomas Tomecek)
- packit: fedora renamed master branch to rawhide (Tomas Tomecek)
- Fix minor typo (Yuri Chornoivan)
- po: Add trust/trust.c to POTFILES.in (Daiki Ueno)
- po: Update POTFILES.in (Daiki Ueno)
- trust: Make more strings translatable (Daiki Ueno)
- p11-kit: Make more strings translatable (Daiki Ueno)
- common: Enable message translation in p11_tool_main (Daiki Ueno)
- meson: Make sure to set PROJECT_NAME and ENABLE_NLS for 'nls' option (Daiki Ueno)
- build: Add fuzz/meson.build in the distribution (Daiki Ueno)
- fuzz: Move the directory out of build/ (Daiki Ueno)
- Release all library/mock resources before exit (David Cook)
- Add separate oss-fuzz Makefile target (David Cook)
- Add build targets for future additional fuzzers (David Cook)
- Build fuzzer target from meson/ninja (David Cook)
- Explicit dependency for virtual-fixed-generated.h (David Cook)
- Build fuzzer target from automake (David Cook)
- rpc_fuzzer: Clean up buffer before exit (David Cook)
- New set of fuzzer seeds (David Cook)
- github: Remove unnecessary SRCDIR envvar (Daiki Ueno)
- github: Use runuser instead of su for building and testing (Daiki Ueno)
- github: Use composite action to simplify the main recipe (Daiki Ueno)
- github: Use pre-built container image for building (Daiki Ueno)
- README.md: Add GitHub workflow status (Daiki Ueno)
- travis: Remove configurations other than FreeBSD (Daiki Ueno)
- autotools: Fix for VPATH build (Daiki Ueno)
- github actions: Initial CI setup (Anderson Toshiyuki Sasaki)
- modules: p11_kit_initialize_module: Remove redundant module unref (Daiki Ueno)
- server: Account for NUL byte at the end of Unix domain socket path (Daiki Ueno)
- compat: Expose FreeBSD specific issetugid, getresuid, and getresgid (Daiki Ueno)
- compat: Remove <unistd.h> inclusion from compat.h (Daiki Ueno)
- compat: Avoid unused variables warning in fdwalk emulation (Daiki Ueno)
- compat: Pacify ASan complaints on intentionally leaked buffer (Daiki Ueno)
- meson: Link trust/client modules explicitly to -ldl (Daiki Ueno)
- p11-kit/lists.c: Add stdint.h to fix compilation (Daniel Engberg)
- Follow-up to arithmetic overflow fix (David Cook)
- Check for arithmetic overflows before allocating (David Cook)
- Check attribute length against buffer size (David Cook)
- Fix bounds check in p11_rpc_buffer_get_byte_array (David Cook)
- Fix buffer overflow in log_token_info (David Cook)
- common: Don't assume __STDC_VERSION__ is always defined (Daiki Ueno)
- compat: getauxval: correct compiler macro for FreeBSD (Daiki Ueno)
- compat: fdwalk: add guard for Linux specific local variables (Daiki Ueno)
- meson: Add missing libtasn1 dependency (Daiki Ueno)
- travis: Add freebsd build (Daiki Ueno)
- anchor: Prefer persistent format when storing anchor (Daiki Ueno)
- travis: Run "make check" along with "make distcheck" for coverage (Daiki Ueno)
- travis: Use python3 as the default Python interpreter (Daiki Ueno)
- travis: Route to Ubuntu 20.04 base image (Daiki Ueno)
- meson: Set -fstack-protector for MinGW64 cross build (Daiki Ueno)
- meson: expand ternary operator in function call for compatibility (Daiki Ueno)
- meson: Use custom_target for generating external XML entities (Daiki Ueno)
- meson: Allow building manpages without gtk-doc (Jan Alexander Steffens (heftig))
- Rename is_path_component to is_path_separator (Alexander Sosedkin)
- Use is_path_component in one more place (Alexander Sosedkin)
- Remove more duplicate separators in p11_path_build (Alexander Sosedkin)
- common: Fix infloop in p11_path_build (Daiki Ueno)
- Use inclusive language on certificate distrust (Daiki Ueno)
- proxy: C_CloseAllSessions: Make sure that calloc args are non-zero (Daiki Ueno)
- build: Use calloc in a consistent manner (Daiki Ueno)
- meson: Allow override of default bashcompdir. Fixes meson regression (issue #322).  Pass -Dbashcompdir=/xxx to meson. (John Hein)
- common: Check for a NULL locale before freeing it (Tavian Barnes)
- p11_test_copy_setgid: Skip setgid tests on nosuid filesystems (Anders Kaseorg)
- unix-peer: replace incorrect include1 (Rosen Penev)
- test-compat: Skip getprogname test if BUILDDIR contains a symlink (Daiki Ueno)
- add trust-extract-compat into EXTRA-DIST (Xℹ Ruoyao)
- meson: install trust-extract-compat (Xℹ Ruoyao)
- rename trust-extract-compat.in to trust-extract-compat (Xℹ Ruoyao)

* Fri Apr 16 2021 Mohan Boddu <mboddu@redhat.com> - 0.23.22-4
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Tue Jan 26 2021 Daiki Ueno <dueno@redhat.com> - 0.23.22-3
- Suppress intentional memleak in getprogname emulation (#1905581)

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.22-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Dec 11 2020 Packit Service <user-cont-team+packit-service@redhat.com> - 0.23.22-1
- Release 0.23.22 (Daiki Ueno)
- Follow-up to arithmetic overflow fix (David Cook)
- Check for arithmetic overflows before allocating (David Cook)
- Check attribute length against buffer size (David Cook)
- Fix bounds check in p11_rpc_buffer_get_byte_array (David Cook)
- Fix buffer overflow in log_token_info (David Cook)
- common: Don't assume __STDC_VERSION__ is always defined (Daiki Ueno)
- compat: getauxval: correct compiler macro for FreeBSD (Daiki Ueno)
- compat: fdwalk: add guard for Linux specific local variables (Daiki Ueno)
- meson: Add missing libtasn1 dependency (Daiki Ueno)
- travis: Add freebsd build (Daiki Ueno)
- anchor: Prefer persistent format when storing anchor (Daiki Ueno)
- travis: Run "make check" along with "make distcheck" for coverage (Daiki Ueno)
- travis: Use python3 as the default Python interpreter (Daiki Ueno)
- travis: Route to Ubuntu 20.04 base image (Daiki Ueno)
- meson: Set -fstack-protector for MinGW64 cross build (Daiki Ueno)
- meson: expand ternary operator in function call for compatibility (Daiki Ueno)
- meson: Use custom_target for generating external XML entities (Daiki Ueno)
- meson: Allow building manpages without gtk-doc (Jan Alexander Steffens (heftig))
- Rename is_path_component to is_path_separator (Alexander Sosedkin)
- Use is_path_component in one more place (Alexander Sosedkin)
- Remove more duplicate separators in p11_path_build (Alexander Sosedkin)
- common: Fix infloop in p11_path_build (Daiki Ueno)
- proxy: C_CloseAllSessions: Make sure that calloc args are non-zero (Daiki Ueno)
- build: Use calloc in a consistent manner (Daiki Ueno)
- meson: Allow override of default bashcompdir. Fixes meson regression (issue #322).  Pass -Dbashcompdir=/xxx to meson. (John Hein)
- common: Check for a NULL locale before freeing it (Tavian Barnes)
- p11_test_copy_setgid: Skip setgid tests on nosuid filesystems (Anders Kaseorg)
- unix-peer: replace incorrect include1 (Rosen Penev)
- test-compat: Skip getprogname test if BUILDDIR contains a symlink (Daiki Ueno)
- add trust-extract-compat into EXTRA-DIST (Xℹ Ruoyao)
- meson: install trust-extract-compat (Xℹ Ruoyao)
- rename trust-extract-compat.in to trust-extract-compat (Xℹ Ruoyao)

* Thu Nov 12 2020 Alexander Sosedkin <asosedkin@redhat.com> - 0.23.21-3
- Add an explicit build dependency on xsltproc

* Tue Aug 18 2020 Packit Service <user-cont-team+packit-service@redhat.com> - 0.23.21-2
- new upstream release: 0.23.21

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Wed Jan 29 2020 Daiki Ueno <dueno@redhat.com> - 0.23.20-1
- Update to upstream 0.23.20 release

* Wed Jan 22 2020 Daiki Ueno <dueno@redhat.com> - 0.23.19-1
- Update to upstream 0.23.19 release
- Check archive signature in %%prep
- Switch to using Meson as the build system

* Mon Sep 30 2019 Daiki Ueno <dueno@redhat.com> - 0.23.18.1-1
- Update to upstream 0.23.18.1 release

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.16.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Thu May 23 2019 Daiki Ueno <dueno@redhat.com> - 0.23.16.1-1
- Update to upstream 0.23.16.1 release

* Thu May 23 2019 Daiki Ueno <dueno@redhat.com> - 0.23.16-1
- Update to upstream 0.23.16 release

* Mon Feb 18 2019 Daiki Ueno <dueno@redhat.com> - 0.23.15-3
- trust: Ignore unreadable content in anchors

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.15-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Jan 21 2019 Daiki Ueno <dueno@redhat.com> - 0.23.15-1
- Update to upstream 0.23.15 release

* Fri Jan 11 2019 Nils Philippsen <nils@tiptoe.de> - 0.23.14-3
- use spaces instead of tabs consistently
- prefer fixed closures to libffi closures (#1656245, patch by Daiki Ueno)

* Mon Oct 29 2018 James Antill <james.antill@redhat.com> - 0.23.14-2
- Remove ldconfig scriptlet, now done via. transfiletrigger in glibc.

* Fri Sep 07 2018 Daiki Ueno <dueno@redhat.com> - 0.23.14-1
- Update to upstream 0.23.14 release

* Wed Aug 15 2018 Daiki Ueno <dueno@redhat.com> - 0.23.13-3
- Forcibly link with libpthread to avoid regressions (rhbz#1615038)

* Wed Aug 15 2018 Daiki Ueno <dueno@redhat.com> - 0.23.13-2
- Fix invalid memory access on proxy cleanup

* Fri Aug 10 2018 Daiki Ueno <dueno@redhat.com> - 0.23.13-1
- Update to upstream 0.23.13 release

* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.12-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed May 30 2018 Daiki Ueno <dueno@redhat.com> - 0.23.12-1
- Update to upstream 0.23.11 release

* Wed Feb 28 2018 Daiki Ueno <dueno@redhat.com> - 0.23.10-1
- Update to upstream 0.23.10 release

* Thu Feb 08 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.9-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Thu Oct 05 2017 Daiki Ueno <dueno@redhat.com> - 0.23.9-2
- server: Make it possible to eval envvar settings

* Wed Oct 04 2017 Daiki Ueno <dueno@redhat.com> - 0.23.9-1
- Update to upstream 0.23.9

* Fri Aug 25 2017 Kai Engert <kaie@redhat.com> - 0.23.8-2
- Fix a regression caused by a recent nss.rpm change, add a %%ghost file
  for %%{_libdir}/libnssckbi.so that p11-kit-trust scripts install.

* Tue Aug 15 2017 Daiki Ueno <dueno@redhat.com> - 0.23.8-1
- Update to 0.23.8 release

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.7-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Jun  2 2017 Daiki Ueno <dueno@redhat.com> - 0.23.7-1
- Update to 0.23.7 release

* Thu May 18 2017 Daiki Ueno <dueno@redhat.com> - 0.23.5-3
- Update p11-kit-modifiable.patch to simplify the logic

* Thu May 18 2017 Daiki Ueno <dueno@redhat.com> - 0.23.5-2
- Make "trust anchor --remove" work again

* Thu Mar  2 2017 Daiki Ueno <dueno@redhat.com> - 0.23.5-1
- Update to 0.23.5 release
- Rename -tools subpackage to -server and remove systemd unit files

* Fri Feb 24 2017 Daiki Ueno <dueno@redhat.com> - 0.23.4-3
- Move p11-kit command back to main package

* Fri Feb 24 2017 Daiki Ueno <dueno@redhat.com> - 0.23.4-2
- Split out command line tools to -tools subpackage, to avoid a
  multilib issue with the main package.  Suggested by Yanko Kaneti.

* Wed Feb 22 2017 Daiki Ueno <dueno@redhat.com> - 0.23.4-1
- Update to 0.23.4 release

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Jan  6 2017 Daiki Ueno <dueno@redhat.com> - 0.23.3-2
- Use internal hash implementation instead of NSS (#1390598)

* Tue Dec 20 2016 Daiki Ueno <dueno@redhat.com> - 0.23.3-1
- Update to 0.23.3 release
- Adjust executables location from %%libdir to %%libexecdir

* Thu Feb 04 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0.23.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Jan 12 2016 Martin Preisler <mpreisle@redhat.com> - 0.23.2-1
- Update to stable 0.23.2 release

* Tue Jun 30 2015 Martin Preisler <mpreisle@redhat.com> - 0.23.1-4
- In proxy module don't call C_Finalize on a forked process [#1217915]
- Do not deinitialize libffi's wrapper functions [#1217915]

* Thu Jun 18 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.23.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Feb 21 2015 Till Maas <opensource@till.name> - 0.23.1-2
- Rebuilt for Fedora 23 Change
  https://fedoraproject.org/wiki/Changes/Harden_all_packages_with_position-independent_code

* Fri Feb 20 2015 Stef Walter <stefw@redhat.com> - 0.23.1-1
- Update to 0.23.1 release

* Thu Oct 09 2014 Stef Walter <stefw@redhat.com> - 0.22.1-1
- Update to 0.22.1 release
- Use SubjectKeyIdentifier as a CKA_ID if possible rhbz#1148895

* Sat Oct 04 2014 Stef Walter <stefw@redhat.com> 0.22.0-1
- Update to 0.22.0 release

* Wed Sep 17 2014 Stef Walter <stefw@redhat.com> 0.21.3-1
- Update to 0.21.3 release
- Includes definitions for trust extensions rhbz#1136817

* Fri Sep 05 2014 Stef Walter <stefw@redhat.com> 0.21.2-1
- Update to 0.21.2 release
- Fix problems with erroneous messages printed rhbz#1133857

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.21.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Thu Aug 07 2014 Stef Walter <stefw@redhat.com> - 0.21.1-1
- Update to 0.21.1 release

* Wed Jul 30 2014 Tom Callaway <spot@fedoraproject.org> - 0.20.3-3
- fix license handling

* Fri Jul 04 2014 Stef Walter <stefw@redhat.com> - 0.20.3-2
- Update to stable 0.20.3 release

* Fri Jun 06 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.20.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat Jan 25 2014 Ville Skyttä <ville.skytta@iki.fi> - 0.20.2-2
- Own the %%{_libdir}/pkcs11 dir in -trust.

* Tue Jan 14 2014 Stef Walter <stefw@redhat.com> - 0.20.2-1
- Update to upstream stable 0.20.2 release
- Fix regression involving blacklisted anchors [#1041328]
- Support ppc64le in build [#1052707]

* Mon Sep 09 2013 Stef Walter <stefw@redhat.com> - 0.20.1-1
- Update to upstream stable 0.20.1 release
- Extract compat trust data after we've changes
- Skip compat extraction if running as non-root
- Better failure messages when removing anchors

* Thu Aug 29 2013 Stef Walter <stefw@redhat.com> - 0.19.4-1
- Update to new upstream 0.19.4 release

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.19.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Jul 24 2013 Stef Walter <stefw@redhat.com> - 0.19.3-1
- Update to new upstream 0.19.3 release (#967822)

* Wed Jun 05 2013 Stef Walter <stefw@redhat.com> - 0.18.3-1
- Update to new upstream stable release
- Fix intermittent firefox cert validation issues (#960230)
- Include the manual pages in the package

* Tue May 14 2013 Stef Walter <stefw@redhat.com> - 0.18.2-1
- Update to new upstream stable release
- Reduce the libtasn1 dependency minimum version

* Thu May 02 2013 Stef Walter <stefw@redhat.com> - 0.18.1-1
- Update to new upstream stable release
- 'p11-kit extract-trust' lives in libdir

* Thu Apr 04 2013 Stef Walter <stefw@redhat.com> - 0.18.0-1
- Update to new upstream stable release
- Various logging tweaks (#928914, #928750)
- Make the 'p11-kit extract-trust' explicitly reject
  additional arguments

* Thu Mar 28 2013 Stef Walter <stefw@redhat.com> - 0.17.5-1
- Make 'p11-kit extract-trust' call update-ca-trust
- Work around 32-bit oveflow of certificate dates
- Build fixes

* Tue Mar 26 2013 Stef Walter <stefw@redhat.com> - 0.17.4-2
- Pull in patch from upstream to fix build on ppc (#927394)

* Wed Mar 20 2013 Stef Walter <stefw@redhat.com> - 0.17.4-1
- Update to upstream version 0.17.4

* Mon Mar 18 2013 Stef Walter <stefw@redhat.com> - 0.17.3-1
- Update to upstream version 0.17.3
- Put the trust input paths in the right order

* Tue Mar 12 2013 Stef Walter <stefw@redhat.com> - 0.16.4-1
- Update to upstream version 0.16.4

* Fri Mar 08 2013 Stef Walter <stefw@redhat.com> - 0.16.3-1
- Update to upstream version 0.16.3
- Split out system trust module into its own package.
- p11-kit-trust provides an alternative to an nss module

* Tue Mar 05 2013 Stef Walter <stefw@redhat.com> - 0.16.1-1
- Update to upstream version 0.16.1
- Setup source directories as appropriate for Shared System Certificates feature

* Tue Mar 05 2013 Stef Walter <stefw@redhat.com> - 0.16.0-1
- Update to upstream version 0.16.0

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Mon Sep 17 2012 Kalev Lember <kalevlember@gmail.com> - 0.14-1
- Update to 0.14

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Jul 16 2012 Kalev Lember <kalevlember@gmail.com> - 0.13-1
- Update to 0.13

* Tue Mar 27 2012 Kalev Lember <kalevlember@gmail.com> - 0.12-1
- Update to 0.12
- Run self tests in %%check

* Sat Feb 11 2012 Kalev Lember <kalevlember@gmail.com> - 0.11-1
- Update to 0.11

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec 20 2011 Matthias Clasen <mclasen@redhat.com> - 0.9-1
- Update to 0.9

* Wed Oct 26 2011 Kalev Lember <kalevlember@gmail.com> - 0.8-1
- Update to 0.8

* Mon Sep 19 2011 Matthias Clasen <mclasen@redhat.com> - 0.6-1
- Update to 0.6

* Sun Sep 04 2011 Kalev Lember <kalevlember@gmail.com> - 0.5-1
- Update to 0.5

* Sun Aug 21 2011 Kalev Lember <kalevlember@gmail.com> - 0.4-1
- Update to 0.4
- Install the example config file to documentation directory

* Wed Aug 17 2011 Kalev Lember <kalevlember@gmail.com> - 0.3-2
- Tighten -devel subpackage deps (#725905)

* Fri Jul 29 2011 Kalev Lember <kalevlember@gmail.com> - 0.3-1
- Update to 0.3
- Upstream rewrote the ASL 2.0 bits, which makes the whole package
  BSD-licensed

* Tue Jul 12 2011 Kalev Lember <kalevlember@gmail.com> - 0.2-1
- Initial RPM release
