# builddeps
Building build dependencies for given packages

Build debian package: `dpkg-deb --build builddeps`

Install the package: `dpkg -i builddeps.deb; apt-get install -f`
