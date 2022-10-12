import argparse
from openpyxl import load_workbook
import time
import os
import sys
from xml.dom.minidom import parse
import requests
import shutil
from dblp_xml import dblp_xml_dict

root_path, _ = os.path.split(os.path.abspath(__file__))
parser = argparse.ArgumentParser()
parser.add_argument('--search_years', type=int, default=2,
                    help='number of years queried to check for COI.')
parser.add_argument('-n', '--times_and_years', nargs='+', default=[],
                    help='[a, b] means co-auther >= a times in last b years.')
parser.add_argument('--pc_file', type=str, default=root_path+'/data/pc_members.xlsx',
                    help='file with all pc members')

class Logger(object):
    def __init__(self, file_path: str = "./Default.log"):
        self.terminal = sys.stdout
        self.log = open(file_path, "a")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass

def save_xml(xml_dict):
    if(not os.path.exists(root_path+'/tmp')):
        os.mkdir(root_path+'/tmp')
    for idx in xml_dict:
        r = requests.get(xml_dict[idx])
        with open (root_path+'/tmp/{}.xml'.format(idx), 'wb') as f:
            f.write(r.content)
            f.close()
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
    args.xml_path = root_path+'/tmp/'
    print(args)
    save_xml(dblp_xml_dict)
    names = os.listdir(args.xml_path)
    result_dict1 = check(args.search_years)

    if(os.path.exists(root_path+'/result.txt')):
        os.remove(root_path+'/result.txt')
    sys.stdout = Logger(root_path+'/result.txt')
    
    print('co-auther in last', args.search_years, 'year(s):')
    for name in result_dict1:
        print(name, ':', str(result_dict1[name]))
    if(args.times_and_years != []):
        args.times_and_years = list(map(int, args.times_and_years))
        print()
        result_dict2 = check(args.times_and_years[1], time_flag = args.times_and_years[0])
        print('co-auther >=', args.times_and_years[0], 'time(s) in last', args.times_and_years[1], 'year(s):')
        for name in result_dict2:
            print(name, ':', str(result_dict2[name]))
    
        print('\nTotal result:')
        for name in result_dict1:
            print(name,':')
            tmp_set = set()
            tmp_set.update(result_dict1[name])
            tmp_set.update(result_dict2[name])
            print(tmp_set)
            print()
    shutil.rmtree(root_path+'/tmp')