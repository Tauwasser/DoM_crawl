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
    ap.add_argument('infile', help='CSV input file.')
    ap.add_argument('outfile', help='CSV output file.')
    args = ap.parse_args()
    
    infile = args.infile
    outfile = args.outfile
    
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
    
    with open(infile, 'r', newline='') as csvfile:
        csv_in = csv.reader(csvfile, delimiter=';')
        for row in csv_in:
        
            rows += 1
            
            md5 = row[0]
            name = row[1]
            goodDump = row[4] == 'True'
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
    
    with open(outfile, 'w', newline='') as csvfile:
        csv_out = csv.writer(csvfile, delimiter=';')
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

if __name__ == '__main__':
    sys.exit(main())