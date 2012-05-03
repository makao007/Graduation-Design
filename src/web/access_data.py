#coding:utf-8
import psycopg2
import hashlib

import scrapy

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"

conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

def pagesave (url, title, desc, text, download_time, last_modify ):
    global cur
    cur.execute ("insert into weburls(url, title, description, content, download_time, last_modify) values (%s,%s,%s,%s,%s,%s) ", (url, title, desc, text, download_time, last_modify))


def get_all_url ():
    global cur
    cur.execute("select distinct(url) from websource")
    result = cur.fetchall()
    return [url[0] for url in result]

#url, save_func, match_url, max_deep, max_page
scr = scrapy.Scrapy('', pagesave,'',2,100)
scr.join_queue(get_all_url())
scr.start_scrapy()


conn.commit()
cur.close()
conn.close()
