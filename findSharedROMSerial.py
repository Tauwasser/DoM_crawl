#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import argparse
import xlwt
import csv

def main():

    # argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument('--keyset', default='EPU', help='Region codes to check for difference.')
    ap.add_argument('infile', nargs='+', help='CSV input files.')
    ap.add_argument('outfile', help='XLS output file.')
    args = ap.parse_args()
    
    infiles = args.infile
    outfile = args.outfile
    keyset = args.keyset
    
    if (len(keyset) < 2 or len(keyset) > 3):
        print('Keyset must be two to three characters long')
        return -1
    
    k0 = keyset[0]
    k1 = keyset[1]
    k2 = keyset[-1]
    
    metadata = dict() # MD5 to Code, full serial
    result_wb = xlwt.Workbook(encoding='UTF-8')
    shared_sheet = result_wb.add_sheet('Shared Codes')
    disjoint_sheet = result_wb.add_sheet('Disjoint Codes')
    
    header = ['MD5', 'ROM Serial 1', 'ROM Serial 2', 'Name 1', 'Name 2']
    for ix, elem in enumerate(header):
        shared_sheet.write(0, ix, elem)
    header = ['MD5 1', 'MD5 2', 'ROM Serial 1', 'ROM Serial 2', 'Name 1', 'Name 2']
    for ix, elem in enumerate(header):
        disjoint_sheet.write(0, ix, elem)
    
    shared_sheet_row = 1
    disjoint_sheet_row = 1
    
    disjoint_data = dict() # Code without E/P to MD5
    
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
                
                if (serial == '' or serial == 'none' or serial == 'unk'):
                    # nothing to be done about it
                    continue
                
                if (serial.endswith(' CHN')):
                    # filter CHN releases
                    continue
                
                if ('(3DS Virtual Console)' in name):
                    # filter 3DS Virtual Console
                    continue
                
                if (rom == ''):
                    # nothing to be done about it
                    continue
                
                rom_parts = rom.split('-')
                if (len(rom_parts) < 2):
                    # fix BigFred entries
                    code = rom_parts[0]
                else:
                    code = rom_parts[1]
                
                if (code[-1] in keyset):
                    game = code[:-1]
                    region = code[-1]
                    if (game not in disjoint_data):
                        disjoint_data[game] = {}
                    
                    disjoint_data[game][region] = {'md5': md5, 'rom': rom, 'name': name}
                
                if ('code' in metadata[md5] and code != metadata[md5]['code']):
                    row = [md5, metadata[md5]['rom'], rom, metadata[md5]['name'], name]
                    row = [str(e) for e in row]
                    for ix, e in enumerate(row):
                        shared_sheet.write(shared_sheet_row, ix, e)
                    shared_sheet_row += 1
                else:
                    metadata[md5]['code'] = code
                    metadata[md5]['rom'] = rom
    
    for k, v in disjoint_data.items():
        if (len(v) > 1):
            md5s = set([v[e]['md5'] for e in v])
            if (len(md5s) > 1):
                key0 = k0 if k0 in v else k2
                key1 = k1 if k1 in v else k2
                row = [v[key0]['md5'], v[key1]['md5'], v[key0]['rom'], v[key1]['rom'], v[key0]['name'], v[key1]['name']]
                row = [str(e) for e in row]
                for ix, e in enumerate(row):
                    disjoint_sheet.write(disjoint_sheet_row, ix, e)
                disjoint_sheet_row += 1
    
    result_wb.save(outfile)
    return 0
    
if __name__ == '__main__':
    sys.exit(main())