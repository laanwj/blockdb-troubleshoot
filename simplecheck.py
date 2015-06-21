#!/usr/bin/python
'''
Simple iteration+lookup check of databases.
Should reproduce failures in case of corruption.
'''
# W.J. 2015
from __future__ import print_function,division
import leveldb
import sys

base = sys.argv[1]

print('Checking chain state')
l = leveldb.LevelDB(base + '/chainstate',paranoid_checks=True)
count = 0
for x in l.RangeIter(verify_checksums=True):
    x2 = l.Get(x[0],verify_checksums=True)
    assert(x2 == x[1])
    count += 1
print('%i records checked' % count)
 
print('Checking block index')
l2 = leveldb.LevelDB(base + '/blocks/index',paranoid_checks=True)
count = 0
for x in l2.RangeIter(verify_checksums=True):
    x2 = l2.Get(x[0],verify_checksums=True)
    assert(x2 == x[1])
    count += 1
print('%i records checked' % count)
