# -*- coding: utf-8 -*-
"""
Created on Mon Nov 04 18:38:18 2013

@author: Amandine

Hello, 

I am trying to drag and drop QStandardItems that are in a QStandardItemModel 
represented by a QListView in Icon viewMode. The aim is to graphically reorder 
the icons of the list (there is no external drag and drop).

It works fine to just drag, drop and reorder the items into the model (and see 
it in the view). However, what I would like to do is to change what happens 
during the drag-and-drop operation : by default, the selected items follow 
the cursor, but are not gathered together, which is ugly. You can see an 
example of what happens in the picture bellow, which is taken when the mouse 
is still pressed.

![How items selected move during the drag-and-drop operation][1]


  [1]: http://i.stack.imgur.com/wbyeD.png

To change this, I would like to reimplement the methods showing that, in 
order to display only one image following the cursor during the drag-and-drop 
operation, and then call the dropEvent method to reorder according to the 
new item positions. To display that, I tried to override the dragMoveEvent 
or mouseMoveEvent methods like that:

    class MyQListView(QtGui.QListView):

        def __init__(self, parent):
            QtGui.QListView.__init__(self, parent)
            self.setAcceptDrops(True)
            self.setDragEnabled(True)
            self.boolTest = True

        def mouseMoveEvent(self, event):
            print('drag move event')
            size = QtCore.QSize(40, 40)
            pixmap = self.parent().cache[self.parent().list_img[0]].\
                        scaled(size)
            mimeData = QtCore.QMimeData() #no need for mimeData
            drag = QtGui.QDrag(self)
            drag.setMimeData(mimeData)
            drag.setPixmap(pixmap)
            drag.setHotSpot(QtCore.QPoint(0, 0))
            drag.exec_()
            print 'source : ', drag.source(), '    dest : ', drag.target()


When I call drag.exec_(), then, the dropEvent method is not called when I 
release the mouse (whereas before I override this method (or if I comment 
the 'drag.exec_' line), it worked fine). Hence, the QDrag object seems to 
block all drag-and-drop signals. 

Moreover, when I use this method, my image is displayed as wanted, but with
 a "forbidden" cursor, meaning that drag-and-drop seems to be disabled. 
 Nethertheless, I enabled it. 

Moreover, in the last line of code, drag.target() is always None.

If I put the same method in dragMoveEvent(self, event) instead of 
mouseMoveEvent(self, event), everything freezes when I release the mouse 
after drag-and-drop.



I am using Qt4.7 with Python 2.7 on Windows 7.
"""
from PyQt4 import QtGui, QtCore
import os

import time

import re
#from itertools import groupby

#PATH_TO_TEST = r'D://Amandine DONNEES//Photos//Photos famille//' +\
#                r'2013//Lyon_12-13-14-Avril'
PATH_TO_TEST = r'.'

def tryint(char):
    """
    try if the character char is an int
    """
    try:
        return int(char)
    except:
        return char

def alphanum_key(name):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', name) ]


class MyQListView(QtGui.QListView):
    """ ListView with icons with text bellow.
    Drag and drop enabled : 
        you can drag an item/several items, and put it where you
        want it to be by dropping it.
        During drag operation, will display the icon(s), with number of items
        selected.
        When dropped, reorder the items
    """
    
    def __init__(self, parent):
        QtGui.QListView.__init__(self, parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtGui.QAbstractItemView.InternalMove)
        #to be able to selected several items
        self.setSelectionMode(QtGui.QListView.ExtendedSelection)
        #items from left to right
        self.setFlow(0)
        #go to next line of no more place in horizontal for next item
        self.setWrapping(True)
        #show icons with text below
        self.setViewMode(QtGui.QListView.IconMode)
        #able to drop only on the grid
        self.setMovement(QtGui.QListView.Snap)
        self.setGridSize(QtCore.QSize(150, 150))
        self.setIconSize(QtCore.QSize(100, 100))
        #adjust rows of items when widget is resized
        self.setResizeMode(QtGui.QListView.Adjust)
        #boolean to allow drag or not
        self.boolTest = False
            
    def move_element(self, itemSrc, itemDest):
        """ When mouse released after a drag and drop operation, move
        elements according to their new position
        """
        # item where mouse is released
        if itemDest is None:
            # if no item, put it at the end of the item list
            destRow = self.model().rowCount()
        else :
            # if item exists, destRow is the row of this item
            destRow = itemDest.row()
#        print "destRow", destRow 
   
        # itemSrc is the list of the items in the order in which they 
        #were selected
        # put this list into the current order of items
        itemSrc = sorted(itemSrc, key = lambda x: -x.row())
        # Get the list of rows of selected items to be moved 
        srcRows = [i.row() for i in itemSrc]
        # Get file names corresponding to the rows, and remove them from 
        #item list
        itemsToInsert = [self.parent().list_img.pop(i) for i in srcRows]
#        print "reste liste", self.parent().list_img
        itemsToInsert.reverse()
#        print "items to insert", itemsToInsert
        # Count how many items we have just removed before the dest row
        #to know where we now have to insert the items 
        nbElemInfDest  = sum([1 for i in srcRows if i < destRow])
#        print "nb_elem inf dest", nbElemInfDest
#        print "endroit d'insertion", destRow-nbElemInfDest
        # Reconstruct the list with new order of items
        self.parent().list_img =\
                        self.parent().list_img[:destRow-nbElemInfDest] +\
                        itemsToInsert +\
                        self.parent().list_img[destRow-nbElemInfDest:]
                        
        # Update model in order to see the new order into the view  
        self.parent().update_model()

    def wheelEvent(self, event):
        """ When mous wheel is moved
        If moved only : scroll up/down into the list view
        If moved + ctrl pressed : change icon size of listView Items
        """
        # wheel only = scroll up/down in the listView
        super(MyQListView, self).wheelEvent(event)
        delta = self.parent().slider.value() + event.delta()/20
        modified = QtGui.QApplication.keyboardModifiers()
        # Ctrl+wheel = change size of icons in listView (via slider value)
        if modified == QtCore.Qt.ControlModifier:
            self.parent().slider.setValue(delta)
        
    def dragEnterEvent(self, event):
        """ 
        Drag accepted only if it is a drag from the qlistView
        """
        print "listWidget dragenter"
        if event.mimeData().hasFormat('MyQListView Item'):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        """
        we accept the left drag, without setting a dropAction
        """
        print "dragLeave"
        event.accept()
        
    def dragMoveEvent(self, event):  
        """
        Accept drag if it is from the qlistview
        """
        super(MyQListView, self).dragMoveEvent(event)
        print "qlistview dragmove"
        #if the drag is from an item of the qlistview, accept it
        if event.mimeData().hasFormat('MyQListView Item'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        #else, ignore (will put a 'forbidden' cursor)
        else:
#            self.highlightedRect = QtCore.QRect()
            event.ignore()
        #on redessine le rectangle qu'on vient de modifier
#        self.update(updateRect)

    def dropEvent(self, drop_event):
        """
        we drop only if the qdrag is from the qlistView
        When dropped, reorder items : 
            items selected go to the place where they are dropped.
        """
        print('listView drop event')
        if drop_event.mimeData().hasFormat('MyQListView Item'):
            #get items selected (=to be moved)
            itemSrc = [self.model().itemFromIndex(index) for
                        index in self.selectedIndexes()]
            #get item on which it was dropped (=where to insert the 
            #selected items)
            itemDest = self.model().\
                            itemFromIndex(self.indexAt(drop_event.pos()))
            #move the items as asked
            self.move_element(itemSrc, itemDest)
            #set action to move event
            drop_event.setDropAction(QtCore.Qt.MoveAction)
            drop_event.accept()
        else:
            drop_event.ignore()

    def create_mini_pixmap(self):
        """
        Create the pixmap to display following the cursor during
        drag and drop operation
        = icon of selected item(s) gathered together 
            + number of selected item(s)
        """
        size = QtCore.QSize(40, 40)
        pixmap = self.parent().cache[self.parent().list_img[0]].scaled(size)
        #transparent
        painter = QtGui.QPainter(pixmap)
        painter.setCompositionMode(painter.CompositionMode_DestinationIn)
        painter.fillRect(pixmap.rect(), QtGui.QColor(0, 0, 0, 127))
        painter.end()
        return pixmap     

    def mousePressEvent(self, event):
        """ 
        If mouse pressed on a selected item, start drag and drop.
        Otherwise, do default 
        """
        print "plistview mouse press"
        QtGui.QListView.mousePressEvent(self, event)
        # Check if where we clic is a selected item
        clicOn = self.indexAt(event.pos())
#        print event.pos()
#        print self.visualRect(clicOn)
        if clicOn in self.selectedIndexes():
            self.boolTest = True
        #if not, return - don't start a drag and drop
        else:
            self.boolTest = False
            return
        #Create QByteArray to put data in QDrag QMimeData
        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        #get pixmap to display during drag and drop
        pixmap = self.create_mini_pixmap()
        
        #put pixmap into info for QDrag QMimeData
        dataStream << pixmap #<< location
        
        mimeData = QtCore.QMimeData()
        mimeData.setData('MyQListView Item', itemData)
        # Create QDrag with mimeData and pixmap
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(0, 0))
        drag.setPixmap(pixmap)
        
        #execute QDrag.
        #If accepted by other than MoveAction : it has left the window
        if drag.exec_(QtCore.Qt.MoveAction) != QtCore.Qt.MoveAction:
            print "not moved"
            
    def paintEvent(self, event):
        super(MyQListView, self).paintEvent(event)
        print "paintEvent"
        print event.rect() 
        
        rect = self.visualRect(self.indexAt(QtCore.QPoint(104,55)))
        print rect
        rect.setX(rect.x() - 10)
        rect.setWidth(10)

        painter = QtGui.QPainter()
        painter.begin(self.viewport())
#        painter.fillRect(event.rect(), QtCore.Qt.white)

#        if self.highlightedRect.isValid():
        painter.setBrush(QtGui.QColor(0, 0, 100, 127))
        painter.setPen(QtCore.Qt.NoPen)
        painter.drawRect(rect)

#        for rect, pixmap in zip(self.pieceRects, self.piecePixmaps):
#            painter.drawPixmap(rect, pixmap)

        painter.end()


        
        
            
            
            
        
class ExplorateurListView(QtGui.QWidget):
    """
    A widget representing a file explorator, with a 
    customized QListView (MyQListView) and a slider to change icon sizes
    Contains the model for the QListView, with all image file names of the
    opened folder
    """
    
    def __init__(self):
        QtGui.QWidget.__init__(self)
        
        #widgets
        self.layout = QtGui.QVBoxLayout()
        self.modele = QtGui.QStandardItemModel(self)
        self.vue_liste =  MyQListView(self)
        self.slider = QtGui.QSlider(QtCore.Qt.Horizontal)
        
        #other attributes
        #list of image filenames
        self.list_img = []   
        #dict : cache[filename]=pixmap to save the pixmap 
        self.cache = {}
        
        # initialisation
        self.vue_liste.setModel(self.modele)
        self.slider.setRange(20, 500)
        self.slider.setValue(100)
        self.create_model(PATH_TO_TEST)
        self.layout.addWidget(self.vue_liste)
        self.layout.addWidget(self.slider)
        self.setLayout(self.layout)
        self.setWindowTitle('Move pictures')

        #Connections signal - slot
        self.slider.valueChanged.connect(self.update_icon_size)
        
    def update_model(self):
        """ 
        Reorder items in the model as required
        (called after a drag and drop operation in the view)
        """
        t1 = time.clock()        
        self.modele.clear()
        print 'temps modele.clear() : ', time.clock()-t1
        t1 = time.clock()
        for file_name in self.list_img:
            t2 = time.clock()
            pixmap = QtGui.QPixmap()
            if not file_name in self.cache:                
                print 'cache pas exister', file_name
                pixmap = QtGui.QPixmap(PATH_TO_TEST + os.sep + file_name)
                pixmap = pixmap.scaledToWidth(
                                    500, QtCore.Qt.SmoothTransformation)
                self.cache[file_name] = pixmap
            else:
                pixmap = self.cache[file_name]                     
            icone = QtGui.QIcon(pixmap)
            item = QtGui.QStandardItem(icone, file_name) 
            self.modele.appendRow(item)    
            print 'temps update 1 image : ', time.clock()-t2, file_name
            
        print "temps update modele : ", time.clock()-t1

    def create_model(self, chemin):
        """
        Create the model for the QListView. 
        Get all image file names, and create icons from the images rescaled.
        """
        imgExt = ('bmp', 'png', 'jpg', 'jpeg')
        self.list_img = [name for name in os.listdir(chemin) 
                    if name.lower().endswith(imgExt)]
        self.list_img.sort(key=alphanum_key)

        t1 = time.clock()        
        for file_name in self.list_img:
            t2 = time.clock()
            pixmap = QtGui.QPixmap(PATH_TO_TEST + os.sep + file_name)
            pixmap = pixmap.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
     
            if not file_name in self.cache:
                self.cache[file_name] = pixmap                 
            icone = QtGui.QIcon(pixmap)
            item = QtGui.QStandardItem(icone, file_name) 
            self.modele.appendRow(item)
            print 'temps chargement 1 image : ', time.clock()-t2, file_name
        print "temps creation modele : ", time.clock()-t1
        
    def update_icon_size(self, event):
        """
        Update the size of the icons in the MyQListView
        """
        self.vue_liste.setIconSize(QtCore.QSize(event, event))
        self.vue_liste.setGridSize(QtCore.QSize(event + 50, event + 50))    
            