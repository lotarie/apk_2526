from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
import shapefile      #pip install pyshp
from algorithms import *


class Draw(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pol = QPolygonF()
        self.__q = QPointF(100, 100)
        self.__add_vertex = True
        #Options for drawing multiple polygons at once on the same canvas
        self.__polygons = []
        self.__current_polygon = QPolygonF()
        self.__highlight_index = -1

    def mousePressEvent(self, e):
        #Get cursor coordinates 
        x = e.position().x()
        y = e.position().y()
        
        #Create polygon vertex
        if self.__add_vertex == True:
            #Multiple options for drawing multiple polygons at once on the same canvas
            if e.button() == Qt.MouseButton.LeftButton:
                #Create new point
                p = QPointF(x,y)
                #New point at the end of the current polygon
                self.__current_polygon.append(p)
            #right click to finish the current polygon and start a new one
            elif e.button() == Qt.MouseButton.RightButton:
                #Check if the current polygon is not empty
                if not self.__current_polygon.isEmpty():
                    #New dictionary to store the outer layer of the polygon and its holes
                    complex_polygon = {
                        "outer": QPolygonF(self.__current_polygon),
                        "holes": []
                    }
                    #Add the current polygon to the list of polygons and start a new one
                    self.__polygons.append(complex_polygon)
                    #Create new empty polygon
                    self.__current_polygon = QPolygonF()
            #middle click to finish current polygon and add it as a hole to the last created polygon
            elif e.button() == Qt.MouseButton.MiddleButton:
                #Check if the current polygon is not empty and there is at least one completed polygon to add the hole to
                if not self.__current_polygon.isEmpty() and len(self.__polygons) > 0:
                    #Add the current polygon as a hole to the last created polygon
                    self.__polygons[-1]["holes"].append(self.__current_polygon)
                    #Create new empty polygon
                    self.__current_polygon = QPolygonF()
            
        #Set new q coordinates
        else: 
            self.__q.setX(x)
            self.__q.setY(y)
            #Reset highlighted polygon index when point is moved to ensure that no polygon remains highlighted if the point is outside of all polygons
            self.__highlight_index = -1
                    
        #Repaint
        self.repaint()
     

    def paintEvent(self, e):
        #Draw situation
        qp = QPainter(self)
        
        #Start draw
        qp.begin(self)
        
        #Set attributes, polygon
        qp.setPen(Qt.GlobalColor.black)
        qp.setBrush(Qt.GlobalColor.yellow)
        
        #Drawing for all curently created polygons
        for i, complex_pol in enumerate(self.__polygons):
            #Path that can combine outer and inner layer of the polygon 
            #(the logic of this with the corresponding function changes in this part of the code were consulted with AI)
            path = QPainterPath()
            
            #Add the outer layer of the polygon to the path
            path.addPolygon(complex_pol["outer"])
            #Bug fix that was identified with the use of AI that closes the created subpath to ensure that the last edge is drawn 
            #correctly and the polygon is displayed as intended
            path.closeSubpath()
            
            #Add all possible inner layers of the polygon to the path
            for hole in complex_pol["holes"]:
                path.addPolygon(hole)
                path.closeSubpath()
                
            #Set a rule to ensure transparency of the holes
            path.setFillRule(Qt.FillRule.OddEvenFill)
            
            #Highlight the polygon if its index matches the highlighted polygon index
            if i == self.__highlight_index:
                qp.setBrush(Qt.GlobalColor.red)
            #Otherwise use the default yellow brush
            else:
                qp.setBrush(Qt.GlobalColor.yellow)
             
            #Change from drawPol to drawPath to correctly display polygons with holes because the original function didn't support them
            qp.drawPath(path)
            
        #AI fix that fixed the issue with higlighting polygons when they were created in unusual order
        qp.setBrush(Qt.BrushStyle.NoBrush)
        #Highlight the current polygon being created
        qp.drawPolygon(self.__current_polygon)
        
        #Draw polygon
        qp.drawPolygon(self.__pol)
        
        #Set attributes, point
        qp.setBrush(Qt.GlobalColor.red)
        
        #Draw point
        r = 5
        qp.drawEllipse(int(self.__q.x()-r), int(self.__q.y()-r), 2*r, 2*r)
        
        #End draw
        qp.end()
        
    def changeStatus(self):
        #Input source: point or polygon
        self.__add_vertex = not (self.__add_vertex)
        
    def clearData(self):
        #Clear data
        self.__pol.clear()
        self.__polygons.clear()
        self.__current_polygon.clear()
        self.repaint()
        self.__q.setX(-25)
        self.__q.setY(-25)
    
    def getQ(self):
        #Return point
        return self.__q
    
    def getPol(self):
        #Return all completed polygons
        all_pols = self.__polygons.copy()
        #Add the current polygon being created if it's not empty
        if not self.__current_polygon.isEmpty():
            #Change to the right dictionary format to be consistent with the other polygons in the list
            temp = {"outer": self.__current_polygon, "holes": []}
            all_pols.append(temp)
        return all_pols
    
    def setHighlightedPolygon(self, index: int):
        #Set highlighted polygon index
        self.__highlight_index = index
        self.repaint()

    def LoadShapesToScene(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Shapefile", "", "Shapefiles (*.shp)")
        
        if not file_path:
            return

        raw_polygons = []
        
        #Initialize global max and min x and y coordinates
        glob_min_x = float('inf')
        glob_max_x = float('-inf')
        glob_min_y = float('inf')
        glob_max_y = float('-inf')

        #Read points and find the bounding box
        
        #The options how to load a shapefile were consulted with AI
        #It pointed out several options like geopandas, fiona, bit-parsing the file manually,
        #but the pyshp library was chosen as the most suitable for this project due to its simplicity and ease of use 
        #for reading shapefiles without the need for additional dependencies,
        #which is ideal for a project focused on basic geometric operations and visualization. 
        #The AI also helped identify potential issues with coordinate transformations and scaling, 
        #ensuring that the shapefile is displayed correctly on the canvas regardless of its original coordinate system or dimensions.
        #But didn't suggest any specific code for loading the shapefile, 
        #so the implementation was done based on the documentation and examples provided by the pyshp library.
        
        with shapefile.Reader(file_path) as shp:
            for shape_record in shp.shapeRecords():
                points = shape_record.shape.points
                if not points: 
                    continue
                
                #Update global bounds directly from the raw coordinates
                for x, y in points:
                    if x < glob_min_x: 
                        glob_min_x = x
                        
                    if x > glob_max_x: 
                        glob_max_x = x
                        
                    if y < glob_min_y: 
                        glob_min_y = y
                        
                    if y > glob_max_y: 
                        glob_max_y = y
                    
                raw_polygons.append(points)

        if not raw_polygons:
            return

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

        #Transform all coordinates and create QPolygonFs
        self.__polygons = []
        
        for points in raw_polygons:
            scaled_points = []
            for x, y in points:
                #Shift to 0,0 > scale > add offset
                screen_x = (x - glob_min_x) * scale + x_offset
                
                #Y-axis is inverted. Maps go up, screens go down.
                screen_y = canvas_height - ((y - glob_min_y) * scale + y_offset)
                
                scaled_points.append(QPointF(screen_x, screen_y))
                
            #Save to the dictionary defined for polygons with holes
            outer_poly = QPolygonF(scaled_points)
            self.__polygons.append({"outer": outer_poly, "holes": []})

        self.repaint()