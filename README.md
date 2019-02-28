# builddeps
The package contains utilities for generating a build order for given packages.

Build the debian package from source: `cd src; dpkg-deb --build builddeps ../packages`.

Install the package: `dpkg -i builddeps*.deb; apt-get install -f`.

Generate dependency list for packages: `/opt/builddeps/generate-order.py [packages]`.

Build the packages: `sudo sh /opt/builddeps/root-build.sh`.

