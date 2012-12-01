'''
Created on Nov 29, 2012

@author: jason
'''
import os
import sys
import numpy as np
import struct

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
  print myReader.read('int32')
  print myReader.read('double')
  print myReader.read('double')
  print myReader.read('int32')

#  mad_file.read((char*)&numZUPTs, sizeof(int));
#  for(int jj = 0; jj!=numZUPTs; ++jj)
#  {
#    //read in the start and end time of each zupt
#    double startTime, endTime;
#    mad_file.read((char*)&startTime, sizeof(double));
#    mad_file.read((char*)&endTime, sizeof(double));
#
#  }
#
#  int numIMUMeas;
#  mad_file.read((char*)&numIMUMeas, sizeof(int));
#
#  for(int jj = 0; jj!=numIMUMeas; ++jj)
#  {
#
#    mad_file.read((char*)&time, sizeof(double));
#    mad_file.read((char*)&x, sizeof(double));
#    mad_file.read((char*)&y, sizeof(double));
#    mad_file.read((char*)&z, sizeof(double));
#    mad_file.read((char*)&roll, sizeof(double));
#    mad_file.read((char*)&pitch, sizeof(double));
#    mad_file.read((char*)&yaw, sizeof(double));
#  }


if __name__ == '__main__':
  madpath = '/home/jason/Desktop/indoorclassification/jason/LBNL/20120312-1/output/lbnl_CL_3D.mad'
  madpath = 'test.mad'
  parseMadFile(madpath)