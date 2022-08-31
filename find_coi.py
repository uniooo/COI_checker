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
parser.add_argument('--years_and_times', type=list, default=[4, 10],
                    help='[a, b] means co-auther >= a times in last b years.')
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

def check(search_years, time_flag = None):
    years = list(map(str,[i for i in range(time.localtime(time.time())[0] - search_years, time.localtime(time.time())[0]+1)]))
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
    result_dict = dict()
    for name in result:
        if(name not in result_dict):
            result_dict[name] = list()
        for coi in result[name]:
            if(time_flag == None):
                result_dict[name].append(coi[0])
            else:
                if(coi[1] >= time_flag):
                    result_dict[name].append(coi[0])
    return result_dict

if __name__ == '__main__':
    args = parser.parse_args()
    names = os.listdir(args.xml_path)
    result_dict1 = check(args.search_years)
    print('co-auther in last', args.search_years, 'year(s):')
    for name in result_dict1:
        print(name, ':', str(result_dict1[name]))
    if(args.years_and_times != []):
        print()
        result_dict2 = check(args.years_and_times[1], time_flag = args.years_and_times[0])
        print('co-auther >=', args.years_and_times[0], 'time(s) in last', args.years_and_times[1], 'year(s):')
        for name in result_dict2:
            print(name, ':', str(result_dict2[name]))
