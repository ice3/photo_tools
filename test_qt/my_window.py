# -*- coding: utf-8 -*-
"""
Created on Mon Nov 04 18:38:18 2013

@author: Amandine
"""
from PyQt4 import QtGui, QtCore
import os

import time

import re
from itertools import groupby

#path_to_test = r'D://Amandine DONNEES//Photos//Photos famille//2013//Lyon_12-13-14-Avril'
path_to_test = r'.'

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
    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)
        self.setAcceptDrops(True)

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
        if modified == QtCore.Qt.ControlModifier:
            self.parent().slider.setValue(delta)
        
    def dragMoveEvent(self, event):
        print "call dragMove"
#        super(MyQListView, self).mouseMoveEvent(event)
        #TODO : http://stackoverflow.com/questions/14395799/pyqt4-drag-and-drop
        event.setDropAction(QtCore.Qt.MoveAction)
        event.accept()
        
    def mousePressEvent(self, event):
        drag = QtGui.QDrag(self)
##        print event.source()
        mimeData = QtCore.QMimeData()
        size = QtCore.QSize(40, 40)
        pixmap = self.parent().cache[self.parent().list_img[0]].scaled(size)
#        painter = QtGui.QPainter(pixmap)
#        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
#        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
#        painter.end()
        drag.setMimeData(mimeData)
        drag.setPixmap(pixmap)
        drag.setHotSpot(-QtCore.QPoint(0, 0))
#        print event.pos()
        drag.exec_(QtCore.Qt.MoveAction)
        
    def dropEvent(self, drop_event):
        print "call drop"
#        print self.model().itemFromIndex(self.indexAt(drop_event.pos()))
        item_src = [self.model().itemFromIndex(index) for 
                    index in self.selectedIndexes()]
        item_dest = self.model().itemFromIndex(self.indexAt(drop_event.pos()))
#        print 'source, dest', item_src, item_dest
        self.move_element(item_src, item_dest)
        drop_event.setDropAction(QtCore.Qt.MoveAction)
        drop_event.accept()
        

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
        self.theIconProvider = MyIconProvider()
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
            item.setDragEnabled(True)
            item.setDropEnabled(True)
            self.modele.appendRow(item)
            print 'temps chargement 1 image : ', time.clock()-t2, file_name
        print "temps creation modele : ", time.clock()-t1
        
    def update_icon_size(self, event):
        self.vue_liste.setIconSize(QtCore.QSize(event, event))
        self.vue_liste.setGridSize(QtCore.QSize(event + 50, event + 50))    
            
            
            
            
            
            
            
            
            
            
            
class ExplorateurGraphicView(QtGui.QGraphicsView):
    def __init__(self):
        QtGui.QGraphicsView.__init__(self)
        self.scene = QtGui.QGraphicsScene(None)
        self.setScene(self.scene)
        self.taille = 50
        pix = QtGui.QPixmap("DSCN2382.JPG").scaledToWidth(self.taille)
        pix2 = QtGui.QPixmap("DSCN2382.JPG").scaledToWidth(self.taille)
        pix3 = QtGui.QPixmap("DSCN2382.JPG").scaledToWidth(self.taille)
        #pix.load("DSCN2382.JPG")
        self.scene.addPixmap(pix)
        self.scene.addPixmap(pix2)
        self.scene.addPixmap(pix)
        self.scene.addPixmap(pix3)
        self.show()

class MyIconProvider(QtGui.QFileIconProvider):    
    def icon(self, info):
        cache = QtGui.QPixmapCache()
        filepath = info.canonicalFilePath()
        pixmap = QtGui.QPixmap()        
        if not cache.find(filepath, pixmap):
            pixmap.load(filepath)
            cache.insert(filepath, pixmap)
        
        if pixmap.isNull() :
            return QtGui.QFileIconProvider.icon(info)
        else :
            return QtGui.QIcon(pixmap)            
            
            
class TableViewDragDrop(QtGui.QTableView):
    def dropEvent(self, dropEvent):
        print self.model().itemFromIndex(self.indexAt(dropEvent.pos()))
        item_src = self.model().itemFromIndex(self.selectedIndexes()[0])
        item_dest = self.model().itemFromIndex(self.indexAt(dropEvent.pos()))
        print item_src, item_dest
        src_row = item_src.row()
        src_col = item_src.column()
        dest_row = item_dest.row()
        dest_col = item_dest.column()
        super(TableViewDragDrop,self).dropEvent(dropEvent)
        self.model().setItem(dest_row, dest_col, item_src)
        #self.model().setItem(src_row, src_col, item_dest)
#        super(TableViewDragDrop,self).dropEvent(dropEvent)
#        self.setItem(src_row,src_col, item_dest)


class MyExplorateur(QtGui.QWidget):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.files = QtGui.QStandardItemModel(self)
        #self.finder = QtGui.QTableView(self)
        
        #self.finder.dropEvent.connect(TableViewDragDrop.dropEvent)
        self.finder = TableViewDragDrop(self)
        self.taille = 20
        self.finder.setIconSize(QtCore.QSize(self.taille, self.taille))
        self.finder.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        plop = QtGui.QHBoxLayout(self)
        self.setLayout(plop)
        plop.addWidget(self.finder)
        self.finder.horizontalHeader().hide()
        self.finder.verticalHeader().hide()
        self.finder.setShowGrid(False)
        self.create_model(".")
        self.finder.setModel(self.files)
        self.finder.resizeColumnsToContents()
        self.finder.resizeRowsToContents()

        
    def create_model(self, chemin):
        dossier = QtCore.QDir(chemin)
        nbFilePerRow = 7  
        
        infosContenuDossier = dossier.entryInfoList(QtCore.QDir.AllEntries | 
                QtCore.QDir.NoDotAndDotDot, QtCore.QDir.DirsFirst)
        for num, _file in enumerate(infosContenuDossier):
            rowIcone = round((num+1)/(nbFilePerRow+1))*2
            columnIcone = num%nbFilePerRow
            icone = QtGui.QIcon(QtGui.QFileIconProvider().icon(_file).pixmap(100,100))  
            #icone = QtGui.QIcon(QtGui.QPixmap("DSCN2382.JPG"))            
            item = QtGui.QStandardItem(icone, "plop")
            self.files.setItem(rowIcone, columnIcone, item)

    
        
            
            
                   

class MyMainWindow(QtGui.QWidget):
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
#        self.finder = TableSwitcher(12, 8, self)
        plop = QtGui.QHBoxLayout(self)
        self.setLayout(plop)
        plop.addWidget(self.finder)
        self.finder.horizontalHeader().hide()
        self.finder.verticalHeader().hide()
        self.finder.setShowGrid(False)
        self.finder.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.listageFichiers(".")
        
    def listageFichiers(self, chemin):
        hauteurImage = 48
        hauteurTexte = 18
         
        nbFilePerRow = self.finder.columnCount()        
        
        dossier = QtCore.QDir(chemin)
        infosContenuDossier = dossier.entryInfoList(QtCore.QDir.AllEntries | 
                QtCore.QDir.NoDotAndDotDot, QtCore.QDir.DirsFirst)
        print infosContenuDossier
        print os.listdir('.')
     
        for num, _file in enumerate(infosContenuDossier):
            rowIcone = round((num+1)/(nbFilePerRow+1))*2
            columnIcone = num%nbFilePerRow
     
            foo = QtGui.QFileIconProvider()
            print foo.icon(_file).pixmap(10,10)
            icone = QtGui.QLabel()
            icone.setAlignment(QtCore.Qt.AlignCenter);
            icone.setPixmap(foo.icon(_file).pixmap(hauteurImage, hauteurImage))
            self.finder.setCellWidget(rowIcone, columnIcone, icone)
             
            finderItem = QtGui.QTableWidgetItem(_file.fileName())
            finderItem.setTextAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignHCenter);
            self.finder.setItem(rowIcone+1, columnIcone, finderItem)
             
            self.finder.setRowHeight(rowIcone, hauteurImage)
            self.finder.setRowHeight(rowIcone+1, hauteurTexte*2.5);
             
            self.finder.setColumnWidth(columnIcone, hauteurImage*2.5);
