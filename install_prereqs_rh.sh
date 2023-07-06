#!/bin/bash
set +h -exuo pipefail

# Handle CentOS/Fedora prerequisites
yum -y install gcc-c++ git python3-devel bison flex m4 autoconf automake make rpm-build texinfo help2man gettext-devel libtool rsync tmux
