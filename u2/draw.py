from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import shapefile

class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__building = QPolygonF()
        self.__mbr = QPolygonF()
        self.__ch = QPolygonF()
        
        # Lists (for loaded shapefiles)
        self.__buildings = []
        self.__mbrs = []  
        self.__chs = []  

        
    def mousePressEvent(self, e):
        #Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        #Create new point
        p = QPointF(x,y)
        
        #Add P to polygon
        self.__building.append(p)
        
        #Repaint
        self.repaint()
        

    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
        
        #Set pen and brush
        qp.setPen(Qt.GlobalColor.black)
        qp.setBrush(Qt.GlobalColor.lightGray)
        
        # Draw manual building
        qp.drawPolygon(self.__building) 
        
        # Draw all loaded buildings
        for b in self.__buildings:      
            qp.drawPolygon(b)
        
        #Draw convex hulls
        qp.setPen(Qt.GlobalColor.blue)
        qp.setBrush(Qt.GlobalColor.transparent)
        qp.drawPolygon(self.__ch)
        for ch in self.__chs:
            qp.drawPolygon(ch)
        
        #Draw mbrs
        qp.setPen(Qt.GlobalColor.red)
        qp.setBrush(Qt.GlobalColor.transparent)
        qp.drawPolygon(self.__mbr)
        
        # Draw all loaded MBRs
        for mbr in self.__mbrs:         
            qp.drawPolygon(mbr)
        
        qp.end()
        
        
    def setMBR(self, mbr:QPolygonF):
        #Set MBR
        self.__mbr = mbr
        
    
    #Add a setter for multiple MBRs
    def setMBRs(self, mbrs: list):
        self.__mbrs = mbrs
        

    def setCH(self, ch:QPolygonF):
        #Set CH
        self.__ch = ch  
        
        
    def getBuilding(self):
        #Get building
        return self.__building
    
    #Add a getter for the loaded buildings
    def getBuildings(self):
        return self.__buildings
    
    
    def clearResult(self):
        self.__ch.clear()
        self.__mbr.clear()
        
        # Clear the multiple results as well
        self.__mbrs.clear()
        self.__chs.clear()
        
        self.repaint()
    
    
    def LoadShapesToScene(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)")
        
        if not file_path:
            return
        
        #Initialize global max and min x and y coordinates
        glob_min_x = float('inf')
        glob_max_x = float('-inf')
        glob_min_y = float('inf')
        glob_max_y = float('-inf')
        
        raw_polygons = []

        with shapefile.Reader(file_path) as shp:
            for shape_record in shp.shapeRecords():
                shape = shape_record.shape
                if shape.shapeType == shapefile.POLYGON:
                    points = shape.points
                    raw_polygons.append(points)
                    
                    #Update global max and min x and y coordinates
                    for point in points:
                        x, y = point
                        glob_min_x = min(glob_min_x, x)
                        glob_max_x = max(glob_max_x, x)
                        glob_min_y = min(glob_min_y, y)
                        glob_max_y = max(glob_max_y, y)
        
        #Calculate the dimensions
        shp_width = glob_max_x - glob_min_x
        shp_height = glob_max_y - glob_min_y
        
        #Prevent division by zero 
        if shp_width == 0: 
            shp_width = 1
            
        if shp_height == 0: 
            shp_height = 1

        #Calculate canvas dimensions & scale factor
        canvas_width = self.width()
        canvas_height = self.height()
        
        #Leave a 5% margin so the shapefile doesn't touch the edge
        margin = 0.05
        usable_width = canvas_width * (1 - 2 * margin)
        usable_height = canvas_height * (1 - 2 * margin)

        #Scale
        scale_x = usable_width / shp_width
        scale_y = usable_height / shp_height
        scale = min(scale_x, scale_y)

        #Center the map on the canvas
        x_offset = (canvas_width - (shp_width * scale)) / 2
        y_offset = (canvas_height - (shp_height * scale)) / 2
        

        
        for points in raw_polygons:
            scaled_points = []
            for x, y in points:
                screen_x = (x - glob_min_x) * scale + x_offset
                screen_y = canvas_height - ((y - glob_min_y) * scale + y_offset)
                scaled_points.append(QPointF(screen_x, screen_y))

            self.__buildings.append(QPolygonF(scaled_points))
        self.repaint()
        
        
        
        