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

PATH=${INSTALL_DIR}/${PHASE1_TOOLS_DIR}/bin:$PATH

for pkg in ${STAGE1_PACKAGES[@]}
do
	get_package_name
	set_package_vars
	do_srpm_prep ${pkgname_lower}-${pkg_version} ${pkgname_lower}.spec
	do_build 
done

echo "Stage 1 completed successfully"
