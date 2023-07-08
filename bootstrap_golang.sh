#!/bin/bash
set +h -exuo pipefail

SCRIPT_DIR=$(readlink -f $(dirname "$0"))

CONFIGRCFILE="${SCRIPT_DIR:?}/common.rc"
if [ -f "$CONFIGRCFILE" ]; then
        . "$CONFIGRCFILE"
else
        echo "The script config file $CONFIGRCFILE was not found, exiting"
        exit 1
fi
if [ -f "$STAGE3_PACKAGESRCFILE" ]; then
    . "$STAGE3_PACKAGESRCFILE"
else
    echo "The package config file $STAGE3_PACKAGESRCFILE was not found; exiting"
    exit 1
fi

if [ ! -f /.in_chroot ]; then
	echo "Error: this script must be run from within the chroot environment. Do a:"
	echo "    sudo chroot ${INSTALL_DIR} /bin/bash"
	echo "And then rerun it"
	exit 1
fi

# Some script-specific stuff:
# - install bootstrap builds to a temporary directory
# - use that temporary directory over the system install locations
#    until we've got the packages built
# - use ccache to speed up compilation
INSTALL_PREFIX="/p3"
OLDPATH=$PATH
OLDLDPATH=${LD_LIBRARY_PATH:-}
PATH="${INSTALL_PREFIX}/bin:$PATH"
LD_LIBRARY_PATH="${INSTALL_PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export PATH LD_LIBRARY_PATH
CC="ccache gcc"
CXX="ccache g++"
export CC CXX

SRC_DIR="${RPMBUILD_TOPDIR}/BUILD"

GOLANG_VERSION='1.18.4'
GOLANG_TARBALL="go${GOLANG_VERSION}.linux-armv6l.tar.gz"
GOLANG_URL="https://go.dev/dl/${GOLANG_TARBALL}"
GOLANG_CHECKSUM="7dfeab572e49638b0f3d9901457f0622c27b73301c2b99db9f5e9568ff40460c  $GOLANG_TARBALL"
GOLANG_RPMBUILD='rpmbuild -bb --undefine '%_annotated_build' --undefine '%_annobin_gcc_plugin' --nodebuginfo --clean --nocheck'
GOLANG_PRE_RPMBUILD_CMD='sed -i -e $'\'s:GOROOT_BOOTSTRAP=.*:GOROOT_BOOTSTRAP=${INSTALL_PREFIX}/go:g\'' ${RPMBUILD_TOPDIR}/SPECS/golang.spec'
GOLANG_INSTALL_PKGS="golang*"

mkdir -p "${INSTALL_PREFIX}"
pushd "$INSTALL_PREFIX" || exit 1
curl -L -O "$GOLANG_URL"

echo "$GOLANG_CHECKSUM" | sha256sum -c
if [ $? -ne 0 ]; then
	echo "Go $GOLANG_VERSION tarball failed checksum"
	exit 1
fi

tar xzf $GOLANG_TARBALL

GOLANG_VERSION='1.18.4'
GOLANG_RPMBUILD='rpmbuild -bb --undefine '%_annotated_build' --undefine '%_annobin_gcc_plugin' --nodebuginfo --clean --nocheck'
GOLANG_PRE_RPMBUILD_CMD='sed -i -e $'\'s:GOROOT_BOOTSTRAP=.*:GOROOT_BOOTSTRAP=${INSTALL_PREFIX}/go:g\'' ${RPMBUILD_TOPDIR}/SPECS/golang.spec'
GOLANG_INSTALL_PKGS="golang*"

for pkg in "GOLANG"
do
	get_package_name
	set_package_vars
	do_rpmbuild_and_install ${pkgname_lower}-${pkg_version} ${pkgname_lower}.spec	
done
