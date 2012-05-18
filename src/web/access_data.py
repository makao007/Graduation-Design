# coding=utf-8

import psycopg2
import hashlib
import thread
import time
import json,urllib

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

def pagesave (url, title, desc, text, download_time, last_modify, focus_id ):
    global cur,conn
    title = utf8(title)
    desc  = utf8(desc)
    text  = utf8(text)
    url   = utf8(url)
    cur.execute ("delete from weburls where url=%s ;" , (url,))

    
    try:
        cur.execute ("insert into weburls(url, title, description, content, last_modify) values (%s,%s,%s,%s,%s) RETURNING id;", (url, title, desc, text, last_modify))

        temp = cur.fetchone()[0]    #url_id

        cur.execute ("insert into weburl_focus (url_id, focus_id) values (%s, %s) ; " , (temp, focus_id)) 
    except:
        print url, title,desc
        pass

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
    sql = "select url from weburls where download_time > current_timestamp - interval '%s hours' ;"
    cur.execute (sql , (update_time,))
    return [i[0] for i in cur.fetchall()]

def get_all_urls (focus_id):
    global cur
    cur.execute ("select distinct(url) from websource where focus_id = %s ;", (focus_id,))
    return [i[0] for i in cur.fetchall()]

def get_all_fid ():
    global cur
    cur.execute ("select id from webfocus ")
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

def save_scrapy_log (data):
    if data.get('visited_len') == 1:
        return
    cur.execute ("insert into webscrapy_log (content) values (%s);" , (urllib.quote(json.dumps(data)),))
    conn.commit()

#url, save_func, match_url, max_deep, max_page
def scrapy_content(config,fid):
            scr = scrapy.Scrapy('', pagesave,fid,'',int(config.get('max_deep')),int(config.get('max_page')))
            scr.join_visited(get_visited_urls(int(config.get('keep_time'))))
            scr.join_queue(get_all_urls(fid))
            data = scr.start_scrapy()        #begin scrapy 
            save_scrapy_log (data)

        #time.sleep(config.get('sleep'))


def load_config ():
    cur.execute("select * from webconfig where id=1")
    result = cur.fetchone()
    if result:
        result = json.loads(urllib.unquote(result[1]))
    else:
        result = {'max_page': 100, 'max_deep': 2, 'scy_stop': 60, 'search_num': 20, 'keyword_num': 10, 'scy_wait': 10}

    import socket
    socket.setdefaulttimeout(int(result.get('scy_wait')))
    return result

def go ():
    while 1:
        focus_id = get_all_fid()
        for fid in focus_id:
            config = load_config()
            scrapy_content (config,fid)
            split_word (config)
            print 'sleep %s seconds ' % config.get('scy_stop')
            time.sleep(int(config.get('scy_stop')))
        if len(focus_id):
            print 'sleep %s seconds ' % config.get('scy_stop')
            time.sleep(int(config.get('scy_stop')))

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
