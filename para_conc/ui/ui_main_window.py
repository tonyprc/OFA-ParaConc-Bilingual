#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tony Chang (42716403@qq.com)

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
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWidgets import (QMainWindow, QGridLayout, QHBoxLayout, QVBoxLayout, QFormLayout, QAction, QComboBox,QFileDialog,
                             QGroupBox, QPushButton, QLineEdit, QLabel, QRadioButton, QStatusBar,QSizePolicy,QMessageBox,
                             QButtonGroup,QTextBrowser,QTabWidget,QTreeView,QTreeWidget,QTreeWidgetItem,QMenu,
                             QCheckBox, QDoubleSpinBox, QAbstractItemView, QWidget, QListWidget, QMessageBox, QSplitter,
                             QColorDialog, QFontDialog)

from PyQt5.QtWidgets import QApplication
from langdetect import detect, detect_langs, DetectorFactory
from para_conc.core.GetLang import GetLang
from para_conc.core.corpus import Corpus
from para_conc.core.searchResultConverter import SearchResultConverter
from para_conc.core.search_configure import SearchMode, ColorMode
from para_conc.ui.ui_sub_window import ContextWindow
from enum import Enum
from pathlib import Path
       
class UIMainWindow(QMainWindow):
    save_text = pyqtSignal()
    save_html = pyqtSignal()
    search = pyqtSignal()
    load_files = pyqtSignal(list)
    file_open_request = pyqtSignal(str)
    keyColorChanged = pyqtSignal(int)
    closeFiles = pyqtSignal()
    closeCurrentFiles = pyqtSignal()
    select_item = pyqtSignal()
    display_request = pyqtSignal(str, str)
    add_segs = pyqtSignal()

    def __init__(self, parent=None):
        super(UIMainWindow, self).__init__(parent)
        currentDir = Path.cwd()
        self.outPutDir = currentDir.joinpath("saved_files")
        dataDir = currentDir.joinpath("app_data")
        self.imageDir = dataDir.joinpath("images")
        self.workFileDir = dataDir.joinpath("workfiles")

        self.colorMode = ColorMode()
        self.context_setting_window = ContextWindow()

        self.src_mode = 1        
        
        openFileAction=QAction(QIcon(str(self.imageDir / "more.png")),'&打开文件',self, triggered=self.openFileRequest)
        openFileAction.setStatusTip('单击打开文件，Ctrl+鼠标左键打开多个文件')        
        openDirAction=QAction(QIcon(str(self.imageDir / "opendir.png")),'&打开目录',self, triggered=self.openDirRequest)
        openDirAction.setStatusTip('载入目录下所有TXT文件')
        closeFileAction=QAction(QIcon(str(self.imageDir / "close.png")),'&关闭选定文件',self, triggered=self.closeCurrentFiles)
        closeFileAction.setStatusTip('关闭选中的单个或多个文件')
        closeFilesAction=QAction(QIcon(str(self.imageDir / "clear.png")),'&关闭全部文件',self, triggered=self.closeFiles)
        closeFilesAction.setStatusTip('关闭当前目录所有TXT文件')
        outTxtAction = QAction(QIcon(str(self.imageDir / "txt.png")),'&输出TXT', self, triggered=self.save_text)
        outTxtAction.setStatusTip('将当前检索结果保存为TXT文本文件')
        outHtmlAction = QAction(QIcon(str(self.imageDir / "html.png")),'输出HTML', self, triggered=self.save_html)
        outHtmlAction.setStatusTip('将当前检索结果保存为HTML网页文件')
        aboutAction = QAction(QIcon(str(self.imageDir / "about.png")),'&关于我们', self, triggered=self._info)
        aboutAction.setStatusTip('显示软件制作信息')
        exitAction = QAction(QIcon(str(self.imageDir / "quit.ico")),'&退出', self, triggered=self.close)
        exitAction.setStatusTip('退出本软件')
        
        displaySourceAction=QAction('&显示语料来源',self, checkable=True, triggered=self.displaySource)
        displaySourceAction.setChecked(True)
        displaySourceAction.setStatusTip('在检索结果各句后附加显示相应文件名称') 
        displayContextAction=QAction('&显示语境',self, checkable=True, triggered=self.displayContext)    
        displayContextAction.setStatusTip('在检索结果各句下方显示包含该句在内的语料')
        displayContextRangeAction = QAction(QIcon(str(self.imageDir / "context.png")),'&设置语境',self, triggered=self.setContextRange)   
        displayContextRangeAction.setStatusTip('在检索结果各句下方显示包含该句在内的指定行数的语料')
        hiWordColorAction = QAction(QIcon(str(self.imageDir / "C1.png")),'&设置关键词高亮颜色',self, triggered=self.setHiWordColor)
        hiWordColorAction.setStatusTip('设置语料检索窗口中检索词的高亮颜色')
        hiSentColorAction = QAction(QIcon(str(self.imageDir / "C2.png")),'&设置关键句高亮颜色',self, triggered=self.setHiSentColor)
        hiSentColorAction.setStatusTip('设置语料检索窗口中检索词所在句子在语境中的高亮颜色')
        noteColorAction = QAction(QIcon(str(self.imageDir / "C3.png")),'&设置语源标注颜色',self, triggered=self.setNoteColor)
        noteColorAction.setStatusTip('设置语料检索窗口中语料来源标注信息的颜色')
        segAction = QAction(QIcon(str(self.imageDir / "convert.png")),'&SEG赋码工具',self, triggered=self.add_segs)
        segAction.setStatusTip('将双语生语料文本文件转换为带seg标记的cuc文本文件')
        
        menubar = self.menuBar()
        menubar.setContextMenuPolicy(Qt.PreventContextMenu)
        fileMenu = menubar.addMenu('文件')
        fileMenu_loadGroup = fileMenu.addMenu(QIcon(str(self.imageDir / "add.png")),'语料加载')
        fileMenu_loadGroup.addAction(openFileAction)
        fileMenu_loadGroup.addAction(openDirAction)
        fileMenu_unloadGroup = fileMenu.addMenu(QIcon(str(self.imageDir / "remove.png")),'语料卸载')
        fileMenu_unloadGroup.addAction(closeFileAction)
        fileMenu_unloadGroup.addAction(closeFilesAction)        
        fileMenu_saveGroup = fileMenu.addMenu(QIcon(str(self.imageDir / "save.png")),'语料输出')
        fileMenu_saveGroup.addAction(outTxtAction)
        fileMenu_saveGroup.addAction(outHtmlAction)
        fileMenu.addAction(exitAction)
        settingMenu = menubar.addMenu('&设置')        
        colorMenu=settingMenu.addMenu(QIcon(str(self.imageDir / "palette.png")),"颜色设置")
        colorMenu.addAction(hiWordColorAction)
        colorMenu.addAction(hiSentColorAction)
        colorMenu.addAction(noteColorAction)
        displayMenu=settingMenu.addMenu(QIcon(str(self.imageDir / "view.png")),"附加信息设置")
        displayMenu.addAction(displayContextRangeAction)
        displayMenu.addAction(displaySourceAction)
        displayMenu.addAction(displayContextAction)
        segMenu = menubar.addMenu('工具')
        segMenu.addAction(segAction)
        infoMenu = menubar.addMenu('关于')
        infoMenu.addAction(aboutAction)
        
        
        # region create window
        self._inputFrame = QGroupBox()
        self._inputFrame.setFixedHeight(60)
        self._input_layout = QHBoxLayout()
        self._input_layout.setSpacing(2)
        self._src_mode_opt =QComboBox()        
        self._src_mode_opt.setFixedWidth(85)
        self._src_mode_opt.setFixedHeight(25)
        self._src_mode_opt.addItem("普通模式")
        self._src_mode_opt.addItem("拓展模式")
        self._src_mode_opt.addItem("正则模式")
        self._src_mode_opt.setCurrentIndex(1)
        
        self._input_box = QLineEdit()
        self._input_box.setFixedHeight(25)
        #self._input_box.setFixedWidth(400)
        self._input_button = QPushButton("检索")
        self._input_button.clicked.connect(self.search)
        self._input_button.setFixedWidth(80)
        self._input_button.setFixedHeight(25)
        
        self._input_layout.addWidget(self._src_mode_opt)
        self._input_layout.addWidget(self._input_box)
        self._input_layout.addWidget(self._input_button)
        self._inputFrame.setLayout(self._input_layout)

        self._src_result_form = QGroupBox("语料检索")
        self._src_result_form.setAlignment(Qt.AlignCenter)       
       
        self._resultWindow = QTextBrowser(parent)
        self._resultWindow.setFrameStyle(0)
        self._resultWindow.setStyleSheet("QTextBrowser{background-color:%s}"% ('WhiteSmoke'))
       
        self._src_result_formLayout = QVBoxLayout()
        self._src_result_formLayout.addWidget(self._resultWindow)
        self._src_result_form.setLayout(self._src_result_formLayout)


        self._rightFrame = QSplitter(Qt.Vertical)
        rightLayout = QVBoxLayout(self._rightFrame)
        rightLayout.setSpacing(0)
        rightLayout.addWidget(self._src_result_form)
        rightLayout.addWidget(self._inputFrame)        
        rightLayout.setAlignment(Qt.AlignCenter)
        self._rightFrame.setStretchFactor(1,0)

        self._leftFrame = QSplitter(Qt.Vertical)
        
        self._corpusFrame = QGroupBox('语料列表')
        self._corpusFrameLayout = QVBoxLayout()
        self._corpusWindow = QListWidget()
        self._corpusWindow.setStyleSheet("QListWidget{background-color:%s}"% ("WhiteSmoke"))
        self._corpusWindow.setFixedWidth(180)
        self._corpusWindow.setMaximumWidth(180)
        self._corpusWindow.setSortingEnabled(True)
        self._corpusWindow.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._corpusWindow.itemSelectionChanged.connect(self.select_item)
        self._corpusWindow.setContextMenuPolicy(Qt.CustomContextMenu)
        self._corpusWindow.customContextMenuRequested.connect(self.listItemRightClicked)
        self._corpusWindow.itemDoubleClicked.connect(self.openCurrentFileRequest)
        self._corpusFrameLayout.addWidget(self._corpusWindow)
        self._corpusFrame.setLayout(self._corpusFrameLayout)

        self._statFrame = QGroupBox('语料统计')
        self._statFrame.setFixedHeight(80)
        self._statLayout = QFormLayout()
        self._statLayout.setSpacing(2)
        self._file_stats = QLabel()
        self._char_stats = QLabel()
        self._hit_stats = QLabel()
        self._file_stats.setText("0")
        self._char_stats.setText("0")
        self._hit_stats.setText("0")
        self._statLayout.addRow(QLabel("语料文件个数："), self._file_stats)
        self._statLayout.addRow(QLabel("语料字符总数："), self._char_stats)
        self._statLayout.addRow(QLabel("命中句对组数："), self._hit_stats)
        self._statFrame.setLayout(self._statLayout)

        self._leftFrame.addWidget(self._corpusFrame)
        self._leftFrame.addWidget(self._statFrame)
        self._leftFrame.setStretchFactor(1,0)
               
        mainWidget = QWidget()
        mainLayout = QHBoxLayout(mainWidget)
        mainLayout.addWidget(self._leftFrame)
        mainLayout.addWidget(self._rightFrame)
        mainLayout.setSpacing(2)        
        self.setCentralWidget(mainWidget)

        # ----------创建主窗口状态栏----------
        self._statusBar = QStatusBar()
        self._statusBar.showMessage("欢迎使用傲飞双语一对一平行检索工具!")
        self._copyRightLabel = QLabel("OFA @ 抚顺职业技术学院（抚顺师专）外语系 Since 2020")
        self._statusBar.addPermanentWidget(self._copyRightLabel)
        self.setStatusBar(self._statusBar)

        # ----------设置页面尺寸及标题等----------
        self.setGeometry(100, 100, 800, 600)
        self.setObjectName("MainWindow")
        self.setWindowTitle("傲飞双语一对一平行检索工具")
        self.setWindowIcon(QIcon(str(currentDir / "app_data/workfiles/myIcon.png")))
        self.setIconSize(QSize(100, 40))
        # endregion 创建窗口

    #设置语料来源显示选项，向主窗口传参，用于主窗口检索
    def txt2cuc(self):
        pass
    
    def displaySource(self, state):
        show_source = 'on'
        if state == 0:
            show_source = 'off'
        self.display_request.emit("show_source", show_source)
            
    def displayContext(self, state):
        show_context = 'off'
        if state == 1:
            show_context = 'on'
        self.display_request.emit("show_context", show_context)

    def setContextRange(self):        
        self.context_setting_window.show()


    def setHiWordColor(self):
        hwdColor = QColorDialog.getColor(Qt.red,self)
        if hwdColor.isValid():
            self.colorMode.set_color(1,hwdColor.name())
            self.keyColorChanged.emit(1)
    
    def setHiSentColor(self):
        hstColor = QColorDialog.getColor(Qt.blue,self)
        if hstColor.isValid():
            self.colorMode.set_color(2, hstColor.name())
            self.keyColorChanged.emit(2)
    
    def setNoteColor(self):
        noteColor = QColorDialog.getColor(Qt.gray,self)
        if noteColor.isValid():
            self.colorMode.set_color(3,noteColor.name())
            self.keyColorChanged.emit(3)
    
    #通过预设独立函数将检索模式选项数字化
    def search_mode(self) -> SearchMode:
        src_mode = self._src_mode_opt.currentText()
        if src_mode == "普通模式":
            return SearchMode.NORMAL
        if src_mode == "正则模式":
            return SearchMode.REGEX
        return SearchMode.EXTENDED

    def search_text(self):
        return self._input_box.text()
  
    def openCurrentFileRequest(self,item):
        self.file_open_request.emit(item.text())
       
    def openFileRequest(self): 
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self,"打开文件夹", "","Text files(*.txt)", options=options)
        fileLens=0
        if files:
            #向main_window发出文件列表
            self.load_files.emit(files)               
              
    def openDirRequest(self):        
        options = QFileDialog.Options()
        options |= QFileDialog.ShowDirsOnly
        presentDir = QFileDialog.getExistingDirectory(self,"打开文件夹", "",options=options)
        if presentDir!= "":            
            self._statusBar.showMessage('正在加载所有文件，请稍候...')
            filesInDir = os.listdir(presentDir)
            files = [os.path.join(presentDir, name).replace("\\",'/') for name in filesInDir if name.endswith(".txt")]
            # 向main_window发出文件列表
            self.load_files.emit(files) 
                
    def listItemRightClicked(self, QPos):
        item_num = self._corpusWindow.count()
        if item_num != 0:
            self.listMenu= QMenu()                                                  
            listMenuItem = self.listMenu.addAction(QIcon(str(self.imageDir /"close.png")),"关闭当前文件")
            listMenuItem.triggered.connect(self.closeCurrentFiles) #指向main_window
            parentPosition = self._corpusWindow.mapToGlobal(QPoint(0, 0))
            self.listMenu.move(parentPosition + QPos)
            self.listMenu.show()
   
    def _info(self):
        QMessageBox.about(self, "About Us",
                          '''<p align='center'>傲飞双语一对一平行检索工具 V.0.0.1<br>Windows Version 2021\
                          <br>抚顺职业技术学院（抚顺师专）外语系 版权所有<br>软件制作：\
                          <br>Tony Chang<br>电子邮件：42716403@qq.com</p>''')    

    
 

