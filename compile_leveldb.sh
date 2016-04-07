#!/bin/sh
# build leveldb.so
set -e;

(
    cd py-leveldb/leveldb
    make clean
    make libleveldb.a LDFLAGS='-Bstatic' OPT='-fPIC -O2 -DNDEBUG '
    make leveldbutil
)

(
    cd py-leveldb
    rm -rf build
    python3 setup.py build
)

ln -sf py-leveldb/build/lib.*/leveldb.*.so .
ln -sf py-leveldb/leveldb/leveldbutil .

