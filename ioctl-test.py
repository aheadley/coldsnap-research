#!/usr/bin/env python

import fcntl
import struct
import array
import os
import re

FIBMAP      = 0x01
FIGETBSZ    = 0x02

def get_figetbsz(handle):
    buf = array.array('L', [0])
    result = fcntl.ioctl(handle.fileno(), FIGETBSZ, buf)
    return buf[0]

def get_fibmap(handle, i):
    buf = array.array('L', [i])
    result = fcntl.ioctl(handle.fileno(), FIBMAP, buf)
    return buf[0]

def get_file_blocks(handle):
    block_size = get_figetbsz(handle)
    file_size = os.fstat(handle.fileno()).st_size
    block_count = (file_size + block_size - 1) / block_size
    return [get_fibmap(handle, i) for i in xrange(block_count)]

def read_block(device_handle, block_num):
    block_size = get_figetbsz(device_handle)
    device_handle.seek(block_num * block_size)
    return device_handle.read(block_size)

def get_block_device_map():
    with open('/proc/partitions', 'rb') as parts:
        lines = [line.strip() for line in parts][2:]
    device_map = {}
    for line in lines:
        m = re.match(r'(\d+)\s+(\d+)\s+(\d+)\s+(.+)', line)
        device_map[(int(m.group(1)), int(m.group(2)))] = m.group(4)
    return device_map

if __name__ ==  '__main__':
    import sys

    block_device_map = get_block_device_map()

    for filename in sys.argv[1:]:
        with open(filename, 'rb') as file_handle:
            result = get_file_blocks(file_handle)
        fstat = os.stat(filename)
        dev_mn = (int(fstat.st_dev >> 8), int(fstat.st_dev & 0xFF))
        with open(os.path.join('/dev', block_device_map[dev_mn]), 'rb') as dev:
            blocks = [read_block(dev, b) for b in result]

        print ''.join(blocks)
