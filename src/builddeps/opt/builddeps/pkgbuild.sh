#!/bin/sh

set -e

dir=`dirname "$0"`/build/$1
mkdir -p "$dir"
cd "$dir"

apt-get source $1
apt-get build-dep -y $1
cd */debian
DEB_BUILD_OPTIONS=nocheck debuild -b -uc -us
apt-get install -y $1
dpkg -i ../../$1*.deb

