#!/bin/bash
set +h -exuo pipefail

if [ "$(id -u)" == "0" ]; then
        echo "This script is dangerous and must not be run as $(id -un); exiting"
        exit 1
fi

SCRIPT_DIR=$(readlink -f $(dirname "$0"))

CONFIGRCFILE="${SCRIPT_DIR:?}/common.rc"
if [ -f "$CONFIGRCFILE" ]; then
        . "$CONFIGRCFILE"
else
        echo "The script config file $CONFIGRCFILE was not found, exiting"
        exit 1
fi
if [ -f "$STAGE12_PACKAGESRCFILE" ]; then
    . "$STAGE12_PACKAGESRCFILE"
else
    echo "The package config file $STAGE12_PACKAGESRCFILE was not found; exiting"
    exit 1
fi

if [ ! -d "${INSTALL_DIR}/${CHROOT_SRC_DIR}" ]; then
       mkdir "${INSTALL_DIR}/${CHROOT_SRC_DIR}"
fi

for pkg in "${STAGE2_PACKAGES[@]}"
do
	get_package_name
	set_package_vars
	do_srpm_prep "${pkgname_lower}-${pkg_version}" "${pkgname_lower}".spec
	srcdir=$(eval "echo $pkg_src_dir")
	copy_source_to_chroot "$srcdir" "${INSTALL_DIR:?}/${CHROOT_SRC_DIR:?}"
done

cp -av "${SCRIPT_DIR}" "${INSTALL_DIR}${CHROOT_SCRIPT_DIR}"
