#!/bin/sh
# build leveldb.so
set -e;

#(
#    cd py-leveldb/leveldb
#    make clean
#    make libleveldb.a LDFLAGS='-Bstatic' OPT='-fPIC -O2 -DNDEBUG '
#    make leveldbutil
#)

(
    cd py-lmdb
    rm -rf build
    python3 setup.py build
)

ln -s py-lmdb/build/lib.*/lmdb .

