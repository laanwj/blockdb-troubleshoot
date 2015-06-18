#!/usr/bin/python3
'''
Script to report bitflips between two files.
'''
import sys
with open(sys.argv[1],'rb') as f:
    ad = f.read()
with open(sys.argv[2],'rb') as f:
    bd = f.read()

dl = len(ad)
assert(dl == len(bd))

def popcount8(x):
    #  parallel reduction, avoid carries
    ## abcdefgh -> aabbccdd
    x = (x & 0x55) + ((x & 0xaa)>>1)
    ## aabbccdd -> aaaabbbb
    x = (x & 0x33) + ((x & 0xcc)>>2)
    ## aaaabbbb -> aaaaaaaa
    x = (x & 0x0f) + ((x & 0xf0)>>4)
    return x

print('ofs      | orig | err  | xor | pop')
print('---------+------+------+-----+----')
errors = 0
for i in range(dl):
    xd = ad[i] ^ bd[i]
    if xd:
        flips = popcount8(xd)
        print('%08x |  %02x  |  %02x  | %02x  | %i' % (i, ad[i], bd[i], xd, flips))
        errors += flips
print()
print('Total bitflips: %i' % errors)

