#coding=utf-8

import mmseg   
mmseg.dict_load_defaults()    
text = '今天的天气真好啊，我们一起出去玩一下吧'
algor = mmseg.Algorithm(text)    
word  = []
for tok in algor:    
    word.append(tok.text)

print ' '.join(word).decode('utf8').encode('gb2312')

n = raw_input()
