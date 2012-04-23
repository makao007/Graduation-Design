#coding:utf-8
import psycopg2
import hashlib

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"

conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

# create user infomation table
cur.execute ("create table if not exists webuser (id serial primary key, username varchar(100) unique not null, password char(32) not null, created timestamp default now());")

us1 = 'user'
pw1 = hashlib.md5('1234').hexdigest()
cur.execute ("insert into webuser (username,password) values (%s,%s)", (us1,pw1) )

cur.execute ('select * from webuser;');
result = cur.fetchone()
print result

# create item table
cur.execute ("create table if not exists webfocus (id serial primary key, userid serial references webuser(id), title varchar(100) not null, keywords varchar(200) not null; sources varchar(1024) not null, created timestamp default now()); ")

# create urls talbe
cur.execute ("create table if not exists weburls  (id serial primary key, url varchar(1024) not null, title varchar(1000), indexed boolean default false, created timestamp default now()); "); 

#create website content table
cur.execute ("create table if not exists webcontents (id serial primary key, urlid serial references weburls(id), content text ); ")



cur.

conn.commit()

cur.close()
conn.close()


