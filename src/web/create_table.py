#coding:utf-8
import psycopg2
import hashlib

dbname = "webpy"
dbuser = "webpy"
dbpawd = "1234"

conn = psycopg2.connect(database=dbname, user=dbuser, password=dbpawd, host='localhost', port=5432)
cur  = conn.cursor()

cur.execute ("create table if not exists weburls  (id serial primary key, url varchar(1024) not null, title varchar(1024), last_modify char(30), download_time timestamp default now(), content text, description varchar(10240), splited boolean default false); ")

# create user infomation
cur.execute ("create table if not exists webuser (id serial primary key, username varchar(100) unique not null, password char(32) not null, created timestamp default now());")

cur.execute ("create table if not exists webfocus (id serial primary key, userid serial references webuser(id) on delete cascade, title varchar(100) not null, created timestamp default now()); ")

cur.execute ("create table if not exists websource (id serial primary key, url varchar(1024), focus_id serial references webfocus (id) on delete cascade); ")

cur.execute ("create table if not exists webkeywords (id serial primary key, word varchar(100) not null, focus_id serial references webfocus (id) on delete cascade); ")

cur.execute ("create table if not exists weburl_focus(url_id serial references weburls (id) on delete cascade ,focus_id serial references webfocus (id) on delete cascade); ")

cur.execute ("create table if not exists weburl_content_split (id serial primary key, url_id serial references weburls (id), title varchar(2048), content text, description varchar(10240)); ")

cur.execute ("create table if not exists webadmin (id serial primary key, username varchar(20) not null unique, password char(32) not null, created timestamp default now() );")

cur.execute ("create table if not exists webconfig (id serial primary key, config varchar(1024), created timestamp default now()) ; ")

#cur.execute ("create table if not exists webquery_log (id serial primary key , 

#cur.execute ("insert into webuser (username,password) values (%s,%s)", ('user',hashlib.md5('1234').hexdigest()) )
cur.execute ("insert into webadmin (username,password) values (%s,%s)", ('user',hashlib.md5('1234').hexdigest()) )

cur.execute ('select * from webuser;');
result = cur.fetchone()
print result

conn.commit()

cur.close()
conn.close()


