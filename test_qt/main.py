# -*- coding: utf-8 -*-
"""
Created on Mon Nov 04 18:36:28 2013

@author: Amandine
"""

#pour lancer l'application
import sys
import my_window

# Python Qt4 bindings for GUI objects
from PyQt4 import QtGui

#for translation process :*
from PyQt4 import QtCore

if __name__ == '__main__':
    """
    Method called to launch VIVECA program, set-up language, etc.
    """
    #create a Qt application
    print 'debut'
    APP = QtGui.QApplication(sys.argv)

    MA_FENETRE = my_window.ExplorateurListView()
    MA_FENETRE.show()
    sys.exit(APP.exec_())
    