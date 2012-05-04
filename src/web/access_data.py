#coding:utf-8
import psycopg2
import hashlib

import scrapy
import split_cn

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"

conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

def pagesave (url, title, desc, text, download_time, last_modify ):
    global cur

    cur.exeute ("delete from weburls where url = %s ;" % url)

    cur.execute ("insert into weburls(url, title, description, content, last_modify) values (%s,%s,%s,%s,%s,%s) ", (url, title, desc, text, last_modify))

# check the url in the database , update time default 60 minute
def check_db_url (url, update_time = 60):
    sql = "select id from weburls where url=%s and download_time < current_timestamp - interval '%s minutes' ;"
    cur.execute (sql % (url, update_time))
    if cur.fetchone():
        return True
    else:
        return False

def get_all_url ():
    global cur
    cur.execute("select distinct(url) from websource")
    result = cur.fetchall()
    return [url[0] for url in result]

def save_splited (url_id, title, description, content):
    #delete odl record
    cur.execute ("delete from weburl_content_split where url_id = %s ;" % url_id)

    #add new splited record
    sql = "insert into weburl_content_split (url_id, title, description, content) values (%s,%s,%s,%s) ;"
    cur.execute (sql % (url_id, title, description, content))
    
    #update weburls table flag
    cur.execute ("update weburls set splited = true where id=%s ;" % url_id)


def split_word ():
    sql = "select id,title,description,content from weburls where splited=false"
    cur.execute (sql)
    result = cur.fetchall()
    for i in result
        title = split_cn.split_text(i.title)
        descr = split_cn.split_text(i.descrption)
        conte = split_cn.split_text(i.content)


#url, save_func, match_url, max_deep, max_page
scr = scrapy.Scrapy('', pagesave,'',2,100)
scr.join_queue(get_all_url())
scr.start_scrapy()


conn.commit()
cur.close()
conn.close()
