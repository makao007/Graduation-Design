#coding:utf-8
import psycopg2
import hashlib

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"

conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

cur.execute ("create table if not exists weburls  (id serial primary key, url varchar(1024) not null, title varchar(1000), last_modify char(30), download_time char(30), content text, description varchar(10240) );"); 

# create user infomation
cur.execute ("create table if not exists webuser (id serial primary key, username varchar(100) unique not null, password char(32) not null, created timestamp default now());")

cur.execute ("create table if not exists webfocus (id serial primary key, userid serial references webuser(id) on delete cascade, title varchar(100) not null, created timestamp default now()); ")

cur.execute ("create table if not exists websource (id serial primary key, url varchar(1024), focus_id serial references webfocus (id) on delete cascade); ")

cur.execute ("create table if not exists webkeywords (id serial primary key, word varchar(100) not null, focus_id serial references webfocus (id) on delete cascade); ")

#cur.execute ("insert into webuser (username,password) values (%s,%s)", ('user',hashlib.md5('1234').hexdigest()) )

cur.execute ('select * from webuser;');
result = cur.fetchone()
print result

conn.commit()

cur.close()
conn.close()

