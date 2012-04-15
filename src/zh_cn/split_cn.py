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


#加载新的词库
def load_new_dict_file (file_list):
    new_dict = []
    for i in file_list:
        new_dict.append(file(i).read().split('/'))

    return new_dict

#new_dict_file = ['dict_two.txt','dict_thr.txt','dict_for.txt','dict_fiv.txt','dict_oth.txt']
#分词，正向最大的长度分词
def split_article (s,new_dict):
    i=0
    max_len = len(new_dict)
    txt_len = len(s)
    word_list = []
    s = cn_encode(s)

    while i<txt_len :
        k = max_len
        for dindex in range(max_len-1):
            if i + k > txt_len:
                k = txt_len - i
            if s[i:i+k] in new_dict[max_len-2-dindex]:
                break
            k -= 1
        print s[i:i+k],'/',
        word_list.append(s[i:i+k])
        i += k

    return '/'.join(word_list)


def test_split_article ():
    s = """股票分割解读：创始人想控制投票权

ugmbbc发布于 2012-04-15 23:22:06|1148 次阅读 字体：大 小 打印预览       


Google最近宣布发行一档新股票给目前的股东，亦即实质上将股票一分为二。这是一种不寻常的方式，反应出Google的创始人希望保护公司的长期利益。以下为此项计划的问与答：

　　问：Google为何采取此一行动？

　　答：Google目前的股票结构，焦点专注于创始人的投票权，包括佩奇(Larry Page)，布林(Sergey Brin)与执行董事长施密特(Eric Schmidt)。Google担心因为发放新股给员工及透过买进股票而并购来的企业，会稀释投票权。Google说，这种情况并没有立即发生的危险，但 同时也认为应立即采取防范行动。

　　“一定要了解，这项计划需要很长时间，才会对管理发挥效用，”佩奇与布林在一封信件上写到。“因为我们清楚知道想做什么，所以没有必要延后采取行动。”

　　问：这对目前的股东有何影响？

　　答：投资人目前拥有的是A股。他们将获得相同数量，但没有投票权的C股。A股股价将一分为二，如果在分割时，该股价为600美元，则分割后，A 股价值为300美元，C股价值也为300美元。投资人将拥有原先二倍数量的股票，但总投票权与股票价值不会改变。亦即如果A持有100股股票，每股价值 600美元，分割后，他将拥有200股，每股价值为300美元。A仍将拥有100股投票权，股价总值仍为60000美元。投资人可自由单独买卖A股或C 股，新股也将拥有自己的代号。如果A卖出100股C股，他将通过A股拥有100股投票权，股票价值为30000美元。但是如果A卖出100股A股，他的C 股便没有投票权，但股票价值仍为30000美元。

　　问：这对Google而言，是否是一种新的策略？

　　答：不是。该公司自2004年上市以来，其创始人便强调需要长期掌控公司。他们认为必须持有投票权才能达到目的。其股票结构的设计，自始就是为 保留投票权给佩奇，布林与施密特。佩奇与布林声称，只有将焦点置于长期目标，Google才能更为成功，短期即使获利、营收无法达成华尔街目标，也在所不 惜。这几位创始人指出，第一台使用Android操作系统的手机花了三年才得以推出，又花了三年才让这套系统广为接受。他们不希望投资人用短视利益的心态 进行投票。

　　问：那么，这究竟是股票分割，还是股息？

　　答：传统上，两者都不是。股票实质上已被分割，因为每股价值已被减半。但股票分割是让小股东有能力购买股票，而在Google的计划下，此一行动主要目的在掌握控制权。此一行动也可视为是发放股息，但投资人获得的不是现金，而是股票。

　　问：决议已确定了吗？

　　答：在6月21日，即Google的股东年会上，此一计划必须获得股东的通过。由于三位创始人掌控了多数投票权，预期将可获得通过。

　　问：这计划何时实施？

　　答：此一计划于6月可望获得通过，届时Google将会宣布详细情形。"""
    
    new_dict_file = ['dict_two.txt','dict_thr.txt','dict_for.txt','dict_fiv.txt','dict_oth.txt']
    split_article (s,load_new_dict_file(new_dict_file))
    
test_split_article ()
