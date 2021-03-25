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

import pandas as pd

class SearchResultConverter:
    def __init__(self):
        pass

    def lst2pd(self, numlist, langlist, sentlist):
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_colwidth', 10000)
        df = pd.DataFrame({'num': numlist, \
                           'lang': langlist, \
                           'sent': sentlist})
        df.set_index(['num', 'lang'], inplace=True)
        return df    
    
    def pdf2html(self,df_data, font_id, font_size):
        tm_html=df_data.to_html(header=None, index=True,index_names=False,escape=False,col_space='5',border='2')
        tm_html = tm_html.replace('border="2"',
                                  'border="2", style="border-collapse:collapse;font-family:{};font-size:{}pt;"'.format(font_id,font_size,))
        tm_html = tm_html.replace('valign="top"',
                                  'valign="middle" align="center"')
        tm_html = tm_html.replace('<table',
                                  '<html>\n<body>\n<table cellpadding = "5"')
        tm_html = tm_html.replace('</table>',
                                  '</table>\n</body>\n</html>')
        tm_html = tm_html.replace('<th>',
                                  '<th valign="middle" align="center">')
        tm_html=tm_html.replace('font_color','font color')
        return tm_html
    
