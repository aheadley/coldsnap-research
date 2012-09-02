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

if __name__ == '__main__':
    import sys

    base_dir = sys.argv[1]
    backup_dir = sys.argv[2]

    device_name = coldsnap.get_block_device_map() \
        [coldsnap.block_mn_from_int(os.stat(backup_dir).st_dev)]

    data = {
        'file_block_map': {},
        'block_hash_set': set(),
    }

    with open(os.path.join('/dev', device_name), 'rb') as dev_handle:
        for path in coldsnap.walk_fs(backup_dir):
            blocks = [get_block_tuple(dev_handle, bn) \
                for bn in coldsnap.get_file_blocks_by_name(path)]
            data['file_block_map'][path] = [h[1] for h in blocks]
            for block in blocks:
                save_block(base_dir, block[1], block[2])

    data['block_hash_set'] = list(data['block_hash_set'])
    with open(os.path.join(base_dir, 'data.json'), 'w') as df:
        json.dump(data, df, indent=2)
