#!/bin/sh

RELEASE=stable
SCRIPT_DIR=/opt/builddeps/
CHRD="$SCRIPT_DIR/$RELEASE-chroot"

install_vbox() {
  apt-get install -y build-essential
  apt-get install -y  linux-headers-$(uname -r)
}

clean() {
  rm -rf "/opt/builddeps/$RELEASE-chroot"
  debootstrap $RELEASE "$CHRD" http://deb.debian.org/debian/
}

get_bootstrap() {
  chroot "$CHRD" apt-get install -y build-essential
  chroot "$CHRD" dpkg -l | tail -n +6 | cut -f3 -d' ' >"$SCRIPT_DIR"/bootstrap.pkg
}

#clean
get_bootstrap

