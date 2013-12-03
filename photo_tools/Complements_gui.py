# -*- coding: utf-8 -*-
"""
Created on Fri Nov 22 22:05:07 2013

@author: Amandine & Matthieu
"""

import os

from PyQt4 import QtGui, QtCore

import grille_explorateur

os.system("pyuic4 fenetre_principale.ui > fenetre_principale.py")
import fenetre_principale

class MyMainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.ui = fenetre_principale.Ui_MainWindow()
        self.ui.setupUi(self)
#        self.ui.grille_widget = grille_explorateur.ExplorateurListView()
    
        self.dirModel = QtGui.QFileSystemModel()
        self.dirModel.setRootPath("/")
        
#        print self.ui.frame.setSi

        self.ui.treeView_2.setModel(self.dirModel)
        self.ui.treeView_2.setColumnHidden(1, True)
        self.ui.treeView_2.setColumnHidden(2, True) 
        self.ui.treeView_2.setColumnHidden(3, True) 
        self.ui.treeView_2.setHeaderHidden(True)
        
        _resize = lambda : self.ui.treeView_2.resizeColumnToContents(0)
        self.ui.treeView_2.clicked.connect(_resize)
        self.ui.treeView_2.expanded.connect(_resize)
        self.dirModel.layoutChanged.connect(_resize)        
        self.ui.treeView_2.collapsed.connect(_resize)
        
        
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(20, 500)
        self.slider.setValue(100)
                
        self.explorateur = grille_explorateur.ExplorateurListView(self.slider)
        
        self.spacer = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        
        self.ui.gridLayout_2.addWidget(self.explorateur, 0, 0, 1, 2)        
        self.ui.gridLayout_2.addWidget(self.slider, 1, 1, 1, 1)
        self.ui.gridLayout_2.addItem(self.spacer, 1, 0, 1, 1)