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

import os, json, sys, re

import pandas as pd

from PyQt5.QtCore import Qt, QSize, pyqtSignal,QModelIndex, QPoint
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QAction, QComboBox,QFileDialog,
                             QGroupBox, QPushButton, QLineEdit, QLabel, QRadioButton, QStatusBar,QSizePolicy,QMessageBox,
                             QButtonGroup,QTextBrowser,QTabWidget,QTreeView,QTreeWidget,QTreeWidgetItem,QMenu,
                             QCheckBox, QAbstractItemView, QWidget, QListWidget, QMessageBox, QSplitter,
                             QColorDialog, QApplication)

from pathlib import Path

from langdetect import detect, detect_langs, DetectorFactory
from para_conc.ui.ui_main_window import UIMainWindow
from para_conc.ui.ui_sub_window import SubWindow, MessageBox
from para_conc.core.corpus import Corpus
from para_conc.core.GetLang import GetLang
from para_conc.core.search_configure import SearchMode, DisplayMode
from para_conc.core.searchResultConverter import SearchResultConverter
from para_conc.core.seg_adder import SegAdder #引入SEG赋码模块

       
class MainWindow:
    
    def __init__(self):
        currentDir = Path.cwd()
        self.outPutDir = currentDir.joinpath("saved_files")
        dataDir = currentDir.joinpath("app_data")
        self.workFileDir = dataDir.joinpath("workfiles")
        self.corpusDir = dataDir.joinpath("corpus")        
        lemmaFileName = self.workFileDir.joinpath('en_lemma.txt')
        synFileName = self.workFileDir.joinpath('syndict.txt')
        
        self._stopchar_en_list = "\,\.\:\"\'\*\^\# \$\@\!~\(\)\_\-\+\=\{\}\[\]\?\/\<\>\&\%\;\\"
        self._stopchar_zh_list = "，。：、；“”’！…—（）《》｛｝【】？"
        self._regex_char_regex=r"\*|\^|\# |\$|\@|\!|\(|\)|\-|\+|\=|\{|\}|\[|\]|\?|\<|\>|\\|\|"
        
        self.en_lemma_dict = {}
        with open(lemmaFileName, 'r', encoding='utf-8-sig') as f:
            tag_corpus = [line.strip() for line in f.readlines()]
            for line in tag_corpus:
                word = line.split('\t')[0]
                lemmas = line.split('\t')[-1].split(',')
                self.en_lemma_dict[word] = lemmas

        self.syn_dict = {}
        with open(synFileName, 'r', encoding='utf-8-sig') as f:
            syn_corpus = [line.strip() for line in f.readlines()]
            for line in syn_corpus:
                word = line.split('=')[0]
                syns = line.split('=')[-1].split(',')
                self.syn_dict[word] = syns

        self.corpera = ""
        self.fileShowList = []
        self.fileOpenList = []
        self.fileSelectedList = []                
        self.result_list = []
        self.temp_html = ""
        self.font_name = "Arial"
        self.font_size = 11
        self.font_style = "Regular"
               
        self.locate_lg = GetLang()
        self.converter = SearchResultConverter()
        self.text_frame = SubWindow()
        self.display_mode = DisplayMode()
        
        self._ui = UIMainWindow()
        self._ui.save_text.connect(self.save_text)
        self._ui.save_html.connect(self.save_html)
        self._ui.search.connect(self.search)
        self._ui.load_files.connect(self.load_file_corpus)
        self._ui.closeFiles.connect(self.unload_file_corpus)
        self._ui.closeCurrentFiles.connect(self.close_current_files)
        self._ui.select_item.connect(self.select_item)
        self._ui.file_open_request.connect(self.open_current_file)
        self._ui.keyColorChanged.connect(self.reload_key_color)
        self._ui.display_request.connect(self.setDisplayMode)
        self._ui.add_segs.connect(self.addSegs) # 接收来自UIMainWindow的赋码操作请求
        self._ui.show()

    def addSegs(self):
        # 调出赋码模块，执行操作
        self.add_seg_act = SegAdder()
        self.add_seg_act.show()
        
    def getContextRange(self):
        context_left_range = self._ui.context_setting_window._sent_l_box.value()
        context_right_range = self._ui.context_setting_window._sent_r_box.value()
        return int(context_left_range), int(context_right_range)
        
    def setDisplayMode(self, item, state):
        self.display_mode.set_mode(item, state)
        
    def show_alert(self, message):
        alert_box = QMessageBox(QMessageBox.Warning, "错误提示", message)
        alert_box.setStandardButtons(MessageBox.Ok)
        button_changed = alert_box.button(MessageBox.Ok)
        button_changed.setText("确定")
        alert_box.exec()
        
    def load_file_corpus(self, files): 
        if files:
            alert_list = []
            for fileName in files:
                showName=fileName.split("/")[-1]
                #检查双语文件是否已对齐
                with open(fileName, 'r', encoding= 'utf-8-sig') as f:
                    text_list = [x.strip() for x in f.readlines()]
                    total_length = len(text_list)%2
                    if total_length == 0:
                        pass
                    else:
                        alert_list.append(showName)
                        showName = ""
                    if showName != "" and showName not in self.fileShowList:
                        self.fileShowList.append(showName)
                        self.fileOpenList.append(fileName)
                        self._ui._corpusWindow.addItem(showName)
                    elif showName != "":                 
                        self._ui._statusBar.showMessage('该语料已成功加载，请勿反复加载！',3000)
                    else:
                        pass                    
            num_items = self._ui._corpusWindow.count()
            if num_items != 0:
                self.corpera = Corpus()
                self.corpera.read_data(self.fileOpenList)
                self._ui._statusBar.showMessage('语料已成功加载！',3000)
                self._ui._file_stats.setText(str(self.corpera.article_count))
                self._ui._char_stats.setText(str(self.corpera.total_length))
            if alert_list:
                alert_info = "以下语料未对齐，请核实后重新加载！\n"+'\n'.join(alert_list)
                self.show_alert(alert_info)
                
            return self.corpera

    def unload_file_corpus(self):
        if self.fileShowList != []:
            self.fileShowList.clear()
            self.fileOpenList.clear()
            self.fileSelectedList.clear()
            self.result_list.clear()
            self.corpera = ""
            self.temp_html = ""            
            self._ui._corpusWindow.clear()
            self._ui._resultWindow.clear()
            self._ui._file_stats.setText("0")
            self._ui._char_stats.setText("0")
            self._ui._hit_stats.setText("0")
            self._ui._statusBar.showMessage('全部文件已清空')

    def close_current_files(self):
        if self.fileSelectedList!=[]:
            total_num = len(self.fileSelectedList)
            i=0
            for i in range(total_num):
                for fileOpenName in self.fileOpenList:
                    if self.fileSelectedList[i] in fileOpenName:
                        self.fileOpenList.remove(fileOpenName)
                        self.fileShowList.remove(self.fileSelectedList[i])
                i+=1
            self._ui._corpusWindow.clear()
            self._ui._resultWindow.clear()
            self.result_list.clear()
            if self.fileOpenList != []:
                for showName in self.fileShowList:
                    self._ui._corpusWindow.addItem(showName)
                self.corpera = Corpus()
                self.corpera.read_data(self.fileOpenList)                   
                self._ui._statusBar.showMessage(f'已成功卸载{total_num}个文件！',3000)         
                self._ui._file_stats.setText(str(self.corpera.article_count))
                self._ui._char_stats.setText(str(self.corpera.total_length))
                self._ui._hit_stats.setText("0")
            else:
                self._ui._statusBar.showMessage(f'已成功卸载{total_num}个文件！',3000)         
                self._ui._file_stats.setText("0")
                self._ui._char_stats.setText("0")
                self._ui._hit_stats.setText("0")
                self.fileShowList.clear()
                self.fileOpenList.clear()
                self.fileSelectedList.clear()
                self.result_list.clear()
                self.corpera = ""
                self.temp_html = ""            
                self._ui._resultWindow.clear()
                

    def open_current_file(self,file_id):       
        for article in self.corpera.articles:
            if article.title == file_id:
                self.title_shown = 'Full Text of ' + article.title.replace('.txt','')
                num_list = []
                lang_list = []
                sent_list = []                
                for sent in article.sents:
                    num_list.append(sent.num)
                    lang_list.append("原文")
                    sent_list.append(sent.sent_sl)
                    num_list.append(sent.num)
                    lang_list.append("译文")
                    sent_list.append(sent.sent_tl)
                df_data = self.converter.lst2pd(num_list, lang_list, sent_list)
                self.result_html = self.converter.pdf2html(df_data)
                self.text_frame.setStyleSheet("QTextBrowser{background-color:%s}"% ('WhiteSmoke'))
                self.text_frame.setWindowTitle(self.title_shown)
                self.text_frame.setText(self.result_html)
                self.text_frame.show()

    def reload_key_color(self, mode_num):
        if self.temp_html:
            self._ui._resultWindow.clear()
            if mode_num == 2:
                self.temp_html = re.sub(r'<font color=\w+ id=2>','<font color={} id=2>'.format(self._ui.colorMode.ColorSet['HWD']), self.temp_html)
            if mode_num == 3:
                self.temp_html = re.sub(r'<font color=\w+ id=3>','<font color={} id=3>'.format(self._ui.colorMode.ColorSet['HST']), self.temp_html)
            if mode_num == 4:
                self.temp_html = re.sub(r'<font color=\w+ id=4>','<font color={} id=4>'.format(self._ui.colorMode.ColorSet['SRC']), self.temp_html)           
            self._ui._resultWindow.setHtml(self.temp_html)
            self._ui._corpusWindow.setStyleSheet("QListWidget{background-color:%s}"% ('WhiteSmoke'))
            self._ui._resultWindow.setStyleSheet("QTextBrowser{background-color:%s}"% ('WhiteSmoke'))
            return self.temp_html
                
    def select_item(self):
        self.fileSelectedList.clear()
        for item in self._ui._corpusWindow.selectedItems():
            if item.text() not in self.fileSelectedList:
                self.fileSelectedList.append(item.text())
                
    def inputCheck(self):
        input_word = self._ui.search_text()
        # don't strip here for the sake of regex input
        search_mode = self._ui.search_mode()
        if input_word == "":
            self._ui._statusBar.showMessage("请输入检索词！", 3000)
            inputWord = ""
        elif input_word.strip() == "":
            self._ui._statusBar.showMessage("请输入有效检索词！", 3000)
            inputWord = ""
        elif search_mode == SearchMode.REGEX:
            inputWord = input_word
        else:
            # to ensure no regex appeared in other mode
            m=re.search(self._regex_char_regex, input_word)
            if m:
                self._ui._statusBar.showMessage("如想进行正则检索，请先选择正则模式，再输入正则表达式！", 3000)
                inputWord = ""
            else:
                # strip here to remove spaces
                input_word = input_word.strip()
                if input_word[0] in self._stopchar_en_list:
                    self._ui._statusBar.showMessage("您输入的检索词为标点符号，请输入有效检索词", 3000)
                    inputWord = ""
                elif input_word[0] in self._stopchar_zh_list:
                    self._ui._statusBar.showMessage("您输入的检索词为标点符号，请输入有效检索词", 3000)
                    inputWord = ""
                else:
                    inputWord = input_word                    
        return inputWord

    def zh_src_word_wrapper(self, input_word):
        src_mode = self._ui.search_mode()
        if src_mode == SearchMode.REGEX:
            src_word = re.compile(r"{}".format(input_word))
        #拓展检索即中文同义词检索
        elif src_mode == SearchMode.EXTENDED:           
            input_word = input_word.strip()
            word_list = [input_word]
            for key, values in self.syn_dict.items():
                if input_word == key:
                    for syn in values:
                        word_list.append(syn)
                if input_word in values:
                    if key not in word_list:
                        word_list.append(key)
                    for syn in values:
                        if syn not in word_list:
                            word_list.append(syn)
            new_word = r'('+ '|'.join(word_list) + r')'
            src_word = re.compile(r"{}".format(new_word))
        else:
            src_word = input_word
        return src_word

    def en_src_word_wrapper(self, input_word):
        src_mode = self._ui.search_mode()
        if src_mode == SearchMode.NORMAL:
            src_word = re.compile(r"\b{}\b".format(input_word))
        elif src_mode == SearchMode.REGEX:
            src_word = re.compile(r"{}".format(input_word))
        else:
            src_word_list = []
            src_wrd_list = input_word.split()
            for word in src_wrd_list:
                if word.isalpha() and word != word.upper():
                    lower_word = word.lower()
                    capitalize_word = word.capitalize()
                    if word == lower_word or word == capitalize_word:
                        if lower_word in self.en_lemma_dict.keys():
                            t = [v + '|' + v.capitalize() for v in self.en_lemma_dict[lower_word]]
                            src_word_list.append(r'\b(' + lower_word + r'|' + capitalize_word + '|' + '|'.join(t) + r')\b')
                        else:
                            t = []
                            for key, value in self.en_lemma_dict.items():  # 用户输入检索词存在于词性还原字典值内的情况
                                if lower_word in value:
                                    t.extend([v + '|' + v.capitalize() for v in value if v != lower_word])
                                    t.append(key + '|' + key.capitalize())
                                else:
                                    pass
                            if t:
                                src_word_list.append(r'\b(' + lower_word + '|' + capitalize_word + '|' + '|'.join(t) + r')\b')
                            else:
                                src_word_list.append(r'\b(' + lower_word + '|' + capitalize_word + r')\b')
                    else:
                        src_word_list.append(r'(\b' + word + r'\b)')
                else:
                    src_word_list.append(r'(\b' + word + r'\b)')
            if len(src_word_list) == 1:
                src_word = '\s'.join(src_word_list)
            elif len(src_word_list) > 1:
                src_word = r'(' + '\s'.join(src_word_list) + r')'
        return src_word

    def search(self):
        self.result_list.clear()
        key_word = self.inputCheck()
        if key_word:
            src_lang = self.locate_lg.detect_lang(key_word)
            self._ui._resultWindow.clear()
            self.sents_left, self.sents_right = self.getContextRange()
            if src_lang in ['zh', 'ja', 'ko']:
                src_word = self.zh_src_word_wrapper(key_word)
                try:                    
                    self.result_list = self.zh_searcher(src_word, self.corpera, self.display_mode.show_source, self.display_mode.show_context, self.sents_left, self.sents_right, \
                                                        self._ui.colorMode.ColorSet['HWD'], self._ui.colorMode.ColorSet['SRC'], self._ui.colorMode.ColorSet['HST'])
                    self.print_result(self.result_list)
                except:
                    self._ui._statusBar.showMessage("当前检索出现未知错误，请重试！", 3000)
            else:
                src_word = self.en_src_word_wrapper(key_word)
                try:
                    self.result_list = self.en_searcher(src_word, self.corpera, self.display_mode.show_source, self.display_mode.show_context, self.sents_left, self.sents_right, \
                                                        self._ui.colorMode.ColorSet['HWD'], self._ui.colorMode.ColorSet['SRC'], self._ui.colorMode.ColorSet['HST'])
                    self.print_result(self.result_list)
                except:
                    self._ui._statusBar.showMessage("当前检索出现未知错误，请重试！", 3000)

    def zh_searcher(self, src_word, corpera, show_source, show_context, sents_left, sents_right, hwd_color, note_color, hst_color):
        result_list = []
        i = 1
        for article in corpera.articles:
            if article.sl in ['zh', 'zh-cn', 'zh-tw', 'ja', 'ko']:
                for sent in article.sents:
                    #改用re.findall,命中格式为列表
                    zh_src_result = re.findall(src_word, sent.sent_sl)
                    if zh_src_result:
                        #使重复值唯一化，以免发生重复替换现象
                        word_hit=set(zh_src_result)
                        #建立替换句
                        new_zh_sent = sent.sent_sl
                        for word in word_hit:
                            #逐个替换成高光词汇
                            new_kwd = '<font_color={} id=1><b>'.format(hwd_color)+word+"</b></font>"
                            new_zh_sent = re.sub(word, new_kwd, new_zh_sent)
                        if show_source == 'on':
                            sent_source = '<p align = "right"><font_color={} id=3>—— '.format(note_color) + article.title +'</font></p>'
                        else:
                            sent_source = ''
                    
                        result_list.append(str(i)+'\t'+"原文"+ '\t'+new_zh_sent + sent_source)
                        sl_context,tl_context = article.get_context(sent.num, hst_color, sents_left, sents_right)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+sl_context)
                        result_list.append(str(i)+'\t'+"译文"+ '\t'+sent.sent_tl + sent_source)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+tl_context)                    
                        i += 1
                    else:
                        pass
            if article.tl in ['zh', 'zh-cn', 'zh-tw', 'ja', 'ko']:
                for sent in article.sents:
                    zh_src_result = re.findall(src_word, sent.sent_tl)
                    if zh_src_result:
                        word_hit=set(zh_src_result)
                        new_zh_sent = sent.sent_tl
                        for word in word_hit:
                            new_kwd = '<font_color={} id=1><b>'.format(hwd_color)+word+"</b></font>"
                            new_zh_sent = re.sub(word, new_kwd, new_zh_sent)                        
                        if show_source == 'on':
                            sent_source = '<p align = "right"><font_color={} id=3>—— '.format(note_color) + article.title +'</font></p>'
                        else:
                            sent_source = ''                    
                        result_list.append(str(i)+'\t'+"原文"+ '\t'+sent.sent_sl + sent_source)
                        sl_context,tl_context = article.get_context(sent.num, hst_color, sents_left, sents_right)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+ sl_context)
                        result_list.append(str(i)+'\t'+"译文"+ '\t'+ new_zh_sent + sent_source)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+ tl_context)                    
                        i += 1
                    else:
                        pass                
                
        return result_list 
            
    def en_searcher(self, src_word, corpera, show_source, show_context, sents_left, sents_right, hwd_color, note_color, hst_color):
        i = 1
        result_list =[]
        for article in corpera.articles:            
            if article.sl in ['en', 'de', 'fr', 'it', 'es', 'la', 'ru']:
                for sent in article.sents:                    
                    en_src_result = re.findall(src_word, sent.sent_sl)
                    if en_src_result:
                        word_hit = set(en_src_result)
                        new_en_sent = sent.sent_sl
                        for word in word_hit:
                            new_kwd = '<font_color={} id=1><b>'.format(hwd_color)+word+"</b></font>"
                            new_en_sent = re.sub(word, new_kwd, new_en_sent)
                        if show_source == 'on':
                            sent_source = '<p align = "right"><font_color={} id=3>—— '.format(note_color) + article.title +'</font></p>'
                        else:
                            sent_source = ''
                    
                        result_list.append(str(i)+'\t'+"原文"+ '\t'+new_en_sent + sent_source)
                        sl_context,tl_context = article.get_context(sent.num, hst_color, sents_left, sents_right)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+sl_context)
                        result_list.append(str(i)+'\t'+"译文"+ '\t'+sent.sent_tl + sent_source)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+tl_context)                    
                        i += 1
                    else:
                        pass
            if article.tl in ['en', 'de', 'fr', 'it', 'es', 'la', 'ru']:
                for sent in article.sents:
                    en_src_result = re.findall(src_word, sent.sent_tl)
                    if en_src_result:
                        word_hit = set(en_src_result)
                        new_en_sent = sent.sent_tl
                        for word in word_hit:
                            new_kwd = '<font_color={} id=1><b>'.format(hwd_color)+word+"</b></font>"
                            new_en_sent = re.sub(word, new_kwd, new_en_sent)                        
                        if show_source == 'on':
                            sent_source = '<p align = "right"><font_color={} id=3>—— <i>'.format(note_color) + article.title +'</i></font></p>'
                        else:
                            sent_source = ''                  
                        result_list.append(str(i)+'\t'+"原文"+ '\t'+sent.sent_sl + sent_source)
                        sl_context,tl_context = article.get_context(sent.num, hst_color, sents_left, sents_right)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+ sl_context)
                        result_list.append(str(i)+'\t'+"译文"+ '\t'+ new_en_sent + sent_source)
                        if show_context == 'on':                        
                            result_list.append(str(i)+'\t'+"语境"+ '\t'+ tl_context)                    
                        i += 1
                    else:
                        pass
                    
        return result_list

    def print_result(self, result_list):
        if result_list:
            self.result_list = result_list
            if self.display_mode.show_context == 'on':
                result_length = int(len(result_list)/4)
            else:
                result_length = int(len(result_list)/2) 
            num_list = []
            lang_list = []
            sent_list = []
            for result in result_list:
                num = result.split('\t')[0]
                lang = result.split('\t')[1]
                sent = result.split('\t')[2]
                num_list.append(num)
                lang_list.append(lang)
                sent_list.append(sent)
            df_data = self.converter.lst2pd(num_list, lang_list, sent_list)
            self.result_html = self.converter.pdf2html(df_data, self.font_name, self.font_size)
            self.temp_html = self.result_html
            self._ui._resultWindow.setText(self.result_html)
            self._ui._hit_stats.setText(str(result_length))
        else:
            self._ui._statusBar.showMessage('很抱歉，未找到符合条件的句对！',3000)  
            self._ui._hit_stats.setText("0")
            self.result_list = []
            self.temp_html = ""        
            
        return self.result_list, self.temp_html            
        
    def save_text(self):
        if self.result_list is not None and len(self.result_list):
            srcInput = self._ui._input_box.text().strip()
            file_id_path = self.outPutDir.joinpath(srcInput)
            file_id = file_id_path.with_suffix('.output.txt')
            result='\n'.join(self.result_list)
            result=re.sub(r'<b>(\w+)</b>','【\g<1>】',result)
            result=re.sub(r'<(.*?)>','',result)
            with open(file_id, 'w', encoding='utf-8') as f:
                f.write(result)
            self._ui._statusBar.showMessage(f'检索结果已成功保存为"{srcInput}_output.txt"')
        else:
            self._ui._statusBar.showMessage("很抱歉，检索结果未能成功保存为TXT文件")
            
    def save_html(self):
        if self.temp_html:
            srcInput = self._ui._input_box.text().strip()
            file_id_path = self.outPutDir.joinpath(srcInput)
            file_id = file_id_path.with_suffix('.output.html')
            with open(file_id, 'w', encoding='utf-8') as f:
                f.write(self.temp_html)
            self._ui._statusBar.showMessage(f'检索结果已成功保存为"{srcInput}_output.html"')
        else:
            self._ui._statusBar.showMessage("很抱歉，检索结果未能成功保存为html文件")

