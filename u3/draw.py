from turtle import mode

from PyQt6 import QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from random import *

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__points =[]
        self.__DT = []
        self.__contours = []
        self.__TIN = []
        self.__drawmode = ""
        
        
    def mousePressEvent(self, e):
        #Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        #Get random z
        z_min = 200
        z_max = 600
        z = random() * (z_max - z_min) + z_min

        #Create new point
        p = QPoint3DF(x, y, z)
        
        #Add P to polygon
        self.__points.append(p)
        
        #Repaint
        self.repaint()
        

    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Draw TIN analaysis results (Partialy created with AI)
        if self.__TIN:
            if self.__drawmode == "slope":
                max_slope = max([t.getSlope() for t in self.__TIN], default=1.0)
                max_slope = max(10.0, max_slope)
            
                for t in self.__TIN:
                    slope = t.getSlope()
                    
                    #Slope limit between 0 and 90 degrees
                    slope = min(90.0, max(0.0, slope))
                    
                    #Linear interpolation of color based on slope
                    r = int(255 * (slope / 90.0))
                    g = int(255 * (1 - (slope / 90.0)))
                    b = 0
                    
                    #Set paint brush color based on slope
                    color = QColor(r, g, b)
                    qp.setBrush(QBrush(color))
                    qp.setPen(QPen(Qt.GlobalColor.darkGray))
                    
                    #Create polygon object
                    polygon = QPolygonF([t.getP1(), t.getP2(), t.getP3()])
                    qp.drawPolygon(polygon)
            #Drawing of exposure
            elif self.__drawmode == "aspect":
                for t in self.__TIN:
                        aspect = t.getAspect()
                        
                        if aspect == -1:
                            #Flat area, use gray color
                            color = QColor(150, 150, 150)
                        else:
                            #Map aspect to hue (0-360 degrees) and convert to QColor
                            hue = aspect / 360.0
                            color = QColor.fromHslF(hue, 1.0, 0.5)
                            
                        qp.setBrush(QBrush(color))
                        pen = QPen(Qt.GlobalColor.darkGray)
                        pen.setWidth(1)
                        qp.setPen(pen) 
                        qp.drawPolygon(QPolygonF([t.getP1(), t.getP2(), t.getP3()]))
        
        #Create new pen
        pen = QPen()
        
        #Set properties, edges
        pen.setColor(Qt.GlobalColor.green)
        qp.setPen(pen)
        
        #Draw edges
        for e in self.__DT:
            qp.drawLine(e.getStart(), e.getEnd())
            
        #Set properties, contours
        pen.setColor(Qt.GlobalColor.gray)
        qp.setPen(pen)
        
        #Draw contour lines
        for c in self.__contours:
            qp.drawLine(c.getStart(), c.getEnd())
        
        #Set properties, points
        pen.setWidth(8)
        pen.setColor(Qt.GlobalColor.red)
        #Change cap style to round for better visibility of points
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        qp.setPen(pen)
        qp.drawPoints(self.__points)
        #Draw points
        qp.drawPoints(self.__points)
        
        
        
    def setDT(self, DT):
        #Set DT
        self.__DT = DT
        
    
    def getDT(self):
        return self.__DT
    

    def getPoints(self):
        #Get points
        return self.__points
    
    def setTIN(self, TIN, mode="slope"):
        #Set TIN
        self.__TIN = TIN
        self.__drawmode = mode
    
    def clearResult(self):
        # Clear results of analyses
        self.__DT.clear()
        self.__contours.clear()
        self.__TIN.clear()
        self.repaint()
        
    def clearAll(self):
        # Clear all elements including points
        self.__points.clear()
        self.__DT.clear()
        self.__contours.clear()
        self.__TIN.clear()
        self.repaint()
        
    def setContours(self, contours):
        #Set contour lines
        self.__contours = contours
        