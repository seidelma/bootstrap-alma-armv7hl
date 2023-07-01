#!/usr/bin/bash
set +h -exuo pipefail
# Install/configure Raspberry Pi OS (ie, Debian) prerequisites

sudo apt install build-essential tmux bison flex m4 autoconf automake make libtool rsync rpm python3-dev gawk autopoint openjdk-11-jdk texinfo

[ -f ~/.rpmmacros ] && cp ~/.rpmmacros{,.orig}
cat > ~/.rpmmacros << EOF
%_buildshell    /usr/bin/bash
%gpgverify      /usr/bin/true
%__isa_bits	32
%rhel		9

%python_wheel_pkg_prefix	python3
EOF

if grep -q aarch64 /proc/sys/kernel/arch; then
    echo "WARNING: you are running a 64-bit kernel."
    echo "This will cause GCC compilation to fail with:"
    echo "  undefined reference to `host_detect_local_cpu(int, char const**)'"
    echo ""
    echo "Use a 32-bit kernel (on RPi 3/4 set arm_64bit=0 in /boot/config.txt)"
    echo "and reboot to continue safely."
fi
