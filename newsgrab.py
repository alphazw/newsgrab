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
    result= indexpage.select(rule_url)
    return result

#get href attribution from the given result in a list for <a href=...></a>
def get_href(par):
    tmp_a = []
    for b in par:
        tmp_a.append(b['href'])

    return tmp_a

#Complete url, if the url not starts with domain name, if the base not ends with /, than plus /
#if the url starts with /, than remove /
def completeurl(base, url):

    if not base.endswith('/'): base = base+'/'

    if not url.startswith('base'):
        if url.startswith('/'):
            return base+url[1:]
        else:
            return base+url
    else:
        return url

def test_irecycler():
    url = r"http://www.irecyclingtimes.com/News-list?news_column_id=16_8_9_11_5_17_7_12"
    rule_url = r"table#news_list_tb a"

    print get_href(get_newslist(url,rule_url))

def test_actionintell():
    url = "http://www.action-intell.com/category/news-briefing/"
    rule_url="h1.entry-title a"

    print get_href(get_newslist(url, rule_url))

if __name__ == "__main__":
    # test_irecycler()
    # test_actionintell()
    url =[]
    # url.append([r'http://www.irecyclingtimes.com/News-list?news_column_id=16_8_9_11_5_17_7_12',r'table#news_list_tb a'])
    # url.append([r'http://www.action-intell.com/category/news-briefing/','h1.entry-title a'])
    # url.append([r'http://www.theimagingchannel.com/channel-news','h3 a'])
    # url.append([r'http://www.therecycler.com/latest-news/','h2 a'])
    # url.append(['http://tonernews.com/forums/forum/industry-news/','li.bbp-body ul li.bbp-topic-title a.'])
    url.append(['http://www.rechargeasia.com/index.php/Table/News/3D-Printing/','ul.list_ulList_1 li a'])
    print url
    a=[]
    for u in url:
        a =a + get_href(get_newslist(u[0],u[1]))
    print a
