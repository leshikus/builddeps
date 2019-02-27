#!/bin/sh

RELEASE=stable
SCRIPT_DIR=/opt/builddeps/
BUILD_FILE=/tmp/build.sh
CHRD="$SCRIPT_DIR/$RELEASE-chroot"

get_bootstrap() {
  rm -rf "/opt/builddeps/$RELEASE-chroot"
  debootstrap $RELEASE "$CHRD" http://deb.debian.org/debian/
  chroot "$CHRD" sh <<EOF
mount none /proc -t proc  
apt-get install -y build-essential devscripts
fgrep deb-src /etc/apt/sources.list || {
  echo 'deb-src http://deb.debian.org/debian stable main' >> /etc/apt/sources.list
  apt-get update
}
EOF
  chroot "$CHRD" dpkg -l | tail -n +6 | cut -f3 -d' ' >"$SCRIPT_DIR"/bootstrap.pkg
}

run_build() {
  test -f "$BUILD_FILE" || {
    echo Cannot find $BUILD_FILE
    exit -1
  }

  cp $BUILD_FILE "$CHRD"
  chroot "$CHRD" sh -evx /`basename "$BUILD_FILE"`
}

get_bootstrap
run_build

