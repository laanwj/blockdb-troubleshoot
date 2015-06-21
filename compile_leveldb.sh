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
    python setup.py build
)

cp py-leveldb/build/lib.*/leveldb.so .
cp py-leveldb/leveldb/leveldbutil .

