# -*- coding: utf-8 -*-
"""
Created on Sat Nov 09 22:53:54 2013

@author: Amandine
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov 08 20:02:04 2013

@author: Amandine
"""

import sys
from PyQt4 import QtGui, QtCore
import os, time

path_to_test = r'.'


class ListView(QtGui.QListView):
    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
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

    def move_element(self, item_src, item_dest):
        # là où on relache la souris
        if item_dest is None:
            # si pas d'item à cet endroit, on met à la fin
            dest_row = self.model().rowCount()
        else :
            # sinon, on met à l'endroit demandé
            dest_row = item_dest.row()
        print "dest_row", dest_row    
#         item_src liste dans l'ordre où on clique les objets
#         on la remet dans l'ordre des photos
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
        
    def mouseMoveEvent(self, e):
#        QtGui.QListView.mouseMoveEvent(self, e)
        print "call mouseMove"
#        if e.buttons() != QtCore.Qt.RightButton:
#            return

        # write the relative cursor position to mime data
        mimeData = QtCore.QMimeData()
        # simple string with 'x,y'
        mimeData.setText('%d,%d' % (e.x(), e.y()))

        # let's make it fancy. we'll show a "ghost" of the button as we drag
        # grab the button to a pixmap
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
        if e.button() == QtCore.Qt.LeftButton:
            print 'press'
            
    def wheelEvent(self, event):
        super(ListView, self).wheelEvent(event)
        delta = self.parent().slider.value() + event.delta()/20
        modified = QtGui.QApplication.keyboardModifiers()
        if modified == QtCore.Qt.ControlModifier:
            self.parent().slider.setValue(delta)

class Example(QtGui.QWidget):
    def __init__(self):
        super(Example, self).__init__()
        self.initUI()


    def initUI(self):
        self.cache = {}
        self.setAcceptDrops(True)
        
        self.layout = QtGui.QVBoxLayout()
        
        self.vue_liste = ListView(self)
        self.modele = QtGui.QStandardItemModel(self)
        self.vue_liste.setModel(self.modele)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        
        self.create_model(path_to_test)
        self.layout.addWidget(self.vue_liste)
        self.layout.addWidget(self.slider)
        self.setLayout(self.layout)
        
        self.slider.setRange(20, 500)
        self.slider.setValue(100)

        self.setWindowTitle('Copy or Move')
        self.setGeometry(300, 300, 400, 400)
        self.slider.valueChanged.connect(self.update_icon_size)
        
    def create_model(self, chemin):
        img_ext = ('bmp', 'png', 'jpg', 'jpeg')
        self.list_img = [name for name in os.listdir(chemin) 
                    if name.lower().endswith(img_ext)]
#        self.list_img.sort(key=alphanum_key)

#        t1 = time.clock()        
        for file_name in self.list_img:
#            t2 = time.clock()
            pixmap = QtGui.QPixmap(path_to_test + os.sep + file_name)
            pixmap = pixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
     
            if not file_name in self.cache:
                self.cache[file_name] = pixmap                 
            icone = QtGui.QIcon(pixmap)
            item = QtGui.QStandardItem(icone, file_name) 
            self.modele.appendRow(item)
#            print 'temps chargement 1 image : ', time.clock()-t2, file_name
#        print "temps creation modele : ", time.clock()-t1

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


    def dragEnterEvent(self, e):
        print "call drag"
        e.accept()


    def dropEvent(self, e):
        print "call drop"
        # get the relative position from the mime data
        mime = e.mimeData().text()
        x, y = map(int, mime.split(','))
        dest = QtCore.QPoint(x, y)
        print "mime", x, y
        print "pos", e.pos()   
        
        print self.modele.itemFromIndex(self.vue_liste.indexAt(dest))
        item_src = [self.modele.itemFromIndex(index) for
                    index in self.vue_liste.selectedIndexes()]
        item_dest = self.modele.itemFromIndex(self.vue_liste.indexAt(e.pos()))
        print 'source, dest', item_src, item_dest
        self.vue_liste.move_element(item_src, item_dest)
#        self.vue_liste.move_element(item_src, item_dest)
        e.setDropAction(QtCore.Qt.MoveAction)

        
#        if e.keyboardModifiers() & QtCore.Qt.ShiftModifier:
#            # copy
#            # so create a new button
#            button = ListView(self)
#            # move it to the position adjusted with the cursor position at drag
#            button.move(e.pos()-QtCore.QPoint(x, y))
#            # show it
#            button.show()
#            # store it
#            self.buttons.append(button)
#            # set the drop action as Copy
#            e.setDropAction(QtCore.Qt.CopyAction)
#        else:
#            # move
#            # so move the dragged button (i.e. event.source())
#            e.source().move(e.pos()-QtCore.QPoint(x, y))
#            # set the drop action as Move
#            e.setDropAction(QtCore.Qt.MoveAction)
##         tell the QDrag we accepted it
        e.accept()
        
    def update_icon_size(self, event):
        self.vue_liste.setIconSize(QtCore.QSize(event, event))
        self.vue_liste.setGridSize(QtCore.QSize(event + 50, event + 50)) 



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    ex.show()
    app.exec_()  