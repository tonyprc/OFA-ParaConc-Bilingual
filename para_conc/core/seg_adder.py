#!/usr/bin/python3
# -*- coding: utf-8 -*-
# OFA Mate V.1.0.0 for OFA ParaConc
# Copyright (c) 2020 Tony Chang (42716403@qq.com)

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

import sys, os, json
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt,QSize,pyqtSignal
from PyQt5.QtGui import QIcon,QTextCursor
from PyQt5.QtWidgets import (QMainWindow,QGridLayout,QHBoxLayout,QVBoxLayout,QAction,QComboBox,QDoubleSpinBox,
                             QToolBox,QGroupBox,QPushButton,QLineEdit,QLabel,QRadioButton,QStatusBar,QButtonGroup,
                             QCheckBox,QCompleter,QAbstractItemView,QWidget,QListWidget,QTextEdit,QFileDialog)

class SegAdder(QMainWindow):
    open_raw_files = pyqtSignal()
    add_seg = pyqtSignal()
    def __init__(self,parent = None):
        super(SegAdder,self).__init__(parent)
        # 使用pathlib库，避免出现文件路径/与\不统一问题，获取当前目录的方法。
        currentDir = Path.cwd()

        self.present_dir = ""
        self.file_list = []

        self._fileloader_frame = QGroupBox()
        self._fileloader_frame.setAlignment(Qt.AlignCenter)
        
        self._fileloader_layout = QHBoxLayout()
        self._file_openBox = QLineEdit()
        self._file_openBox.setFixedWidth(300)
        self._file_openBox.setReadOnly(False)
        self._file_openButton = QPushButton()
        self._file_openButton.setText("打开文件夹")
        self._file_openButton.setFixedWidth(80)
        self._file_openButton.clicked[bool].connect(self.open_raw_files)
        self._file_addSegButton = QPushButton("开始赋码")
        self._file_addSegButton.setFixedWidth(80)
        self._file_addSegButton.clicked[bool].connect(self.add_seg)
        self._fileloader_layout.addWidget(self._file_openBox)
        self._fileloader_layout.addWidget(self._file_openButton)
        self._fileloader_layout.addWidget(self._file_addSegButton)

        self._fileloader_frame.setLayout(self._fileloader_layout)

        self._filedisplay_box = QTextEdit()
          
        mainWidget = QWidget()
        mainLayout = QVBoxLayout(mainWidget)
        mainLayout.setSpacing(2)
        mainLayout.addWidget(self._fileloader_frame)
        mainLayout.addWidget(self._filedisplay_box)
        self.setCentralWidget(mainWidget)       
        
        
        #----------设置页面尺寸及标题等----------
        self.setGeometry(200, 50, 200, 300)
        self.setWindowTitle("文本文件SEG赋码工具")
        # QIcon只接受字符串式的网址，且不接受windowpath对象，因此不能用joinpath连接。
        self.setWindowIcon(QIcon(str(currentDir / "app_data/images/convert.png")))
        self.setIconSize(QSize(100, 40))
        self.show()

    def open_raw_files(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        presentDir = QFileDialog.getExistingDirectory(self, "打开文件夹", "", options = options)
        if presentDir:
            self._file_openBox.setText(presentDir)            
            # 使用pathlib库，避免出现文件路径/与\不统一问题。
            self.present_dir = Path(presentDir)
            # 用Path.iterdir()会产生文件完整路径对象列表，不便于进一步筛选内容，还是用os
            self.file_list = os.listdir(presentDir)
        return self.present_dir, self.file_list

    def add_seg(self):
        if self.present_dir:
            if self.file_list:
                self._filedisplay_box.clear()
                self.screened_list = [file for file in self.file_list if "CUC.txt" not in file]
                self.file_num = len(self.screened_list)
                self._filedisplay_box.setText(f">>> 本次共加载{self.file_num}个待赋码文件。\n>>> 现在开始赋码，请稍候...")
                j = 0
                for file_name in self.screened_list:
                    #实时显示进程
                    QApplication.processEvents()
                    #合并路径，形成新windowpath网址
                    file_id = self.present_dir.joinpath(file_name)
                    #在后缀名前加上CUC标志
                    file_save_id = file_id.with_suffix('.CUC.txt')
                    #获取路径中的文件名部分
                    file_save_name = file_save_id.name                                           
                    bi_list=[]
                    with open (file_id,'rt', encoding='utf-8-sig') as f:
                        para_tank=f.readlines()
                        zh_para=para_tank[0::2]
                        en_para=para_tank[1::2]
                        for i,(x,y) in enumerate(zip(zh_para,en_para),start=1):
                            a='<seg id="'+str(i)+'">'+x.strip().replace('[P]','')+'</seg>'
                            b='<seg id="'+str(i)+'">'+y.strip().replace('[P]','')+'</seg>'
                            bi_list.append(a)
                            bi_list.append(b)
                        #将光标后移至尾部，并追加提示文字。
                        self._filedisplay_box.moveCursor(QTextCursor.End)
                        self._filedisplay_box.append(f">>> {file_name} 赋码完毕！") 
                    if bi_list:
                        j += 1
                        cuc_text='\n'.join(bi_list)
                        with open (file_save_id,'wt', encoding='utf-8-sig') as f:
                            f.write(cuc_text)
                            self._filedisplay_box.moveCursor(QTextCursor.End)
                            file_left = self.file_num - j
                            if  file_left == 0:
                                self._filedisplay_box.append(f">>> 赋码文件已保存为 {file_save_name}\n>>> 所有文件已赋码完毕！")
                            else:                                    
                                self._filedisplay_box.append(f">>> 赋码文件已保存为 {file_save_name}！\n>>> 还有{file_left}个文件待赋码。")
                                   
            else:
                self._filedisplay_box.clear()
                self._filedisplay_box.setText(f">>> 此目录为空，请加载有效文件夹！")
            
        else:
            self._filedisplay_box.clear()
            self._filedisplay_box.setText(f">>> 您尚未选择任何文件夹，请选择待赋码文件所在文件夹！")               
        
        
#def main():
#    app = QApplication(sys.argv)
#    mainWindow = SegAdder()
#    sys.exit(app.exec_())


#if __name__ == '__main__':
#    main()


