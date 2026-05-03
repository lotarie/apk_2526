from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class Edge:
    def __init__(self, p1, p2):
        self.__start = p1
        self.__end = p2
        
    def getStart(self):
        return self.__start
    
    def getEnd(self):
        return self.__end
    
    def switchOrientation(self):
        return Edge(self.__end, self.__start)
        
    def __eq__(self, other):
        return self.__start == other.__start and self.__end == other.__end
        