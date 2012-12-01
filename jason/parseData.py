'''
Created on Nov 29, 2012

@author: jason
'''
import os
import sys
import numpy as np
import struct
import math
import cPickle
import csv

class BinaryReaderEOFException(Exception):
    def __init__(self):
        pass
    def __str__(self):
        return 'Not enough bytes in file to satisfy read request'

class BinaryReader:
    # Map well-known type names into struct format characters.
    typeNames = {
        'int8'   :'b',
        'uint8'  :'B',
        'int16'  :'h',
        'uint16' :'H',
        'int32'  :'i',
        'uint32' :'I',
        'int64'  :'q',
        'uint64' :'Q',
        'float'  :'f',
        'double' :'d',
        'char'   :'s'}

    def __init__(self, fileName):
        self.file = open(fileName, 'rb')
        
    def read(self, typeName):
        typeFormat = BinaryReader.typeNames[typeName.lower()]
        typeSize = struct.calcsize(typeFormat)
        value = self.file.read(typeSize)
        if typeSize != len(value):
            raise BinaryReaderEOFException
        return struct.unpack(typeFormat, value)[0]
    
    def __del__(self):
        self.file.close()

def parseMadFile(filename):
  myReader = BinaryReader(filename)
  numZUPTs = myReader.read('int32')
  for i in xrange(numZUPTs):
    myReader.read('double')
    myReader.read('double')
  numMeasures = myReader.read('int32')
#  print numMeasures
  
  listofreadings = {}
  
  for i in xrange(numMeasures):
    time = myReader.read('double')
    x = myReader.read('double')
    y = myReader.read('double')
    z = myReader.read('double')
    roll = myReader.read('double')
    pitch = myReader.read('double')
    yaw = myReader.read('double')
    listofreadings[time] = (x,y,z,roll,pitch,yaw)
  
  return listofreadings

def parseMCDFile(filename):
  def string2float(list):
    return [float(x) for x in list]
  f = open(filename)
  name, numimages = f.readline().rstrip().split()
  numimages = int(numimages)
  karray = string2float(f.readline().rstrip().split())
  kmat = np.reshape(karray, (3,3))
  rot_offset = string2float(f.readline().rstrip().split())
  rot_offset = np.reshape(rot_offset, (3,3))
  trans_offset = string2float(f.readline().rstrip().split())
  trans_offset = [(x/1000) for x in trans_offset]
  
  listofimages = []
  
  for i in xrange(numimages): 
    imgpath, time = f.readline().rstrip().split()
    time = float(time)
    listofimages.append((imgpath, time))
  
  f.close()
  return (kmat, rot_offset, trans_offset, listofimages)
    
def parseModelFile(filename):
  f = open(filename)
  listofplanes = []
  numplanes = int(f.readline().rstrip())
  for i in xrange(numplanes):
    numvertices = int(f.readline().rstrip())
    plane_ABCD = f.readline().rstrip().split()
    plane_ABCD = [float(x) for x in plane_ABCD]
    listofvertices = np.empty((numvertices, 3))
    for j in xrange(numvertices):
      str = f.readline()
#      print str.rstrip().split()
      listofvertices[j,:] = np.array(str.rstrip().split())
    listofplanes.append((i, numvertices, plane_ABCD, listofvertices))
  f.close()
  return listofplanes
    
def projectBack(tran_ctow, rot_ctow, listofplanes, kmat, dist_thres, angle_diff):
  udim = kmat[0, 2]*2
  vdim = kmat[1, 2]*2
  kmatinv = np.linalg.inv(kmat)
  centerofcamera = np.transpose(np.array([[kmat[0, 2], kmat[1, 2] , 1]]))
  cameradir = np.dot(rot_ctow, np.dot(kmatinv, centerofcamera))
      
  tran_ctow = np.transpose(tran_ctow)
  rot_wtoc = np.transpose(rot_ctow)
  tran_wtoc = -1*np.dot(rot_wtoc, tran_ctow)
  
  listofmatched = []
  for planenum, numvertices, plane_ABCD, listofvertices in listofplanes:
    planenormal = np.array([plane_ABCD[:-1]])
    planenormal = planenormal/np.linalg.norm(planenormal)
#    print planenormal
#    print cameradir
    anglecamplane = math.degrees(math.acos(np.dot(planenormal, cameradir)/(np.linalg.norm(planenormal)*np.linalg.norm(cameradir))))
    if anglecamplane > angle_diff and anglecamplane < 180-angle_diff:
      continue
    for i in xrange(numvertices):
      vertex = np.transpose([listofvertices[i,:]])
      pcamera = np.add(np.dot(rot_wtoc, vertex), tran_wtoc)
      z = pcamera[2,0]
#      print tran_ctow
#      print rot_ctow
#      print tran_wtoc
#      print rot_wtoc
#      print vertex
#      print kmat
#      print pcamera
#      print z
      uv = (1/z)*np.dot(kmat, pcamera)
      u = round(uv[0,0])
      v = round(uv[1,0])
#      print u, v
      dist_to_cam = np.linalg.norm(vertex-tran_ctow)
#      print dist_to_cam
      if 0<=u<udim and 0<=v<vdim and z>0 and dist_to_cam < dist_thres:
        print "matched plane " + str(planenum)
        listofmatched.append(planenum)
        break
  return listofmatched
  
def getCloseTime(timekeys, time):
  difflist = [abs(x - time) for x in timekeys]
  mintimeindex = difflist.index(min(difflist))
  return timekeys[mintimeindex]

def generateRotMat(roll, pitch, yaw):
  rmat = np.array([[1, 0, 0], [0, math.cos(roll), -math.sin(roll)], [0, math.sin(roll), math.cos(roll)]])
  pmat = np.array([[math.cos(pitch), 0, math.sin(pitch)], [0,1, 0], [-math.sin(pitch), 0, math.cos(pitch)]])
  ymat = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw),0], [0,0,1]])
  rotmat = np.dot(ymat, np.dot(pmat, rmat))
  return rotmat

def mat_to_quat(mat):
  epsilon = 0.00001
  def copysign(x,y):
    if y >= 0:
      sign = 1
    else:
      sign = -1
    return sign * abs(x)
  
  Qxx = mat[0,0]
  Qyy = mat[1,1]
  Qzz = mat[2,2]
  
  Qxy = mat[0,1]
  Qxz = mat[0,2]
  
  Qyx = mat[1,0]
  Qyz = mat[1,2]
  
  Qzx = mat[2,0]
  Qzy = mat[2,1]
    
  t = Qxx+Qyy+Qzz
  r = math.sqrt(1+t+epsilon)
  w = 0.5*r
  x = copysign(0.5*math.sqrt(1+Qxx-Qyy-Qzz+epsilon), Qzy-Qyz)
  y = copysign(0.5*math.sqrt(1-Qxx+Qyy-Qzz+epsilon), Qxz-Qzx)
  z = copysign(0.5*math.sqrt(1-Qxx-Qyy+Qzz+epsilon), Qyx-Qxy)
  
  return (w,x,y,z)

def getImagePlaneDict():
  dist_thres = 1000 #maximum distance between camera and plane 
  angle_diff = 90 #maximum difference in angle between plane normal and camera direction
  dataset = 'CoryHall'
  madpath = 'CoryHall/20121119-1/output/coryf3_CL_3D.mad'
  mcdpaths = ['CoryHall/right_right.mcd', 'CoryHall/right_up.mcd', 'CoryHall/left_left.mcd', 'CoryHall/left_up.mcd']
  modelpath = 'cory3rdfloorv3.model'

  if not os.path.isfile(dataset+'.pkl'):
    img_plane_dict = {}
    timedict = parseMadFile(madpath)
    timekeys = timedict.keys()
    listofplanes = parseModelFile(modelpath)
    for mcdpath in mcdpaths:
      kmat, rot, trans, listofimages = parseMCDFile(mcdpath)
      print "Number of Images:", len(listofimages)
      for i, imageinfo in enumerate(listofimages):
        imgpath, time = imageinfo
    #    if i != 1300:
    #      continue
        print imgpath
        closetime = getCloseTime(timekeys, time)
        
        x,y,z,r,p,y = timedict[closetime]
        r = math.radians(r)
        p = math.radians(p)
        y = math.radians(y)
        totaltrans = np.array([np.add([x,y,z], trans)])
        totalrot = np.dot(rot, generateRotMat(r,p,y))
        matchedplanes = projectBack(totaltrans, totalrot, listofplanes, kmat, dist_thres, angle_diff)
        img_plane_dict[imgpath] = (totaltrans, mat_to_quat(totalrot), matchedplanes, kmat)
  
    with open(dataset + '.pkl', 'wb') as f:
      cPickle.dump(img_plane_dict, f)
      
  else:
    with open(dataset+'.pkl', 'rb') as f:
      img_plane_dict = cPickle.load(f)
  
  return img_plane_dict

def findImagesforPlane(listofplanes, img_plane_dict, outputname):
  def mat2string(a):
    myStr = ''
    h,w = a.shape
    a = np.reshape(a, h*w)
    for i in xrange(h*w):
      myStr += str(a[i]) + ' '
    return myStr.rstrip()
  def array2string(a):
    myStr = ''
    for element in a:
      myStr += str(element) + ' '
    return myStr.rstrip()
  f = open(outputname, 'wb')
  myWriter = csv.writer(f, delimiter=';')
  myWriter.writerow(['Plane Number', 'Image Path', 'Translation', 'Rotation', 'K Matrix'])
  for imgpath, imginfo in img_plane_dict.items():
    tran, rot, matchedplanes, kmat = imginfo
    for plane in listofplanes:
      if plane in matchedplanes:
        myWriter.writerow([str(plane), imgpath, mat2string(tran), array2string(rot), mat2string(kmat)])

  f.close()
  
if __name__ == '__main__':
  listofplanes = [1,2,3,4,5]
  img_plane_dict = getImagePlaneDict()
  outputname = 'results.txt'
  findImagesforPlane(listofplanes, img_plane_dict, outputname)
  
    
  