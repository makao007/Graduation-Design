#coding=utf-8

import psycopg2

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"
conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

cur.execute ("drop table weburl_content_split")
cur.execute ("drop table webkeywords")
cur.execute ("drop table weburl_focus")
cur.execute ("drop table websource")
cur.execute ("drop table weburls")
cur.execute ("drop table webfocus")
cur.execute ("drop table webuser")

conn.commit()
cur.close()
conn.close()
