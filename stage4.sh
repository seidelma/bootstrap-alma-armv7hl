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
STAGE_REPO_DIR="$STAGE4_REPO_DIR"

pkg_sucs=()
pkg_fail=()
for pkg in $(python ${SCRIPT_DIR}/get_buildable_packages.py); do
    mock_build_opts="--additional-package=pyproject-rpm-macros"
    pkgfile="$(basename $pkg)"
    if mock_build "$pkg"; then
        createrepo "$STAGE_REPO_DIR"
        pkg_sucs+=($pkgfile)
        echo "Building package $pkgfile succeeded"
    else
        pkg_fail+=($pkgfile)
        echo "Building package $pkgfile failed; continuing"
    fi
    echo "${#pkg_sucs[@]} successes, ${#pkg_fail[@]} failures so far"
done

printf "%-40.40s\t%40.40s" "Succeeded Packages" "Failed Packages"
if [ "${#pkg_sucs[@]}" -ge "${#pkg_fail[@]}" ]; then
    j="${#pkg_fail[@]}"
    for i in "${!pkg_sucs[@]}"; do
        if [ "$i" -le "$j" ]; then
            printf "%-40.40s\t%40.40s" "${pkg_sucs[$i]}" "${pkg_fail[$i]}"
        else
            printf "%-40.40s" "${pkg_sucs[$i]}"
        fi
    done
else
    j="${#pkg_sucs[@]}"
    for i in "${!pkg_fail[@]}"; do
        if [ "$i" -le "$j" ]; then
            printf "%-40.40s\t%40.40s" "${pkg_sucs[$i]}" "${pkg_fail[$i]}"
        else
            printf "%-40.40s\t%40.40s" "" "${pkg_fail[$i]}"
        fi
    done
fi
