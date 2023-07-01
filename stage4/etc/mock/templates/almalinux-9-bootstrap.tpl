config_opts['chroot_setup_cmd'] = 'install bash bzip2 coreutils cpio diffutils redhat-release findutils gawk glibc-minimal-langpack grep gzip info patch redhat-rpm-config rpm-build sed shadow-utils tar unzip util-linux which xz'
config_opts['dist'] = 'el9.alma'  # only useful for --resultdir variable subst
config_opts['releasever'] = '9'
config_opts['package_manager'] = 'dnf'
config_opts['extra_chroot_dirs'] = [ '/run/lock', ]
config_opts['bootstrap_image'] = 'quay.io/almalinuxorg/almalinux:9'


config_opts['dnf.conf'] = """
[main]
keepcache=1
debuglevel=2
reposdir=/dev/null
logfile=/var/log/yum.log
retries=20
obsoletes=1
gpgcheck=0
assumeyes=1
syslog_ident=mock
syslog_device=
metadata_expire=0
mdpolicy=group:primary
best=1
install_weak_deps=0
protected_packages=
module_platform_id=platform:el9
user_agent={{ user_agent }}


[stage3]
name=AlmaLinux $releasever - Stage 3 bootstrap
# baseurl=https://repo.almalinux.org/almalinux/$releasever/BaseOS/$basearch/os/
baseurl=file:///mnt/alma/stage3/rpms
enabled=1
cost=999999
gpgcheck=0
gpgkey=file:///usr/share/distribution-gpg-keys/alma/RPM-GPG-KEY-AlmaLinux-9
fastestmirror=1
skip_if_unavailable=False

[stage4]
name=AlmaLinux $releasever - Mock Stage 4 bootstrap
baseurl=file:///mnt/alma/mock-stage4/rpms
enabled=1
cost=1
gpgcheck=0
gpgkey=file:///usr/share/distribution-gpg-keys/alma/RPM-GPG-KEY-AlmaLinux-9
fastestmirror=1

[source]
name=AlmaLinux $releasever - Source
baseurl=file:///mnt/alma/src/all
enabled=0
gpgcheck=1
gpgkey=file:///usr/share/distribution-gpg-keys/alma/RPM-GPG-KEY-AlmaLinux-9
fastestmirror=1
"""
