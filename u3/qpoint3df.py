from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *


class QPoint3DF(QPointF):
    def __init__(self, x, y, z):
        super().__init__(x,y)
        self.__z = z
        
    def z(self):
        return self.__z