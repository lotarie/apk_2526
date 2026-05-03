from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from qpoint3df import *
from math import *
from edge import *
from triangle import *

class Algorithms:
    
    def __init__(self):
        pass
    
    def getPointLinePosition(self, a, b, p):
        #Analyze point and aline position (half plane test)
        tolerance = 1.0e-6
        
        #Components of vectors
        ux = b.x() - a.x()
        uy = b.y() - a.y()
        vx = p.x() - a.x()
        vy = p.y() - a.y()
        
        #Test criterion
        t = ux*vy - vx*uy
        
        #Point in the left half plane
        if t > tolerance:
            return 1
        
        #Point in the right half plane
        if t < -tolerance:
            return 0
    
        #Point on the line
        return -1
        
    
    def getNearestPoint(self, p, points):
        #Find point nearest to p in points
        p_nearest = None
        d_min = inf
        
        #Process all points
        for p_i in points:
            
            #Point p different from p_i
            if p != p_i:            
                #Coordinate differences
                dx = p.x() - p_i.x()
                dy = p.y() - p_i.y()
                 
                #Compute distance          
                dist = sqrt(dx**2 + dy**2)
                
                #Update minimum
                if dist < d_min:
                    d_min = dist
                    p_nearest = p_i
                    
        return p_nearest
    
    
    def get2LinesAngle(self, p1:QPointF, p2:QPointF, p3:QPointF, p4:QPointF):
        #Angle between two lines
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
    
    
    def findDelaunayPoint(self, p1, p2, points):
        #Find Delaunay point to the edge
        p_dt = None
        phi_max = 0

        #Process all points
        for p_i in points:
            
            #Point pi different from p1 and p2
            if p_i != p1 and p_i != p2:
                
                #Point in the left halfplane
                if self.getPointLinePosition (p_i, p1, p2) == 1:
                    
                    #Compute phi
                    phi = self.get2LinesAngle(p_i, p2, p_i, p1)
                    
                    #Update maximum
                    if phi > phi_max:
                        phi_max = phi
                        p_dt = p_i
        return p_dt
                    
    def createDT(self, points):
        #Create Delaunay triangulation                 
        DT = []
        AEL = [] 
        
        #Find pivot
        q = min(points, key = lambda k: k.y())   
        
        #Find point nearest to q
        qn = self.getNearestPoint(q, points)       
        
        #Create new edges
        e = Edge(q, qn)
        es = Edge(qn, q)  
        
        #Edges to AEL
        AEL.append (e)
        AEL.append (es) 
        
        #Repeat until AEL is empty             
        while AEL:
            #Take first edge
            e1 = AEL.pop()
            
            #Switch orientation
            e1s = e1.switchOrientation()
            
            #Find Delaunay point
            p_dt = self.findDelaunayPoint(e1s.getStart(), e1s.getEnd(), points)
            
            #Jump to the next iteration
            if p_dt == None:
                continue
            
            #Create new edges
            e2 = Edge(e1s.getEnd(), p_dt)
            e3 = Edge(p_dt, e1s.getStart())
            
            #Add new edges to DT
            DT.append(e1s)
            DT.append(e2)
            DT.append(e3)
                 
            #Update AEL
            self.updateAEL(e2,AEL)
            self.updateAEL(e3,AEL)
            
        return DT
    
    
    def updateAEL(self, e, AEL):
        #Verify if e in AEL with diffferent orientation
        es = e.switchOrientation()
        
        #Edge e in AEL, remove
        if es in AEL:
            AEL.remove(es)
            
        #Add e to AEL
        else:
            AEL.append(e) 
            
            
    def getContourPoint(self, p1, p2, z):
        #Compute intersection line and plane
        xb = (p2.x() - p1.x())/(p2.z() - p1.z()) * (z - p1.z()) + p1.x()
        yb = (p2.y() - p1.y())/(p2.z() - p1.z()) * (z - p1.z()) + p1.y()
        
        return QPoint3DF(xb, yb, z)
    
    
    def createContourLines(self, DT, z_min, z_max, dz):
        #Create contour lines using linear interpolation
        contour_lines = []
        
        #Process all contour lines
        for z in range(z_min, z_max, dz):
            
            #Traverse dt triangles one by one
            for i in range(0, len(DT), 3):
                
                #Triangle vertices
                p1 = DT[i].getStart()
                p2 = DT[i+1].getStart()
                p3 = DT[i+1].getEnd()
                
                #Height differences
                dz1 = z - p1.z()
                dz2 = z - p2.z()
                dz3 = z - p3.z()
                
                #Skip triangle
                if dz1 == 0 and dz2 == 0 and dz3 == 0:
                    continue
                
                #Edge (p1, p2) is colinear
                elif dz1 == 0 and dz2 == 0:
                    contour_lines.append(DT[i])
                    
                #Edge (p2, p3) is colinear
                elif dz2 == 0 and dz3 == 0:
                    contour_lines.append(DT[i+1])
                
                #Edge (p3, p1) is colinear
                elif dz3 == 0 and dz1 == 0:
                    contour_lines.append(DT[i+2])
                    
                #Edges (p1, p2) and (p2, p3) intersected by plane
                elif (dz1*dz2 <= 0) and (dz2*dz3 <= 0):
                    self.createContourLineSegment(p1, p2, p3, z, contour_lines)   
                  
                #Edges (p3, p1) and (p1, p2) intersected by plane      
                elif (dz2*dz3 <= 0) and (dz3*dz1 <= 0):
                    self.createContourLineSegment(p2, p3, p1, z, contour_lines)
                
                #Edges (p3, p1) and (p1, p2) intersected by plane
                elif (dz3*dz1 <= 0) and (dz1*dz2 <= 0):
                    self.createContourLineSegment(p3, p1, p2, z, contour_lines)
                    
        return contour_lines
    
    def getDeterminant(self, mat):
        #Calculate determinant of 3x3 matrix
        return (mat[0][0] * (mat[1][1] * mat[2][2] - mat[1][2] * mat[2][1]) -
                mat[0][1] * (mat[1][0] * mat[2][2] - mat[1][2] * mat[2][0]) +
                mat[0][2] * (mat[1][0] * mat[2][1] - mat[1][1] * mat[2][0]))
    
    def getPlaneParameters(self, p1, p2, p3):
            #Common denominator of matrix (x, y, 1)
            D = self.getDeterminant([
                [p1.x(), p1.y(), 1],
                [p2.x(), p2.y(), 1],
                [p3.x(), p3.y(), 1]
            ])
            
            #(AI debbuged) - Solution for when two points have the same x and y coordinates
            if D == 0:
                return 0, 0, 0
                
            #Numerator for "a" matrix (y, z, 1)
            Na = self.getDeterminant([
                [p1.y(), p1.z(), 1],
                [p2.y(), p2.z(), 1],
                [p3.y(), p3.z(), 1]
            ])
            
            #Numerator for "b" matrix (x, z, 1)
            Nb = self.getDeterminant([
                [p1.x(), p1.z(), 1],
                [p2.x(), p2.z(), 1],
                [p3.x(), p3.z(), 1]
            ])
            
            #Numerator for "c" matrix (x, y, z)
            Nc = self.getDeterminant([
                [p1.x(), p1.y(), p1.z()],
                [p2.x(), p2.y(), p2.z()],
                [p3.x(), p3.y(), p3.z()]
            ])
            
            #Plane parameters
            a = Na / D
            b = Nb / D
            c = Nc / D
            
            return a, b, c
        
    def createTIN(self, DT):
        #Create TIN from DT
        TIN = []
        
        #Process all triangles
        for i in range(0, len(DT), 3):
            #Triangle vertices
            p1 = DT[i].getStart()
            p2 = DT[i+1].getStart()
            p3 = DT[i+1].getEnd()
               
            #Create triangle and add to TIN
            t = Triangle(p1, p2, p3)
            TIN.append(t)
            
        return TIN
    
    def analyzeSlope(self, TIN):
        #Calcualtion for each triangle in TIN
        for t in TIN:
            p1 = t.getP1()
            p2 = t.getP2()
            p3 = t.getP3()
            
            #Vector creation for edges u and v
            ux = p2.x() - p1.x()
            uy = p2.y() - p1.y()
            uz = p2.z() - p1.z()
            vx = p3.x() - p1.x()
            vy = p3.y() - p1.y()
            vz = p3.z() - p1.z()
            
            #Cross product to get normal vector
            a = uy*vz - uz*vy
            b = uz*vx - ux*vz
            c = ux*vy - uy*vx
            
            #Normal vector length
            n_norm = (a**2 + b**2 + c**2)**0.5
            
            if n_norm == 0:
                continue
            
            #Calculation of deviation of phi
            arg = abs(c) / n_norm
            #AI debbuged - Correcting argument to be within valid range for acos
            if arg > 1:
                arg = 1
            elif arg < -1:
                arg = -1
            phi = acos(arg)
            
            #Convert to degrees
            slope_deg = degrees(phi)
            t.setSlope(slope_deg)
            
        return TIN
    
    def analyzeExposition(self, TIN):
        #Calculation for each triangle in TIN
        for t in TIN:
            p1 = t.getP1()
            p2 = t.getP2()
            p3 = t.getP3()
            
            #Vector creation for edges u and v
            ux = p2.x() - p1.x()
            uy = p2.y() - p1.y()
            uz = p2.z() - p1.z()
            vx = p3.x() - p1.x()
            vy = p3.y() - p1.y()
            vz = p3.z() - p1.z()
            
            #Cross product to get normal vector
            a = uy*vz - uz*vy
            b = uz*vx - ux*vz

            #Azimuth calculation (AI debbuged using atan2)
            azimuth = atan2(b, a)
            
            #Convert to degrees and adjust range
            azimuth_deg = degrees(azimuth)
            
            #AI debbuged - Adjusting azimuth to be within 0-360 degrees
            if azimuth_deg < 0:
                azimuth_deg += 360
                
            t.setAspect(azimuth_deg)
            
        return TIN
        
        
    
    def createContourLineSegment(self, p1, p2, p3, z, contour_lines):
        #Create contour line segment
        
        #Line and plane intersection
        a = self.getContourPoint(p1, p2, z)
        b = self.getContourPoint(p2, p3, z)
        
        #Create edge, contour
        e = Edge(a, b)
    
        #Add contour to the list
        contour_lines.append(e)
        