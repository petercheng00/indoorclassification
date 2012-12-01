import sys
from math import *


RevitScale = 0.000022192257
distThresh = 0.0001
sizeThresh = 1


def within(val1, val2, e=0.01):
    if (val1 > val2):
        return (val1 - val2) < e
    else:
        return (val2 - val1) < e

def mag(v):
    return sqrt(pow(v[0],2) + pow(v[1],2) + pow(v[2],2))
	
def dist(p1, p2):
	v = [p2[0] - p1[0], p2[1]-p1[1], p2[2]-p1[2]]
	m = mag(v)
	if ( m < 0):
		m = 0 - m
	return m
        
def maxDist(points):
	ret = 0.0
	for i in range(len(points)):
		for j in range(i+1, len(points)):
			ret = max(ret, dist(points[i], points[j]))
	return ret
    
def perimSub2(points):
    max1 = 0
    max2 = 0
    total = 0
    for i in range(len(points)-1):
        currDist = dist(points[i], points[i+1])
        if (currDist > max1):
            total += max2
            max2 = max1
            max1 = currDist
        elif (currDist > max2):
            total += max2
            max2 = currDist
        else:
            total += currDist
    return total

def avgDist(points):
    total = 0
    if (len(points) == 1):
        print "what"
        print points
    for i in range(len(points) - 1):
        total += dist(points[i], points[i+1])
    return total/(len(points)-1)
		
def area(p1, p2, p3):
    v1 = dist(p1, p2)
    v2 = dist(p1, p3)
    return v1 * v2
    
def center(points):
    totalX = 0.0
    totalY = 0.0
    totalZ = 0.0
    for point in points:
        totalX += point[0]
        totalY += point[1]
        totalZ += point[2]
    avgX = totalX / len(points)
    avgY = totalY / len(points)
    avgZ = totalZ / len(points)
    return [avgX, avgY, avgZ]
    
def bbArea(points):
    minX = points[0][0]
    maxX = points[0][0]
    minY = points[0][1]
    maxY = points[0][1]
    minZ = points[0][2]
    maxZ = points[0][2]
    for point in points:
        minX = min(minX, point[0])
        maxX = max(maxX, point[0])
        minY = min(minY, point[1])
        maxY = max(maxY, point[1])
        minZ = min(minZ, point[2])
        maxZ = max(maxZ, point[2])
    xDist = maxX - minX
    yDist = maxY - minY
    zDist = maxZ - minZ
    return max(xDist * yDist, xDist * zDist, yDist * zDist)
    
def sameSlope(p1, p2, p3):
    d1 = [0.0, 0.0, 0.0]
    d2 = [0.0, 0.0, 0.0]
    d1[0] = p2[0] - p1[0]
    d1[1] = p2[1] - p1[1]
    d1[2] = p2[2] - p1[2]
    d2[0] = p3[0] - p2[0]
    d2[1] = p3[1] - p2[1]
    d2[2] = p3[2] - p2[2]
    d1mag = mag(d1)
    d2mag = mag(d2)
    d1[0] = d1[0] / d1mag
    d1[1] = d1[1] / d1mag
    d1[2] = d1[2] / d1mag
    d2[0] = d2[0] / d2mag
    d2[1] = d2[1] / d2mag
    d2[2] = d2[2] / d2mag
    if (dist(d1, d2) < 0.001):
        return True
    return False
        
def sameNormal(v1, v2):
    return ((within(v1[0], v2[0]) and
            within(v1[1], v2[1]) and
            within(v1[2], v2[2])) or
            (within(v1[0], -1.0 * v2[0]) and
             within(v1[1], -1.0 * v2[1]) and
             within(v1[2], -1.0 * v2[2])))
             
def perpNormal(v1, v2):
    return within(v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2], 0)

def getNormal(p1, p2, p3):
    v1 = [p2[0] - p1[0], p2[1]-p1[1], p2[2]-p1[2]]
    v2 = [p3[0] - p1[0], p3[1]-p1[1], p3[2]-p1[2]]
    n = [0.0, 0.0, 0.0]
    n[0] = v1[1] * v2[2] - v1[2] * v2[1]
    n[1] = v1[2] * v2[0] - v1[0] * v2[2]
    n[2] = v1[0] * v2[1] - v1[1] * v2[0]
    
    magn = mag(n)
    if (magn != 0):
        n[0] = n[0]/magn
        n[1] = n[1]/magn
        n[2] = n[2]/magn
    return n

def planeEquation(p1, p2, p3):
    x1 = p1[0]
    y1 = p1[1]
    z1 = p1[2]
    x2 = p2[0]
    y2 = p2[1]
    z2 = p2[2]
    x3 = p3[0]
    y3 = p3[1]
    z3 = p3[2]
    a = y1 * (z2 - z3) + y2 * (z3 - z1) + y3 * (z1 - z2)
    b = z1 * (x2 - x3) + z2 * (x3 - x1) + z3 * (x1 - x2)
    c = x1 * (y2 - y3) + x2 * (y3 - y1) + x3 * (y1 - y2)
    if (a < 0.00001 and a > -0.00001):
	    a = 0
    if (b < 0.00001 and b > -0.00001):
	    b = 0
    if (c < 0.00001 and c > -0.00001):
	    c = 0
    mag = sqrt(pow(a, 2.0) + pow(b, 2.0) + pow(c, 2.0))
    if mag != 0:
        a = a / mag
        b = b / mag
        c = c / mag
    d = -1 * (a * x1 + b * y1 + c * z1)
    return [a, b, c, d]
    
def validVertex(v, plane):
    if len(plane) == 0:
        return True
    prevVertex = plane[len(plane)-1]
    if len(plane) >= 1:
        if ((within(prevVertex[0], v[0], distThresh)) and
            (within(prevVertex[1], v[1], distThresh)) and
            (within(prevVertex[2], v[2], distThresh))):
            return False
    if len(plane) >= 2:
        prevVertex2 = plane[len(plane)-2]
        if (sameSlope(prevVertex2, prevVertex, v)):
            plane.pop()
            return True
    return True
    
    
def readFile(fileName):
    global totalArea
    inFile = open(fileName, "r")
    line = inFile.readline()
    planes = []
    currPlane = []
    prevNorm = [0.0, 0.0, 0.0]
    prevCenter = [0.0, 0.0, 0.0]
    index = 1
    while line:
        if ("AcDbPolyFaceMeshVertex" in line):
            currVertex = []
            inFile.readline() #10
            currVertex.append(float(inFile.readline()) * RevitScale)
            inFile.readline() #20
            currVertex.append(float(inFile.readline()) * RevitScale)
            inFile.readline() #30
            currVertex.append(float(inFile.readline()) * RevitScale)
            
            if (validVertex(currVertex, currPlane)):
			    currPlane.append(currVertex)
        elif ("SEQEND" in line):
            currNorm = getNormal(currPlane[0],
                                    currPlane[len(currPlane)/2],
                                    currPlane[len(currPlane)-1])
            currCenter = center(currPlane)
            if ((len(currPlane) > 2) and
                (perimSub2(currPlane) > sizeThresh) and
                (not (sameNormal(currNorm, prevNorm) and 
                    (dist(currCenter, prevCenter) < distThresh)))):
                    
                planes.append(currPlane)
                prevNorm = currNorm
                prevCenter = currCenter
            currPlane = []
        line = inFile.readline()   
    inFile.close()
    return planes

def writeFile(fileName, planes):
    outFile = open(fileName, "w")
    outFile.write(str(len(planes)) + '\n')
#    outFile.write(str(1) + '\n')
    counter = 1
    for plane in planes:
        if counter != 308 and counter != 310:
            outFile.write(str(len(plane)) + '\n')
            currEquation = planeEquation(plane[0], plane[len(plane)/2], plane[len(plane)-1])
            outFile.write(str(currEquation[0]) + " " + str(currEquation[1]) + " " + str(currEquation[2]) + " " + str(currEquation[3]) + '\n')
            for vertex in plane:
                outFile.write(str(vertex[0]) + " " + str(vertex[1]) + " " + str(vertex[2]) + '\n')
        counter = counter + 1
    outFile.close()
    
if __name__ == "__main__":
    planes = readFile(sys.argv[1])
    '''    print "sizeThresh: ", sizeThresh
    newPlanes = []
    prevNorm = [0, 0, 0]
    prevCenter = [0, 0, 0]
    counter = 1
    for plane in planes:
        if counter <= 108:
            currArea = perimSub2(plane)
            currNorm = getNormal(plane[0], 
                                 plane[len(plane)/2],
                                 plane[len(plane)-1])
            currCenter = center(plane)
            if ((currArea > sizeThresh) and
                (not (sameNormal(currNorm, prevNorm) and dist(currCenter, prevCenter) < distThresh))):
    #            (not within(currArea, prevArea)) and
    #            (not sameNormal(currNorm, prevNorm))):
                newPlanes.append(plane)
    #            prevArea = currArea
                prevNorm = currNorm
                prevCenter = currCenter
        counter = counter + 1'''
    print "num planes ", len(planes)
    writeFile(sys.argv[2], planes)