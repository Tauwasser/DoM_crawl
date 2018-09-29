#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import argparse
import csv
from re import compile

def main():

    # argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument('infile', nargs='+', help='CSV input files.')
    ap.add_argument('outfile', help='CSV output file.')
    args = ap.parse_args()
    
    infiles = args.infile
    outfile, outfile_ext = os.path.splitext(args.outfile)
    
    rows = 0
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
                synthetic = False
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
                    synthetic = True
                metadata[md5]['code'] = prefix + region + '-' + str(revision)
                metadata[md5]['is_synthetic'] = synthetic
    
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
        game_id = serial[1][:-1]
        region_id = serial[1][-1]
        
        if (game_id not in game_map):
            game_map[game_id] = {'type': serial[0]}
        
        game_data = game_map[game_id]
        if (game_data['type'] != serial[0]):
            print('Error: CGB and DMG have same serial: {0:s} vs. {1:s}!'.format(game_data['type'] + '-' + game_id, serial[0] + '-' + serial[1]))

if __name__ == '__main__':
    sys.exit(main())