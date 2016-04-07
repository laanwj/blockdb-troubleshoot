Collected bitcoin block database troubleshooting tools.

Run `./compile_leveldb.sh` to build the necessary `leveldb.so` python module,
as well as `leveldbutil`.

Do not use existing python-leveldb with these tools! The internal library is
specifically tweaked to be exactly like Bitcoin's. Using an external
leveldb can result in the databases becoming incompatible with Bitcoin
due to, for example, different compression settings or version drift.

dependencies
-------------
apt-get install python3-setuptools
