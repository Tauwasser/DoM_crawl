#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import argparse
import csv
import yaml
from re import compile

def main():

    # argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument('infile', nargs='+', help='CSV input files.')
    ap.add_argument('outfile', help='CSV output file.')
    args = ap.parse_args()
    
    infiles = args.infile
    outfile, outfile_ext = os.path.splitext(args.outfile)
    
    metadata = dict()
    
    region_match = {
        '(Germany)'       : 'D',
        '(France)'        : 'F',
        '(Europe)'        : 'X',
        '(Japan)'         : 'J',
        '(USA, Europe)'   : 'E',
        '(USA)'           : 'E',
        '(World)'         : 'X',
        '(Japan, Europe)' : 'X',
        '(Spain)'         : 'S',
        '(Australia)'     : 'E',
        '(Japan, USA)'    : 'A',
        '(Netherlands)'   : 'H',
        '(USA, Australia)': 'E',
        '(Italy)'         : 'I',
        '(Sweden)'        : 'W',
    }
    revision_match = {
        '0': 0,
        '1': 1,
        '2': 2,
        '3': 3,
        'A': 1,
        'B': 2,
        'C': 3,
        'D': 4,
    }
    regex = compile('.*\(Rev ([0123ABCD])\).*')
    
    for infile in infiles:
        rows = 0
        with open(infile, 'r', newline='') as csvfile:
            csv_in = csv.reader(csvfile, delimiter=';')
            for row in csv_in:
            
                rows += 1
                
                if (rows == 1):
                    # skip header
                    continue
                
                md5 = row[0]
                name = row[1]
                goodDump = row[4] == 'True' or row[4] == 'TRUE'
                serial = row[7]
                rom = row[9]
                
                if (not(goodDump)):
                    continue
                
                if (md5 not in metadata):
                    metadata[md5] = {'name': name}
                
                if ('code' in metadata[md5] and not metadata[md5]['is_synthetic']):
                    # already done
                    continue
                
                if (rom != ''):
                    metadata[md5]['code'] = rom
                    metadata[md5]['is_synthetic'] = False
                    continue
                
                if (serial == '' or serial == 'none' or serial == 'unk'):
                    # nothing to be done about it
                    continue
                
                if (serial.endswith(' CHN')):
                    # filter CHN releases
                    continue
                
                if ('(3DS Virtual Console)' in name):
                    # filter 3DS Virtual Console
                    continue
                
                revision = 0
                m = regex.match(name)
                if (m is not None):
                    revision = revision_match[m.group(1)]
                
                prefix = serial
                if (serial.count('-') > 1):
                    prefix = serial.rsplit('-', serial.count('-') - 1)[0]
                # default: region code already included in regular code
                region = ''
                prefixes = prefix.split('-')
                if (len(prefixes) < 2):
                    # fix BigFred entries
                    prefix = 'DMG-' + prefixes[0]
                    region = ''
                elif (len(prefixes[1]) < 3):
                    region = None
                    for e in region_match:
                        if e in name:
                            region = region_match[e]
                            break
                    if (region is None):
                        print('Error: cannot determine region for {0:s}.'. format(name))
                        break
                metadata[md5]['code'] = prefix + region + '-' + str(revision)
                metadata[md5]['is_synthetic'] = True
    
    is_synthetic = 0
    has_code = 0
    
    with open(outfile + '_list' + outfile_ext, 'w', newline='') as csvfile:
        csv_out = csv.writer(csvfile, delimiter=';')
        row = ['MD5', 'ROM Serial', 'Name (No-Intro)', 'is_synthetic']
        csv_out.writerow(row)
        for md5, entry in metadata.items():
            if ('code' not in entry):
                print(entry['name'])
                continue
            has_code += 1
            if entry['is_synthetic']:
                is_synthetic += 1
            row = [md5, entry['code'], entry['name'], str(entry['is_synthetic'])]
            csv_out.writerow(row)
    
    print('has_code: {0:d}/{1:d} ({2:d} synthetic)'.format(has_code, len(metadata), is_synthetic))
    
    # convert to game map
    # do some sanity checks
    game_map = dict()
    for md5, entry in metadata.items():
        
        if ('code' not in entry):
            continue
        
        serial = entry['code'].split('-', 2)
        if (len(serial) < 3):
            print(serial)
        game_id = serial[0] + '-' + serial[1][:-1] # keep CGB/DMG prefix
        region_id = serial[1][-1]
        revision = int(serial[2])
        
        if (game_id not in game_map):
            game_map[game_id] = {}
        
        game_data = game_map[game_id]
        
        if (region_id not in game_data):
            game_data[region_id] = {}
        
        if (revision in game_data[region_id]):
            print('Error: duplicate game {0:s} for {1:s} vs {2:s}.'.format(game_id + region_id + '-' + str(revision), entry['name'], game_data[region_id][revision]['name']))
            continue
        
        game_data[region_id][revision] = {'revision': revision, 'name': entry['name'], 'is_synthetic': entry['is_synthetic'], 'md5': md5, 'code': entry['code']}

    with open(outfile + '.yaml', 'w', newline='') as yamlfile:
        yaml.dump(game_map, yamlfile)
    
    with open(outfile + '_dmg.yaml', 'w', newline='') as yamlfile:
        dmg_data = {k: v for k, v in game_map.items() if not(k.startswith('CGB-'))}
        yaml.dump(dmg_data, yamlfile)
    
    with open(outfile + '_cgb.yaml', 'w', newline='') as yamlfile:
        cgb_data = {k: v for k, v in game_map.items() if k.startswith('CGB-')}
        yaml.dump(cgb_data, yamlfile)
    
    dmg_games = len(dmg_data)
    dmg_revisions = 0
    cgb_games = len(cgb_data)
    cgb_revisions = 0
    
    for _, v in dmg_data.items():
        for region in v:
            for revision in v[region]:
                dmg_revisions += 1

    for _, v in cgb_data.items():
        for region in v:
            for revision in v[region]:
                cgb_revisions += 1

    print('Found {1:d} revisions for {0:d} DMG game entries.'.format(dmg_games, dmg_revisions))
    print('Found {1:d} revisions for {0:d} CGB game entries.'.format(cgb_games, cgb_revisions))
    return 0
    
if __name__ == '__main__':
    sys.exit(main())