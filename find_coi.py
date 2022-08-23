import argparse
from openpyxl import load_workbook
import time
import os
from xml.dom.minidom import parse

parser = argparse.ArgumentParser()
parser.add_argument('--xml_path', type=str, default='./data/',
                    help='the path of files to find coi. Currently only support the xml file from dblp')
parser.add_argument('--search_years', type=int, default=3,
                    help='number of years queried to check for COI.')
parser.add_argument('--pc_file', type=str, default='./data/pc_members.xlsx',
                    help='file with all pc members')

def get_paper(path, query_years):
    xml_data = parse(path)
    rootNode = xml_data.documentElement
    nodes = list(rootNode.getElementsByTagName('article')) + list(rootNode.getElementsByTagName('inproceedings'))
    coi_authors = dict()
    
    for node in nodes:
        year = node.getElementsByTagName('year')[0].childNodes[0].data
        if(year not in query_years):
            continue
        authors = node.getElementsByTagName('author')
        for author in authors:
            name = author.childNodes[0].data.rstrip('0123456789').rstrip()
            if(name not in coi_authors):
                coi_authors[name] = 1
            else:
                coi_authors[name] += 1
    return coi_authors

args = parser.parse_args()
years = list(map(str,[i for i in range(time.localtime(time.time())[0] - args.search_years, time.localtime(time.time())[0]+1)]))
names = os.listdir(args.xml_path)

coi_authors_dict = dict()
for name in names:
    if(name[-4:] != '.xml'):
        continue
    coi_authors_list = get_paper(args.xml_path+name, years)
    coi_authors_dict[name] = coi_authors_list

result = dict()
wb = load_workbook(filename = args.pc_file)
pc_sheet = wb['Sheet1']
for row in pc_sheet.values:
    check_name = row[0]+' '+row[1]
    for name in coi_authors_dict:
        if(check_name in coi_authors_dict[name]):
            if(name not in result):
                result[name] = list()
            result[name].append([check_name, coi_authors_dict[name][check_name]])
for name in result:
    for coi in result[name]:
        print(name + ' : ' + str(coi))
