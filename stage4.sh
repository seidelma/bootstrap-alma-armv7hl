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
if [ -f "$STAGE4_PACKAGESRCFILE" ]; then
    . "$STAGE4_PACKAGESRCFILE"
else
    echo "The package config file $STAGE4_PACKAGESRCFILE was not found; exiting"
    exit 1
fi

if [ ! -f /.in_chroot ]; then
    echo "Error: this script must be run from within the chroot environment. Do a:"
    echo "    sudo chroot ${INSTALL_DIR} /bin/bash"
    echo "And then rerun it"
    exit 1
fi

STAGE_SPECFILE_DIR="${SCRIPT_DIR}/stage4/SPECS"

pkg_sucs=0
pkg_fail=0
for pkg in $(python ${SCRIPT_DIR}/get_buildable_packages.py); do
    mock_build_opts="--additional-package=pyproject-rpm-macros"
    if mock_build "$pkg"; then
        createrepo "$STAGE4_REPO_DIR"
        let "pkg_sucs=$pkg_sucs+1"
        echo "$pkg_sucs packages completed successfully"
    else
        let "pkg_fail=$pkg_fail+1"
        echo "Building package $pkg failed; continuing"
    fi
    echo "$pkg_sucs successes, $pkg_fail failures so far"
done
