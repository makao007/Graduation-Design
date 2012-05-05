# coding=utf-8

import psycopg2
import hashlib
import thread
import time

from pymmseg import mmseg

import scrapy
import split_cn

def utf8(s):
        try:
            ss = s.decode('gbk').encode('utf-8')
        except:
            try:
                ss = s.decode('gb2312').encode('utf-8')
            except:
                try:
                    ss = unicode(s, 'utf-8')
                except:
                    try:
                        ss = s.encode('utf-8')
                    except:
                        ss = s
        return ss

def pagesave (url, title, desc, text, download_time, last_modify ):
    global cur,conn
    print url,title
    title = utf8(title)
    desc  = utf8(desc)
    text  = utf8(text)
    cur.execute ("delete from weburls where url=%s ;" , (url,))

    cur.execute ("insert into weburls(url, title, description, content, last_modify) values (%s,%s,%s,%s,%s) RETURNING id;", (url, title, desc, text, last_modify))
    #cur.execute ("insert into weburls(url, title) values (%s,%s) RETURNING id;", (url, title))

    #cur.execute  ("insert into weburls (url, title, description, content, last_modify) values (%s,utf8(%s,%s,%s,%s) ; ", (url, title, desc, text, last_modify,))

    temp = cur.fetchone()[0]    #url_id

    cur.execute ("select focus_id from websource where url=%s ;", (url,))
    for i in cur.fetchall():
        cur.execute ("insert into weburl_focus (url_id, focus_id) values (%s, %s) ; " , (temp, i[0])) 

    conn.commit()

# check the url in the database , update time default 60 minute
def check_db_url (url, update_time = 60):
    sql = "select id from weburls where url=%s and download_time < current_timestamp - interval '%s minutes' ;"
    cur.execute (sql , (url, update_time))
    if cur.fetchone():
        return True
    else:
        return False

def get_visited_urls (update_time = 60):
    sql = "select url from weburls where download_time > current_timestamp - interval '%s minutes' ;"
    cur.execute (sql , (update_time,))
    return [i[0] for i in cur.fetchall()]

def get_all_urls ():
    global cur
    cur.execute("select distinct(url) from websource ;")
    return [i[0] for i in cur.fetchall()]

def save_splited (url_id, title, description, content):
    #delete odl record
    cur.execute ("delete from weburl_content_split where url_id = %s ;", (url_id,))

    #add new splited record
    sql = "insert into weburl_content_split (url_id, title, description, content) values (%s,%s,%s,%s) ;"
    cur.execute (sql , (url_id, title, description, content))
    
    #update weburls table flag
    cur.execute ("update weburls set splited = true where id=%s ;" , (url_id,))

    print 'split word ', url_id

    conn.commit()

def split_word_text (s):
    result = []
    algor = mmseg.Algorithm(s)    
    for tok in algor:    
        result.append (tok.text)
    return ' '.join(result)


def split_word (config):
        #while 1:
        sql = "select id,title,description,content from weburls where splited=false"
        cur.execute (sql)
        result = cur.fetchall()
        for i in result:
            #title = split_cn.split_text(i[1])
            #descr = split_cn.split_text(i[2])
            #print len(i[3]),title, descr
            #conte = split_cn.split_text(i[3])

            title = split_word_text(i[1])
            descr = split_word_text(i[2])
            conte = split_word_text(i[3])

            save_splited (i[0], title, descr, conte)

        #time.sleep(config.get('sleep'))

#url, save_func, match_url, max_deep, max_page
def scrapy_content(config):
        #while 1:
        scr = scrapy.Scrapy('', pagesave,'',2,100)
        scr.join_visited(get_visited_urls())
        scr.join_queue(get_all_urls())
        scr.start_scrapy()        #begin scrapy 
        print 'scrapy done. wait ... %d seconds' % config.get('sleep')

        #time.sleep(config.get('sleep'))


def go ():
    config = {'sleep':3*6}
    while 1:
        scrapy_content (config)
        split_word (config)
        time.sleep(config.get('sleep'))
    #thread.start_new_thread(scrapy_content, (config,))
    #thread.start_new_thread(split_word, (config,))



if __name__ == "__main__":

    dbname = "webpy"
    dbuser = "webpy"
    dbpawd = "1234"
    conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
    cur  = conn.cursor()

    mmseg.dict_load_defaults()   #split chinese word

    go()
    
    conn.commit()
    cur.close()
    conn.close()
