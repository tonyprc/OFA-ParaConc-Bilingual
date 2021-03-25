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
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow, QTextBrowser, QMessageBox, QDoubleSpinBox, QLabel, QPushButton, QGroupBox, QGridLayout
from PyQt5.QtGui import QIcon

class SubWindow(QMainWindow):
    def __init__(self, parent=None):
        super(SubWindow, self).__init__(parent)
        currentDir = Path.cwd()
        dataDir = currentDir.joinpath("app_data")
        self.imageDir = dataDir.joinpath("images")
        
        self.setWindowTitle('双语全文')
        self.setGeometry(100, 100, 800, 600)
        self._browser = QTextBrowser(self)
        self.setCentralWidget(self._browser)

        self.setWindowIcon(QIcon(str(self.imageDir / "fulltext.png")))
       
    def setText(self, text):
        self._browser.setText(text)
        
    def setTitle(self, title):
        self.setWindowTitle(title)

class ContextWindow(QMainWindow):
    def __init__(self, parent=None):
        super(ContextWindow, self).__init__(parent)
        currentDir = Path.cwd()
        dataDir = currentDir.joinpath("app_data")
        self.imageDir = dataDir.joinpath("images")
        
        self.setWindowTitle('语境设置')
        self.setGeometry(100, 100, 80, 80)
        self.setFixedSize(220, 120)
        
        self._frame = QGroupBox()
        
        self._sent_l_label = QLabel("关键句句前总句数：")
        self._sent_l_box = QDoubleSpinBox()
        self._sent_l_box.setFixedWidth(80)
        self._sent_l_box.setMinimum(0)
        self._sent_l_box.setMaximum(10)
        self._sent_l_box.setDecimals(0)
        self._sent_l_box.setValue(1)        
        self._sent_r_label = QLabel("关键句句后总句数：")
        self._sent_r_box = QDoubleSpinBox()
        self._sent_r_box.setMinimum(0)
        self._sent_r_box.setMaximum(10)
        self._sent_r_box.setDecimals(0)
        self._sent_r_box.setValue(1)
        self._ok_button = QPushButton()
        self._ok_button.setText("确定")
        self._ok_button.clicked.connect(self.close)
        self._ok_button.setFixedWidth(80)
        

        self._form_layout = QGridLayout()
        self._form_layout.addWidget(self._sent_l_label, 0, 0)
        self._form_layout.addWidget(self._sent_l_box, 0, 1)
        self._form_layout.addWidget(self._sent_r_label, 1, 0)
        self._form_layout.addWidget(self._sent_r_box, 1, 1)
        self._form_layout.addWidget(self._ok_button, 2, 1)
        self._frame.setLayout(self._form_layout)
        
        self.setCentralWidget(self._frame)
        self.setWindowIcon(QIcon(str(self.imageDir / "context.png")))

class MessageBox(QMessageBox):
    def __init__(self):
        QMessageBox.__init__(self)        
        self.setTitle("警告信息")
        self.setText("以下未加载语料存在未对齐问题，请核实后重新加载！")
        self.setStandardButtons(QMessageBox.Close)
        
    def set_text(self, text):
        self.setText(text)
