#!/bin/sh

set -evx

test -n "$1" || {
  echo Usage: $0 [package name]
  exit 1
}

dir0=`dirname "$0"`
dir1="$dir0"/build/$1
mkdir -p "$dir1"
cd "$dir1"

apt-get source $1
apt-get build-dep -y $1
cd */debian
cpu=`lscpu | grep '^CPU(' | awk '{ print $2 }'`
DEB_BUILD_OPTIONS='nocheck parallel=$cpu' debuild -b -uc -us
apt-get install -y $1
dpkg -i ../../$1_*.deb

# if successful
cd "$dir0"
rm -rf build/"$1" &

