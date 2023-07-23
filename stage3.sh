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
if [ -f "$STAGE3_PACKAGESRCFILE" ]; then
    . "$STAGE3_PACKAGESRCFILE"
else
    echo "The package config file $STAGE3_PACKAGESRCFILE was not found; exiting"
    exit 1
fi

# Shut up Perl
export LC_ALL=POSIX

PATH=/usr/bin:/usr/sbin

STAGE_SPECFILE_DIR="${SCRIPT_DIR}/stage3/SPECS"
STAGE_REPO_DIR="$STAGE3_REPO_DIR"

stage3_setup () {
	cp $SCRIPT_DIR/stage3/rpmmacros ~/.rpmmacros
	cat > /root/.bashrc << EOF
PS1="[chroot \w]# "

EOF
}	

stage3_setup

for pkg in "${STAGE3_PACKAGES[@]}" "${STAGE3_REBUILD_PACKAGES[@]}"
do
        get_package_name
        set_package_vars
	do_rpmbuild_and_install ${pkgname_lower}-${pkg_version} ${pkgname_lower}.spec
done

echo "Stage 3 completed successfully"
