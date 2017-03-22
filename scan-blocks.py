#!/usr/bin/python3
'''
Scan a block file for block headers and extents, find overlapping extents.
'''
import json
import struct
import re
import os
import base64
import sys
import hashlib
import datetime
import time
import binascii
from collections import namedtuple

settings = {}
MAX_BLOCK_SIZE = 1024*1024

def uint32(x):
    return x & 0xffffffff

def bytereverse(x):
    return uint32(( ((x) << 24) | (((x) << 8) & 0x00ff0000) |
               (((x) >> 8) & 0x0000ff00) | ((x) >> 24) ))

def bufreverse(in_buf):
    out_words = []
    for i in range(0, len(in_buf), 4):
        word = struct.unpack('@I', in_buf[i:i+4])[0]
        out_words.append(struct.pack('@I', bytereverse(word)))
    return b''.join(out_words)

def wordreverse(in_buf):
    out_words = []
    for i in range(0, len(in_buf), 4):
        out_words.append(in_buf[i:i+4])
    out_words.reverse()
    return b''.join(out_words)

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
    hash_str = binascii.b2a_hex(hash).decode()
    return hash_str

def get_block_hashes(settings):
    blkindex = []
    f = open(settings['hashlist'], "r")
    for line in f:
        line = line.rstrip()
        blkindex.append(line)

    print("Read " + str(len(blkindex)) + " hashes")

    return blkindex

def mkblockmap(blkindex):
    blkmap = {}
    for height,hash in enumerate(blkindex):
        blkmap[hash] = height
    return blkmap

def run(fname, settings, blkmap):
    print("Input file " + fname)
    try:
        inF = open(fname, "rb")
    except IOError:
        print("Premature end of block data")
        return

    data = inF.read()
    ptr = 0
    last_start = last_end = None

    while True:
        ptr = data.find(settings['netmagic'], ptr)
        if ptr == -1:
            return
        inhdr = data[ptr:ptr+8]

        inMagic = inhdr[:4]
        inLenLE = inhdr[4:]
        su = struct.unpack("<I", inLenLE)
        if (inMagic != settings['netmagic']) or su[0] > MAX_BLOCK_SIZE:
            ptr += 1
            continue
            
        inLen = su[0] - 80 # length without header
        blk_hdr = data[ptr+8:ptr+88]

        hash_str = calc_hash_str(blk_hdr)
        data_end = ptr + 88 + inLen
        warning = ''
        if last_end is not None:
            if ptr < last_end:
                warning = 'Overlap with last block (0x%08x,0x%08x)' %(last_start, last_end)
            elif ptr != last_end:
                warning = 'Block doesn\'t start at expected position 0x%08x' % (data_end)

        blknum = blkmap.get(hash_str,-1)
        #if warning or blknum == -1:
        print('0x%08x-0x%08x %s %6d %s' % (ptr, data_end, hash_str,blknum, warning))

        last_start = ptr
        last_end = data_end
        ptr += 1

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: list-blocks.py blkXXX.dat")
        sys.exit(1)
    settings['netmagic'] = binascii.a2b_hex('f9beb4d9')
    settings['hashlist'] = 'hashes.txt'
    blkindex = get_block_hashes(settings)
    blkmap = mkblockmap(blkindex)
    for fname in sys.argv[1:]:
        run(fname, settings, blkmap)


