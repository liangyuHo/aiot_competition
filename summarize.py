#-*- encoding:utf-8 -*-
from __future__ import print_function

import sys
try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except:
    pass

import codecs
from textrank4zh import TextRank4Keyword, TextRank4Sentence

def summary(txtFile):
    text = txtFile.replace(' ','。')
    tr4w = TextRank4Keyword()

    tr4w.analyze(text=text, lower=True, window=2)   # py2中text必须是utf8编码的str或者unicode对象，py3中必须是utf8编码的bytes或者str对象

    print( '關鍵詞：' )
    for item in tr4w.get_keywords(20, word_min_len=1):
        print(item.word, item.weight)

    print()
    print( '關鍵短句：' )
    result = []
    for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2):
        result.append(phrase)

    tr4s = TextRank4Sentence()
    tr4s.analyze(text=text, lower=True, source = 'all_filters')

    print()
    print( '摘要：' )
    for item in tr4s.get_key_sentences(num=3):
        print(item.index, item.weight, item.sentence)
    return(result)