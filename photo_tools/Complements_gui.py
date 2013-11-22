# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 22:05:07 2013

@author: Amandine & Matthieu
"""

import os

from PyQt4 import QtGui, QtCore

os.system("pyuic4 fenetre_principale.ui > fenetre_principale.py")
import fenetre_principale

class MyMainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui = fenetre_principale.Ui_MainWindow()
        self.ui.setupUi(self)