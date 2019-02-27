#!/bin/sh

PKG=${1:-bash awk sed}

install_vbox() {
  apt-get install -y build-essential
  apt-get install -y  linux-headers-$(uname -r)
}

install_pkg() {
  apt-get install -y build-essential fakeroot devscripts
}

install_pkg

