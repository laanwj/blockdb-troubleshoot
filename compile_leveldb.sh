#!/bin/sh
# build leveldb.so
set -e;

(
    cd py-leveldb/leveldb
    make clean
    make out-static/libleveldb.a LDFLAGS='-Bstatic' OPT='-fPIC -O2'
    make out-static/leveldbutil
    ln -sf out-static/libleveldb.a libleveldb.a
)

(
    cd py-leveldb
    rm -rf build
    python3 setup.py build
)

ln -sf py-leveldb/build/lib.*/leveldb.*.so .
ln -sf py-leveldb/leveldb/out-static/leveldbutil .

