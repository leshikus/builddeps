# builddeps
Building build dependencies for given packages.

Build the debian package: `cd src; dpkg-deb --build builddeps ../packages`.

Install the package: `dpkg -i builddeps*.deb; apt-get install -f`.

