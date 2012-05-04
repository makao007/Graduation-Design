#coding=utf-8

""" 此文件用于中文分词前的词库处理，将现有的词库按字数分类"""

import codecs
import sys
import re

#获取字典内容
def get_dict_content (dpath):
    return file(dpath)

def read_file (filename):
    r = codecs.open(filename, "r","utf-8")
    content = r.read()
    r.close()
    return content
    #return file(filename).read()

def write_file (filename, dict_array) :
    w = codecs.open(filename, "w","utf-8")
    w.write(dict_array)
    w.close()

#转换中文编码
def cn_encode (s):
    try:
        return unicode(s,'utf8')
    except:
        try:
            return s.decode('gbk').encode('utf8')
        except:
            try:
                return s.decode('gb2312').encode('utf8')
            except:
                return s

#将字典按字数分类,最长的词为5个汉字
def create_new_dict (contents,max_word):
    new_dict_file_len = max_word
    new_dict = [ [] for i in range(new_dict_file_len) ]

    for line in contents:
        if not line:
            continue
        temp = line.strip().split()
        tem = cn_encode(temp[0])
        tem_len = len(tem)

        if tem_len == 1:
            continue
        elif tem_len <= new_dict_file_len:
            new_dict[tem_len-2].append(tem)
        else:
            new_dict[-1].append(tem)
    
    return new_dict


#测试中文编码问题
def test_encode ():
    line = file('dict3.txt').readline()
    temp = line.strip().split()
    word = temp[0].replace('\n','').replace('  ','')
    print word, len(word)
    s  = cn_encode (word)
    print s,len(s)

#test_encode()

def match_english(s):
    s = s.encode('gbk')
    return len(re.search(r"[a-zA-Z0-9:]{2,}",s).group(0))

def is_alnum(s):
    try:
        s = s.encode('gbk')
    except:
        s = s.encode('utf8')
    return s.isalnum()

def pre_split (s):
    s=cn_encode(s)
    sign = cn_encode("[。，！`《》<>\.,//\t\r?]")
    s=re.sub(sign,'',s)
    return s

#new_dict_file = ['dict_two.txt','dict_thr.txt','dict_for.txt','dict_fiv.txt','dict_oth.txt']
#分词，正向最大的长度分词
def split_article (s,new_dict):
    i=0
    s = pre_split(s)
    max_len = len(new_dict)
    max_en_len = 20
    txt_len = len(s)
    word_list = []
    while i<txt_len :
        k = max_len
        for dindex in xrange(max_len-1):

            if is_alnum(s[i:i+k]) :
                en_len = match_english(s[i:i+max_en_len])
                k = en_len
                break

            if i + k > txt_len:
                k = txt_len - i
            if k <= 0:
                break
            if s[i:i+k] in new_dict[max_len-2-dindex]:
                break
            k -= 1
        word_list.append(s[i:i+k])
        if k<=0:
            break
        i += k
    return ' '.join(word_list)


def test_split_article ():

    dict_path = "dict.txt"   #词库文件
    dict_leng = 5            #最长词的字数
    s = read_file('test.txt')  #测试数据
    ss = split_article (s, create_new_dict(get_dict_content(dict_path),dict_leng))
    write_file('result.txt', ss.replace('\n','\r\n'))    #保存数据到result.txt

    #t  = re.compile(r'\s{2,}',re.M|re.S)
    #write_file ('result.txt', t.sub('\s',ss))
    
test_split_article ()
