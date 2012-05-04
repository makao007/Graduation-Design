import web
import json
import hashlib

#web.config.debug = False
web.config.session_parameters['timeout'] = 3600

db = web.database(dbn='postgres', user='webpy', pw='1234', db='webpy')
render = web.template.render('templates/')
urls = (
    '/', 'index',
    '/add_user','add_user',
    '/test', 'mytest',
    '/login', 'login', 
    '/logout', 'logout',
    '/islogin', 'islogin',
    '/add_cate','add_cate',
    '/del_cate','del_cate',
    '/categorys', 'categorys',
    '/relative',  'relative',
    '/favicon.ico', 'favicon',
    )

app = web.application (urls, locals())
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'is_login': False, 'username':'', 'user_id': -1})
    web.config._session = session
else:
    session = web.config._session

#session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'is_login':False,'username':''})

def response (flag, text) :
    return """{"status":%s, "text":"%s" }""" % (flag, text)

def to_login():
    if not session.is_login and session.user_id < 0:
        raise web.seeother('/')

def check_user_cate (uid, fid):
    temp = dict(user_id=uid, focus_id=fid)
    result = db.select ('webfocus', temp, where="id=$focus_id and userid=$user_id", limit=1) 
    if result:
        return True
    else:
        return False

class index:
    def GET(self):
        #return 'hello world'
        return render.index()

class add_user:
    def GET(self):
        info = web.input()
        user = str(info.get('user')).strip()
        pawd = str(info.get('pawd1')).strip()
        pawd = hashlib.md5(pawd).hexdigest()
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
        if (session.is_login):
            return response(1,session.username)
        info = web.input()
        user = info.get('username')
        pawd = hashlib.md5(str(info.get('password',''))).hexdigest()
        temp = dict(name=user,pawd=pawd)
        result = db.select ('webuser', temp, where="username=$name and password=$pawd", limit=1) 
        if len(result) > 0:
            session.is_login = True
            session.username = user
            session.user_id  = result[0].id
            print session.user_id

            return response(1, user)
        else:
            return response(0, 'login fail')

class islogin:
    def GET(self):
        if (session.is_login):
            return response(1, session.username)
        else :
            return response(0, '')

class logout:
    def GET (self):
        session.kill()
        return 'logout'


class mytest:
    def GET (self):
        result = db.select ("webfocus")
        data   = [i.title for i in result]
        title  = {'title': data}
        return json.dumps ({'title':result})
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

def get_user_info_template(sql, user_id, step='\n'):
    source = db.query(sql, vars={'userid':user_id})
    ss = {}
    for i in source:
        val = i.id
        if ss1.has_key(val):
            ss[val] += i.url + step
        else:
            ss[val]  = i.url + step
    return ss
    

def get_user_source (user_id):
    sql = "select webfocus.id as id,websource.url as url from webfocus,websource where webfocus.userid=$userid and webfocus.id = websource.focus_id";
    return get_usr_info_template (sql, user_id)


def get_user_keyword (user_id):
    sql = "select webfocus.id as id,webkeywords.word as word from webfocus,webkeywords where webfocus.userid=$userid and webfocus.id = webkeywords.focus_id"
    return get_user_info_template(sql, user_id)

class categorys:
    def GET (self):
        to_login()
        user_id = session.user_id
        
        tmp1 = dict (userid=user_id)
        category = db.select ('webfocus', tmp1, where="userid=$userid",order="created DESC")


        step = '\n'
        
        ss1 = get_user_source(user_id)

        ss3 = []
        names = []
        for k in category:
            ss3.append ( [k.id, k.title, ss1[k.id], ss2[k.id]] )
            names.append (k.title)


        #web.header('Content-type', 'application/json')
        web.header('Content-type','text/javascript')
        data = json.dumps({'names':names, 'name_info': ss3})

        #jsonp
        return web.input().get('callback') + '(' + data + ');'

class relative:
    def GET (self):
        to_login()
        user_id = session.user_id

        source  = get_user_source()
        keyword = get_user_keyword()

        return 

class favicon:
    def GET (self):
        web.redirect ('/static/favicon.ico')
        #raise web.seeother('/static/favicon.ico')
    

if __name__ == "__main__":
    app.run()
