# builddeps
Building build dependencies for given packages.

Build the debian package: `cd src; dpkg-deb --build builddeps ../packages`.

Install the package: `dpkg -i builddeps*.deb; apt-get install -f`.

Generate dependency list for : `/opt/builddeps/generate-order.py [packages]`.

Build the packages: `sudo sh /opt/builddeps/root-build.sh`.

