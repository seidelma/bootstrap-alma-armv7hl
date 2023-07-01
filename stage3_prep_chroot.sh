#!/bin/bash
set +h -exuo pipefail

SCRIPT_DIR=$(readlink -f $(dirname "$0"))

CONFIGRCFILE="${SCRIPT_DIR:?}/common.rc"
if [[ ! -f /.in_chroot || $(id -u) -ne 0 ]]; then
    echo "This script should be run as root from the chroot, like"
    echo "    sudo chroot <chroot-dir> <$0>"
    exit 1
fi

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

# Mount the SRPM directory read-only for safety
[ -d "$SRPM_REPO_MPOINT" ] || mkdir -pv "$SRPM_REPO_MPOINT"
if mountpoint -q "${SRPM_REPO_MPOINT}"; then
    mount -o remount,ro "${SRPM_REPO_MPOINT}"
else
    mount -o ro "$SRPM_REPO_FSLABEL" "$SRPM_REPO_MPOINT"
fi
[ -d "$SRPM_REPO_DIR" ] || mkdir -pv "$SRPM_REPO_DIR"

# Mount the stage3 rpm directory read-write
[ -d "$STAGE3_REPO_MPOINT" ] || mkdir -pv "$STAGE3_REPO_MPOINT"
if mountpoint -q "${STAGE3_REPO_MPOINT}"; then
    echo -n ""
else
    mount "$STAGE3_REPO_FSLABEL" "$STAGE3_REPO_MPOINT"
fi
[ -d "$STAGE3_REPO_DIR" ] || mkdir -pv "$STAGE3_REPO_DIR"
