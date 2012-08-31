#!/usr/bin/env python

import fcntl
import struct
import array
import os
import re

# from linux/fs.h
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
    # is it even possible for these to not be sequential? I guess that would be
    # fragmentation?
    return [get_fibmap(handle, i) for i in xrange(block_count)]

def read_block(device_handle, block_num):
    block_size = get_figetbsz(device_handle)
    device_handle.seek(block_num * block_size)
    return device_handle.read(block_size)

def get_block_device_map():
    # this includes all block devices (even unmounted), might want to read from /proc/mounts and
    # filter by supported fs types, or use /proc/partitions to filter /proc/mounts
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
        print ':: {0} ::'.format(filename)
        with open(filename, 'rb') as file_handle:
            result = get_file_blocks(file_handle)
        fstat = os.stat(filename)
        print 'Size: {0}'.format(fstat.st_size)
        dev_mn = (int(fstat.st_dev >> 8), int(fstat.st_dev & 0xFF))
        print 'Device MJ/MN: {0}'.format(dev_mn)
        # dunno if these are guaranteed to be nodes in /dev, will assume they are
        # for now
        with open(os.path.join('/dev', block_device_map[dev_mn]), 'rb') as dev:
            print 'Device Path: {0}'.format(dev.name)
            blocks = [read_block(dev, b) for b in result]
        print 'Bytes read: {0}'.format(len(''.join(blocks)))
