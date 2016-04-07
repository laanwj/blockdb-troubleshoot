#!/usr/bin/python3
'''Convert leveldb database to lmdb'''
import argparse
import leveldb, lmdb
import os, errno, sys

USE_SPARSE_FILES = sys.platform != 'darwin'

def remove_if_exists(p):
    try:
        os.remove(p)
    except FileNotFoundError:
        pass

def prepare_lmdb(p):
    # create path if it didn't exist
    os.makedirs(p, mode=0o755, exist_ok=True)
    # clean out any existing lmdb
    remove_if_exists(os.path.join(p, "data.mdb"))
    remove_if_exists(os.path.join(p, "lock.mdb"))

def parse_args():
    parser = argparse.ArgumentParser(description='Convert leveldb database to lmdb')
    parser.add_argument('leveldb_in', type=str, help='Path of leveldb database to process')
    parser.add_argument('lmdb_out', type=str, help='Path of lmdb to create (will be destroyed if it exists)')
    parser.add_argument('lmdb_mapsize', type=int, help='lmdb mapsize')
    return parser.parse_args()

def main():
    args = parse_args()
    prepare_lmdb(args.lmdb_out)

    # unfortunately leveldb has no way to count the number of keys,
    # so no % progress display can be given
    l = leveldb.LevelDB(args.leveldb_in)
    env = lmdb.open(args.lmdb_out, map_size=args.lmdb_mapsize, writemap=USE_SPARSE_FILES)
    with env.begin(write=True) as txn:
        count = 0
        for x in l.RangeIter():
            txn.put(x[0], x[1], append=True)
            if (count % 10000)==0:
                print('%i' % count, end='\r')
            count += 1
        print('Committing transaction')

if __name__ == '__main__':
    main()

