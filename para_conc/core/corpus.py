#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2020 Tony Chang (42716403@qq.com)

# Disclaimer:

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import re
from para_conc.core.GetLang import GetLang

class Sent:
    def __init__(self):
        self.num = ''
        self.sent_sl = ''
        self.sent_tl = ''
        
    def get_sent(self, sent_num, sent_sl, sent_tl):        
        self.num = sent_num
        self.sent_sl = sent_sl
        self.sent_tl = sent_tl
        
class Article:
    def __init__(self, file_id):
        #文章标题
        self.title = file_id.split("/")[-1]
        # 文章句库
        self.sents = []
        # 文章句库数量
        self.sent_count = len(self.sents)
        self.length = ''
        self.sl = ""
        self.tl = ""       
 

    def get_bi_lang(self, sent_list):
        lang_finder = GetLang()           
        sl_sample_list = [sent.sent_sl for sent in sent_list[:2]]
        tl_sample_list = [sent.sent_tl for sent in sent_list[:2]]
        sl_sample = " ".join(sl_sample_list)
        tl_sample = " ".join(tl_sample_list)
        sl = lang_finder.get_lang(sl_sample)
        tl = lang_finder.get_lang(tl_sample)
        return sl,tl 
        
    def get_context(self, sent_num, hst_color, sents_left, sents_right):
        current_sent_idx = int(sent_num) - 1
        fore_sent_idx = current_sent_idx - sents_left
        hind_sent_idx = current_sent_idx + sents_right
        current_sent_sl = '<font color={} id=3>'.format(hst_color) + self.sents[current_sent_idx].sent_sl + '</font>'
        current_sent_tl = '<font color={} id=3>'.format(hst_color) + self.sents[current_sent_idx].sent_tl + '</font>'
        if fore_sent_idx <= 0:
            fore_sent_sl = ""
            fore_sent_tl = ""
        else:
            fore_sent_sl_list = []
            fore_sent_tl_list = []
            for x in range(fore_sent_idx, current_sent_idx):
                fore_sent_sl_list.append(self.sents[x].sent_sl)
                fore_sent_tl_list.append(self.sents[x].sent_tl)                
            fore_sent_sl = "".join(fore_sent_sl_list)
            fore_sent_tl = " ".join(fore_sent_tl_list)
        if hind_sent_idx >= self.sent_count - 1:
            hind_sent_sl = ""
            hind_sent_tl = ""
        else:
            hind_sent_sl_list = []
            hind_sent_tl_list = []
            for y in range(current_sent_idx+1,hind_sent_idx+1):
                hind_sent_sl_list.append(self.sents[y].sent_sl)
                hind_sent_tl_list.append(self.sents[y].sent_tl)                
            hind_sent_sl = "".join(hind_sent_sl_list)
            hind_sent_tl = " ".join(hind_sent_tl_list)
            
        sent_sl_context = fore_sent_sl + current_sent_sl + hind_sent_sl
        sent_tl_context = fore_sent_tl + " " + current_sent_tl + " " +hind_sent_tl
        sent_tl_context = sent_tl_context.strip()

        return sent_sl_context, sent_tl_context        
    

# 语料库
class Corpus:
    def __init__(self):
        # 文章列表
        self.articles = []
        # 文章数量
        self.article_count = ''
        self.total_length = ''                
        
    # 语料赋值，data为打开文件名列表    
    def read_data(self, data):
        files_length = 0
        for file_id in data:
            # 单篇文章赋值
            file_data = Article(file_id)            
            # 读取seg文件            
            with open(file_id,"r",encoding="utf-8") as f:
                # 读取整篇文章
                mytext = f.read()
                # 去除seg标记
                mytext = re.sub(r'<seg.*?>(.*)?</seg>', '\g<1>', mytext)
                # 统计单篇字符数
                mytext_length = len(mytext)
                # 单篇字符数赋值
                file_data.length = mytext_length
                # 语料总字数数累加
                files_length += mytext_length
                # 拆分成列表
                lines = mytext.split('\n')
                mytextlist= [line.strip() for line in lines]            
                # 交叉读取源语，目标语句列表
                sl_list = mytextlist[0::2]
                tl_list = mytextlist[1::2]
                # 建立带句编号的双句句对库，同时去除seg标记
                for i,(sent_sl, sent_tl) in enumerate(zip(sl_list,tl_list),start=1):
                    sent_num = str(i)
                    # 创建双语单句
                    bi_sent = Sent()
                    bi_sent.get_sent(sent_num, sent_sl, sent_tl)
                    # 将双语单句加入文章中的句子列表
                    file_data.sents.append(bi_sent)
                    
            # 更新单篇文章句子总数
            file_data.sent_count = len(file_data.sents)
            file_data.sl, file_data.tl = file_data.get_bi_lang(file_data.sents)
            # 将单篇文章加入语料文章列表
            self.articles.append(file_data)
        # 更新语料文章总数
        self.article_count = len(self.articles)
        self.total_length = files_length

