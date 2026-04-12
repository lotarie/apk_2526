from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from math import *
import numpy as np
import numpy.linalg as np2

class Algorithms:
    
    def __init__(self):
        pass
    
    def get2VectorsAngle(self, p1:QPointF, p2:QPointF, p3:QPointF, p4:QPointF):
        #Angle between two vectors
        ux = p2.x() - p1.x()    
        uy = p2.y() - p1.y()
        
        vx = p4.x() - p3.x()
        vy = p4.y() - p3.y()    
        
        #Dot product
        dot = ux*vx + uy*vy
        
        #Norms
        nu = (ux**2 + uy**2)**0.5
        nv = (vx**2 + vy**2)**0.5
        
        #Correct interval
        arg = dot/(nu*nv)
        arg = max(-1, min(1,arg)) 
        
        return acos(arg)
    
    def getOrientation(self, p1:QPointF, p2:QPointF, p3:QPointF):
        #Calculate determinant, return positive if counter-clockwise, negative if clockwise and zero if collinear
        return (p2.x() - p1.x()) * (p3.y() - p1.y()) - (p2.y() - p1.y()) * (p3.x() - p1.x())
    
    def getDistance(self, p1:QPointF, p2:QPointF):
        #Squared distance between two points
        return (p2.x() - p1.x())**2 + (p2.y() - p1.y())**2
    
    def createCHGraham(self, pol:QPolygonF):
        #Too few points error handling
        if pol.count() < 3:
            return pol
        #Pivot q (minimize y)
        q = min(pol, key = lambda p: (p.y(), p.x()))
        #List conversion and sorting by polar angle with q
        points = [pol[i] for i in range(pol.count())]
        points.remove(q)
        #Primary sort by polar angle, secondary sort by distance to q
        points.sort(key=lambda p: (atan2(p.y() - q.y(), p.x() - q.x()), self.getDistance(q, p)))
        #Colinear points with same polar angle as q are sorted by distance we need to reverse them to maintain correct order
        filtered_points = []
        for i in range(len(points)):
            if i < len(points) - 1:
                angle1 = atan2(points[i].y() - q.y(), points[i].x() - q.x())
                angle2 = atan2(points[i + 1].y() - q.y(), points[i + 1].x() - q.x())
                if abs(angle1 - angle2) < 1e-6:
                    continue
            filtered_points.append(points[i])
        
        #Inicialzation of S 
        if len(filtered_points) < 2:
            return QPolygonF([q] + filtered_points)
        
        S = [q, filtered_points[0]]
        #Process all points (reapeat for j < n)
        for i in range(1, len(filtered_points)):
            while len(S) > 1 and self.getOrientation(S[-2], S[-1], filtered_points[i]) <= 0:
                S.pop()
            #Add point to S
            S.append(filtered_points[i])
        #Convert S to QPolygonF
        ch_graham = QPolygonF()
        for p in S:
            ch_graham.append(p)
        return ch_graham
        
        
    
    def createCH(self, pol:QPolygonF):
        #Create Convex Hull using Jarvis Scan
        ch = QPolygonF()
        
        #Find pivot q (minimize y)
        q = min(pol, key = lambda k: k.y())

        #Find left-most point (minimize x)
        s = min(pol, key = lambda k: k.x())
        
        #Initial segment
        pj = q
        pj1 = QPointF(s.x(), q.y())
        
        #Add to CH
        ch.append(pj)
        
        #Find all points of CH
        while True:
            #Maximum and its index
            omega_max = 0
            index_max = -1
            
            #Browse all points
            for i in range(len(pol)):
                
                #Different points
                if pj != pol[i]:
                    
                    #Compute omega
                    omega = self.get2VectorsAngle(pj, pj1, pj, pol[i])
            
                    #Actualize maximum
                    if(omega > omega_max):
                        omega_max = omega
                        index_max = i
                    
            #Add point to the convex hull
            ch.append(pol[index_max])
            
            #Reasign points
            pj1 = pj
            pj = pol[index_max]
            
            # Stopping condition
            if pj == q:
                break
            
        return ch
    
    
    def createMMB(self, pol:QPolygonF):
        # Create min max box and compute its area

        #Points with extreme coordinates        
        p_xmin = min(pol, key = lambda k: k.x())
        p_xmax = max(pol, key = lambda k: k.x())
        p_ymin = min(pol, key = lambda k: k.y())
        p_ymax = max(pol, key = lambda k: k.y())
        
        #Create vertices
        v1 = QPointF(p_xmin.x(), p_ymin.y())
        v2 = QPointF(p_xmax.x(), p_ymin.y())
        v3 = QPointF(p_xmax.x(), p_ymax.y())
        v4 = QPointF(p_xmin.x(), p_ymax.y())
        
        #Create new polygon
        mmb = QPolygonF([v1, v2, v3, v4])
        
        #Area of MMB
        area = (v2.x() - v1.x()) * (v3.y() - v2.y())
        
        return mmb, area

    def rotatePolygon(self, pol:QPolygonF, sig:float):
        #Rotate polygon according to a given angle
        pol_rot = QPolygonF()

        #Process all polygon vertices
        for i in range(len(pol)):

            #Rotate point
            x_rot = pol[i].x() * cos(sig) - pol[i].y() * sin(sig)
            y_rot = pol[i].x() * sin(sig) + pol[i].y() * cos(sig)

            #Create QPoint
            vertex = QPointF(x_rot, y_rot)

            # Add vertex to rotated polygon
            pol_rot.append(vertex)

        return pol_rot
    
    
    def createMBR(self, building:QPolygonF):
        #Create minimum bounding rectangle using repeated construction of mmb
        sigma_min = 0
        
        #Convex hull
        ch = self.createCHGraham(building)
        
        #Initialization
        mmb_min, area_min = self.createMMB(ch)
        
        # Process all edges of convex hull
        n = len(ch)
        for i in range(n):
            #Coordinate differences
            dx = ch[(i+1)%n].x() - ch[i].x()
            dy = ch[(i+1)%n].y() - ch[i].y()
            
            # Compute direction
            sigma = atan2(dy, dx)
            
            #Rotate convex hull
            ch_r = self.rotatePolygon(ch, -sigma)
        
            #Compute min-max box
            mmb, area = self.createMMB(ch_r)
            
            #Did we find a better min-max box?
            if area < area_min:    
                #Update minimum
                area_min = area
                mmb_min = mmb
                sigma_min = sigma
                
        #Back rotation
        return  self.rotatePolygon(mmb_min, sigma_min) 

    
    def getArea(self, pol:QPolygonF):
        #Compute area    
        area = 0
        n = len(pol)
        
        # Process all vertices
        for i in range(n):
            area += pol[i].x() * (pol[(i + 1) % n].y() - pol[(i - 1 + n) % n].y())
            
        return abs(area)/2    
    
        
    def resizeRectangle(self, building:QPolygonF, mbr: QPolygonF):
        #Resizing rectangle area to match building area
        
        #Area of the rectangle
        A = self.getArea(mbr)
        
        #Debugging: prevent division by zero
        if A == 0:
            return mbr
        
        #Area of the building
        Ab = self.getArea(building)
        
        #Fraction of both areas
        k = Ab / A
        
        #Compute centroid of the rectangle
        x_c = (mbr[0].x()+mbr[1].x()+mbr[2].x()+mbr[3].x()) / 4
        y_c = (mbr[0].y()+mbr[1].y()+mbr[2].y()+mbr[3].y()) / 4
        
        #Compute vectors 
        v1_x = mbr[0].x() - x_c
        v1_y = mbr[0].y() - y_c 
        
        v2_x = mbr[1].x() - x_c
        v2_y = mbr[1].y() - y_c 

        v3_x = mbr[2].x() - x_c
        v3_y = mbr[2].y() - y_c 
        
        v4_x = mbr[3].x() - x_c
        v4_y = mbr[3].y() - y_c
        
        #Resize vectors v1 - v4 
        v1_x_res = v1_x * sqrt(k)
        v1_y_res = v1_y * sqrt(k)
        
        v2_x_res = v2_x * sqrt(k)
        v2_y_res = v2_y * sqrt(k)
        
        v3_x_res = v3_x * sqrt(k)
        v3_y_res = v3_y * sqrt(k)
        
        v4_x_res = v4_x * sqrt(k)
        v4_y_res = v4_y * sqrt(k)
        
        #Compute new vertices
        p1_x = v1_x_res + x_c  
        p1_y = v1_y_res + y_c 
        
        p2_x = v2_x_res + x_c  
        p2_y = v2_y_res + y_c 
        
        p3_x = v3_x_res + x_c  
        p3_y = v3_y_res + y_c 
        
        p4_x = v4_x_res + x_c  
        p4_y = v4_y_res + y_c
        
        # Compute new coordinates
        p1 = QPointF(p1_x,  p1_y)
        p2 = QPointF(p2_x,  p2_y)
        p3 = QPointF(p3_x,  p3_y)
        p4 = QPointF(p4_x,  p4_y)   
        
        #Create polygon
        mbr_res = QPolygonF()
        mbr_res.append(p1)
        mbr_res.append(p2)
        mbr_res.append(p3)
        mbr_res.append(p4)
       
        return mbr_res
    
    
    def simplifyBuildingMBR(self, building:QPolygonF):
        #Simplify building using MBR
        mbr = self.createMBR(building)
        
        #Resize rectangle
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res
    
    
    
    def simplifyBuildingPCA(self, building:QPolygonF):
        #Simplify building using PCA
        X, Y = [], []
        
        #Convert polygon vertices to matrix
        for p in building:
            X.append(p.x())
            Y.append(p.y())
            
        #Create A
        A = np.array([X, Y])

        #Compute covariance matrix
        C = np.cov(A)
        
        #Singular Value Decomposition
        [U, S, V] = np2.svd(C)
        
        #Compute direction of the principal component
        sigma = atan2(V[0][1], V[0][0])

        #Rotate building by -sigma
        build_rot = self.rotatePolygon(building, -sigma)
        
        #Create min-max box
        mmb, area = self.createMMB(build_rot)
        
        #Rotate min-max box by sigma
        mbr = self.rotatePolygon(mmb, sigma)
        
        #Resize min-max box
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res
    
    
    def simplifyBuildingLongestEdge(self, building:QPolygonF):
        max_length = 0
        longest_edge = (QPointF(), QPointF())
        n = len(building)
        
        #Find longest edge 
        for i in range(n):
            p1 = building[i]
            p2 = building [(i+1) % n]
            length = sqrt( (p2.x()-p1.x())**2 + (p2.y()-p1.y())**2 )
            
            if length > max_length:
                max_length = length
                longest_edge = (p1, p2)
        
        #Compute direction of the longest edge
        sigma = atan2(longest_edge[1].y() - longest_edge[0].y(), longest_edge[1].x() - longest_edge[0].x())
        
        #Rotate building by -sigma
        rot = self.rotatePolygon(building, -sigma)
        
        #Create min/max box 
        mmb, area = self.createMMB(rot)
        
        #Rotate min-max box by sigma
        mbr = self.rotatePolygon(mmb, sigma)
        
        #Resize min-max box
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res
    
    
    def simplifyBuildingWallAverage(self, building:QPolygonF):
        n = len(building)
        
        #Sums 
        sum_rs = 0
        sum_s = 0
        
        #Direction of the first edge 
        sigma1 = atan2(building[1].y() - building[0].y(), building[1].x() - building[0].x())
        
        #Process all edges 
        for i in range(n):
            p1 = building[i]
            p2 = building [(i+1) % n]
            
            dx = p2.x() - p1.x()
            dy = p2.y() - p1.y()
            
            #Edge length 
            s_i = sqrt(dx**2 + dy**2)
            
            #Edge direction 
            sigma_i = atan2(dy, dx)
            
            #Relative angle 
            omega_i = sigma_i - sigma1
            
            #Calculate pi/2 multiple 
            k_i = (2 * omega_i) / pi
            
            #Oriented remainder ( here 92 deg yields r > 0 and 88 deg yields r < 0)
            r_i = (k_i - round(k_i)) * (pi/2)
            
            #Update sums
            sum_rs = sum_rs + (r_i * s_i)
            sum_s = sum_s + s_i

        #Compute main direction of the building
        sigma_avg = sigma1 + (sum_rs / sum_s)
        
        #Rotate building by -sigma_avg
        rot = self.rotatePolygon(building, -sigma_avg)
        
         #Create min/max box 
        mmb, area = self.createMMB(rot)
        
        #Rotate min-max box by sigma
        mbr = self.rotatePolygon(mmb, sigma_avg)
        
        #Resize min-max box
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res
         

    def simplifyBuildingWeightedBisector(self, building:QPolygonF):
        n = len(building)
        
        diagonals = []
        
        #Compute all diagonals of the building
        for i in range(n):
            for j in range(i + 1, n):
                p1 = building[i]
                p2 = building[j]
                
                dx = p2.x() - p1.x()
                dy = p2.y() - p1.y()
                
                #Compute length of diagonal
                length = sqrt(dx**2 + dy**2)
                
                #Compute angle 
                sigma = atan2(dy, dx)
                
                #Normalize angle (diagonals are undirected)
                sigma = sigma % pi 
                
                diagonals.append((length, sigma))
        
        #Sort diagonals 
        diagonals.sort(key= lambda x: x[0], reverse=True)
        
        #Get two longest diagonals 
        s1, sigma1 = diagonals[0]
        s2, sigma2 = diagonals[1]
        
        #Compute main direction of the building
        sigma_avg = (s1*sigma1 + s2*sigma2) / (s1 + s2)
        
        #Rotate building by -sigma_avg
        rot = self.rotatePolygon(building, - sigma_avg)
        
        #Create min/max box 
        mmb, area = self.createMMB(rot)
        
        #Roate min-max box by sigma_avg
        mbr = self.rotatePolygon(mmb, sigma_avg)
        
        #Resize 
        mbr_res = self.resizeRectangle(building, mbr)
        
        return mbr_res