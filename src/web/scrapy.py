#coding=utf-8
""" scrapy """

import re
import datetime
import urllib,urllib2
import hashlib
import urlparse

class Scrapy:
    # source url, max deep, match url
    def __init__ (self, url,save_func, match_url='', max_deep=2,max_page=1000):
        self.src_url = url
        self.pre_url = ''
        self.cur_url = url

        self.cur_deep= 1
        self.max_deep= max_deep

        self.cur_page= 1
        self.max_page= max_page

        self.mat_url = match_url
        self.content = ''
        self.unvisit = []
        self.visited = []
        self.unvisit_hash = []
        self.visited_hash = []

        self.begin_time = ''
        self.ends_time  = ''

        self.stop_flag  = False
        self.last_deep_url = ''
    
        self.save_func  = save_func

        self.join_queue ([url])
    
    def _md5 (self, p):
        return hashlib.md5(p).hexdigest()

    def _fetch (self):
        last_modify = ''
        print 'downloading %s ...' % self.cur_url
        try:
            #temp = urllib.urlopen(self.cur_url)
            #last_modify = temp.headers.get('last-modified','')
            #self.content = temp.read()

            request =urllib2.Request(self.cur_url)
            request.add_header('User-Agent','Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.162 Safari/535.19')
            response =urllib2.urlopen(request)
            last_modify  = response.headers.get('last-modified','')
            self.content = response.read()
        except:
            self.content = ''
            print 'download %s error ' % self.cur_url

        ana = Analyze(self.cur_url, self.content, datetime.datetime.now(), last_modify, self.save_func)
        ana.save_record()

    def _findurls (self):
        if self.stop_flag :
            return []
        if self.cur_deep > self.max_deep:
            return []

        urls = re.findall (r"""<a .*?href\s*=\s*(["']?)(.*?)\1.*?>""", self.content, re.I|re.S|re.M)
        result = []
        for i in urls:
            url = i[1].strip()
            if url.lower().startswith('javascript:'):
                continue
            tmp = urlparse.urljoin(self.cur_url,url).strip()
            if '#' in tmp:
                tmp = tmp[:tmp.index('#')]

            if self._match_url (tmp): 
                result.append(tmp)


        result = list(set(result))
        if len(result)==0:
            self.last_deep_url = self.pre_url
            self.cur_deep += 1
        elif self.cur_deep==1:
            self.last_deep_url = result[-1]
            self.cur_deep += 1
        elif self.cur_url == self.last_deep_url:
            self.last_deep_url = result[-1]
            self.cur_deep += 1
            

        if self.cur_page+len(result) > self.max_page:
            tmp = self.cur_page
            self.cur_page = self.max_page
            self.stop_flag = True
            return result[:self.max_page-tmp]
        else:
            self.cur_page += len(result)
            return result

    def _match_url (self, url):
        if (url.startswith(self.src_url)):
            return True
        if self.mat_url == '':
            return False
        try:
            tmp = re.compile (self.mat_url,re.I|re.M|re.S)
            if tmp.match(url):
                return True
            else:
                return False
        except:
            return False


    def _checkin_url (self, md5_url):
        if md5_url not in self.unvisit_hash and md5_url not in self.visited_hash :
                return True
        return False

    def _checkin (self, urls):
        for url in urls:
            md5_url = self._md5(url)
            if self._checkin_url (md5_url):
                self.unvisit.append (url)
                self.unvisit_hash.append (md5_url)

    def _response (self) :
        self.ends_time  = datetime.datetime.now()
        return {'start_time': self.begin_time, 'end_time':self.ends_time, 
                'source_url': self.src_url,  'max_deep': self.max_deep, 
                'match_url' : self.mat_url,  'visited_url': self.visited, 
                'visited_hash': self.visited_hash, 'unvisit_url': self.unvisit,
                'unvisit_hash': self.unvisit_hash }

    def join_visited (self, urls):
        for url in urls:
            #self.visited.append (url)
            self.visited_hash.append (self._md5(url))

    def join_queue (self, urls):
        for url in urls:
            if self._checkin_url (self._md5(url)):
                self.unvisit.append (url)
                self.unvisit_hash.append (self._md5(url))


    def start_scrapy (self):
        self.begin_time = datetime.datetime.now()
        while self.unvisit:
            self.unvisit_hash.pop(0)
            self.cur_url = self.unvisit.pop(0).strip()
            self.pre_url = self.cur_url
            if not self.cur_url:
                continue
            self._fetch()
            self._checkin (self._findurls())
            #self.visited.append(self.cur_url)
            self.visited_hash.append (self._md5(self.cur_url))

        return self._response ()

class Analyze:
    def __init__ (self, url, content, created, last_modify, save_data):
        self.url     = url
        self.title   = ''
        self.content = content
        self.body_text= ''
        self.description = ''
        self.last_modify = last_modify
        self.created     = created

        self._get_title()
        self._get_desc ()
        self._get_body_text()

        self.save_data = save_data


    def _get_title (self):
        temp = re.search (r"""<\s*title.*?>(.*?)</title>""", self.content, re.I|re.M|re.S)
        if temp :
            self.title = temp.group(1)

    def _get_desc (self):
        temp = re.search (r"""<meta.*?name\s*=\s*["']?description["']?.*?content\s*=\s*["']?(.*?)["']?\s*>""", self.content, re.I|re.M|re.S)
        if temp:
            self.description = temp.group(1)
        
    def _get_body_text (self):
        ss = self.content.replace('\n','').replace('\r','')
        ss = re.sub("\s{3,},", "  ", ss)

        t = re.compile (r"<style.*?</style>",re.I|re.S|re.M)
        ss = t.sub("",ss)

        t = re.compile (r"<script.*?</style>",re.I|re.M|re.S)
        ss = t.sub("",ss)

        t = re.compile (r"<.+?>",re.I|re.M|re.S)
        ss = t.sub('',ss)

        self.body_text = ss

    def save_record(self):
        self.save_data (self.url, self.title, self.description, self.body_text, self.created, self.last_modify)

