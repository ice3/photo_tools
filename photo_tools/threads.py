# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 19:49:14 2013

@author: Amandine
"""
import threading
import time
from PyQt4 import QtGui, QtCore
import os

class threadedImageLoading(threading.Thread):
    def __init__(self, i, file_name, parent) :
        super(threadedImageLoading, self).__init__()
        self.i = i        
        self.file_name = file_name
        self.parent = parent
        
    def run(self) :
        print "lolilol  debut : " + str(self.i)
        complete_file_name =  self.parent.path + os.sep + self.file_name
        icone = QtGui.QIcon(complete_file_name)
        
        self.parent.modele.item(self.i).setIcon(icone)
        image = QtGui.QImage(complete_file_name)
        image = image.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
        self.parent.queue.append([image, self.file_name])            
        print "lololol fin " + str(self.i)
        time.sleep(0.5)
    
    
class loadAllImages(threading.Thread):
    def __init__(self, parent) :    
        super(loadAllImages, self).__init__()
        self.l_threads = []
        self.parent = parent
    
    def run(self):
#        time.sleep(1)
        t1 = time.clock()
        for i, file_name in enumerate(self.parent.list_img):
            t2 = time.clock()
            complete_file_name =  self.parent.path + os.sep + file_name
            tic = time.clock()
            icone = QtGui.QIcon(complete_file_name)
            print "load qicon", time.clock()- tic
            self.parent.modele.item(i).setIcon(icone)

            t3 = time.clock()
            image = QtGui.QImage(complete_file_name)
            print "time load 1 image", time.clock() - t3
            image = image.scaledToWidth(500, QtCore.Qt.SmoothTransformation)
            self.parent.queue.append([image, file_name])            
            print "load 1 image", time.clock() - t2
#            t = threadedImageLoading(i, file_name, self.parent)
#            t.start()
#            self.l_threads.append(t)

        print "temps create model", time.clock() - t1
#        [t.join() for t in self.l_threads]
        self.parent.emit(QtCore.SIGNAL("imagesLoaded()"))
        print 'fin all images'
        
    
