#!/usr/bin/env python

import hashlib
import math

BLOCK_SIZE      = 4096
BUFFER_LEN      = 512

def iterate_blocks(device_handle):
    read_size = BLOCK_SIZE * BUFFER_LEN
    print 'Reading {0} bytes at a time'.format(read_size)
    buf = device_handle.read(read_size)
    while buf: #buf will be empty at EOF
        for i in xrange(max(1, len(buf) / BLOCK_SIZE)):
            yield buf[i * BLOCK_SIZE:(i+1) * BLOCK_SIZE]
        buf = device_handle.read(read_size)

def get_block_hash(block):
    return hashlib.sha1(block).hexdigest()

if __name__ == '__main__':
    import sys

    for block_device in sys.argv[1:]:
        with open(block_device, 'rb') as device_handle:
            block_hashes = list(get_block_hash(b) for b in iterate_blocks(device_handle))
            unique_hashes = set(block_hashes)
            print 'Device {d} :: {u} Unique Blocks : {t} Total Blocks'.format(
                u=len(unique_hashes), t=len(block_hashes), d=block_device)
            print 'Deduplication would save: {0} bytes'.format(
                (len(block_hashes) - len(unique_hashes)) * BLOCK_SIZE)
