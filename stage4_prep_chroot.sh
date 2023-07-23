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

# Create a repository from the stage3 packages we built
mount -o remount,rw "$STAGE3_REPO_MPOINT"
createrepo "$STAGE3_REPO_DIR"

cp -av "$CHROOT_SCRIPT_DIR"/stage4/etc/mock/* /etc/mock
ln -sf /etc/mock/almalinux-9-armv7hl.cfg /etc/mock/default.cfg

# Remove distribution GPG keys from the chroot
# Mock tries to copy its contents to its build env
# We're not ready to sign anything, and it slows Mock down considerably
rm -rf /usr/share/distribition-gpg-keys/*

# Remount the stage3 repo mountpoint read-only for safety
mount -o remount,ro "$STAGE3_REPO_MPOINT"

# Mount the stage4 repo and create an empty repo in it
[ ! -d "$STAGE4_REPO_MPOINT" ] && mkdir -pv "$STAGE4_REPO_MPOINT"
if mountpoint -q "$STAGE4_REPO_MPOINT"; then 
	echo -n ""
else
	mount "$STAGE4_REPO_FSLABEL" "$STAGE4_REPO_MPOINT"
fi
[ ! -d "$STAGE4_REPO_DIR" ] && mkdir -pv "$STAGE4_REPO_DIR"
createrepo "$STAGE4_REPO_DIR"

# Rebuild RPM macros packages because they are turned off
# in stage3 redhat-rpm-config. If that is built before any
# of these it causes all subsequent builds to fail
for pkg in "${SRPM_REPO_DIR}"/{efi,epel,fonts,ghc,go,kernel,lua,ocaml,openblas,perl,pyproject,python,R,rust}*rpm-macros*; do
    if mock_build "$pkg"; then
        echo "$pkg finished succesfully"
    else
        echo "$pkg failed"
    fi
done
createrepo "$STAGE4_REPO_DIR"

mount -o remount,rw "$SRPM_REPO_MPOINT"
for pkg in "$SRPM_REBUILD_PACKAGES"; do
    mock_rebuild_srpm_from_specfile "$pkg"
done
mount -o remount,ro "$SRPM_REPO_MPOINT"

