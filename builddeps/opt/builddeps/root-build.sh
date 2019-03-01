#!/bin/sh

RELEASE=stable
SCRIPT_DIR=/opt/builddeps
BUILD_FILE=/tmp/build.sh
CHRD="$SCRIPT_DIR/$RELEASE-chroot"

get_bootstrap() {
  umount "$CHRD"/proc "$CHRD"/sys "$CHRD"/dev || true
  rm -rf "/opt/builddeps/$RELEASE-chroot"
  debootstrap $RELEASE "$CHRD" http://deb.debian.org/debian/
  mount --bind /proc "$CHRD"/proc
  mount --bind /dev "$CHRD"/dev
  mount --bind /sys "$CHRD"/sys
  chroot "$CHRD" sh <<EOF
apt-get install -y build-essential devscripts
echo 'deb-src http://deb.debian.org/debian stable main' >> /etc/apt/sources.list
apt-get update
echo 'en_US.UTF-8 UTF-8' >/etc/locale.gen
locale-gen
EOF
}

run_build() {
  test -f "$BUILD_FILE" || {
    echo Cannot find $BUILD_FILE
    exit 1
  }

  cp "$BUILD_FILE" "$SCRIPT_DIR"/pkgbuild.sh "$CHRD"
  chroot "$CHRD" sh -vx /`basename "$BUILD_FILE"` 2>&1 | tee "$CHRD"/build.log
}

get_bootstrap
run_build

