# -*- coding:utf8 -*-
__author__ = 'Matthieu FALCE & Amandine PERRIN'


#pour lancer l'application
import sys
import Complements_gui

# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui


if __name__ == '__main__':
    """
   
    """
    #create a Qt application
    print 'debut'
    APP = QtGui.QApplication(sys.argv)

    MA_FENETRE = Complements_gui.MyMainWindow()
    MA_FENETRE.show()
    sys.exit(APP.exec_())
