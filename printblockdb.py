#!/usr/bin/python

import leveldb
import binascii
import socket
import struct
import io
import sys
import os
import hashlib
from collections import defaultdict
from operator import attrgetter

def uint32(x):
    return x & 0xffffffffL

def bytereverse(x):
    return uint32(( ((x) << 24) | (((x) << 8) & 0x00ff0000) |
               (((x) >> 8) & 0x0000ff00) | ((x) >> 24) ))

def bufreverse(in_buf):
    out_words = []
    for i in range(0, len(in_buf), 4):
        word = struct.unpack('@I', in_buf[i:i+4])[0]
        out_words.append(struct.pack('@I', bytereverse(word)))
    return ''.join(out_words)

def wordreverse(in_buf):
    out_words = []
    for i in range(0, len(in_buf), 4):
        out_words.append(in_buf[i:i+4])
    out_words.reverse()
    return ''.join(out_words)

def calc_hdr_hash(blk_hdr):
    hash1 = hashlib.sha256()
    hash1.update(blk_hdr)
    hash1_o = hash1.digest()

    hash2 = hashlib.sha256()
    hash2.update(hash1_o)
    hash2_o = hash2.digest()

    return hash2_o

def calc_hash_str(blk_hdr):
    hash = calc_hdr_hash(blk_hdr)
    hash = bufreverse(hash)
    hash = wordreverse(hash)
    hash_str = hash.encode('hex')
    return hash_str

def deser_b128varint(f):
    n = 0
    while True:
        ch = struct.unpack("<b", f.read(1))[0]
        n = (n << 7) | (ch & 0x7f)
        if (ch & 0x80):
            n = n + 1
        else:
            return n
def deser_uint256(f):
	r = 0L
	for i in xrange(8):
		t = struct.unpack("<I", f.read(4))[0]
		r += t << (i * 32)
	return r

class CDiskBlockIndex(object):
    def __init__(self):
        self.nVersion = 0
        self.nHeight = 0
        self.nStatus = 0
        self.nTx = 0
        self.nFile = 0
        self.nDataPos = 0
        self.nUndoPos = 0
    def deserialize(self,f):
        self.nVersion = deser_b128varint(f)
        self.nHeight = deser_b128varint(f)
        self.nStatus = deser_b128varint(f)
        self.nTx = deser_b128varint(f)
        self.nFile = deser_b128varint(f)
        self.nDataPos = deser_b128varint(f)
        self.nUndoPos = deser_b128varint(f)
    def __repr__(self):
        return "CDiskBlockIndex(nVersion=%d nHeight=%d nStatus=%d nTx=%d nFile=%d nDataPos=%d nUndoPos=%d)" % (self.nVersion, self.nHeight, self.nStatus, self.nTx, self.nFile, self.nDataPos, self.nUndoPos)

class CBlockFileInfo(object):
    def __init__(self):
        self.nBlocks = 0
        self.nSize = 0
        self.nUndoSize = 0
        self.nHeightFirst = 0
        self.nHeightLast = 0
        self.nTimeFirst = 0
        self.nTimeLast = 0
    def deserialize(self, f):
        self.nBlocks = deser_b128varint(f)
        self.nSize = deser_b128varint(f)
        self.nUndoSize = deser_b128varint(f)
        self.nHeightFirst = deser_b128varint(f)
        self.nHeightLast = deser_b128varint(f)
        self.nTimeFirst = deser_b128varint(f)
        self.nTimeLast = deser_b128varint(f)
    def __repr__(self):
        return "CBlockFileInfo(nBlocks = %d nSize=%d nUndoSize=%d  nHeightFirst=%d nHeightLast=%d nTimeFirst=%d nTimeLast=%d)" % (self.nBlocks, self.nSize, self.nUndoSize, self.nHeightFirst, self.nHeightLast, self.nTimeFirst, self.nTimeLast)

def check_size(fname, given_size):
    disk_size = os.stat(fname).st_size
    if (disk_size != given_size):
        print("[error] %s: db/disk size mismatch disk=%d db=%d diff=%d" % (fname, disk_size, given_size, disk_size-given_size))
        return False
    return True

if len(sys.argv) != 2:
    print("Usage: %s datadir" % sys.argv[0])
    exit(-1)

settings = {}
settings['netmagic'] = 'f9beb4d9'.decode('hex')
settings['hashlist'] = 'hashes.txt'
MAX_BLOCK_SIZE = 1024*1024

datadir = sys.argv[1]
dbname = datadir + '/blocks/index'
db = leveldb.LevelDB(dbname)

print('Loading block database')
per_file = defaultdict(list)
count = 0
for k,v in db.RangeIter():
    if k[0] == 'b':
        st = io.BytesIO(k[1:])
        x = deser_uint256(st)
        stv = io.BytesIO(v)
        cdbi = CDiskBlockIndex()
        cdbi.deserialize(stv)
        #print(cdbi)
        #print('%3i %08x %064x' % (cdbi.nFile, cdbi.nDataPos, x))
        if cdbi.nDataPos != 0:
            cdbi.hash_str = '%064x' % (x)
            per_file[cdbi.nFile].append(cdbi)
        count += 1
        #if count > 100:
        #    break

# sort blocks per file by position
for fnum,blocks in per_file.iteritems():
    blocks.sort(key=attrgetter('nDataPos'))
filenums = sorted(per_file.keys())

for fnum in filenums:
    blocks = per_file[fnum]
    print('Checking file %i' % fnum)
    bfn = datadir + '/blocks/blk%05d.dat' % fnum
    prev_begin = None
    prev_end = None

    with open(bfn, 'rb') as f:
        for cdbi in blocks:
            f.seek(cdbi.nDataPos - 8)
            inhdr = f.read(8)
            inLen = struct.unpack("<I", inhdr[4:])[0]
            if inhdr[:4] != settings['netmagic'] or inLen > MAX_BLOCK_SIZE:
                print('%3i %08x Invalid block' % (cdbi.nFile, cdbi.nDataPos))
                exit(1)
            (span_begin, span_end) = (cdbi.nDataPos - 8, cdbi.nDataPos + inLen)
            if prev_end is not None:
                if span_begin < prev_end:
                    print('%3i %08x Overlapping block %08x-%08x,%08x-%08x' % (cdbi.nFile, cdbi.nDataPos, span_begin, span_end, prev_begin, prev_end))
                elif span_begin != prev_end:
                    print('%3i %08x Gap between blocks %08x-%08x,%08x-%08x' % (cdbi.nFile, cdbi.nDataPos, span_begin, span_end, prev_begin, prev_end))

            blk_hdr = f.read(80)
            hash_str = calc_hash_str(blk_hdr)
            if hash_str != cdbi.hash_str:
                print('%3i %08x %s != %s' % (cdbi.nFile, cdbi.nDataPos, hash_str, cdbi.hash_str))

            prev_begin = span_begin
            prev_end = span_end
'''
for k,v in db.RangeIter():
    if k[0] == 'f':
        blknum = struct.unpack('<i',k[1:5])[0]

        st = io.BytesIO(v)
        cbfi = CBlockFileInfo()
        cbfi.deserialize(st)
        print("Block file %d: %s" % (blknum, cbfi))
        bfn = datadir + '/blocks/blk%05d.dat' % blknum
        rfn = datadir + '/blocks/rev%05d.dat' % blknum

        check_size(bfn, cbfi.nSize)
        check_size(rfn, cbfi.nUndoSize)

#        print(cbfi) 
'''
