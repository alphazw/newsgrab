from openpyxl import load_workbook
from bs4 import BeautifulSoup
import requests, re, sqlite3, hashlib
import datetime, smtplib, email

DBFile = '/Users/Mavericks/Documents/newsgrab/data.db'
DEBUG = True

def log(s):
    if DEBUG:
        print s

#generate hash
def generate_hash(text=""):
    return hashlib.sha256(text).hexdigest()

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

def get_article(pageurl, rule_title, rule_content, rule_click, rule_date):
    indexcontent = get_indexpage(indexpage_url)
    indexpage = BeautifulSoup(indexcontent,'lxml')

    article_title= indexpage.select(rule_title)
    article_content = indexpage.select(rule_content)
    article_click = indexpage.select(rule_click)
    article_date = indexpage.select(rule_date)

    return article_title, article_content, article_click, article_date

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

    if not url.startswith(base):
        if url.startswith('/'):
            return base+url[1:]
        else:
            return base+url
    else:
        return url

def retrieveNewlist():
    try:
        conn = sqlite3.connect(DBFile)
        cur = conn.cursor()
        sql_sitelist = 'SELECT name, baseurl,listpageurl, listpageurl_rule, sitelist_id, articletitle_rule, articlecontent_rule, articleclick_rule, articledate_rule FROM sitelist'
        # sql_sitelist = "select * from sitelist"
        cur.execute(sql_sitelist)
        sitelist = cur.fetchall()

        for u in sitelist:
            u_name, u_baseurl, u_listpageurl, u_listpageurl_rule, u_sitelist_id, u_articletitle_rule, u_articlecontent_rule, u_articleclick_rule, u_articledate_rule = u[0], u[1], u[2], u[3], u[4], u[5], u[6], u[7], u[8]
            url_newslist = get_href(get_newslist(u_listpageurl,u_listpageurl_rule))
            # log("_"*20)
            # log('Retrieving NewsList from ')
            # log(u_name)
            # log(u_sitelist_id)
            # log(u_baseurl)
            # log(u_listpageurl)
            # log(u_listpageurl_rule)
            # log("-"*20)
            for u_n in url_newslist:
                u_n = completeurl(u_baseurl, u_n)
                u_hash = generate_hash(u_n)

                if not duplicatecheck(u_hash):
                    sql_newslist = "INSERT INTO newslist (newsurl, sitelist_id, hash, adddate, articletitle_rule, articlecontent_rule, articleclick_rule, articledate_rule ) VALUES (%s,%s,%s,%s.%s,%s,%s)"
                    conn.execute(sql_newslist,(u_articletitle_rule, u_articlecontent_rule, u_articleclick_rule, u_articledate_rule))
                # log(u_n)
                # log(generate_hash(u_n))

        #write result to database
        # for r in result:
        #
        #     r_hash = generate_hash(r)
        #     log("hash %s",r_hash)
        #     duplicatechecksql = "SELECT * FROM newslist WHERE hash = %s"
        #     cur.execute(duplicatechecksql,r_hash)
        #     checkresult = cur.fetchall()
        #
        #     if checkresult == "":
        #         insertsql = "INSERT INTO newslist (newsurl, adddate, hash) VALUES (%s,%s, %s)"
        #         # cur = conn.cursor()
        #         cur.execute(insertsql,(r,datetime.datetime.date(), r_hash))
        #     log(r)
        # # result = []
        # log(urls)
    except sqlite3.Error as e:
        log(e)

    finally:
        cur.close()
        conn.close()
        log("Database Closed")

    return True

#to-do:needs get rule of each urls.
def retrieveNewsContent():
    try:
        conn = sqlite3.connect(DBFile)
        cur = conn.cursor()
        sitelistsql = 'SELECT * from newslist WHERE date=%s'+ datetime.datetime.strftime('Y-M-D')
        
        cur.execute(sitelistsql)
        sitelist = cur.fetchall()

        for u in sitelist:
            
            u_newsurl, u_articletitle_rule, u_articlecontent_rule, u_articleclick_rule, u_articledate_rule = u[1], u[2], u[3], u[4], u[5]
            news_title, news_content, news_click, news_date = get_article(u_newsurl,u_articletitle_rule, u_articlecontent_rule, u_articleclick_rule, u_articledate_rule)

            adddate = datetime.datetime.strftime('Y-M-D')
            u_hash = generate_hash(u)
            insertsql = "INSERT INTO newscontent (title, content, click, articledate, adddate, hash) VALUES(%s, %s, %s, %s, %s, %s )"
            cur.execute(insertsql,(news_title, news_content, news_click, news_articledate, adddate, u_hash))


    except sqlite3.Error as e:
        print e

    finally:
        cur.close()
        conn.close()
        print "database closed"

    return True

def duplicatecheck(hash):
    sql_duplicatecheck = "SELECT * FROM newslist WHERE hash=%s"
    conn.executive(sql_duplicatecheck,hash)
    if conn.fetchall() == None:
        return True
    else:
        return False

# def get_newscontent(newsurl, at_rule, ac_rule, ad_rule, ack_rule):
#     sql_newscontent = "INSERT INTO newscontent (articletitle, articlecontent,  articleclick, articledate, hash, adddate) VALUES(%s, %s, %s, %s, %s, %s)"
#     newscontent = get_article(newsurl, at_rule,ac_rule, ack_rule, ad_rule)
#     hash, adddate = generate_hash(newsurl), datetime.datetime.now().date()

#     conn.executive(sql_newscontent,(newscontent, hash, adddate))


#build reports from the content in the database by selecting by today()
def buildReport():
    sql_report = "SELECT articletitle, articlecontent, articleclick, articledate FROM newscontent WHERE adddate = %s"
    adddate = datetime.datetime.now().date()

    conn.executive(sql_report,adddate)
    contentlist = conn.fetchall()

    for cl in contentlist:
        cl_articletitle, cl_articlecontent, cl_articleclick, cl_articledate = cl[0],cl[1],cl[2],cl[3],c[4]
        cl_brief = generate_brief(cl_articlecontent)

        log("-"*20)
        log(cl_articletitle)
        log(cl_articledate)
        log(cl_brief)
        log("="*10)
        log(cl_articlecontent)

    return True

# sendemail(), used for sending email out using SMTP protocol
def sendemail(username, password, replyfrom, replyto, emailbody):
    try:
        server = smtplib.SMTP('smtp.gmail.com:587')
        server.starttls()
        server.login(username, password)
        server.sendmail(replyfrom, replyto, emailbody)
        server.quit()
    except:
        show_status('unable to reply email to %s' % replyto)


if __name__ == "__main__":
    # test_irecycler()
    # test_actionintell()
    # url =[]
    # url.append([r'http://www.irecyclingtimes.com/News-list?news_column_id=16_8_9_11_5_17_7_12',r'table#news_list_tb a'])
    # url.append([r'http://www.action-intell.com/category/news-briefing/','h1.entry-title a'])
    # url.append([r'http://www.theimagingchannel.com/channel-news','h3 a'])
    # url.append([r'http://www.therecycler.com/latest-news/','h2 a'])
    # url.append(['http://tonernews.com/forums/forum/industry-news/','li.bbp-body ul li.bbp-topic-title a.'])
    # url.append(['http://www.rechargeasia.com/index.php/Table/News/3D-Printing/','ul.list_ulList_1 li a'])
    # print url
    # a=[]
    # for u in url:
    #     a =a + get_href(get_newslist(u[0],u[1]))
    # print a
    retrieveNewlist()
    