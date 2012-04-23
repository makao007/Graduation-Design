import web
import hashlib

web.config.debug = False
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
    )

app = web.application (urls, locals())
session = web.session.Session(app, web.session.DiskStore('sessions'), initializer={'is_login':False,'username':''})

class index:
    def GET(self):
        #return 'hello world'
        return render.index()

class add_user:
    def GET(self):
        info = web.input()
        user = str(info.get('user'))
        pawd = str(info.get('pawd1'))
        pawd = hashlib.md5(pawd).hexdigest()
        temp = dict(name=user)
        if len(db.select ('webuser', temp,where="username=$name", limit=1))>0:
            return 'user exists'
        else:
            db.insert ('webuser',username=user, password=pawd)
            session.is_login = True
            session.username = user
            return 'add user successful'

def response (flag, text) :
    return """{"status":%s, "text":"%s" }""" % (flag, text)

class login:
    def GET(self):
        if (session.is_login):
            return response(1,session.username)
        info = web.input()
        user = str(info.get('username'))
        pawd = hashlib.md5(str(info.get('password',''))).hexdigest()
        temp = dict(name=user,pawd=pawd)
        if len(db.select ('webuser', temp, where="username=$name and password=$pawd", limit=1)) > 0:
            session.is_login = True
            session.username = user

            print response(1, user)
            return response(1, user)
        else:
            return response(0, 'login fail')

class islogin:
    def GET(self):
        if (session.is_login):
            return response(1, session.username)
        else :
            return response(0, '')

class mytest:
    def GET (self):
        user = web.input().get('id')
        session.count += 1
        return 'show session <a href=/show>show</a>'


class logout:
    def GET (self):
        session.kill()
        return 'logout'

if __name__ == "__main__":
    app.run()
