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
 - `stage1.sh` bootstraps a minimal development environment from the AlmaLinux source RPMs, making it possible to `chroot` into the new environment and run `stage2.sh`.
 - `stage2.sh` takes the minimal environment and leaves it in a state capable of running `rpm` and `rpmbuild`.
 - `stage3.sh` uses `rpm` and `rpmbuild` to build and install packages required to run `mock`, with which all the rest of the system can be (re)built.
 - `stage4.sh` uses `mock` to rebuild the entire distribution.
 - The (planned, not yet implemented) stage5 is just another pass of stage4, but with stage3 removed so the system is self-hosting.

## Howto
1. Download the AlmaLinux source RPMs to your local machine. Copy all the SRPMs to one directory, or link them with something like `mkdir all_pkgs; for pkg in repos/*/Packages; do ln -sv ../$pkg all_pkgs; done`. Edit `common.rc` as necessary.
1. Ensure you have the prerequisite packages installed using `install_prereqs_deb.sh` or `install_prereqs_rpm.sh`, depending on the package manager on your system.
1. Run `stage1_prep.sh` as a non-root user. This will create the chroot directory (or clean any files in it if it exists!), and install kernel headers from the Alma distribution into it for stage1.
2. Run `stage1.sh` as a non-root user. This will build the chroot environment.
2. Run `stage2_prep_chroot.sh`, which will create users, mountpoints, etc. in the chroot directory. This requires `sudo` privileges for `install`, `mount`, and `chroot`. 
2. Run `stage2_prep_packages.sh` to copy packages and the build scripts into the chroot.
2. As the root user, do `chroot $INSTALL_DIR /bin/bash` to start a root shell in the chroot directory.
2. Run `stage2.sh` from the chroot environment to continue building packages required for `rpm` and `rpmbuild`.
3. Run `stage3_prep_chroot.sh`. This will copy the Java environment and CA certificates from the host (needed for building some stage3 packages), mount the source tree and the destination directory for stage3 RPMs in the chroot, and create some files required for stage3.
3. Run `stage3.sh` from the chroot environment to build the packages required to run `mock`.
4. Run `stage4_prep_chroot.sh`, which remounts the stage3 RPM directory read-only, and mounts the stage4 RPM directory.
4. Run `stage4.sh` to build the rest of the system with `mock`.
