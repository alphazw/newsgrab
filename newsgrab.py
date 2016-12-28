#
# Update:
#
# 2016-12-20
# + New

from openpyxl import load_workbook
from bs4 import BeautifulSoup
import requests, re
import datetime
RuleFN = 'rulelist.xlsx'


#Build file name with today's date
def get_todayFN():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

#get the rule list from a given excel workbook, return the value of the value into a dict
def get_rulelist(FN):
    wb = load_workbook(filename=FN, read_only=True)
    ws = wb['Sheet1']
    (RL,RW) = ([],[])

    for row in ws.rows:
        for cell in row:
            RW.append(cell.value)

        RL.append(RW)
        RW = []

    return RL

def get_indexpage(url):
    header = {'Accept-Language':'zh-CN,zh;q=0.8','User-Agent':'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36','Connection':'close','Referer': 'https://www.baidu.com/'}
    indexpage =  requests.get(url,headers=header)
    return indexpage.content

#get a newslist from the listpage by applying the rule_url
def get_newslist(indexpage_url, rule_url):
    indexcontent = get_indexpage(indexpage_url)
    indexpage = BeautifulSoup(indexcontent,'lxml')
    p= indexpage.select(rule_url)
    # p = re.compile(rule_url, re.S)
    #alllist = re.findall(p, indexpage)

    return p

def trans2list(par):
    a = []
    for b in par:
        a.append(b['href'])

    return a

def test_irecycler():
    url = r"http://www.irecyclingtimes.com/News-list?news_column_id=16_8_9_11_5_17_7_12"
    rule_url = r"table#news_list_tb a"

    print trans2list(get_newslist(url,rule_url))

if __name__ == "__main__":
    test_irecycler()
