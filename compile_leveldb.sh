#!/bin/sh
# build leveldb.so
set -e;

(
    cd py-leveldb/leveldb
    make clean
    make libleveldb.a LDFLAGS='-Bstatic' OPT='-fPIC -O2 -DNDEBUG '
)

(
    cd py-leveldb
    python setup.py build
)

cp py-leveldb/build/lib.*/leveldb.so .

