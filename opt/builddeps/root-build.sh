#!/bin/sh

RELEASE=stable
SCRIPT_DIR=/opt/builddeps/
BUILD_FILE=/tmp/build.sh
CHRD="$SCRIPT_DIR/$RELEASE-chroot"

clean() {
  rm -rf "/opt/builddeps/$RELEASE-chroot"
  debootstrap $RELEASE "$CHRD" http://deb.debian.org/debian/
}

get_bootstrap() {
  chroot "$CHRD" apt-get install -y build-essential
  chroot "$CHRD" dpkg -l | tail -n +6 | cut -f3 -d' ' >"$SCRIPT_DIR"/bootstrap.pkg
}

run_build() {
  cp $BUILD_FILE "$CHRD"
  chroot "$CHRD" sh -evx /`basename "$BUILD_FILE"`
}

test -f "$BUILD_FILE" || {
  echo Cannot find $BUILD_FILE
  exit -1
}

#clean
#get_bootstrap
run_build

