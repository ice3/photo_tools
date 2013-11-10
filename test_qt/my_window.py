# -*- coding: utf-8 -*-
"""
Created on Mon Nov 04 18:38:18 2013

@author: Amandine
"""
from PyQt4 import QtGui, QtCore
import os

import time

import re

#path_to_test = r'D://Amandine DONNEES//Photos//Photos famille//2013//Lyon_12-13-14-Avril'
path_to_test = r'./img/rapide'

def tryint(s):
    try:
        return int(s)
    except:
        return s

def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]

  
    

class MyQListView(QtGui.QListView):

    def dropEvent(self, drop_event):
        print self.model().itemFromIndex(self.indexAt(drop_event.pos()))
        item_src = [self.model().itemFromIndex(index) for 
                    index in self.selectedIndexes()]
        item_dest = self.model().itemFromIndex(self.indexAt(drop_event.pos()))
        print 'source, dest', item_src, item_dest
        self.move_element(item_src, item_dest)
        
    def move_element(self, item_src, item_dest):
        # là où on relache la souris
        if item_dest is None:
            # si pas d'item à cet endroit, on met à la fin
            dest_row = self.model().rowCount()
        else :
            # sinon, on met à l'endroit demandé
            dest_row = item_dest.row()
        print "dest_row", dest_row    
        # item_src liste dans l'ordre où on clique les objets
        # on la remet dans l'ordre des photos
        item_src = sorted(item_src, key = lambda x: -x.row())
        src_rows =[i.row() for i in item_src]
        items_to_insert = [self.parent().list_img.pop(i) for i in src_rows]
        print "reste liste", self.parent().list_img
        items_to_insert.reverse()
        print "items to insert", items_to_insert
        nb_elem_inf_dest  = sum([1 for i in src_rows if i < dest_row])
        print "nb_elem inf dest", nb_elem_inf_dest
        print "endroit d'insertion", dest_row-nb_elem_inf_dest
        self.parent().list_img = self.parent().list_img[:dest_row-nb_elem_inf_dest] +\
                                items_to_insert + self.parent().list_img[dest_row-nb_elem_inf_dest:]
                                     
        self.parent().update_model()

    def wheelEvent(self, event):
        super(MyQListView, self).wheelEvent(event)
        delta = self.parent().slider.value() + event.delta()/20
        modified = QtGui.QApplication.keyboardModifiers()
        print modified
        if modified == QtCore.Qt.ControlModifier:
            self.parent().slider.setValue(delta)

    def dragMoveEvent(self, event):
        pass


    def resizeEvent(self, event):
        self.change_grid_size()
        super(MyQListView, self).resizeEvent(event)

    def change_grid_size(self):
        """
        Change l'espace entre les items en fonction de la taille de la listView.
        Quand on change la taille de la fenetre (et donc de la liste) les items se réorganisent automatiquement pour
        qu'il y ait le bon nombre d'item par ligne, mais ça laisse un gros espace sur la droite. C'est ce que l'on veut
        changer.
        """

        # width of the QListView
        width = self.size().width()
        # separation between the items
        # we can't use the setSpacing and the setGridSize at the same time (otherwise we would have used setSpacing)
        x_grid_sep = 50
        dx = x_grid_sep + 10 # don't know where the 10 comes from... maybe the right margin...
        img_size = self.iconSize().width()
        # get the size of a grid element (image + spacing)
        grid_elem_size = img_size + dx + self.spacing()
        nb_grid_shown = width / grid_elem_size
        # The number can be bigger than the number of elements in the list
        nb_grid_shown = min(nb_grid_shown, len(self.parent().list_img))
        width_used = nb_grid_shown * grid_elem_size
        # The lost space in the right side that we want to get rid of
        empty_width = width - width_used
        delta_width = empty_width*1.0 / (nb_grid_shown + 1) # +1 for ZeroDivisionError and to count the number of spaces
        space_around_img = QtCore.QSize(50, 30)
        width = QtCore.QSize(delta_width, 0) +  self.iconSize() + space_around_img
        self.setGridSize(width)

class ExplorateurListView(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.layout = QtGui.QVBoxLayout()
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(20, 500)
        self.slider.setValue(100)
#        self.modele = QtGui.QFileSystemModel(self)
#        filters = QtCore.QStringList("*.JPG")
#        self.modele.setRootPath(QtCore.QDir.currentPath())
#        self.modele.setNameFilterDisables(False)
#        self.modele.setIconProvider(self.theIconProvider)
        
        #TODO vider le cache quand on change de dossier            
        #self.cache = QtGui.QPixmapCache()
        self.cache = {}

        self.modele = QtGui.QStandardItemModel(self)
        self.vue_liste = MyQListView(self)
        self.create_model(path_to_test)
        
        self.vue_liste.setFlow(0)
        self.vue_liste.setWrapping(True)
        self.vue_liste.setViewMode(QtGui.QListView.IconMode)
        self.vue_liste.setResizeMode(QtGui.QListView.Adjust)
        self.vue_liste.setMovement(QtGui.QListView.Snap)
        self.vue_liste.setGridSize(QtCore.QSize(150, 150))
        self.vue_liste.setIconSize(QtCore.QSize(100, 100))
#        self.vue_liste.setLayoutMode(QtGui.QListView.Batched)
        self.vue_liste.setBatchSize(3)
#        self.vue_liste.setUniformItemSizes(True)
        self.vue_liste.setSelectionMode(QtGui.QListView.ExtendedSelection)
        self.vue_liste.setModel(self.modele)
#        self.vue_liste.setRootIndex(self.modele.index("."))     
#        self.modele.setNameFilters(filters)
        self.layout.addWidget(self.vue_liste)
        self.layout.addWidget(self.slider)
        self.setLayout(self.layout)    
        
        self.slider.valueChanged.connect(self.update_icon_size)
    

            
    def update_model(self):
        t1 = time.clock()        
        self.modele.clear()
        print 'temps modele.clear() : ', time.clock()-t1
        t1 = time.clock()
        for file_name in self.list_img:
            t2 = time.clock()
            pixmap = QtGui.QPixmap()
#            if not self.cache.find(file_name, pixmap):
            if not file_name in self.cache:                
                print 'cache pas exister', file_name
                pixmap = QtGui.QPixmap(path_to_test + os.sep + file_name)
                pixmap = pixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
                self.cache[file_name] = pixmap
            else:
                pixmap = self.cache[file_name]                     
            icone = QtGui.QIcon(pixmap)
            item = QtGui.QStandardItem(icone, file_name) 
            self.modele.appendRow(item)    
            print 'temps update 1 image : ', time.clock()-t2, file_name
            
        print "temps update modele : ", time.clock()-t1

    def create_model(self, chemin):
        img_ext = ('bmp', 'png', 'jpg', 'jpeg')
        self.list_img = [name for name in os.listdir(chemin) 
                    if name.lower().endswith(img_ext)]
        self.list_img.sort(key=alphanum_key)
#        dossier = QtCore.QDir(chemin)        
#        infosContenuDossier = dossier.entryInfoList(QtCore.QDir.AllEntries | 
#                QtCore.QDir.NoDotAndDotDot, QtCore.QDir.DirsFirst)
        t1 = time.clock()        
        for file_name in self.list_img:
            t2 = time.clock()
            pixmap = QtGui.QPixmap(path_to_test + os.sep + file_name)
            pixmap = pixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
            
#            if not self.cache.find(file_name, pixmap):
#                self.cache.insert(file_name, pixmap)       
            if not file_name in self.cache:
                self.cache[file_name] = pixmap                 
            icone = QtGui.QIcon(pixmap)
            item = QtGui.QStandardItem(icone, file_name) 
            self.modele.appendRow(item)
            print 'temps chargement 1 image : ', time.clock()-t2, file_name
        print "temps creation modele : ", time.clock()-t1
        
    def update_icon_size(self, event):
        self.vue_liste.setIconSize(QtCore.QSize(event, event))
        #self.vue_liste.setGridSize(QtCore.QSize(event + 50, event + 50))
        self.vue_liste.change_grid_size()
