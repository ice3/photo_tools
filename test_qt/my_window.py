# -*- coding: utf-8 -*-
"""
Created on Mon Nov 04 18:38:18 2013

@author: Amandine

Hello, 

I am trying to drag and drop QStandardItems that are in a QStandardItemModel represented by a QListView in Icon viewMode. The aim is to graphically reorder the icons of the list (there is no external drag and drop).

It works fine to just drag, drop and reorder the items into the model (and see it in the view). However, what I would like to do is to change what happens during the drag-and-drop operation : by default, the selected items follow the cursor, but are not gathered together, which is ugly. You can see an example of what happens in the picture bellow, which is taken when the mouse is still pressed.

![How items selected move during the drag-and-drop operation][1]


  [1]: http://i.stack.imgur.com/wbyeD.png

To change this, I would like to reimplement the methods showing that, in order to display only one image following the cursor during the drag-and-drop operation, and then call the dropEvent method to reorder according to the new item positions. To display that, I tried to override the dragMoveEvent or mouseMoveEvent methods like that:

    class MyQListView(QtGui.QListView):

        def __init__(self, parent):
            QtGui.QListView.__init__(self, parent)
            self.setAcceptDrops(True)
            self.setDragEnabled(True)
            self.boolTest = True

        def mouseMoveEvent(self, event):
            print('drag move event')
            size = QtCore.QSize(40, 40)
            pixmap = self.parent().cache[self.parent().list_img[0]].scaled(size)
            mimeData = QtCore.QMimeData() #no need for mimeData
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QtCore.QPoint(0, 0))
            drag.exec_()
            print 'source : ', drag.source(), '    dest : ', drag.target()


When I call drag.exec_(), then, the dropEvent method is not called when I release the mouse (whereas before I override this method (or if I comment the 'drag.exec_' line), it worked fine). Hence, the QDrag object seems to block all drag-and-drop signals. 

Moreover, when I use this method, my image is displayed as wanted, but with a "forbidden" cursor, meaning that drag-and-drop seems to be disabled. Nethertheless, I enabled it. 

Moreover, in the last line of code, drag.target() is always None.

If I put the same method in dragMoveEvent(self, event) instead of mouseMoveEvent(self, event), everything freezes when I release the mouse after drag-and-drop.



I am using Qt4.7 with Python 2.7 on Windows 7.
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
        self.setDragEnabled(True)
#        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        self.setSelectionMode(QtGui.QListView.ExtendedSelection)
        self.setFlow(0)
        self.setWrapping(True)
        self.setViewMode(QtGui.QListView.IconMode)
        self.setMovement(QtGui.QListView.Snap)
        self.setGridSize(QtCore.QSize(150, 150))
        self.setIconSize(QtCore.QSize(100, 100))
        self.setResizeMode(QtGui.QListView.Adjust)
        
        self.bool_test = False
            
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
        
#    def dragEnterEvent(self, event):
#        print("drag enter event")
#        event.acceptProposedAction()        
#        #super(MyQListView, self).dragEnterEvent(event)
#    

    def dragLeaveEvent(self, e):
        print "dragLeave"
        
    
    def mouseMoveEvent(self, e):
        QtGui.QListView.mouseMoveEvent(self, e)
        print "call mouseMove"

        #on regarde où on vient de cliquer :
            #on ne crée le qdrag que si on vient de cliquer sur un item
            #et qu'au moins un item de la liste est selectionné, sinon rien
        clic_on = self.model().itemFromIndex(self.indexAt(e.pos()))
        clic_on = self.indexAt(e.pos())
        
        if not self.bool_test:
            return
#        print clic_on
#        print self.selectedIndexes()
#        if not clic_on in self.selectedIndexes():
#            return

#        if (not isinstance(clic_on, QtGui.QStandardItem)
#                or not self.selectedIndexes()):
#            return
        # write the relative cursor position to mime data
        mimeData = QtCore.QMimeData()
        # simple string with 'x,y'
        mimeData.setText('%d,%d' % (e.x(), e.y()))

        pixmap = self.create_mini_pixmap()

        # make a QDrag
        drag = QtGui.QDrag(self)
        # put our MimeData
        drag.setMimeData(mimeData)
        # set its Pixmap
        drag.setPixmap(pixmap)
        # shift the Pixmap so that it coincides with the cursor position
        drag.setHotSpot(QtCore.QPoint(0, 0))
        print 'source : ', drag.source(), '    dest : ', drag.target()

        # start the drag operation
        # exec_ will return the accepted action from dropEvent
        a = drag.exec_(QtCore.Qt.CopyAction | QtCore.Qt.MoveAction)
        if a == QtCore.Qt.MoveAction:
            print 'moved'
        else:
            print 'copied'
        print "drop action : ", a
        print "copy - move", QtCore.Qt.CopyAction, QtCore.Qt.MoveAction
        print 'source : ', drag.source(), '    dest : ', drag.target()
        
#    def dropEvent(self, drop_event):
#        print('drop event')
#        print self.model().itemFromIndex(self.indexAt(drop_event.pos()))
#        item_src = [self.model().itemFromIndex(index) for
#                    index in self.selectedIndexes()]
#        item_dest = self.model().itemFromIndex(self.indexAt(drop_event.pos()))
#        print 'source, dest', item_src, item_dest
#        self.move_element(item_src, item_dest)

    def create_mini_pixmap(self):
        size = QtCore.QSize(40, 40)
        pixmap = self.parent().cache[self.parent().list_img[0]].scaled(size)
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()
        return pixmap     

    def mousePressEvent(self, e):
        QtGui.QListView.mousePressEvent(self, e)
        clic_on = self.indexAt(e.pos())
        print "clic sur item", clic_on in self.selectedIndexes()
        if clic_on in self.selectedIndexes():
            self.bool_test = True
        else:
            self.bool_test = False
        if e.button() == QtCore.Qt.LeftButton:
            print 'press'
#
#
#class MyQListView(QtGui.QListView):
#    def __init__(self, parent):
#        QtGui.QListView.__init__(self, parent)
##        self.setAcceptDrops(True)
##        self.setDragEnabled(True)
        
##    def startDragEvent(self, event):
##        print 'start drag event'
##        super(MyQListView, self).startDragEvent(event)
##        event.acceptProposedAction()
##        
##    def dragEnterEvent(self, event):
##        print ' drag enter event'
##        super(MyQListView, self).dragEnterEvent(event)
##        event.acceptProposedAction()
##        
#
#    def create_mini_pixmap(self):
#        size = QtCore.QSize(40, 40)
#        pixmap = self.parent().cache[self.parent().list_img[0]].scaled(size)
#        painter = QtGui.QPainter(pixmap)
#        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
#        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
#        painter.end()
#        return pixmap        
#        
##    def dragMoveEvent(self, event):
##        print "call dragMove"
###        super(MyQListView, self).dragMoveEvent(event)
##        #TODO : http://stackoverflow.com/questions/14395799/pyqt4-drag-and-drop
##        event.setDropAction(QtCore.Qt.MoveAction)
##        
##        drag = QtGui.QDrag(self)
##        
##        pixmap = self.create_mini_pixmap()
####        print event.source()
##        mimeData = QtCore.QMimeData()
##        drag.setMimeData(mimeData)
##        drag.setPixmap(pixmap)
##        drag.setHotSpot(-QtCore.QPoint(0, 0))
###        print event.pos()
##        print 'a'
##        drop_action = drag.exec_()
##        print 'source : ', drag.source(), '    dest : ', drag.target()
##        #print drop_action
##        print 'b'        
#        
##    def dropEvent(self, drop_event):
##        print "call drop"
###        print self.model().itemFromIndex(self.indexAt(drop_event.pos()))
##        item_src = [self.model().itemFromIndex(index) for 
##                    index in self.selectedIndexes()]
##        item_dest = self.model().itemFromIndex(self.indexAt(drop_event.pos()))
###        print 'source, dest', item_src, item_dest
##        self.move_element(item_src, item_dest)
##        drop_event.setDropAction(QtCore.Qt.MoveAction)
##        drop_event.accept()

class MyModel (QtGui.QStandardItemModel):
    def supportedDropActions(self):
        #http://stackoverflow.com/questions/13838665/qstandarditemmodel-with-qlistview-external-drop-action-does-not-work
        print('lol plop')
        return QtCore.Qt.MoveAction
        
    
    
#    def flags(self, index):
#        print "flags called"
#        defaultFlag = QtGui.QStandardItemModel().flags(index)
#        if (index.isValid()):
#            return QtCore.Qt.ItemIsDragEnabled | QtCore.Qt.ItemIsDropEnabled |\
#                defaultFlag  | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
#        else:
#            print "index invalid"
#            return QtCore.Qt.ItemIsDropEnabled | defaultFlag
    

class ExplorateurListView(QtGui.QWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.setAcceptDrops(True)
        
        self.cache = {}
        self.layout = QtGui.QVBoxLayout()
        self.modele = QtGui.QStandardItemModel(self)
        self.vue_liste =  MyQListView(self)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.vue_liste.setModel(self.modele)
        self.slider.setRange(20, 500)
        self.slider.setValue(100)
        self.create_model(path_to_test)
        self.layout.addWidget(self.vue_liste)
        self.layout.addWidget(self.slider)
        self.setLayout(self.layout)

        self.setWindowTitle('Move pictures')
        self.setGeometry(300, 300, 400, 400)
#        
#        self.layout = QtGui.QVBoxLayout()
#        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
#        self.slider.setRange(20, 500)
#        self.slider.setValue(100)
#        #TODO vider le cache quand on change de dossier            
#        self.cache = {}
#        self.modele = QtGui.QStandardItemModel(self)
#        self.vue_liste =  MyQListView(self)
#        self.create_model(path_to_test)
#        self.vue_liste.setSelectionMode(QtGui.QListView.ExtendedSelection)
#        self.vue_liste.setDragEnabled(True)
#        self.vue_liste.setAcceptDrops(True)
#        self.vue_liste.setDropIndicatorShown(True)
#        self.vue_liste.setFlow(0)
#        self.vue_liste.setWrapping(True)
#        self.vue_liste.setViewMode(QtGui.QListView.IconMode)
#        self.vue_liste.setResizeMode(QtGui.QListView.Adjust)
#        self.vue_liste.setMovement(QtGui.QListView.Snap)
#        self.vue_liste.setGridSize(QtCore.QSize(150, 150))
#        self.vue_liste.setIconSize(QtCore.QSize(100, 100))
#        self.vue_liste.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
#        self.vue_liste.setDefaultDropAction(QtCore.Qt.MoveAction)
#        self.vue_liste.setDragDropOverwriteMode(True)
#        self.vue_liste.setLayoutMode(QtGui.QListView.Batched)
#        self.vue_liste.setBatchSize(3)
#        self.vue_liste.setUniformItemSizes(True)
        
        self.slider.valueChanged.connect(self.update_icon_size)
        
    def dragEnterEvent(self, e):
        print "call drag"
        e.accept()  
#        
    def dropEvent(self, e):
        print "call drop"
        #accepter des drop depuis la liste seulement
        if e.source() != self.vue_liste:
            print "drop exterieur"
            return
        # get the relative position from the mime data
        mime = e.mimeData().text()
        print mime
        x, y = map(int, mime.split(','))
        print "pos", e.pos()   
        
        print self.modele.itemFromIndex(self.vue_liste.indexAt(e.pos()))
        item_src = [self.modele.itemFromIndex(index) for
                    index in self.vue_liste.selectedIndexes()]
        item_dest = self.modele.itemFromIndex(self.vue_liste.indexAt(e.pos()))
        print 'source, dest', item_src, item_dest
        self.vue_liste.move_element(item_src, item_dest)
#        self.vue_liste.move_element(item_src, item_dest)
        e.setDropAction(QtCore.Qt.MoveAction)
#        print('drop event')
#        print self.modele.itemFromIndex(self.vue_liste.indexAt(drop_event.pos()))
#        item_src = [self.modele.itemFromIndex(index) for
#                    index in self.vue_liste.selectedIndexes()]
#        item_dest = self.modele.itemFromIndex(self.vue_liste.indexAt(drop_event.pos()))
#        print 'source, dest', item_src, item_dest
#        self.vue_liste.move_element(item_src, item_dest)
#        event.setDropAction(QtCore.Qt.MoveAction)
        e.accept()
        
    def update_model(self):
        t1 = time.clock()        
        self.modele.clear()
        print 'temps modele.clear() : ', time.clock()-t1
        t1 = time.clock()
        for file_name in self.list_img:
            t2 = time.clock()
            pixmap = QtGui.QPixmap()
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

        t1 = time.clock()        
        for file_name in self.list_img:
            t2 = time.clock()
            pixmap = QtGui.QPixmap(path_to_test + os.sep + file_name)
            pixmap = pixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
     
            if not file_name in self.cache:
                self.cache[file_name] = pixmap                 
            icone = QtGui.QIcon(pixmap)
            item = QtGui.QStandardItem(icone, file_name) 
            self.modele.appendRow(item)
            print 'temps chargement 1 image : ', time.clock()-t2, file_name
        print "temps creation modele : ", time.clock()-t1
        
    def update_icon_size(self, event):
        self.vue_liste.setIconSize(QtCore.QSize(event, event))
        self.vue_liste.setGridSize(QtCore.QSize(event + 50, event + 50))    
            