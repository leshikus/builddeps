# builddeps
The package contains utilities for generating a build order for given packages.

Build the debian package from source: `cd src; dpkg-deb --build builddeps packages`.

Install the package (should be root@): `dpkg -i packages/builddeps*.deb; apt-get install -f`.

Generate dependency order for packages: `/opt/builddeps/generate-order.py [packages]`.

Build the packages (should be root@): `sudo sh /opt/builddeps/root-build.sh`.

