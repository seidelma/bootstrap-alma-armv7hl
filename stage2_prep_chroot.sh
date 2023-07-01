#!/bin/bash
set +h -exuo pipefail

if [ "$(id -u)" == "0" ]; then
        echo "This script is dangerous and must not be run as $(id -un); exiting"
        exit 1
fi

SCRIPT_DIR=$(readlink -f $(dirname "$0"))

CONFIGRCFILE="${SCRIPT_DIR:?}/common.rc"
if [ -f "$CONFIGRCFILE" ]; then
        . "$CONFIGRCFILE"
else
        echo "The script config file $CONFIGRCFILE was not found, exiting"
        exit 1
fi
if [ -f "$STAGE12_PACKAGESRCFILE" ]; then
    . "$STAGE12_PACKAGESRCFILE"
else
    echo "The package config file $STAGE12_PACKAGESRCFILE was not found; exiting"
    exit 1
fi

if [ ! -d "${INSTALL_DIR}/${CHROOT_SRC_DIR}" ]; then
       mkdir "${INSTALL_DIR}/${CHROOT_SRC_DIR}"
fi

touch "${INSTALL_DIR}/.in_chroot"

outfile="/tmp/prep_chroot.sh"
mkdir -pv $(dirname "${INSTALL_DIR}/$outfile")
cat > "${INSTALL_DIR}$outfile" << "EOCHROOT"
#!/bin/bash
set +h -exuo pipefail
        ln -svf /proc/self/mounts /etc/mtab

        cat > /etc/hosts << EOF
127.0.0.1  localhost $(hostname)
::1        localhost
EOF

        cat > /etc/resolv.conf << EOF
nameserver 10.20.30.254
nameserver 1.1.1.1
EOF

        cat > /etc/passwd << EOF
root:x:0:0:root:/root:/bin/bash
bin:x:1:1:bin:/dev/null:/usr/bin/false
daemon:x:6:6:Daemon User:/dev/null:/usr/bin/false
messagebus:x:18:18:D-Bus Message Daemon User:/run/dbus:/usr/bin/false
uuidd:x:80:80:UUID Generation Daemon User:/dev/null:/usr/bin/false
mockbuild:x:42069:42069:Mock build user:/dev/null:/usr/bin/false
nobody:x:65534:65534:Unprivileged User:/dev/null:/usr/bin/false
EOF

        cat > /etc/group << EOF
root:x:0:
bin:x:1:daemon
sys:x:2:
kmem:x:3:
tape:x:4:
tty:x:5:
daemon:x:6:
floppy:x:7:
disk:x:8:
lp:x:9:
dialout:x:10:
audio:x:11:
video:x:12:
utmp:x:13:
usb:x:14:
cdrom:x:15:
adm:x:16:
messagebus:x:18:
input:x:24:
mail:x:34:
kvm:x:61:
uuidd:x:80:
wheel:x:97:
users:x:999:
mock:x:42069:
nobody:x:65534:
EOF

        mkdir -pv /{boot,home,mnt,opt,srv}
        mkdir -pv /etc/{opt,sysconfig}
        mkdir -pv /lib/firmware
        mkdir -pv /media/{floppy,cdrom}
        mkdir -pv /usr/{,local/}{include,src}
        mkdir -pv /usr/local/{bin,lib,sbin}
        mkdir -pv /usr/{,local/}share/{color,dict,doc,info,locale,man}
        mkdir -pv /usr/{,local/}share/{misc,terminfo,zoneinfo}
        mkdir -pv /usr/{,local/}share/man/man{1..8}
        mkdir -pv /var/{cache,local,log,opt,spool}
        mkdir -pv /var/lib/{color,misc,locate}

        touch /var/log/{btmp,lastlog,faillog,wtmp}
        chgrp -v utmp /var/log/lastlog
        chmod -v 664  /var/log/lastlog
        chmod -v 600  /var/log/btmp

        ln -sfv /run /var/run
        ln -sfv /run/lock /var/lock

        install -dv -m 0750 /root
        install -dv -m 1777 /tmp /var/tmp
        chown -R root:root /{usr,lib,var,etc,bin,sbin}

	echo "PS1=\"[chroot \w]# \"" > /root/.bashrc
EOCHROOT

# If phase1 tools dir still exists, move it out of anything likely to be in $PATH
[ -d "${INSTALL_DIR}/${PHASE1_TOOLS_DIR}" ] && mv "${INSTALL_DIR}/${PHASE1_TOOLS_DIR}" "${INSTALL_DIR}/${PHASE1_TOOLS_DIR}-old"

# If timezone data doesn't exist, copy it over
[ -d "${INSTALL_DIR}/usr/share/zoneinfo" ] || cp -av /usr/share/zoneinfo "${INSTALL_DIR}/usr/share"

# Copy SSL certs (for various SSL-related bits)
if grep -q "redhat" /etc/os-release; then
        cert_bundle="/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem"
        if [ -f "$cert_bundle" ]; then
                mkdir -pv "${INSTALL_DIR}/etc/pki/tls/certs"
                cp -av /etc/pki/ca-trust "${INSTALL_DIR}/etc/pki"
                ln -sv "$cert_bundle" "${INSTALL_DIR}/etc/pki/tls/certs/ca-bundle.crt"
                ln -sv /etc/pki/ca-trust/extracted/openssl/ca-bundle.trust.crt "${INSTALL_DIR}/etc/pki/tls/certs/ca-bundle.trust.crt"
        fi
else
        # debian
        cert_bundle="/etc/ssl/certs/ca-certificates.crt"
        if [ -f "$cert_bundle" ]; then
                mkdir -pv "${INSTALL_DIR}/etc/pki/tls/certs"
                cp -av "$cert_bundle" "${INSTALL_DIR}/etc/pki/tls/certs/ca-bundle.crt"
        fi
fi

# Copy OpenSSL config from crypto-policies.
# crypto-policies seems to be a relatively recent RHEL addition; it's not on centos, debian, ubuntu...
# this is ripped straight from Alma 9.2 aarch64, we need this to build/test stage3 openssl
openssl_config="/etc/crypto-policies/back-ends/opensslcnf.config"
mkdir -pv $(dirname "${INSTALL_DIR}${openssl_config}")
cat > "${INSTALL_DIR}${openssl_config}" << EOF
CipherString = @SECLEVEL=2:kEECDH:kRSA:kEDH:kPSK:kDHEPSK:kECDHEPSK:kRSAPSK:-aDSS:-3DES:!DES:!RC4:!RC2:!IDEA:-SEED:!eNULL:!aNULL:!MD5:-SHA384:-CAMELLIA:-ARIA:-AESCCM8
Ciphersuites = TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256:TLS_AES_128_CCM_SHA256
TLS.MinProtocol = TLSv1.2
TLS.MaxProtocol = TLSv1.3
DTLS.MinProtocol = DTLSv1.2
DTLS.MaxProtocol = DTLSv1.2
SignatureAlgorithms = ECDSA+SHA256:ECDSA+SHA384:ECDSA+SHA512:ed25519:ed448:rsa_pss_pss_sha256:rsa_pss_pss_sha384:rsa_pss_pss_sha512:rsa_pss_rsae_sha256:rsa_pss_rsae_sha384:rsa_pss_rsae_sha512:RSA+SHA256:RSA+SHA384:RSA+SHA512:ECDSA+SHA224:RSA+SHA224
EOF

# Get the host system's java for building tzdata...and java
mkdir -p ${INSTALL_DIR}/usr/lib/jvm
if grep -qi "redhat" /etc/os-release; then
        # Redhat-based distros use symlinks to/from /etc/alternatives so dereference them
        cp -Hav /usr/lib/jvm/java-11-openjdk/ ${INSTALL_DIR}/usr/lib/jvm
        mv ${INSTALL_DIR}/usr/lib/jvm/{java-11-openjdk,bootstrap-jvm}
else
        cp -av /usr/lib/jvm/java-11-openjdk-armhf ${INSTALL_DIR}/usr/lib/jvm/bootstrap-jvm
fi
for file in ${INSTALL_DIR}/usr/lib/jvm/bootstrap-jvm/bin/*; do
        pathfix=$(echo $file | sed "s;${INSTALL_DIR};;")
        ln -sf $pathfix ${INSTALL_DIR}/usr/bin/$(basename $pathfix)
done

# Mount pseudofilesystems
for dir in dev proc sys run; do
	if [ ! -d "${INSTALL_DIR}/$dir" ]; then
		sudo install -dv -m 0755 "${INSTALL_DIR}/$dir"
	fi
done

mountpoint -q "${INSTALL_DIR}/dev"     || sudo mount -vt devtmpfs devtmpfs "${INSTALL_DIR}/dev"
mountpoint -q "${INSTALL_DIR}/dev/pts" || sudo mount -vt devpts devpts "${INSTALL_DIR}/dev/pts"
mountpoint -q "${INSTALL_DIR}/run"     || sudo mount -vt tmpfs tmpfs "${INSTALL_DIR}/run"
mountpoint -q "${INSTALL_DIR}/sys"     || sudo mount -vt sysfs devtmpfs "${INSTALL_DIR}/sys"
mountpoint -q "${INSTALL_DIR}/proc"    || sudo mount -vt proc devtmpfs "${INSTALL_DIR}/proc"

chmod 0755 "${INSTALL_DIR}$outfile"
sudo chroot "${INSTALL_DIR}" "$outfile"

bootstrap_dir=$(readlink -f $(dirname $0))
cp -av "${bootstrap_dir}/" "${INSTALL_DIR}/tmp"
