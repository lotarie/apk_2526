from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from geopandas import *
from math import *


class Algorithms:
    def getBoundingBox(self, pol:QPolygonF):
        #Initialize with infinity to ensure any real coordinate will overwrite these 
        #(probably not needed, but it's a common practice to start with extreme values when looking for min/max form what I found in other projects)
        min_x = float('inf')
        max_x = float('-inf')
        min_y = float('inf')
        max_y = float('-inf')
        
        #Iterate through all vertices of the polygon. This whole algorithm is based on code from StackOverflow: 
        #https://stackoverflow.com/questions/11716268/algorithm-to-find-the-bounding-box-of-a-polygon
        for i in range(len(pol)):
            x = pol[i].x()
            y = pol[i].y()
            
            #Find maximum and minimum for x
            if x < min_x:
                min_x = x
            if x > max_x:
                max_x = x
            #Find maximum and minimum for y
            if y < min_y:
                min_y = y
            if y > max_y:
                max_y = y
        #Return the bouundary limits
        return min_x, max_x, min_y, max_y
    
    def getPointPolygonPositionRC(self, q:QPointF, polygons:list):
        #Calculate through ray casting algorithm if the point is inside the polygon
        for index, complex_pol in enumerate(polygons):
            outer_pol = complex_pol["outer"]
            holes = complex_pol["holes"]
            #Use calculated bounding box to quickly check if the point is outside the polygon
            min_x, max_x, min_y, max_y = self.getBoundingBox(outer_pol)
            #Check if the point lies within this bounding box
            #It must be simultaneously between min_x and max_x and between min_y and max_y
            if not (min_x <= q.x() <= max_x and min_y <= q.y() <= max_y):
                continue

            #Intersects
            k = 0  
            
            #Get a list of all vertices of the polygon, including holes, to process them together
            all_rings = [outer_pol] + holes
        
            #Process all polygon edges including holes
            for pol in all_rings:
                n = len(pol)
                #Repeat for pi, q, pi+1
                for i in range(n):
                    #Start point of the edge
                    xi = pol[i].x() - q.x()
                    yi = pol[i].y() - q.y()
                    
                    #End point of the edge        
                    xi1 = pol[(i+1)%n].x() - q.x()
                    yi1 = pol[(i+1)%n].y() - q.y()
                    
                    #Find suitable segment
                    if ((yi1 > 0) and (yi<= 0) or (yi > 0) and (yi1 <= 0)):
                        
                        #Compute intersection
                        xm = (xi1 * yi - xi * yi1) / (yi1 - yi) 
                        
                        #Correct intersection
                        if xm > 0:
                            
                            #Increment number of intersections
                            k = k + 1   
                            
            #Point is inside the polygon
            if k % 2 == 1:
                return index
                    
        #Point is outside the polygon
        return -1    
    
    def getPointPolygonPositionWN(self, q:QPointF, polygons:list):
        #Analyze point and polygon position using winding number algorithm
        
        for index, complex_pol in enumerate(polygons):
            outer_pol = complex_pol["outer"]
            holes = complex_pol["holes"]
            #Use calculated bounding box to quickly check if the point is outside the polygon
            min_x, max_x, min_y, max_y = self.getBoundingBox(outer_pol)
            #Check if the point lies within this bounding box
            #It must be simultaneously between min_x and max_x AND between min_y and max_y
            if not (min_x <= q.x() <= max_x and min_y <= q.y() <= max_y):
                continue
        
            #Sum of outer angles
            omega_outer = 0
            #Epsilon for floating-point comparison
            epsilon = 1e-6
            #Number of vertices
            n_outer = len(outer_pol)
        
            #Repeat for pi, q, pi+1 for the main outer polygon
            for i in range(n_outer):
                #Check if the point is located on a vertex
                if (outer_pol[i].x() == q.x()) and (outer_pol[i].y()== q.y()):
                    return index
                
                #Start point of the edge
                p_ix = outer_pol[i].x()
                p_iy = outer_pol[i].y()
                
                #End point of the edge
                p_i1x = outer_pol[(i+1) % n_outer].x()
                p_i1y = outer_pol[(i+1) % n_outer].y()
                
                #Determine q position 
                sigma = (p_i1x - p_ix) * (q.y() - p_iy) - (p_i1y - p_iy) * (q.x() - p_ix)
                
                #vectors (q,pi), (q,pi+1)
                v1 = (p_ix - q.x(), p_iy - q.y())
                v2 = (p_i1x - q.x(), p_i1y - q.y())
                
                #calculate angle q, pi, pi+1 
                dot_product = v1[0]*v2[0] + v1[1]*v2[1]
                cos_value = dot_product / ((sqrt(v1[0]**2 + v1[1]**2))*(sqrt(v2[0]**2 + v2[1]**2)))
                cos_value = max(-1.0, min(1.0, cos_value))
                omega_i = acos(cos_value)
                
                #point in right half-plane
                if sigma > 0:
                    omega_outer = omega_outer + omega_i
                #point in left half-plane
                elif sigma < 0:
                    omega_outer = omega_outer - omega_i
            
            #Point is outside the main polygon   
            if abs(abs(omega_outer) - 2 * pi) >= epsilon:
                continue
            
            #Aditional calculation for polygon with holes
            is_in_hole = False
            
            for hole in holes:
                omega_hole = 0
                n_hole = len(hole)
                for i in range(n_hole):
                    #Check if the point is located on a vertex
                    if (hole[i].x() == q.x()) and (hole[i].y()== q.y()):
                        return index
                    
                    #Start point of the edge
                    p_ix = hole[i].x()
                    p_iy = hole[i].y()
                    
                    #End point of the edge
                    p_i1x = hole[(i+1) % n_hole].x()
                    p_i1y = hole[(i+1) % n_hole].y()
                    
                    #Determine q position 
                    sigma = (p_i1x - p_ix) * (q.y() - p_iy) - (p_i1y - p_iy) * (q.x() - p_ix)
                    
                    #vectors (q,pi), (q,pi+1)
                    v1 = (p_ix - q.x(), p_iy - q.y())
                    v2 = (p_i1x - q.x(), p_i1y - q.y())
                    
                    #calculate angle q, pi, pi+1 
                    dot_product = v1[0]*v2[0] + v1[1]*v2[1]
                    cos_value = dot_product / ((sqrt(v1[0]**2 + v1[1]**2))*(sqrt(v2[0]**2 + v2[1]**2)))
                    cos_value = max(-1.0, min(1.0, cos_value))
                    omega_i = acos(cos_value)
                    
                    #point in right half-plane
                    if sigma > 0:
                        omega_hole = omega_hole + omega_i
                    #point in left half-plane
                    elif sigma < 0:
                        omega_hole = omega_hole - omega_i
                
                #Point is inside the hole, so it is outside the polygon
                if abs(abs(omega_hole) - 2 * pi) < epsilon:
                    is_in_hole = True
                    break
                    
            #Return when algorithm is succesfuly calculated 
            if not is_in_hole:
                return index
            
        #Point is outside the polygon
        return -1