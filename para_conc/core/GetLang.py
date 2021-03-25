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

from langdetect import detect, detect_langs, DetectorFactory

# 使用谷歌langdetect检测语言

class GetLang:
    # 设置种子，使检测结果唯一化
    DetectorFactory.seed = 0
    # 对字符串进行检测
    def __init__(self):
        self.lg_id = ""       
        self.lg_rate = ""
        self.lg_input = ''

    def get_lang(self, sample):
        lg_id_found = detect(sample)
        if "-" in lg_id_found:
            lg_id = lg_id_found.split("-")[0].strip()
        else:
            lg_id = lg_id_found.strip()
        self.lg_id = lg_id            
        return self.lg_id
   
    def get_rate(self,sample):
        result_rate = str(detect_langs(sample)[0])
        # 从字符串中提取数字，并转成浮点格式
        self.lg_rate = float(result_rate.split(':')[-1])
        # 返回浮点格式的语言概率
        return self.lg_rate

    # 用户输入语言检测
    def detect_lang(self, text):
        target_lang = 'en'
        for word in text:
            if '\u4e00' <= word <= '\u9fa5' or '\u3400' <= word <= '\u4DB5':
                target_lang = 'zh'
                break
            elif '\u0800' <= word <= '\u4e00':
                target_lang = 'ja'
                break
            elif '\u3130' <= word <= '\u318f' or '\uAC00' <= word <= '\uD7A3':
                target_lang = 'ko'
                break
            else:
                target_lang = 'en'
        self.lg_input = target_lang
        return self.lg_input
    
# 本类的使用方法：        
#def main():
#    string = "检测样本"
#    string2 = ["Tu","es","tres","bien","!"]
#    lgT = GetLang()
#    lgT.get_lang(string)
#    lgT.get_lang_list(string2)
#    lgT.get_rate(string2)
#    print(lgT.lg_id)
#    print(lgT.lg_rate)
    #print(f"检测样本： {lgT.sample}")
    #print(f"检测结果： {lgT.lg_id}")
    #print(f"检测精度： {lgT.lg_rate:.2%}")

#if __name__ == '__main__':
#    main()        



