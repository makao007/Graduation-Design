#coding:utf-8
import psycopg2
import hashlib

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"
db_query = "dbname=%s user=%s password=%s" % (dbname,dbuser,dbpawd)

#conn = psycopg2.connect(db_query)
conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

cur.execute ("create table webuser (id serial primary key, username varchar(100) unique not null, password char(32) not null, created timestamp default now());")


us1 = 'user'
pw1 = hashlib.md5('1234').hexdigest()
cur.execute ("insert into webuser (username,password) values (%s,%s)", (us1,pw1) )

cur.execute ('select * from webuser;');
result = cur.fetchone()
print result

conn.commit()

cur.close()
conn.close()


