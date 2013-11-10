# -*- coding: utf-8 -*-
"""
Created on Sun Nov 10 16:11:58 2013

@author: Amandine
"""

#!/usr/bin/env python


#############################################################################
##
## Copyright (C) 2010 Riverbank Computing Limited.
## Copyright (C) 2010 Nokia Corporation and/or its subsidiary(-ies).
## All rights reserved.
##
## This file is part of the examples of PyQt.
##
## $QT_BEGIN_LICENSE:BSD$
## You may use this file under the terms of the BSD license as follows:
##
## "Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are
## met:
##   * Redistributions of source code must retain the above copyright
##     notice, this list of conditions and the following disclaimer.
##   * Redistributions in binary form must reproduce the above copyright
##     notice, this list of conditions and the following disclaimer in
##     the documentation and/or other materials provided with the
##     distribution.
##   * Neither the name of Nokia Corporation and its Subsidiary(-ies) nor
##     the names of its contributors may be used to endorse or promote
##     products derived from this software without specific prior written
##     permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
## "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
## LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
## A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
## OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
## SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
## LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
## THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
## OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
## $QT_END_LICENSE$
##
#############################################################################


# This is only needed for Python v2 but is harmless for Python v3.
import sip
#sip.setapi('QVariant', 2)

import random

from PyQt4 import QtCore, QtGui

#import puzzle_rc


class PuzzleWidget(QtGui.QWidget):

    puzzleCompleted = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(PuzzleWidget, self).__init__(parent)

        #liste des pixmap des pièces
        self.piecePixmaps = []
        #liste des rectangles où sont placées les pièces 
        #(point x, y en haut à gauche + width = height = 80)
        self.pieceRects = []
        #liste des emplacements sur l'image originale des pièces posées
        self.pieceLocations = []
        #rectangle qui sera visible lors du drag and drop
        self.highlightedRect = QtCore.QRect()
        #nombre d'images bien placées
        self.inPlace = 0

        self.setAcceptDrops(True)
        
        #taille fixe à la taille de l'image : 400*400
        self.setMinimumSize(400, 400)
        self.setMaximumSize(400, 400)

    def clear(self):
        self.pieceLocations = []
        self.piecePixmaps = []
        self.pieceRects = []
        self.highlightedRect = QtCore.QRect()
        self.inPlace = 0
        self.update()

    def dragEnterEvent(self, event):
        #drag accepted only if it is a puzzle piece
        print "puzzle dragenter"
        if event.mimeData().hasFormat('image/x-puzzle-piece'):
            event.accept()
        else:
            event.ignore()

    def dragLeaveEvent(self, event):
        print "puzzle dragleave"
        #effacer le rectangle surligne car on quitte le widget
        updateRect = self.highlightedRect
        self.highlightedRect = QtCore.QRect()
        self.update(updateRect)
        event.accept()

    def dragMoveEvent(self, event):
        print "puzzle dragmove"
        # update rect : union du rectangle highligted et du rectangle dans 
        #lequel est la souris à l'instant -> ce qu'il faudra redessiner
        updateRect = self.highlightedRect.unite(self.targetSquare(event.pos()))

        #si on est en train de dragger une pièce de puzzle et que l'endroit
        # où est la souris n'a pas de pièce pour l'instant, on affiche un 
        #rectangle highlighted là où est la souris pour montrer qu'on
        #peut y mettre la pièce
        if event.mimeData().hasFormat('image/x-puzzle-piece') and self.findPiece(self.targetSquare(event.pos())) == -1:
            self.highlightedRect = self.targetSquare(event.pos())
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        #s'il y a déjà une pièce à l'endroit où on est, où qu'on drag un
        #objet inconnu, on ignore
        else:
            self.highlightedRect = QtCore.QRect()
            event.ignore()
        #on redessine le rectangle qu'on vient de modifier
        self.update(updateRect)

    def dropEvent(self, event):
        print "puzzle drop"
        #if drag is a puzzle piece and there is no piece where we are,
        #put this new piece here
#        print event.mimeData().data()
        if event.mimeData().hasFormat('image/x-puzzle-piece') and self.findPiece(self.targetSquare(event.pos())) == -1:
            pieceData = event.mimeData().data('image/x-puzzle-piece')
            dataStream = QtCore.QDataStream(pieceData, QtCore.QIODevice.ReadOnly)
            #square where the mouse dropped the qdrag
            square = self.targetSquare(event.pos())
            #pixmap and location of the qdrag dropped
            pixmap = QtGui.QPixmap()
            location = QtCore.QPoint()
            dataStream >> pixmap >> location

            #add the new piece into the lists
            self.pieceLocations.append(location)
            self.piecePixmaps.append(pixmap)
            self.pieceRects.append(square)

            self.hightlightedRect = QtCore.QRect()
            self.update(square)

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()

            #si l'emplacement correspond à l'emplacement sur l'image initiale
            #alors, une image bien placee en + :) donc inplace+=1
            if location == QtCore.QPoint(square.x() / 80, square.y() / 80):
                self.inPlace += 1
                #si 25 images bien placees, fini !!
                if self.inPlace == 25:
                    self.puzzleCompleted.emit()
        else:
            self.highlightedRect = QtCore.QRect()
            event.ignore()

    def findPiece(self, pieceRect):
        try:
            return self.pieceRects.index(pieceRect)
        except ValueError:
            return -1

    def mousePressEvent(self, event):
        print "puzzle mouse press"
        #on regarde s'il y a une pièce là où on clique
        square = self.targetSquare(event.pos())
        found = self.findPiece(square)

        if found == -1:
            return
        
        #s'il y a une piece, on l'enleve des listes
        location = self.pieceLocations[found]
        pixmap = self.piecePixmaps[found]
        del self.pieceLocations[found]
        del self.piecePixmaps[found]
        del self.pieceRects[found]
        #si elle etait bien placee, on retire 1 au nombre bien placees
        if location == QtCore.QPoint(square.x() / 80, square.y() / 80):
            self.inPlace -= 1

        self.update(square)

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)

        dataStream << pixmap << location

        mimeData = QtCore.QMimeData()
        mimeData.setData('image/x-puzzle-piece', itemData)
        #qdrag de la piece sur laquelle on est (avec ses infos et sa pixmap)
        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(event.pos() - square.topLeft())
        drag.setPixmap(pixmap)

        if drag.exec_(QtCore.Qt.MoveAction) != QtCore.Qt.MoveAction:
            print "not moved"
            self.pieceLocations.insert(found, location)
            self.piecePixmaps.insert(found, pixmap)
            self.pieceRects.insert(found, square)
            self.update(self.targetSquare(event.pos()))

            if location == QtCore.QPoint(square.x() / 80, square.y() / 80):
                self.inPlace += 1

    def paintEvent(self, event):
        print "puzzle paint"
        painter = QtGui.QPainter()
        painter.begin(self)
        painter.fillRect(event.rect(), QtCore.Qt.white)

        if self.highlightedRect.isValid():
            painter.setBrush(QtGui.QColor("#ffcccc"))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRect(self.highlightedRect.adjusted(0, 0, -1, -1))

        for rect, pixmap in zip(self.pieceRects, self.piecePixmaps):
            painter.drawPixmap(rect, pixmap)

        painter.end()

    def targetSquare(self, position):
        #renvoie le rectangle de 80*80 qui contient la position en x, y
        return QtCore.QRect(position.x() // 80 * 80, position.y() // 80 * 80, 80, 80)


class PiecesList(QtGui.QListWidget):
    def __init__(self, parent=None):
        super(PiecesList, self).__init__(parent)

        self.setDragEnabled(True)
        self.setViewMode(QtGui.QListView.IconMode)
        self.setIconSize(QtCore.QSize(60, 60))
        self.setSpacing(10)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)

    def dragEnterEvent(self, event):
        print "piecelist dragenter"
        if event.mimeData().hasFormat('image/x-puzzle-piece'):
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        print "piecelist drag move"
        if event.mimeData().hasFormat('image/x-puzzle-piece'):
            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print "piece list drop"
        if event.mimeData().hasFormat('image/x-puzzle-piece'):
            pieceData = event.mimeData().data('image/x-puzzle-piece')
            dataStream = QtCore.QDataStream(pieceData, QtCore.QIODevice.ReadOnly)
            pixmap = QtGui.QPixmap()
            location = QtCore.QPoint()
            dataStream >> pixmap >> location

            self.addPiece(pixmap, location)

            event.setDropAction(QtCore.Qt.MoveAction)
            event.accept()
        else:
            event.ignore()

    def addPiece(self, pixmap, location):
        #create a qlistWidgetItem into the pieceList (self)
        pieceItem = QtGui.QListWidgetItem(self)
        #set icon (and text) of the new item
        # pieceItem.setIcon(QtGui.QIcon(pixmap)) ou ligne suivante :
        pieceItem.setData(QtCore.Qt.DecorationRole, pixmap)
#        pieceItem.setText("plop") ou ligne suivante :
        pieceItem.setData(QtCore.Qt.DisplayRole, "plop")
        #save pixmap and location in mime data of the item
        pieceItem.setData(QtCore.Qt.UserRole, pixmap)
        pieceItem.setData(QtCore.Qt.UserRole+1, location)
        #set flags to have items enabled, dragable, selectable...
        pieceItem.setFlags(QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsDragEnabled)

    def startDrag(self, supportedActions):
        print "piece list startdrag"
        item = self.currentItem()

        itemData = QtCore.QByteArray()
        dataStream = QtCore.QDataStream(itemData, QtCore.QIODevice.WriteOnly)
        pixmap =  QtGui.QPixmap(item.data(QtCore.Qt.UserRole))
        location = item.data(QtCore.Qt.UserRole+1)

        dataStream << pixmap << location

        mimeData = QtCore.QMimeData()
        mimeData.setData('image/x-puzzle-piece', itemData)

        drag = QtGui.QDrag(self)
        drag.setMimeData(mimeData)
        drag.setHotSpot(QtCore.QPoint(pixmap.width()/2, pixmap.height()/2))
        drag.setPixmap(pixmap)

        if drag.exec_(QtCore.Qt.MoveAction) == QtCore.Qt.MoveAction:
            self.takeItem(self.row(item))


class MainWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)

        self.puzzleImage = QtGui.QPixmap()

        self.setupMenus()
        self.setupWidgets()

        self.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed,
                QtGui.QSizePolicy.Fixed))
        self.setWindowTitle("Puzzle")

    def openImage(self, path=None):
        if not path:
            path = QtGui.QFileDialog.getOpenFileName(self, "Open Image", '',
                    "Image Files (*.png *.jpg *.bmp)")

        if path:
            newImage = QtGui.QPixmap()
            if not newImage.load(path):
                QtGui.QMessageBox.warning(self, "Open Image",
                        "The image file could not be loaded.",
                        QtGui.QMessageBox.Cancel)
                return

            self.puzzleImage = newImage
            self.setupPuzzle()

    def setCompleted(self):
        QtGui.QMessageBox.information(self, "Puzzle Completed",
                "Congratulations! You have completed the puzzle!\nClick OK "
                "to start again.",
                QtGui.QMessageBox.Ok)

        self.setupPuzzle()

    def setupPuzzle(self):
        size = min(self.puzzleImage.width(), self.puzzleImage.height())
        self.puzzleImage = self.puzzleImage.copy(
                (self.puzzleImage.width() - size)/2,
                (self.puzzleImage.height() - size)/2, size, size).scaled(400, 400, QtCore.Qt.IgnoreAspectRatio, QtCore.Qt.SmoothTransformation)

        #removes all items and selections in the view
        self.piecesList.clear()

        for y in range(5):
            for x in range(5):
                pieceImage = self.puzzleImage.copy(x*80, y*80, 80, 80)
                self.piecesList.addPiece(pieceImage, QtCore.QPoint(x,y))

        random.seed(QtGui.QCursor.pos().x() ^ QtGui.QCursor.pos().y())

        #melange la liste des pièces d'images en en prenant aléatoirement 1
        #de temps en temps dans la liste et la mettant au debut.
        for i in range(self.piecesList.count()):
            if random.random() < 0.5:
                item = self.piecesList.takeItem(i)
                self.piecesList.insertItem(0, item)

        #removes all lists of puzzle pieces, locations ...
        self.puzzleWidget.clear()

    def setupMenus(self):
        fileMenu = self.menuBar().addMenu("&File")

        openAction = fileMenu.addAction("&Open...")
        openAction.setShortcut("Ctrl+O")

        exitAction = fileMenu.addAction("E&xit")
        exitAction.setShortcut("Ctrl+Q")

        gameMenu = self.menuBar().addMenu("&Game")

        restartAction = gameMenu.addAction("&Restart")

        openAction.triggered.connect(self.openImage)
        exitAction.triggered.connect(QtGui.qApp.quit)
        restartAction.triggered.connect(self.setupPuzzle)

    def setupWidgets(self):
        frame = QtGui.QFrame()
        frameLayout = QtGui.QHBoxLayout(frame)

        self.piecesList = PiecesList()

        self.puzzleWidget = PuzzleWidget()

        self.puzzleWidget.puzzleCompleted.connect(self.setCompleted,
                QtCore.Qt.QueuedConnection)

        frameLayout.addWidget(self.piecesList)
        frameLayout.addWidget(self.puzzleWidget)
        self.setCentralWidget(frame)


if __name__ == '__main__':

    import sys

    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    window.openImage('1.JPG')
    window.show()
    sys.exit(app.exec_())
