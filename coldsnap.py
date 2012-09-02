#!/usr/bin/env python

import fcntl
import struct
import array
import os
import re
import hashlib

# from linux/fs.h
FIBMAP      = 0x01
FIGETBSZ    = 0x02


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
    return hashlib.md5(block).hexdigest()

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

def get_file_blocks_by_name(name):
    try:
        with open(name, 'rb') as handle:
            return get_file_blocks(handle)
    except IOError as e:
        print e
        return []

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

def get_block_device_from_file(filename):
    fstat = os.stat(filename)
    return os.path.join('/dev', get_block_device_map()[block_mn_from_int(fstat.st_dev)])

def block_mn_from_int(dev_int):
    return (int(dev_int >> 8), int(dev_int & 0xFF))


def walk_fs(mp):
    for (base, dirs, files) in os.walk(mp):
        for path in (os.path.join(base, f) for f in files):
            yield path
