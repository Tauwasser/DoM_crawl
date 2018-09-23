#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import argparse
from bs4 import BeautifulSoup

def main():

    # argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument('indir', help='Directory containing DoM HTML pages.')
    ap.add_argument('outfile', help='CSV output file.')
    args = ap.parse_args()
    
    indir = args.indir
    outfile = args.outfile
    
    if (not(os.path.isdir(indir))):
        print('Error: input must be a directory!')
        return -1
    
    with open(outfile, 'w', encoding='utf-8') as of:
        for entry in os.scandir(indir):
        
            if (not(entry.name.endswith('.html'))):
                continue
            
            print('Processing {0:s}...'.format(entry.name))
            
            with open(entry.path, 'r', encoding='utf-8') as f:
                contents = f.read()
            
            soup=BeautifulSoup(contents, 'html.parser')
            gameInfo = soup.find('article', id='content')
            if (gameInfo is None):
                print('Warning: {0:s} has no game info. Skipping...'.format(entry.name))
                continue
            
            romName = gameInfo.find('tr', class_='romname_section')
            if (romName is None):
                print('Error: {0:s} has no ROM name info. Skipping...'.format(entry.name))
                continue
            
            romName = next(romName.td.stripped_strings)
            
            if ('[BIOS]' in romName):
                print('Warning: {0:s} is a BIOS. Skipping...'.format(entry.name))
                continue
            if ('(Unl)' in romName):
                print('Warning: {0:s} is a unlicensed. Skipping...'.format(entry.name))
                continue
            if ('(Beta)' in romName or '(Proto)' in romName):
                print('Warning: {0:s} is a beta/prototype. Skipping...'.format(entry.name))
                continue
            
            tables = gameInfo('table', class_='RecordTable')
            dumpTable = None
            for table in tables:
                try:
                    if ('TableTitle' not in table.tr.td['class']):
                        continue
                    if ('Dump(s)' not in table.tr.td.stripped_strings):
                        continue
                    dumpTable = table
                    break
                except:
                    continue
            
            if (dumpTable is None):
                print('Warning: {0:s} has no dump info. Skipping...'.format(entry.name))
                continue
            
            entry = dict()
            for tr in dumpTable('tr', recursive=False):
                tds = list(tr('td', recursive=False))
                if (len(tds) < 3):
                    continue
                field1 = next(tds[1].stripped_strings).rstrip(':')
                try:
                    field2 = next(tds[2].stripped_strings)
                except StopIteration:
                    field2 = ''
                
                if (field1 != 'Type' and 'type' not in entry):
                    # ignore everything until first dump
                    continue
                elif (field1 == 'Type' and 'type' in entry):
                    # write back info so far
                    of.write(entry['md5']+ ';')
                    of.write(romName + ';')
                    for field in ['size', 'type', 'goodDump', 'date', 'datter', 'serial', 'pcb', 'rom', 'stamp']:
                        of.write(entry.get(field, '') + ';')
                    of.write('\n')
                
                fields = {
                    'Media Serial (1)' : 'serial',
                    'Date'             : 'date',
                    'Datter'           : 'datter',
                    'PCB serial(s)'    : 'pcb',
                    'Chip(s) serial(s)': 'rom',
                    'Stamp codes'      : 'stamp',
                    'Size'             : 'size',
                    'MD5'              : 'md5',
                }
                
                if (field1 == 'Type'):
                    entry = {'type': field2, 'goodDump': str(True)}
                    row_css_classes = [e for e in tr['class'] if e]
                    if ('green' not in row_css_classes):
                        print('{0:s}: {1!s}'.format(romName, row_css_classes))
                        entry['goodDump'] = str(False)
                elif (field1 in fields):
                    entry[fields[field1]] = field2
            
            of.write(entry['md5']+ ';')
            of.write(romName + ';')
            for field in ['size', 'type', 'goodDump', 'date', 'datter', 'serial', 'pcb', 'rom', 'stamp']:
                of.write(entry.get(field, '') + ';')
            of.write('\n')
    
if __name__ == '__main__':
    sys.exit(main())
