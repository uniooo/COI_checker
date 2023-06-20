import time
from xml.dom.minidom import parseString
from js import XMLHttpRequest, document, FileReader
from pyscript import Element
import asyncio
from pyodide import create_proxy
from io import BytesIO
import panel as pn
import pandas as pd
from panel.io.pyodide import show
import os

fileInput = pn.widgets.FileInput(accept='.xlsx,.xls')
uploadButton = pn.widgets.Button(name='start COI check!', button_type = 'primary')
table = pn.widgets.Tabulator(pagination='remote', page_size=10)

def process_file(event):
    os.system('cls' if os.name=='nt' else 'clear')
    if fileInput.value is not None:
        xlsx_file = pd.read_excel(BytesIO(fileInput.value), header=None)
        print('read pc members finished')
        start(xlsx_file)
    else:
        print('upload pc members excel file!')
        raise
async def wait_show():
    await show(fileInput, 'fileinput')
    await show(uploadButton, 'upload')
uploadButton.on_click(process_file)
asyncio.ensure_future(wait_show())

def get_paper(url, query_years):
    # xml_data = parse(url)
    req = XMLHttpRequest.new()
    req.open("GET", url, False)
    req.send(None)
    xml_data = parseString(str(req.response))
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

def check(search_years, dblp_dict, xlsx_file, time_flag = None):
    years = list(map(str,[i for i in range(time.localtime(time.time())[0] - search_years, time.localtime(time.time())[0]+1)]))
    coi_authors_dict = dict()
    for name in dblp_dict.keys():
        url = dblp_dict[name]
        coi_authors_list = get_paper(url, years)
        coi_authors_dict[name] = coi_authors_list
    result = dict()
    
    try:
        for row in xlsx_file.itertuples():
            check_name = row[1]+' '+row[2]
            for name in coi_authors_dict:
                if(check_name in coi_authors_dict[name]):
                    if(name not in result):
                        result[name] = list()
                    result[name].append([check_name, coi_authors_dict[name][check_name]])
    except:
        print('There seems to be a problem with the pc member excel file!')
        raise
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

def start(xlsx_file):
    print('----------------------------')
    try:
        search_years_elem = Element("years")
        search_years = int(search_years_elem.value)
    except:
        print('please input currect search year!')
        raise
    try:
        dblp_xml = Element('dblp')
        dblp = dblp_xml.value
        if(dblp[0] != '{' and dblp[-1] != '}'):
            dblp = '{' + dblp + '}'
        dblp_xml_dict = eval(dblp)
    except:
        print('dblp xml input error!')
        raise
    times_and_years_elem = [Element("times"), Element("times-years")] #the number of co-auther times and years. e.g., 4 times in 
    times_and_years = [times_and_years_elem[0].value, times_and_years_elem[1].value]
    if(times_and_years[0] == '' or times_and_years[1] == ''):
        times_and_years = []
    else:
        times_and_years = list(map(int, times_and_years))
    print('start! search years:', search_years, 'times and years', times_and_years)
    
    names = dblp_xml_dict.keys()
    print(names)
    result_dict1 = check(search_years, dblp_xml_dict, xlsx_file)
    print('co-auther in last', search_years, 'year(s):')
    for name in result_dict1:
        print(name, ':', str(result_dict1[name]))
    if(times_and_years != []):
        times_and_years = times_and_years
        print()
        result_dict2 = check(times_and_years[1], dblp_xml_dict, xlsx_file, time_flag = times_and_years[0])
        print('co-auther >=', times_and_years[0], 'time(s) in last', times_and_years[1], 'year(s):')
        for name in result_dict2:
            print(name, ':', str(result_dict2[name]))
    
        print('\nTotal result:')
        for name in result_dict1:
            print(name,':')
            tmp_set = set()
            tmp_set.update(result_dict1[name])
            tmp_set.update(result_dict2[name])
            print(tmp_set)
    print('----------------------------\n')
