%global git_date 20220815
%global git_commit 0fbe86f88d51fb210d536908b10450eb7467e1d6
%{?git_commit:%global git_commit_hash %(c=%{git_commit}; echo ${c:0:7})}

%global _python_bytecompile_extra 0

Name:           crypto-policies
Version:        %{git_date}
Release:        1.git%{git_commit_hash}%{?dist}
Summary:        System-wide crypto policies

License:        LGPLv2+
URL:            https://gitlab.com/redhat-crypto/fedora-crypto-policies
# For RHEL-9 we use the upstream branch rhel9.
Source0:        https://gitlab.com/redhat-crypto/fedora-crypto-policies/-/archive/%{git_commit_hash}/%{name}-git%{git_commit_hash}.tar.gz

BuildArch: noarch
BuildRequires: asciidoc
BuildRequires: libxslt
BuildRequires: openssl
BuildRequires: gnutls-utils >= 3.6.0
BuildRequires: java-1.8.0-openjdk-devel
BuildRequires: bind
BuildRequires: perl-interpreter
BuildRequires: perl-generators
BuildRequires: perl(File::pushd), perl(File::Temp), perl(File::Copy)
BuildRequires: perl(File::Which)
BuildRequires: python3-devel >= 3.6
BuildRequires: python3-pytest
BuildRequires: make

Conflicts: openssl < 1:3.0.1-10
Conflicts: nss < 3.44.0
Conflicts: libreswan < 3.28
Conflicts: openssh < 8.7p1-10
Conflicts: gnutls < 3.7.2-3

%description
This package provides pre-built configuration files with
cryptographic policies for various cryptographic back-ends,
such as SSL/TLS libraries.

%package scripts
Summary: Tool to switch between crypto policies
Requires: %{name} = %{version}-%{release}
Recommends: (grubby if kernel)
Provides: fips-mode-setup = %{version}-%{release}

%description scripts
This package provides a tool update-crypto-policies, which applies
the policies provided by the crypto-policies package. These can be
either the pre-built policies from the base package or custom policies
defined in simple policy definition files.

The package also provides a tool fips-mode-setup, which can be used
to enable or disable the system FIPS mode.

%prep
%setup -q -n fedora-crypto-policies-%{git_commit_hash}-%{git_commit}
%autopatch -p1

%build
%make_build

%install
mkdir -p -m 755 %{buildroot}%{_datarootdir}/crypto-policies/
mkdir -p -m 755 %{buildroot}%{_datarootdir}/crypto-policies/back-ends/
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/crypto-policies/back-ends/
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/crypto-policies/state/
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/crypto-policies/local.d/
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/crypto-policies/policies/
mkdir -p -m 755 %{buildroot}%{_sysconfdir}/crypto-policies/policies/modules/
mkdir -p -m 755 %{buildroot}%{_bindir}

make DESTDIR=%{buildroot} DIR=%{_datarootdir}/crypto-policies MANDIR=%{_mandir} %{?_smp_mflags} install
install -p -m 644 default-config %{buildroot}%{_sysconfdir}/crypto-policies/config
touch %{buildroot}%{_sysconfdir}/crypto-policies/state/current
touch %{buildroot}%{_sysconfdir}/crypto-policies/state/CURRENT.pol

# Drop pre-generated EMPTY policy, we do not need to ship it
rm -rf %{buildroot}%{_datarootdir}/crypto-policies/EMPTY

# Create back-end configs for mounting with read-only /etc/
for d in LEGACY DEFAULT FUTURE FIPS ; do
    mkdir -p -m 755 %{buildroot}%{_datarootdir}/crypto-policies/back-ends/$d
    for f in %{buildroot}%{_datarootdir}/crypto-policies/$d/* ; do
        ln $f %{buildroot}%{_datarootdir}/crypto-policies/back-ends/$d/$(basename $f .txt).config
    done
done

for f in %{buildroot}%{_datarootdir}/crypto-policies/DEFAULT/* ; do
    ln -sf %{_datarootdir}/crypto-policies/DEFAULT/$(basename $f) %{buildroot}%{_sysconfdir}/crypto-policies/back-ends/$(basename $f .txt).config
done

%py_byte_compile %{__python3} %{buildroot}%{_datadir}/crypto-policies/python

%check
make ON_RHEL9=1 test %{?_smp_mflags}

%post -p <lua>
if not posix.access("%{_sysconfdir}/crypto-policies/config") then
    local policy = "DEFAULT"
    local cf = io.open("/proc/sys/crypto/fips_enabled", "r")
    if cf then
        if cf:read() == "1" then
            policy = "FIPS"
        end
        cf:close()
    end
    cf = io.open("%{_sysconfdir}/crypto-policies/config", "w")
    if cf then
        cf:write(policy.."\n")
        cf:close()
    end
    cf = io.open("%{_sysconfdir}/crypto-policies/state/current", "w")
    if cf then
        cf:write(policy.."\n")
        cf:close()
    end
    local policypath = "%{_datarootdir}/crypto-policies/"..policy
    for fn in posix.files(policypath) do
        if fn ~= "." and fn ~= ".." then
            local backend = fn:gsub(".*/", ""):gsub("%%..*", "")
            local cfgfn = "%{_sysconfdir}/crypto-policies/back-ends/"..backend..".config"
            posix.unlink(cfgfn)
            posix.symlink(policypath.."/"..fn, cfgfn)
        end
    end
end

%posttrans scripts
%{_bindir}/update-crypto-policies --no-check >/dev/null 2>/dev/null || :


%files

%dir %{_sysconfdir}/crypto-policies/
%dir %{_sysconfdir}/crypto-policies/back-ends/
%dir %{_sysconfdir}/crypto-policies/state/
%dir %{_sysconfdir}/crypto-policies/local.d/
%dir %{_sysconfdir}/crypto-policies/policies/
%dir %{_sysconfdir}/crypto-policies/policies/modules/
%dir %{_datarootdir}/crypto-policies/

%ghost %config(missingok,noreplace) %{_sysconfdir}/crypto-policies/config

%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/gnutls.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/openssl.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/opensslcnf.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/openssh.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/opensshserver.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/nss.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/bind.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/java.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/javasystem.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/krb5.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/libreswan.config
%ghost %config(missingok,noreplace) %verify(not mode) %{_sysconfdir}/crypto-policies/back-ends/libssh.config
# %verify(not mode) comes from the fact
# these turn into symlinks and back to regular files at will, see bz1898986

%ghost %{_sysconfdir}/crypto-policies/state/current
%ghost %{_sysconfdir}/crypto-policies/state/CURRENT.pol

%{_mandir}/man7/crypto-policies.7*
%{_datarootdir}/crypto-policies/LEGACY
%{_datarootdir}/crypto-policies/DEFAULT
%{_datarootdir}/crypto-policies/FUTURE
%{_datarootdir}/crypto-policies/FIPS
%{_datarootdir}/crypto-policies/back-ends
%{_datarootdir}/crypto-policies/default-config
%{_datarootdir}/crypto-policies/reload-cmds.sh
%{_datarootdir}/crypto-policies/policies

%license COPYING.LESSER

%files scripts
%{_bindir}/update-crypto-policies
%{_mandir}/man8/update-crypto-policies.8*
%{_datarootdir}/crypto-policies/python

%{_bindir}/fips-mode-setup
%{_bindir}/fips-finish-install
%{_mandir}/man8/fips-mode-setup.8*
%{_mandir}/man8/fips-finish-install.8*

%changelog
* Mon Aug 15 2022 Alexander Sosedkin <asosedkin@redhat.com> - 20220815-1.git0fbe86f
- openssh: add RSAMinSize option following min_rsa_size

* Wed Apr 27 2022 Alexander Sosedkin <asosedkin@redhat.com> - 20220427-1.gitb2323a1
- bind: control ED25519/ED448

* Mon Apr 04 2022 Alexander Sosedkin <asosedkin@redhat.com> - 20220404-1.git845c0c1
- DEFAULT: drop DNSSEC SHA-1 exception
- openssh: add support for sntrup761x25519-sha512@openssh.com

* Wed Feb 23 2022 Alexander Sosedkin <asosedkin@redhat.com> - 20220223-1.git5203b41
- openssl: allow SHA-1 signatures with rh-allow-sha1-signatures in LEGACY
- update AD-SUPPORT, move RC4 enctype enabling to AD-SUPPORT-LEGACY
- fips-mode-setup: catch more inconsistencies, clarify --check

* Thu Feb 03 2022 Alexander Sosedkin <asosedkin@redhat.com> - 20220203-1.gitf03e75e
- gnutls: enable SHAKE, needed for Ed448
- fips-mode-setup: improve handling FIPS plus subpolicies
- FIPS: disable SHA-1 HMAC
- FIPS: disable CBC ciphers except in Kerberos

* Tue Feb 01 2022 Alexander Sosedkin <asosedkin@redhat.com> - 20220201-1.git636a91d
- openssl: revert to SECLEVEL=2 in LEGACY
- openssl: add newlines at the end of the output

* Mon Nov 15 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20211115-1.git70de135
- OSPP: relax -ECDSA-SHA2-512, -FFDHE-*
- fips-mode-setup, fips-finish-install: call zipl more often (s390x-specific)

* Wed Sep 22 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210922-1.git6fb269b
- openssl: fix disabling ChaCha20
- update for pylint 2.11

* Tue Sep 14 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210914-1.git97d08ef
- gnutls: reorder ECDSA-SECPMMMR1-SHANNN together with ECDSA-SHANNN
- fix several issues with update-crypto-policies --check

* Mon Aug 09 2021 Mohan Boddu <mboddu@redhat.com> - 20210707-2.git29f6c0b
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Wed Jul 07 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210707-1.git29f6c0b
- gnutls: explicitly enable ECDSA-SECPNNNR1-SHANNN
- packaging: adapt to the RHEL-9 %check-time testing tools availability

* Mon Jun 28 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210628-1.gitdd7d273
- implement scoped policies, e.g., cipher@SSH = ...
- implement algorithm globbing, e.g., cipher@SSH = -*-CBC
- deprecate derived properties:
  tls_cipher, ssh_cipher, ssh_group, ike_protocol, sha1_in_dnssec
- deprecate unscoped form of protocol property
- openssl: set MinProtocol / MaxProtocol separately for TLS and DTLS
- openssh: use PubkeyAcceptedAlgorithms instead of PubkeyAcceptedKeyTypes
- libssh: respect ssh_certs
- restrict FIPS:OSPP further
- improve Python 3.10 compatibility
- update documentation
- expand upstream test coverage
- FUTURE: disable CBC ciphers for all backends but krb5
- openssl: LEGACY must have SECLEVEL=1, enabling SHA1
- disable DHE-DSS in LEGACY
- bump LEGACY key size requirements from 1023 to 1024
- add javasystem backend
- *ssh: condition ecdh-sha2-nistp384 on SECP384R1
- set %verify(not mode) for backend sometimes-symlinks-sometimes-not
- gnutls: use allowlisting

* Tue Jun 22 2021 Mohan Boddu <mboddu@redhat.com> - 20210218-3.git2246c55
- Rebuilt for RHEL 9 BETA for openssl 3.0
  Related: rhbz#1971065

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 20210218-2.git2246c55
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Thu Feb 18 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210218-1.git2246c55
- require 2048 bit params in LEGACY
- require TLSv1.2/DTLSv1.2 in all policies
- disable DSA
- disable 3DES in LEGACY
- drop FFDHE-1024 from LEGACY
- drop (sub)policies we're not going to offer in RHEL-9

* Sat Feb 13 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210213-1.git5c710c0
- exclude RC4 from LEGACY
- introduce rc4_md5_in_krb5 to narrow AD_SUPPORT's impact
- an assortment of small fixes

* Wed Jan 27 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210127-2.gitb21c811
- fix comparison in %post lua scriptlet

* Wed Jan 27 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210127-1.gitb21c811
- don't create /etc/crypto-policies/back-ends/.config in %post

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 20210118-2.gitb21c811
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Mon Jan 18 2021 Alexander Sosedkin <asosedkin@redhat.com> - 20210118-1.gitb21c811
- output sigalgs required by nss >=3.59 (or 3.60 in Fedora case)
- bump Python requirement to 3.6

* Tue Dec 15 2020 Alexander Sosedkin <asosedkin@redhat.com> - 20201215-1.giteb57e00
- Kerberos 5: Fix policy generator to account for macs

* Tue Dec 08 2020 Alexander Sosedkin <asosedkin@redhat.com> - 20201208-1.git70def9f
- add AES-192 support (non-TLS scenarios)
- add documentation of the --check option

* Wed Sep 23 2020 Tomáš Mráz <tmraz@redhat.com> - 20200918-1.git85dccc5
- add RSA-PSK algorithm support
- add GOST algorithms support for openssl
- add GOST-ONLY policy and fix GOST subpolicy
- update-crypto-policies: added --check parameter to perform
  comparison of actual configuration files with the policy

* Thu Aug 13 2020 Tomáš Mráz <tmraz@redhat.com> - 20200813-1.git66d4068
- libreswan: enable X25519 group
- libreswan: properly disable FFDH in ECDHE-ONLY subpolicy
- libreswan: add generation of authby parameter based on sign property
- libssh: Add diffie-hellman-group14-sha256

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20200702-2.gitc40cede
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Mon Jul 13 2020 Tomáš Mráz <tmraz@redhat.com> - 20200702-1.gitc40cede
- OSPP subpolicy: remove AES-CCM
- openssl: handle the AES-CCM removal properly
- openssh/libssh: drop CBC ciphersuites from DEFAULT and FIPS
- add AD-SUPPORT subpolicy which re-enables RC4 for Kerberos
- gnutls: disallow X448/ED448 in FIPS policy
- merge fips-mode-setup package into the scripts subpackage

* Thu Jun 25 2020 Tomáš Mráz <tmraz@redhat.com> - 20200625-1.gitb298a9e
- DEFAULT policy: Drop DH < 2048 bits, TLS 1.0, 1.1, SHA-1
- make the NEXT policy just an alias for DEFAULT as they are now identical
- policies: introduce sha1_in_dnssec value for BIND
- add SHA1 and FEDORA32 policy modules to provide backwards compatibility
  they can be applied as DEFAULT:SHA1 or DEFAULT:FEDORA32
- avoid duplicates of list items in resulting policy

* Wed Jun 24 2020 Tomáš Mráz <tmraz@redhat.com> - 20200619-1.git781bbd4
- gnutls: enable DSA signatures in LEGACY

* Wed Jun 10 2020 Tomáš Mráz <tmraz@redhat.com> - 20200610-1.git7f9d474
- openssh server: new format of configuration to be loaded by config include
- fallback to FIPS policy instead of the default-config in FIPS mode
- java: Document properly how to override the crypto policy
- reorder the signature algorithms to follow the order in default openssl list

* Tue Jun  9 2020 Tomáš Mráz <tmraz@redhat.com> - 20200527-5.gitb234a47
- make the post script work in environments where /proc/sys is not available

* Fri May 29 2020 Tomáš Mráz <tmraz@redhat.com> - 20200527-4.gitb234a47
- move the symlink fix-up script to post and fix it

* Fri May 29 2020 Tomáš Mráz <tmraz@redhat.com> - 20200527-3.gitb234a47
- automatically set up FIPS policy in FIPS mode on first install

* Thu May 28 2020 Tomáš Mráz <tmraz@redhat.com> - 20200527-2.gitb234a47
- require the base package from scripts subpackage
- add Recommends for fips-mode-setup to the scripts subpackage

* Wed May 27 2020 Tomáš Mráz <tmraz@redhat.com> - 20200527-1.gitb234a47
- explicitly enable DHE-DSS in gnutls config if enabled in policy
- use grubby with --update-kernel=ALL to avoid breaking kernelopts
- OSPP subpolicy: Allow GCM for SSH protocol
- openssh: Support newly standardized ECDHE-GSS and DHE-GSS key exchanges
- if the policy in FIPS mode is not a FIPS policy print a message
- openssl: Add SignatureAlgorithms support

* Thu Mar 12 2020 Tomáš Mráz <tmraz@redhat.com> - 20200312-1.git3ae59d2
- custom crypto policies: enable completely overriding contents of the list
  value
- added ECDHE-ONLY.pmod policy module example
- openssh: make LEGACY policy to prefer strong public key algorithms
- openssh: support FIDO/U2F (with the exception of FIPS policy)
- gnutls: add support for GOST ciphers
- various python code cleanups
- update-crypto-policies: dump the current policy to
  /etc/crypto-policies/state/CURRENT.pol

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 20191128-5.gitcd267a5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Tue Jan 14 2020 Tomáš Mráz <tmraz@redhat.com> - 20191128-4.gitcd267a5
- the base package must ship the DEFAULT policy config symlinks in case
  the scripts package is not installed via the weak dependency

* Tue Jan 07 2020 Andrew Jeddeloh <ajeddelo@redhat.com> 20191128-3.gitcd267a5
- split scripts into their own subpackage. See
  https://github.com/coreos/fedora-coreos-tracker/issues/280 for more details.

* Mon Dec 16 2019 Tomáš Mráz <tmraz@redhat.com> - 20191128-2.gitcd267a5
- move the pre-built .config files to /usr/share/crypto-policies/back-ends

* Thu Nov 28 2019 Tomáš Mráz <tmraz@redhat.com> - 20191128-1.gitcd267a5
- add FIPS subpolicy for OSPP
- fips-mode-setup: do not reload daemons when changing policy
- fips-mode-setup: gracefully handle OSTree-based systems
- gnutls: use new configuration file format

* Tue Oct 29 2019 Tomáš Mráz <tmraz@redhat.com> - 20191002-1.gitc93dc99
- update-crypto-policies: fix handling of list operations in policy modules
- update-crypto-policies: fix updating of the current policy marker
- fips-mode-setup: fixes related to containers and non-root execution

* Tue Sep 24 2019 Tomáš Mráz <tmraz@redhat.com> - 20190816-4.gitbb9bf99
- add the /etc/crypto-policies/state directory

* Tue Sep 10 2019 Tomáš Mráz <tmraz@redhat.com> - 20190816-3.gitbb9bf99
- make it possible to use fips-mode-setup --check without dracut
- add .config symlinks so a crypto policy can be set with read-only
  /etc by bind-mounting /usr/share/crypto-policies/<policy> to
  /etc/crypto-policies/back-ends

* Mon Aug 19 2019 Tomáš Mráz <tmraz@redhat.com> - 20190816-2.gitbb9bf99
- run the update-crypto-policies in posttrans
- the current config should work fine with OpenSSL >= 7.9p1
- fix the python bytecompilation

* Fri Aug 16 2019 Tomáš Mráz <tmraz@redhat.com> - 20190816-1.gitbb9bf99
- custom crypto policies support
- openssh: Support new configuration option CASignatureAlgorithms
- libssh: Add libssh as supported backend
- multiple fixes in fips-mode-setup, BLS support

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 20190527-2.git0b3add8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon May 27 2019 Tomáš Mráz <tmraz@redhat.com> - 20190211-1.git0b3add8
- libreswan: coalesce proposals to avoid IKE packet fragmentation
- openssh: add missing curve25519-sha256 to the key exchange list
- nss: map X25519 to CURVE25519

* Thu Apr 25 2019 Tomáš Mráz <tmraz@redhat.com> - 20190211-4.gite3eacfc
- do not fail in the Java test if the EMPTY policy is not really empty

* Thu Mar  7 2019 Zbigniew Jędrzejewski-Szmek <zbyszek@in.waw.pl> - 20190211-3.gite3eacfc
- Split out fips-mode-setup into separate subpackage

* Mon Feb 11 2019 Tomáš Mráz <tmraz@redhat.com> - 20190211-2.gite3eacfc
- add crypto-policies.7 manual page
- Java: Fix FIPS and FUTURE policy to allow RSA certificates in TLS
- cleanup duplicate and incorrect information from update-crypto-policies.8
  manual page
- update-crypto-policies: Fix endless loop
- update-crypto-policies: Add warning about the need of system restart
- FUTURE: Add mistakenly ommitted EDDSA-ED25519 signature algorithm
- openssh: Add missing SHA2 variants of RSA certificates to the policy
- return exit code 2 when printing usage from all the tools
- update-crypto-policies: add --no-reload option for testing

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 20181122-2.git70769d9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Nov 22 2018 Tomáš Mráz <tmraz@redhat.com> - 20181122-1.git70769d9
- update-crypto-policies: fix error on multiple matches in local.d

* Tue Nov 20 2018 Tomáš Mráz <tmraz@redhat.com> - 20181120-1.gitd2b3bc4
- Print warning when update-crypto-policies --set is used in the FIPS mode
- Java: Add 3DES and RC4 to legacy algorithms in LEGACY policy
- OpenSSL: Properly disable non AEAD and AES128 ciphersuites in FUTURE
- libreswan: Add chacha20_poly1305 to all policies and drop ikev1 from LEGACY

* Fri Oct 26 2018 Tomáš Mráz <tmraz@redhat.com> - 20181026-1.gitd42aaa6
- Fix regression in discovery of additional configuration
- NSS: add DSA keyword to LEGACY policy
- GnuTLS: Add 3DES and RC4 to LEGACY policy

* Tue Sep 25 2018 Tomáš Mráz <tmraz@redhat.com> - 20180925-1.git71ca85f
- Use Recommends instead of Requires for grubby
- Revert setting of HostKeyAlgorithms for ssh client for now

* Fri Sep 21 2018 Tomáš Mráz <tmraz@redhat.com> - 20180921-2.git391ed9f
- Fix requires for grubby

* Fri Sep 21 2018 Tomáš Mráz <tmraz@redhat.com> - 20180921-1.git391ed9f
- OpenSSH: Generate policy for sign algorithms
- Enable >= 255 bits EC curves in FUTURE policy
- OpenSSH: Add group1 key exchanges in LEGACY policy
- NSS: Add SHA224 to hash lists
- Print warning when update-crypto-policies --set FIPS is used
- fips-mode-setup: Kernel boot options are now modified with grubby

* Thu Aug  2 2018 Tomáš Mráz <tmraz@redhat.com> - 20180802-1.git1626592
- Introduce NEXT policy

* Mon Jul 30 2018 Tomáš Mráz <tmraz@redhat.com> - 20180730-1.git9d9f21d
- Add OpenSSL configuration file include support

* Tue Jul 24 2018 Tomáš Mráz <tmraz@redhat.com> - 20180723-1.gitdb825c0
- Initial FIPS mode setup support
- NSS: Add tests for the generated policy
- Enable TLS-1.3 if available in the respective TLS library
- Enable SHA1 in certificates in LEGACY policy
- Disable CAMELLIA
- libreswan: Multiple bug fixes in policies

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 20180425-6.git6ad4018
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri May 18 2018 Björn Esser <besser82@fedoraproject.org> - 20180425-5.git6ad4018
- Fix patch0

* Fri May 18 2018 Björn Esser <besser82@fedoraproject.org> - 20180425-4.git6ad4018
- Remove Requires: systemd
- Add Patch to silence warnings from reload-cmds

* Thu May 17 2018 Björn Esser <besser82@fedoraproject.org> - 20180425-3.git6ad4018
- Requires: systemd should be added too

* Thu May 17 2018 Björn Esser <besser82@fedoraproject.org> - 20180425-2.git6ad4018
- Add Requires(post): systemd to fix:
  crypto-policies/reload-cmds.sh: line 1: systemctl: command not found

* Wed Apr 25 2018 Tomáš Mráz <tmraz@redhat.com> - 20180425-1.git6ad4018
- Restart/reload only enabled services
- Do not enable PSK ciphersuites by default in gnutls and openssl
- krb5: fix when more than 2048 bits keys are required
- Fix discovery of additional configurations #1564595
- Fix incorrect ciphersuite setup for libreswan

* Tue Mar  6 2018 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20180306-1.gitaea6928
- Updated policy to reduce DH parameter size on DEFAULT level, taking into
  account feedback in #1549242,1#534532.
- Renamed openssh-server.config to opensshserver.config to reduce conflicts
  when local.d/ appending is used.

* Tue Feb 27 2018 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20180227-1.git0ce1729
- Updated to include policies for libreswan

* Mon Feb 12 2018 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20180112-1.git386e3fe
- Updated to apply the settings as in StrongCryptoSettings project. The restriction
  to TLS1.2, is not yet applied as we have no method to impose that in openssl.
  https://fedoraproject.org/wiki/Changes/StrongCryptoSettings

* Fri Feb 09 2018 Igor Gnatenko <ignatenkobrain@fedoraproject.org> - 20171115-3.git921600e
- Escape macros in %%changelog

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 20171115-2.git921600e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Nov 15 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20171115-1.git921600e
- Updated openssh policies for new openssh without rc4
- Removed policies for compat-gnutls28

* Wed Aug 23 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20170823-1.git8d18c27
- Updated gnutls policies for 3.6.0

* Wed Aug 16 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20170816-1.git2618a6c
- Updated to latest upstream
- Restarts openssh server on policy update

* Wed Aug  2 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20170802-1.git9300620
- Updated to latest upstream
- Reloads openssh server on policy update

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20170606-4.git7c32281
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 25 2017 Igor Gnatenko <ignatenko@redhat.com> - 20170606-3.git7c32281
- Restore Requires(post)

* Mon Jul 24 2017 Troy Dawson <tdawson@redhat.com> 20170606-2.git7c32281
- perl dependency renamed to perl-interpreter <ppisar@redhat.com>
- remove useless Requires(post) <ignatenko@redhat.com>
- Fix path of libdir in generate-policies.pl (#1474442) <tdawson@redhat.com>

* Tue Jun  6 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20170606-1.git7c32281
- Updated to latest upstream
- Allows gnutls applications in LEGACY mode, to use certificates of 768-bits

* Wed May 31 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20170531-1.gitce0df7b
- Updated to latest upstream
- Added new kerberos key types

* Sat Apr 01 2017 Björn Esser <besser82@fedoraproject.org> - 20170330-3.git55b66da
- Add Requires for update-crypto-policies in %%post

* Fri Mar 31 2017 Petr Šabata <contyk@redhat.com> - 20170330-2.git55b66da
- update-crypto-policies uses gred and sed, require them

* Thu Mar 30 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20170330-1-git55b66da
- GnuTLS policies include RC4 in legacy mode (#1437213)

* Fri Feb 17 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160214-2-gitf3018dd
- Added openssh file

* Tue Feb 14 2017 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160214-1-gitf3018dd
- Updated policies for BIND to address #1421875

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 20161111-2.gita2363ce
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Fri Nov 11 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20161111-1-gita2363ce
- Include OpenJDK documentation.

* Tue Sep 27 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160926-2-git08b5501
- Improved messages on error.

* Mon Sep 26 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160926-1-git08b5501
- Added support for openssh client policy

* Wed Sep 21 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160921-1-git75b9b04
- Updated with latest upstream.

* Thu Jul 21 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160718-2-gitdb5ca59
- Added support for administrator overrides in generated policies in local.d

* Thu Jul 21 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160718-1-git340cb69
- Fixed NSS policy generation to include allowed hash algorithms

* Wed Jul 20 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160718-1-gitcaa4a8d
- Updated to new version with auto-generated policies

* Mon May 16 2016 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20160516-1-git8f69c35
- Generate policies for NSS
- OpenJDK policies were updated for opendjk 8

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 20151104-2.gitf1cba5f
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Nov  4 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20151104-1-gitcf1cba5f
- Generate policies for compat-gnutls28 (#1277790)

* Fri Oct 23 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20151005-2-gitc8452f8
- Generated files are put in a %%ghost directive

* Mon Oct  5 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20151005-1-gitc8452f8
- Updated policies from upstream
- Added support for the generation of libkrb5 policy
- Added support for the generation of openjdk policy

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 20150518-2.gitffe885e
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon May 18 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20150518-1-gitffe885e
- Updated policies to remove SSL 3.0 and RC4 (#1220679)

* Fri Mar  6 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20150305-3-git2eeb03b
- Added make check

* Fri Mar  6 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20150305-2-git44afaa1
- Removed support for SECLEVEL (#1199274)

* Thu Mar  5 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20150305-1-git098a8a6
- Include AEAD ciphersuites in gnutls (#1198979)

* Sun Jan 25 2015 Peter Robinson <pbrobinson@fedoraproject.org> 20150115-3-git9ef7493
- Bump release so lastest git snapshot is newer NVR

* Thu Jan 15 2015 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20150115-2-git9ef7493
- Updated to newest upstream version.
- Includes bind policies (#1179925)

* Tue Dec 16 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20141124-2-gitd4aa178
- Corrected typo in gnutls' future policy (#1173886)

* Mon Nov 24 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20141124-1-gitd4aa178
- re-enable SSL 3.0 (until its removal is coordinated with a Fedora change request)

* Thu Nov 20 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20141120-1-git9a26a5b
- disable SSL 3.0 (doesn't work in openssl)

* Fri Sep 05 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20140905-1-git4649b7d
- enforce the acceptable TLS versions in openssl

* Wed Aug 27 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20140827-1-git4e06f1d
- fix issue with RC4 being disabled in DEFAULT settings for openssl

* Thu Aug 14 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20140814-1-git80e1e98
- fix issue in post script run on upgrade (#1130074)

* Tue Aug 12 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20140812-1-gitb914bfd
- updated crypto-policies from repository

* Fri Jul 11 2014 Tom Callaway <spot@fedoraproject.org> - 20140708-2-git3a7ae3f
- fix license handling

* Tue Jul 08 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20140708-1-git3a7ae3f
- updated crypto-policies from repository

* Fri Jun 20 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 20140620-1-gitdac1524
- updated crypto-policies from repository
- changed versioning

* Thu Jun 12 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-7-20140612gita2fa0c6
- updated crypto-policies from repository

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.9-7.20140522gita50bad2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Thu May 29 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-6-20140522gita50bad2
- Require(post) coreutils (#1100335).

* Tue May 27 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-5-20140522gita50bad2
- Require coreutils.

* Thu May 22 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-4-20140522gita50bad2
- Install the default configuration file.

* Wed May 21 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-3-20140520git81364e4
- Run update-crypto-policies after installation.

* Tue May 20 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-2-20140520git81364e4
- Updated spec based on comments by Petr Lautrbach.

* Mon May 19 2014 Nikos Mavrogiannopoulos <nmav@redhat.com> - 0.9-1-20140519gitf15621a
- Initial package build

