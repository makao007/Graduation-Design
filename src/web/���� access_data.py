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

def save_splited (url_id, title, description, content):
    #delete odl record
    cur.execute ("delete from weburl_content_split where url_id = %s ;" % url_id)

    #add new splited record
    sql = "insert into weburl_content_split (url_id, title, description, content) values (%s,%s,%s,%s) ;"
    cur.execute (sql , (url_id, title, description, content))
    
    #update weburls table flag
    cur.execute ("update weburls set splited = true where id=%s ;" , (url_id,))

    conn.commit()


def split_word ():
    sql = "select id,title,description,content from weburls where splited=false"
    cur.execute (sql)
    result = cur.fetchall()
    for i in result:
        title = split_cn.split_text(i[1])
        descr = split_cn.split_text(i[2])
        conte = split_cn.split_text(i[3])
        save_splited (i[0], title, descf, conte)


conn.commit()
cur.close()
conn.close()
