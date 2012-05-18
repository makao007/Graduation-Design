#coding=utf-8

import psycopg2

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"
conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

table_name = ['webconfig', 'webuser_login_log','webquery_log', 'webscrapy_log', 'webadmin','weburl_content_split', 'webkeywords','weburl_focus','websource','weburls','webfocus', 'webuser']

table_name = ['webconfig', 'webuser_login_log', 'webadmin','weburl_content_split', 'webkeywords','weburl_focus','websource','weburls','webfocus', 'webuser']
for i in table_name :
    sql = "drop table %s " % i
    cur.execute (sql)

conn.commit()
cur.close()
conn.close()
