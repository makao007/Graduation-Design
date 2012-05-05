#coding=utf-8
import codecs


def get_dict_content (dpath):
    return file(dpath)

def read_file (filename):
    r = codecs.open(filename, "r","utf-8")
    content = r.read()
    r.close()
    return content

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

result = []
filename = 'dict3.txt'
for i in read_file(filename).split('\r\n'):
    t = cn_encode(i.strip())
    result.append ( str(len(t)) + ' ' + t)
write_file ('new_dict.txt','\r\n'.join(result))
