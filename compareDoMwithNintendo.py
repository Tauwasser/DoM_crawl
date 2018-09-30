#!/usr/bin/env python3
# coding: utf-8

import os
import sys
import argparse
import csv
import yaml
import xlrd
import xlwt
from re import compile

def main():

    # argument parser
    ap = argparse.ArgumentParser()
    ap.add_argument('DMGlist', help='Excel input file for DMG.')
    ap.add_argument('CGBlist', help='Excel input file for CGB.')
    ap.add_argument('CombinedYaml', help='Combined DoM data in yaml format.')
    ap.add_argument('outfile', help='XLS output file.')
    args = ap.parse_args()

    dmg = args.DMGlist
    cgb = args.CGBlist
    yml = args.CombinedYaml
    results = args.outfile
    
    # read Nintendo master lists
    master_data = dict()
    dmg_book = xlrd.open_workbook(dmg)
    dmg_sheet = dmg_book.sheet_by_name('Sheet1')
    cgb_book = xlrd.open_workbook(cgb)
    cgb_sheet = cgb_book.sheet_by_name('Sheet1')
    
    for sheet in [dmg_sheet, cgb_sheet]:
        # read data per row
        nrow = 0
        for row in sheet.get_rows():
            nrow += 1
            if (nrow == 1):
                # skip header
                continue
            prefix = row[1].value
            game = row[2].value[:-1]
            region = row[2].value[-1]
            revision = row[3].value
            name = row[4].value
            id = row[6].value
            
            code = prefix + '-' + game + region + '-' + revision
            master_data[code] = {
                'prefix': prefix,
                'game': game,
                'region': region,
                'revision': revision,
                'name': name,
                'id': id,
            }
    
    with open(yml, 'r') as f:
        yaml_data = yaml.load(f)
    misses = {'DoM': [], 'Nintendo': []}
    
    for k, v in master_data.items():
        
        prefix = v['prefix']
        game = v['game']
        region = v['region']
        revision = int(v['revision'])
        
        try:
            revision_data = yaml_data[prefix + '-' + game][region][revision]
        except KeyError:
            misses['DoM'].append({'id': v['id'], 'name': v['name'], 'serial': k})
    
    for k, v in yaml_data.items():
        for region in v:
            for revision in v[region]:
                entry = v[region][revision]
                code = entry['code']
                if (code not in master_data):
                    misses['Nintendo'].append({'md5': entry['md5'], 'name': entry['name'], 'is_synthetic': entry['is_synthetic'], 'serial': code})
    
    result_wb = xlwt.Workbook(encoding='UTF-8')
    DoM_sheet = result_wb.add_sheet('DoM misses')
    Nintendo_sheet = result_wb.add_sheet('Nintendo misses')
    
    DoM_sheet.write(0, 0, 'Serial')
    DoM_sheet.write(0, 1, 'ID')
    DoM_sheet.write(0, 2, 'Name')
    
    row = 1
    for entry in misses['DoM']:
        DoM_sheet.write(row, 0, entry['serial'])
        DoM_sheet.write(row, 1, entry['id'])
        DoM_sheet.write(row, 2, entry['name'])
        row += 1
    
    Nintendo_sheet.write(0, 0, 'MD5')
    Nintendo_sheet.write(0, 1, 'Serial')
    Nintendo_sheet.write(0, 2, 'Name')
    Nintendo_sheet.write(0, 3, 'is_synthetic')
    
    row = 1
    for entry in misses['Nintendo']:
        Nintendo_sheet.write(row, 0, entry['md5'])
        Nintendo_sheet.write(row, 1, entry['serial'])
        Nintendo_sheet.write(row, 2, entry['name'])
        Nintendo_sheet.write(row, 3, entry['is_synthetic'])
        row += 1
    
    result_wb.save(results)
    return 0

if __name__ == '__main__':
    sys.exit(main())