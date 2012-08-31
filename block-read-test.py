#!/usr/bin/env python

import hashlib

BLOCK_SIZE      = 4096
BUFFER_LEN      = 512

def iterate_blocks(device_handle):
    buf = True
    while buf:
        try:
            buf = device_handle.read(BLOCK_SIZE * BUFFER_LEN)
        except Exception as err:
            print err
            break
        for i in xrange(len(buf) / BLOCK_SIZE):
            yield buf[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE]

def get_block_hash(block):
    return hashlib.sha1(block).hexdigest()

if __name__ == '__main__':
    import sys

    for block_device in sys.argv[1:]:
        with open(block_device, 'rb') as device_handle:
            block_hashes = [get_block_hash(b) for b in iterate_blocks(device_handle)]

    print block_hashes[:10], len(block_hashes)
