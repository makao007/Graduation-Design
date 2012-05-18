#!/user/bin/env python
#coding=utf-8

import web
import json
import hashlib
import time
import re
import urllib

#web.config.debug = False
web.config.session_parameters['timeout'] = 3600

db = web.database(dbn='postgres', user='webpy', pw='1234', db='webpy')
render = web.template.render('templates/')

urls = (
    '/', 'index',
    '/test', 'mytest',
    '/login', 'login', 
    '/logout', 'logout',
    '/islogin', 'islogin',
    '/add_cate','add_cate',
    '/del_cate','del_cate',
    '/categorys', 'categorys',
    '/relative',  'relative',
    '/search', 'search',
    '/favicon.ico', 'favicon',
    '/admin', 'admin',
    '/all_user', 'user_all',
    '/add_user','add_user',
    '/del_user','del_user',
    '/search_log','search_log',
    '/scrapy_log','scrapy_log',
    '/login_log','login_log',
    '/query_log','query_log',
    '/config_qry','config_qry',
    '/config_sav','config_sav',
    '/password', 'password',
    '/admin_is_login','admin_is_login',
    '/admin_login','admin_login',
    '/admin_logout','admin_logout',
    '/update_admin_password','admin_update_password',
    )

app = web.application (urls, locals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'is_login': False, 'username':'', 'user_id': -1, 'isadmin':False, 'admin_id': -1 } )
    web.config._session = session
else:
    session = web.config._session

#session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'is_login':False,'username':''})

def response (flag, text) :
    return """{"status":%s, "text":"%s" }""" % (flag, text)

def to_login():
    if not session.is_login or session.user_id < 0:
        raise web.seeother('/')

def check_user_cate (uid, fid):
    temp = dict(user_id=uid, focus_id=fid)
    result = db.select ('webfocus', temp, where="id=$focus_id and userid=$user_id", limit=1) 
    if result:
        return True
    else:
        return False

def md5 (s):
    return hashlib.md5(s).hexdigest()

class index:
    def GET(self):
        #return 'hello world'
        return render.index()

class add_user:
    def GET(self):
        info = web.input()
        user = str(info.get('user')).strip()
        pawd = str(info.get('pawd1')).strip()
        pawd = md5(pawd)
        temp = dict(name=user)
        if len(db.select ('webuser', temp,where="username=$name", limit=1))>0:
            return response(0,'user exists')
        else:
            db.insert ('webuser',username=user, password=pawd)
            session.is_login = True
            session.username = user
            return response(1,'add user successful')

class login:
    def GET(self):
        #if (session.is_login):
        #   return response(1,session.username)
        info = web.input()
        user = info.get('username').strip()
        pawd = md5(info.get('password','').strip())
        temp = dict(name=user,pawd=pawd)
        result = db.select ('webuser', temp, where="username=$name and password=$pawd", limit=1) 
        if len(result) > 0:
            session.is_login = True
            session.username = user
            session.user_id  = result[0].id

            # add login log
            db.insert ('webuser_login_log', uid=session.user_id,  username=session.username, operation='1')

            return response(1, user)
        else:
            return response(0, 'login fail')

class islogin:
    def GET(self):
        if (session.is_login and session.user_id > -1):
            return response(1, session.username)
        else :
            return response(0, '')

class logout:
    def GET (self):
        if session.is_login :
            db.insert ('webuser_login_log', uid=session.user_id,  username=session.username, operation='2')
        session.kill()
        return 'logout'


class mytest:
    def GET (self):
        result = db.select ("webfocus")
        data   = [i.title for i in result]
        return json.dumps({'titie':data,'userid':session.user_id})
        #return session.user_id

class del_cate:
    def GET (self):
        to_login()
        id = web.input().get ('id')
        if id:
            if not check_user_cate (session.user_id, id):
                return response(0, 'current user not have this category')
            tmp = "id=%s" % id
            if db.delete ('webfocus', where = tmp):
                return response (1, 'delete category succ')
            else:
                return response (0, 'delete fail')

#add or edit cate
class add_cate:
    def GET (self):
        to_login()
        input = web.input()
        id    = input.get('id').strip()
        title = input.get('title').strip()
        keys  = input.get('keys').strip().replace(';','\n').replace('\n\n','\n').split('\n')
        srcs  = input.get('sources').strip().replace(';','\n').replace('\n\n','\n').split('\n')
        

        if not id:
            #add focus
            temp = db.insert ('webfocus', userid= session.user_id, title= title)
        else:
            #edit focus
            if not check_user_cate (session.user_id, id):
                return response(0, 'current user not have this category')

            tmp1 = "id=%s" % id 
            tmp2 = "focus_id=%s" % id 

            db.update ('webfocus', where= tmp1, title = title )

            db.delete ('websource', where= tmp2 )
            db.delete ('webkeywords', where= tmp2 )

            temp = id

        #add source
        for url in srcs:
            if url.startswith('http://') or url.startswith('https://'):
                pass
            else:
                url = 'http://' + url.strip()
            db.insert ('websource',  url= url, focus_id = temp)

        #add keyword
        for keyword in keys:
            word = keyword.strip()
            db.insert ('webkeywords', word=word, focus_id = temp)

        return response(1,'add focus succ')

def get_user_info_template(sql, user_id, step):
    source = db.query(sql, vars={'userid':user_id})
    ss = {}
    for i in source:
        val = i.id
        if ss.has_key(val):
            ss[val] += i.url + step
        else:
            ss[val]  = i.url + step
    return ss
    

def get_user_source (user_id,step='\n'):
    sql = "select webfocus.id as id,websource.url as url from webfocus,websource where webfocus.userid=$userid and webfocus.id = websource.focus_id";
    return get_user_info_template (sql, user_id, step)


def get_user_keyword (user_id, step='\n'):
    sql = "select webfocus.id as id,webkeywords.word as url from webfocus,webkeywords where webfocus.userid=$userid and webfocus.id = webkeywords.focus_id"
    return get_user_info_template(sql, user_id, step)

def get_user_focus_id (user_id):
    sql = "select id from webfocus where userid=$userid"
    result = db.query(sql, vars={'userid':user_id})
    return [i.id for i in result]

class categorys:
    def GET (self):
        to_login()
        user_id = session.user_id
        
        tmp1 = dict (userid=user_id)
        category = db.select ('webfocus', tmp1, where="userid=$userid",order="created DESC")


        step = '\n'
        
        ss1 = get_user_source(user_id)
        ss2 = get_user_keyword(user_id)

        ss3 = []
        for k in category:
            ss3.append ( [k.id, k.title, ss1.get(k.id,''), ss2.get(k.id,'')] )

        #web.header('Content-type', 'application/json')
        web.header('Content-type','text/javascript')
        data = json.dumps({'name_info': ss3})

        #jsonp
        return web.input().get('callback') + '(' + data + ');'

def search_with_focus (fid, keyword, offset=0, num=15):
        # no index
        #sql = "select weburls.title, weburls.description, weburls.download_time, weburls.url from weburls,weburl_focus, weburl_content_split where weburl_focus.focus_id=$fid and weburl_focus.url_id=weburl_content_split.url_id and weburls.id=weburl_content_split.url_id and to_tsvector(weburl_content_split.title|| weburl_content_split.description) @@ to_tsquery($keyword) limit 15;"

        # with index
        sql = "select weburls.title, weburls.description, weburls.download_time, weburls.url from weburls,weburl_focus, weburl_content_split where weburl_focus.focus_id=$fid and weburl_focus.url_id=weburl_content_split.url_id and weburls.id=weburl_content_split.url_id and weburl_content_split.textsearchable_index_col @@ to_tsquery($keyword) limit $numu offset $offset;"
        temp = db.query(sql, vars={'fid':fid, 'keyword': keyword.replace(' ','\ '), 'numu':num, 'offset':offset})
        focus_result = []
        for tmp  in temp:
            focus_result.append ([tmp.download_time.__str__()[:-7], tmp.title, tmp.description, tmp.url])
        return focus_result 

class relative:
    def GET (self):
        to_login()
        user_id = session.user_id
        
        fid = web.input().get('fid')
        num = int(web.input().get('num','15'))
        offset = int(web.input().get('offset','0')) * num

        if fid :
            focus_id = [int(fid)]
        else: 
            focus_id= get_user_focus_id(user_id)
        ss2 = get_user_keyword(user_id,'|')
        
        result = {}
        for fid in focus_id:
            result[fid] = search_with_focus (fid, ss2.get(fid,'')[:-1],offset,num)

        return response_json (result)

def response_json (result):
    web.header('Content-type','text/javascript')
    data = json.dumps(result)
    if web.input().get('callback'):
        return web.input().get('callback') + '(' + data + ');'    #jsonp
    else:
        return result


class search :
    def GET (self):
        search_num = 15 
        t1 = time.time()
        word = web.input().get('word','').strip()
        if not word:
            result = {'word': word, 'data': [], 'time':0}
            return response_json (result)

        for i  in word.split(' '):
            db.insert ('webquery_log', word=i)
        match_field = ''
        if web.input().get('cb_title') and web.input().get('cb_title')=='1' :
            match_field += 'weburl_content_split.title||'
        if web.input().get('cb_desc') and web.input().get('cb_desc')=='1' :
            match_field += 'weburl_content_split.description||'
        if web.input().get('cb_content') and web.input().get('cb_content')=='1' :
            match_field += 'weburl_content_split.content'
        if not match_field:
            match_field = 'weburl_content_split.title'
        if match_field.endswith('||'):
            match_field = match_field[:-2]

        offset = int(web.input().get('offset',0)) * search_num

        word = re.sub(r"\s+",'&',word)
        sql = "select weburls.title, weburls.description, weburls.download_time, weburls.url from weburls, weburl_content_split where weburls.id=weburl_content_split.url_id and %s @@ to_tsquery($keyword) limit %s offset %s ;" % (match_field, search_num, offset)
        temp = db.query(sql, vars={'keyword': word})
        word_result= []
        for tmp  in temp:
            word_result.append ( [tmp.download_time.__str__()[:-7], tmp.title, tmp.description, tmp.url ] )

        t2 = time.time()
        result = {'word': word, 'data': word_result, 'time':t2-t1}
        return response_json (result)

def to_admin():
    if session.isadmin:
        return True
    else:
        raise web.seeother ('/')

class admin:
    def GET (self):
        return render.admin()

class admin_is_login :
    def GET (self):
        if session.isadmin:
            return response (1,'admin')
        else:
            return response (0, 'admin login first')

class admin_login :
    def GET (self):
        username = web.input().get('username','').strip()
        password = web.input().get('password','').strip()
        password = md5(password)
        temp = dict (user=username, pawd=password)
        result = db.select ('webadmin', temp, where="username=$user and password=$pawd") 
        if result:
            session.isadmin = True
            session.admin_id = result[0].id
            return response (1, 'login succeful')
        else:
            return response (0, 'login fail')

class admin_logout:
    def GET (self):
        session.isadmin = False
        raise web.seeother('/admin')

class admin_update_password:
    def GET (self):
        to_admin()
        admin_id = session.admin_id
        old_password = md5(web.input().get('password0','').strip())
        new_password = md5(web.input().get('password1','').strip())
        if old_password and new_password:
            temp = "id=%s and password='%s'" % (admin_id,old_password)
            tmp  = dict(id=admin_id, pw=old_password)
            result = db.select('webadmin', where=temp)
            if result :
                db.update ('webadmin', where=temp, password=new_password)
                return response (1, 'change password succ')
            else:
                return response (0, 'change password fail')
        else:
            return response (0, 'old and new password must not be empty')

class config_qry:
    def GET (self):
        to_admin()
        result = db.select ('webconfig',where="id=1", limit=1,what='config') 
        if result:
            return response(1,result[0].config)
        else:
            return response(0,'no config info')

class config_sav:
    def GET (self):
        to_admin()
        config = {}	
        config['max_page'] = web.input().get('max_page')
        config['max_deep'] = web.input().get('max_deep')
        config['scy_wait'] = web.input().get('scy_wait')
        config['scy_stop'] = web.input().get('scy_stop')
        config['search_num']  = web.input().get('search_num')
        config['keyword_num'] = web.input().get('keyword_num')
        config['keep_time']   = web.input().get('keep_time')

        text = urllib.quote(json.dumps(config))
        if db.update ('webconfig', where="id=1", config = text):
            return response(1, text)
        else :
            return response(0, 'save error')

class login_log :
    def GET (self):
        to_admin()
        offset = web.input().get('page','0').strip()
        max_page = 20
        tmp = db.select ('webuser_login_log', order="id desc", offset=offset, limit = max_page)
        result = [[i.created.__str__()[:-7], i.uid, i.username,i.operation] for i in tmp]

        return json.dumps(result)

class query_log :
    def GET (self):
        to_admin()
        max_page = 10
        #last 24 hour
        sql = "select word,count(id) as mid from webquery_log where created > current_timestamp - interval '%s hours' group by (word) order by mid desc limit %s";
        tmp1 = db.query ( (sql % (24, max_page)))
        result1 = [[i.mid, i.word] for i in tmp1]

        tmp2 = db.query ( (sql % (24*7, max_page)))
        result2 = [[i.mid, i.word] for i in tmp2]

        tmp3 = db.query ( (sql % (24*30, max_page)))
        result3 = [[i.mid, i.word] for i in tmp3]

        return json.dumps ([result1, result2, result3])

class user_all :
    def GET (self):
        to_admin()
        tmp = db.select ('webuser')
        result = [[i.id, i.username, i.created.__str__()[:-7]] for i in tmp]
        return json.dumps (result)

class del_user  :
    def GET (self):
        to_admin()
        id = web.input().get('id')
        tmp = db.delete ('webuser', where=('id='+id) )
        if tmp:
            return response(1, 'delete user succ')
        else:
            return response(0, 'delete user fail')

class scrapy_log:
    def GET (self):
        to_admin()
        tmp = db.select ('webscrapy_log', limit=20, what='content')
        result = [json.loads(urllib.unquote(i.content)) for i in tmp]
        return json.dumps(result)

class favicon:
    def GET (self):
        web.redirect ('/static/favicon.ico')
        #raise web.seeother('/static/favicon.ico')
    
if __name__ == "__main__":
    app.run()
