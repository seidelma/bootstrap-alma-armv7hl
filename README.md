# Arm32 Bootstrap Builder for AlmaLinux 9
These scripts are capable of bootstrapping an environment for natively building RPMs on ARMv7 (aka arm32, armv7hl, armhfp...) roughly following [Fedora's AArch64 bootstrap process](https://fedoraproject.org/wiki/Architectures/AArch64/Bootstrap).  It's based entirely on the freely-available source RPMs from the [AlmaLinux](https://almalinux.org) 9 repos and the [Linux From Scratch](https://linuxfromscratch.org) instructions. They should also work for [Rocky Linux](https://rockylinux.org), should you like that name better.

## Background
Fedora 36 is the last version to support ARMv7 as described [here](https://fedoraproject.org/wiki/Architectures/ARM). I think it really sucks that my 32-bit Raspberry Pi(s) are dead in the water when that goes EOL, so I embarked on a project to see if it would be possible to build AlmaLinux for ARM. Fortunately, the RPM build process (that is, the corresponding specfile for each package) for ARM is intact despite RedHat/Fedora no longer supporting it.

## Prerequisites
A Linux machine with:
 - a working compiler. I tested this with 32-bit versions of Fedora 34 and Raspbian (based on Debian Bullseye 11.5) 
 - the AlmaLinux SRPMs (I used `reposync` to grab them all since the source code doesn't seem to be mirrored and the repo metadata is painfully slow for me)
 - (ideally) `rpm` and `rpmbuild`. It's probably possible to just install the sources (`rpm -ivh`) and prep each package tree (`rpmbuild -bp`) from any old machine but I did it all on a Raspberry Pi 4.
 - a user with `sudo` access to run `mount` and `chroot`, for mounting required pseudofilesystems in the chroot environment and switching to it for stage 2.

If (like me) you're doing this on a Raspberry Pi, you might want to consider:
 - using an external drive, since it's much faster than the internal SD card
 - setting up a small swap partition (ideally, on that external storage)
 - tuning some of the settings, especially parallel make jobs, in `common.rc`. On a RPi 3, running 4 jobs (one for each processor) will cause OOM errors and run the processor really hot.

## Process
`stage1.sh` bootstraps a minimal development environment from the AlmaLinux source RPMs, making it possible to `chroot` into the new environment and run `stage2.sh`.
`stage2.sh` takes the minimal environment and leaves it in a state capable of running `rpm` and `rpmbuild`.
`stage3.sh` uses `rpm` and `rpmbuild` to build and install packages required to run `mock`, with which all the rest of the system can be (re)built.

## Howto
1. Download the AlmaLinux source RPMs to your local machine. Copy all the SRPMs to one directory, or link them with something like `mkdir all_pkgs; for pkg in repos/*/Packages; do ln -sv ../$pkg all_pkgs; done`. Edit `stage1.sh` as necessary with the location and versions of the SRPMs, and specify INSTALL_DIR in it to set the install location of the bootstrap environment.
2. Run `stage1.sh` as a non-root user. This will build the chroot environment.
3. Run `stage2_prep_chroot.sh`, which will create users, mountpoints, etc. in the chroot directory. Then run `stage2_prep_packages.sh` to copy packages and the build scripts into it.
3. As the root user, do `chroot $INSTALL_DIR /bin/bash` to be placed into the new system.
4. Run `stage2.sh` from the chroot environment to continue building packages required for `rpm` and `rpmbuild`.
5. Run `stage3.sh` from the chroot environment to build the packages required to run `mock`.
