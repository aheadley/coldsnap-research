#!/usr/bin/env

import coldsnap
import json
import os

def get_block_tuple(dev_handle, bn):
    block = coldsnap.read_block(dev_handle, bn)
    return (bn, coldsnap.get_block_hash(block), block)

def save_block(base_dir, block_hash, block_data):
    if block_hash not in data['block_hash_set']:
        with open(os.path.join(base_dir, '%s.block' % block_hash), 'wb') as block_file:
            block_file.write(block_data)
        data['block_hash_set'].add(block_hash)

def get_block(base_dir, block_hash):
    with open(os.path.join(base_dir, '%s.block' % block_hash)) as bf:
        return bf.read()

if __name__ == '__main__':
    import sys

    base_dir = sys.argv[1]
    fpattern = sys.argv[2]
    restore_dir = sys.argv[3]

    with open(os.path.join(base_dir, 'data.json'), 'r') as df:
        data = json.load(df)

    for old_path in (p for p in data['file_block_map'] if p.startswith(fpattern)):
        new_path = old_path.replace(fpattern, restore_dir)
        try:
            os.makedirs(os.path.dirname(new_path))
        except os.error as e:
            pass
        with open(new_path, 'w') as nf:
            #print 'writing hashes for %s to %s' % (old_path, new_path)
            nf.write(''.join(get_block(base_dir, bh) for bh in data['file_block_map'][old_path]))
