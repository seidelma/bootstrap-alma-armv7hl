#!/bin/bash
set +h -exuo pipefail

if [ $(id -u) == "0" ]; then
	echo "This script is dangerous and must not be run as $(id -un); exiting"
	exit 1
fi

SCRIPT_DIR=$(readlink -f $(dirname $0))
CONFIGRCFILE="${SCRIPT_DIR}/common.rc"
if [ -f $CONFIGRCFILE ]; then
	. $CONFIGRCFILE
else
	echo "The script config file $CONFIGRCFILE was not found, exiting"
	exit 1
fi
if [ -f $STAGE12_PACKAGESRCFILE ]; then
    . $STAGE12_PACKAGESRCFILE
else
    echo "The package config file $STAGE12_PACKAGESRCFILE was not found; exiting"
    exit 1
fi

init_setup () {
	# Make sure we don't have anything mounted under the install target
	for mp in dev dev/pts proc run sys ${SRPM_REPO_MPOINT}; do
		if mountpoint -q "${INSTALL_DIR}/${mp}"; then
			echo "Error: ${INSTALL_DIR}/${mp} is mounted, umount it first!"
			exit 1
		fi
	done
	rm -rf $INSTALL_DIR/*

	mkdir -p $INSTALL_DIR/usr/bin
	mkdir -p $INSTALL_DIR/usr/sbin
	mkdir -p $INSTALL_DIR/usr/lib

	ln -s usr/bin $INSTALL_DIR/bin
	ln -s usr/sbin $INSTALL_DIR/sbin
	ln -s usr/lib $INSTALL_DIR/lib

	# Don't count on pathfix.py being present
	ln -s /usr/bin/true "${INSTALL_DIR}/usr/bin/pathfix.py"
}

# Of course the kernel just has to be difficult...I mean different
# If running on Fedora 34 leaving %{fedora} set breaks the build
install_kernel_headers () {
	rpm -ivh ${SRPM_REPO_DIR}/kernel-${KERNEL_HEADER_VERSION}*src.rpm
	# Use our fake pathfix.py
	PATH="${INSTALL_DIR}/usr/bin:$PATH" rpmbuild --undefine fedora \
	    --with headers         \
            -bp                    \
	    ${RPMBUILD_TOPDIR}/SPECS/kernel.spec
	# Unfortunately undefining %fedora makes the kernel dirname wonky
	kernel_topdir=$(ls -d $RPMBUILD_TOPDIR/BUILD/kernel-${KERNEL_HEADER_VERSION}*)
	kernel_srcdir=$(ls $kernel_topdir)
	pushd ${kernel_topdir}/${kernel_srcdir}
	make mrproper
	make headers_install INSTALL_HDR_PATH=${INSTALL_DIR}/usr
	popd
}

init_setup
install_kernel_headers kernel-${KERNEL_HEADER_VERSION} kernel.spec
