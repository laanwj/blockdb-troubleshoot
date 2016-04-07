▄▚█▐▙▞█▖▙▐▜▚▖▌▗▟▌▗▐▟▗▌▖▚▟▌▄█▚█▜▌▟█▚▟▟▐▀▙
Collected bitcoin block database troubleshooting tools.
▐▟▌▀▜▗▘▙▝▛▛▄▝▙▚▟▜▚▚▌▝▙▘▟▞▞▞▗▞▞▙▘▙▛▜▟▐▗▙▙

Run `./compile_leveldb.sh` to build the necessary `leveldb.so` python module,
as well as `leveldbutil`.

Do not use existing python-leveldb with these tools! The internal library is
specifically tweaked to be exactly like Bitcoin's. Using an external
leveldb can result in the databases becoming incompatible with Bitcoin
due to, for example, different compression settings or version drift.

dependencies
-------------
```bash
apt-get install python3-setuptools python3-dev
```

lmdb
------
EXPERIMENTAL

Run `./compile_lmdb.sh` to build the `lmdb` module.
This will use py-lmdb's internal `lmdb` module, not the system `lmdb` (if any).

```bash
./leveldb2lmdb.py /data/bitcoin/chainstate /data/bitcoin/chainstate2 $((1024*1024*1024*8))
./leveldb2lmdb.py /data/bitcoin/blocks/index /data/bitcoin/blocks/index2 $((1024*1024*1024*8)) 
```
