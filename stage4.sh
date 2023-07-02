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

pkg_sucs=0
pkg_fail=0
for pkg in $(python ${SCRIPT_DIR}/get_buildable_packages.py); do
    if mock --rebuild $pkg; then
        for file in $(find ${MOCK_RESULT_DIR} -name "*rpm" -a -not -name "*src.rpm"); do
            cp -av "$file" "$STAGE4_REPO_DIR"
        done
        createrepo "$STAGE4_REPO_DIR"
	let "pkg_sucs++"
	echo "$pkg_sucs packages completed successfully"
    else
        let "pkg_fail++"
	echo "Building package $pkg failed; continuing"
    fi
    echo "$pkg_sucs successes, $pkg_fail failures so far"
done
