#!/bin/bash
set +h -exuo pipefail

if [[ $(id -u) != "0" || ! -f /.in_chroot ]]; then
	echo "This script must be run as root within the chroot environment. Do a:"
        echo "    sudo chroot ${INSTALL_DIR} /bin/bash"
        echo "and then rerun it."
	exit 1
fi

SCRIPT_DIR=$(readlink -f $(dirname "$0"))
CONFIGRCFILE="${SCRIPT_DIR}/common.rc"
if [ -f "$CONFIGRCFILE" ]; then
        . "$CONFIGRCFILE"
else
        echo "The script config file $CONFIGRCFILE was not found, exiting"
        exit 1
fi
if [ -f "$STAGE12_PACKAGESRCFILE" ]; then
    . "$STAGE12_PACKAGESRCFILE"
else
    echo "The package config file $PACKAGESRCFILE was not found; exiting"
    exit 1
fi

# Shut up Perl
export LC_ALL=POSIX

PATH=/usr/bin:/usr/sbin

for pkg in "${STAGE2_PACKAGES[@]}"
do
	get_package_name
	set_package_vars
	do_build
done

echo "Stage 2 completed successfully"
