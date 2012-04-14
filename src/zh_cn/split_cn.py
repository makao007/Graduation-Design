#encoding:utf-8
""" 此文件用于中文分词前的词库处理，将现有的词库按字数分类"""

import codecs

#获取字典内容
def get_dict_content (dpath):
    return file(dpath)

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
def create_new_dict (contents,new_dict_file):
    new_dict_file_len = len(new_dict_file)
    new_dict = [ [] for i in range(new_dict_file_len) ]

    for line in contents:
        temp = line.split()
        tem = cn_encode(temp[0])
        tem_len = len(tem)

        if tem_len == 1:
            continue
        elif tem_len <= new_dict_file_len:
            new_dict[tem_len-2].append(tem)
        else:
            new_dict[-1].append(tem)
    
    write_new_dict_file (new_dict_file, new_dict)

#将数组的内容以"/"分隔写入到文件
def write_file (filename, dict_array) :
    w = codecs.open(filename, "w","utf-8")
    w.write('/'.join(dict_array))
    w.close()


#保存已按词长度分类的词库
def write_new_dict_file (dict_file, dict_list):
    for i,j in zip(dict_file,dict_list):
        write_file(i,j)

#生成以长度分类的词库
def begin_make_new_dict():
    dict_path = "dict.txt"
    new_dict_file = ['dict_two.txt','dict_thr.txt','dict_for.txt','dict_fiv.txt','dict_oth.txt']
    create_new_dict(get_dict_content(dict_path), new_dict_file)

#测试中文编码问题
def test_encode ():
    line = file('dict.txt').readline()
    temp = line.split()
    word = temp[0]
    print word, len(word)
    s  = cn_encode (word)
    print s,len(s)

#test_encode()
begin_make_new_dict()
