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

# Some script-specific stuff:
# - install bootstrap builds to a temporary directory
# - use that temporary directory over the system install locations
#    until we've got the packages built
# - use ccache to speed up compilation
INSTALL_PREFIX="/p3"
if [ ! -d "$INSTALL_PREFIX" ]; then
	mkdir -p "$INSTALL_PREFIX"
fi
OLDPATH=$PATH
OLDLDPATH=${LD_LIBRARY_PATH:-}
PATH="${INSTALL_PREFIX}/bin:$PATH"
LD_LIBRARY_PATH="${INSTALL_PREFIX}/lib:${LD_LIBRARY_PATH:-}"
export PATH LD_LIBRARY_PATH
CC="ccache gcc"
CXX="ccache g++"
export CC CXX

SRC_DIR="${RPMBUILD_TOPDIR}/BUILD"

PREREQ_PACKAGES=("LLVM" "CLANG")

LLVM_VERSION='14.0.6'
LLVM_SRC_DIR='${SRC_DIR}/llvm-${LLVM_VERSION}.src'
LLVM_CONFIGURE='cmake -S . -B "bootstrap-build" -G Ninja 
        -DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX}
        -DBUILD_SHARED_LIBS:BOOL=OFF
        -DLLVM_PARALLEL_LINK_JOBS=1
        -DCMAKE_BUILD_TYPE=Release
        -DCMAKE_SKIP_RPATH:BOOL=ON
        -DCMAKE_C_FLAGS_RELEASE="${CFLAGS} -DNDEBUG"
        -DCMAKE_CXX_FLAGS_RELEASE="${CFLAGS} -DNDEBUG"
        -DLLVM_TARGETS_TO_BUILD="ARM"
        -DLLVM_ENABLE_LIBCXX:BOOL=OFF
        -DLLVM_ENABLE_ZLIB:BOOL=ON
        -DLLVM_ENABLE_FFI:BOOL=ON
        -DLLVM_ENABLE_RTTI:BOOL=ON
        -DLLVM_USE_PERF:BOOL=ON
        -DLLVM_BUILD_RUNTIME:BOOL=ON
        -DLLVM_INCLUDE_TOOLS:BOOL=ON
        -DLLVM_BUILD_TOOLS:BOOL=ON
        -DLLVM_INCLUDE_TESTS:BOOL=ON
        -DLLVM_BUILD_TESTS:BOOL=ON
        -DLLVM_LIT_ARGS=-v
        -DLLVM_INCLUDE_EXAMPLES:BOOL=ON
        -DLLVM_BUILD_EXAMPLES:BOOL=OFF
        -DLLVM_INCLUDE_UTILS:BOOL=ON
        -DLLVM_INSTALL_UTILS:BOOL=ON
        -DLLVM_UTILS_INSTALL_DIR:PATH=${INSTALL_PREFIX}/bin
        -DLLVM_TOOLS_INSTALL_DIR:PATH=${INSTALL_PREFIX}/bin
        -DLLVM_INCLUDE_DOCS:BOOL=OFF
        -DLLVM_BUILD_DOCS:BOOL=OFF
        -DLLVM_ENABLE_SPHINX:BOOL=OFF
        -DLLVM_ENABLE_DOXYGEN:BOOL=OFF
        -DLLVM_VERSION_SUFFIX=""
        -DLLVM_BUILD_LLVM_DYLIB:BOOL=ON
        -DLLVM_LINK_LLVM_DYLIB:BOOL=ON
        -DLLVM_BUILD_EXTERNAL_COMPILER_RT:BOOL=ON
        -DLLVM_INSTALL_TOOLCHAIN_ONLY:BOOL=OFF
        -DLLVM_DEFAULT_TARGET_TRIPLE=armv7l-redhat-linux-gnueabihf
        -DSPHINX_WARNINGS_AS_ERRORS=OFF
        -DLLVM_INCLUDE_BENCHMARKS=OFF'
LLVM_MAKE='cmake --build bootstrap-build -j${NPROC} --verbose --target LLVM &&
	   cmake --build bootstrap-build -j${NPROC} --verbose &&
	   cmake --install bootstrap-build'
LLVM_RPMBUILD='rpmbuild -bb --undefine '%_annotated_build' --undefine '%_annobin_gcc_plugin' --nodebuginfo --clean --nodeps --nocheck --without check'
LLVM_INSTALL_PACKAGES='llvm*'

CLANG_VERSION='14.0.6'
CLANG_SRC_DIR='${SRC_DIR}/clang-${CLANG_VERSION}.src'
CLANG_CONFIGURE='cmake -S . -B "bootstrap-build" -G Ninja
	-DCMAKE_INSTALL_PREFIX=${INSTALL_PREFIX}
        -DLLVM_PARALLEL_LINK_JOBS=1
        -DLLVM_LINK_LLVM_DYLIB:BOOL=ON
        -DCMAKE_BUILD_TYPE=Release
        -DPYTHON_EXECUTABLE=/usr/bin/python3.9
        -DCMAKE_SKIP_RPATH:BOOL=ON
        -DCMAKE_C_FLAGS_RELEASE="${CFLAGS} -DNDEBUG"
        -DCMAKE_CXX_FLAGS_RELEASE="${CFLAGS} -DNDEBUG"
        -DCLANG_INCLUDE_TESTS:BOOL=ON
        -DLLVM_EXTERNAL_CLANG_TOOLS_EXTRA_SOURCE_DIR=../clang-tools-extra-${CLANG_VERSION}.src
        -DLLVM_MAIN_SRC_DIR=${INSTALL_PREFIX}/share/llvm/src
        -DLLVM_LIBDIR_SUFFIX=
        -DLLVM_TABLEGEN_EXE:FILEPATH=${INSTALL_PREFIX}/bin/llvm-tblgen
        -DCLANG_ENABLE_ARCMT:BOOL=ON
        -DCLANG_ENABLE_STATIC_ANALYZER:BOOL=ON
        -DCLANG_INCLUDE_DOCS:BOOL=ON
        -DCLANG_PLUGIN_SUPPORT:BOOL=ON
        -DENABLE_LINKER_BUILD_ID:BOOL=ON
        -DLLVM_ENABLE_EH=ON
        -DLLVM_ENABLE_RTTI=ON
        -DLLVM_BUILD_DOCS=ON
        -DLLVM_ENABLE_NEW_PASS_MANAGER=ON
        -DLLVM_ENABLE_SPHINX=OFF
        -DCLANG_LINK_CLANG_DYLIB=ON
        -DSPHINX_WARNINGS_AS_ERRORS=OFF
        -DCLANG_BUILD_EXAMPLES:BOOL=OFF
        -DBUILD_SHARED_LIBS=OFF
        -DCLANG_REPOSITORY_STRING="bootstrap-build"
        -DCLANG_DEFAULT_LINKER=lld
        -DCLANG_DEFAULT_UNWINDLIB=libgcc
        -DGCC_INSTALL_PREFIX=/usr'
CLANG_MAKE='cmake --build bootstrap-build -j${NPROC} --verbose && cmake --install bootstrap-build'
CLANG_RPMBUILD='rpmbuild -bb --undefine '%_annotated_build' --undefine '%_annobin_gcc_plugin' --nodebuginfo --clean --nodeps --nocheck --without check'
CLANG_INSTALL_PACKAGES='clang* python3-clang* git-clang*'

RUST_VERSION='1.62.1'
RUST_SRC_DIR='${SRC_DIR}/rustc-${RUST_VERSION}-src'
RUST_CONFIGURE='./configure 
	--build=armv7hl-redhat-linux-gnueabi
	--host=armv7hl-redhat-linux-gnueabi
	--program-prefix=
	--disable-dependency-tracking
	--prefix=${INSTALL_PREFIX}
	--disable-option-checking
	--build=armv7-unknown-linux-gnueabihf
	--host=armv7-unknown-linux-gnueabihf
	--target=armv7-unknown-linux-gnueabihf
	--set target.armv7-unknown-linux-gnueabihf.linker=gcc
	--set target.armv7-unknown-linux-gnueabihf.cc=gcc
	--set target.armv7-unknown-linux-gnueabihf.cxx=g++
	--set target.armv7-unknown-linux-gnueabihf.ar=ar
	--set target.armv7-unknown-linux-gnueabihf.ranlib=/usr/bin/ranlib
	--llvm-root=/usr
	--enable-llvm-link-shared
	--disable-llvm-static-stdcpp
	--enable-extended
	--tools=cargo
	--disable-rpath
	--debuginfo-level=0
	--debuginfo-level-std=0
	--set rust.codegen-units-std=1
	--dist-compression-formats=gz
	--release-description="Red Hat 1.62.1-1.el9"'
RUST_MAKE='python ./x.py build -j${NPROC} && python ./x.py install -j${NPROC}'
RUST_RPMBUILD='rpmbuild -bb --undefine '%_annotated_build' --undefine '%_annobin_gcc_plugin' --nodebuginfo --clean --nodeps --nocheck'


# Build a local installation of required packages
for pkg in "${PREREQ_PACKAGES[@]}"
do
	get_package_name
	set_package_vars
	do_srpm_prep "${pkgname_lower}-${pkg_version}" "${pkgname_lower}.spec"
	do_build
done

# Now do the native RPM build
for pkg in "${PREREQ_PACKAGES[@]}"
do
	get_package_name
	set_package_vars
	do_rpmbuild_and_install ${pkgname_lower}-${pkg_version} ${pkgname_lower}.spec
done

PATH="$OLDPATH"
LD_LIBRARY_PATH="$OLDLDPATH"
INSTALL_PREFIX="/usr"
export PATH LD_LIBRARY_PATH

for pkg in "RUST"
do
	get_package_name
	set_package_vars
	do_srpm_prep "${pkgname_lower}-${pkg_version}" "${pkgname_lower}.spec"
	do_build
	do_rpmbuild_and_install "${pkgname_lower}-${pkg_version}" "${pkgname_lower}.spec"
done
