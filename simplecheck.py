#!/usr/bin/env python3
'''
Simple iteration+lookup check of databases.
Should reproduce failures in case of corruption.
'''
# W.J. 2015-2017
from __future__ import print_function,division
import leveldb
import sys

N = 10000

def checkdb(pathname):
    print(' * opening %s' % pathname)
    l2 = leveldb.LevelDB(pathname,paranoid_checks=True)
    count = 0
    for x in l2.RangeIter(verify_checksums=True):
        x2 = l2.Get(x[0],verify_checksums=True)
        assert(x2 == x[1])
        count += 1
    print(' * %i records checked' % count)
    # "random" probe
    print(' * probe %d times (trigger bloom filters)' % N)
    for x in range(N):
        key = x.to_bytes(8,byteorder="little")
        try:
            l2.Get(key, verify_checksums=True)
        except KeyError:
            pass

base = sys.argv[1]

print('* Checking chain state')
checkdb(base + '/chainstate')
 
print('* Checking block index')
checkdb(base + '/blocks/index')
