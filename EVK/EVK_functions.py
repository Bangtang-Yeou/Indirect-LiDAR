#Melexis python library wrapper for MLX75027 EVK
# Author: TPT
# Version: 1.1
# For additional support contact -> tof3d@melexis.com

########################### Imports #######################################
###########################################################################

from __future__ import division
from ctypes import *
import ctypes
import os
import numpy as np
from numpy.ctypeslib import ndpointer

px_width=640
px_height=480
SIZE = px_width*px_height

########################### Functions #####################################
###########################################################################

#load the 64-bit dynamic library
mydll = cdll.LoadLibrary('./EVK/EVKlib.dll')

# Connect to EVK
def initAndOpen(p1,p2,p3,p4):
    print('Connecting...')
    connect = mydll.initAndOpen(p1,p2,p3,p4)
    return connect

# Disconnect from the EVK
def close():
    print('Disconnecting...')
    mydll.close()
    return

# reads the corresponding address
# input is the adress in hexadecimal f.e. 0x5712
# return is uint32_t
def readRegister(addr):
    value = mydll.readRegister(addr)
    return value

# writes the corresponding address
# input is the adress in hexadecimal f.e. 0x5712, register value in uint32_t
def writeRegister(addr, regVal):
    mydll.writeRegister(addr, regVal)
    return

# Try to grab a frame within the specified frameTimeout (ms)
# return the number of channels
def getFrame(frameTimeout):
    channels = mydll.getFrame(frameTimeout)
    return channels

# Release the frame
def freeFrame():
    mydll.freeFrame()
    return

# Used when in distance/amplitude Mode or distance/confidence Mode
# returns the distance array of the frame grabbed by getFrame()
def getDistances():
    mydll.getDistances.restype = ndpointer(dtype=ctypes.c_uint16, shape=(SIZE,))
    Dist_array = mydll.getDistances()
    return Dist_array

# Used when in distance/amplitude Mode
# returns the amplitude array of the frame grabbed by getFrame()
def getAmplitudes():
    mydll.getAmplitudes.restype = ndpointer(dtype=ctypes.c_uint16, shape=(SIZE,))
    Ampl_array = mydll.getAmplitudes()
    return Ampl_array

# Used when in distance/confidence Mode
# returns the confidence array of the frame grabbed by getFrame()
def getConfidences():
    mydll.getChannelData.restype = ndpointer(dtype=ctypes.c_uint8, shape=(SIZE,))
    Conf_array = mydll.getChannelData(1)
    return Conf_array

# return the data array according to the channel
# channel can be amplitude / distance / confidence / raw phase x depending on mode
def getChannelData(channel):
    mydll.getChannelData.restype = ndpointer(dtype=ctypes.c_uint16, shape=(SIZE,))
    DATA_array = mydll.getChannelData(channel)
    return DATA_array

# returns the horizontal pixel width (default 640) as uint16_t
def getXSize(channel):
    size = mydll.getXSize(channel)
    return size

# returns the vertical pixel width (default 480) as uint16_t
def getYSize(channel):
    size = mydll.getYSize(channel)
    return size

# change the settings of the EVK
def ChangeMLX75027Settings(IntT, ModF, FrameR, IllP, OutputM):
    if IntT  <=1000 and IntT >=1:
        writeRegister(0x0005, IntT)
    else:
        print("Please enter an integration time between 1us and 1000us")

    if ModF  >=4 and ModF <=100:
        writeRegister(0x0009, ModF*100)
    else:
        print("Please enter a modulation frequency between 4Mhz and 100MHz")

    if FrameR  >=1 and FrameR <=15:
        writeRegister(0x000A, FrameR)
    else:
        print("Please enter a frame rate between 1 and 15")

    if IllP  >=0 and IllP <=100:
        writeRegister(0x0159, IllP)
    else:
        print("Please enter an illumination power between 0% and 100%")

    if OutputM  >=0 and OutputM <=3:
        writeRegister(0x8828, OutputM)
    else:
        print("Please enter a valid output mode ")

# read the settings of the EVK and print to terminal
def ReadMLX75027Settings():
    print("Current settings:")
    print("\t IntegrationTime: \t"+str(readRegister(0x0005))+'us')
    print("\t ModulationFrequency: \t"+str(int(readRegister(0x0009)/100))+'MHz')
    print("\t FrameRate: \t\t"+str(readRegister(0x000A))+'FPS')
    print("\t IlluminationPower: \t"+str(readRegister(0x0159))+'%')
    OutputM=readRegister(0x8828)
    if OutputM == 0:
        print("\t OutputMode:\t\tA-B")
    elif OutputM == 1:
        print("\t OutputMode:\t\tA+B")
    elif OutputM == 2:
        print("\t OutputMode:\t\tA")
    elif OutputM == 3:
        print("\t OutputMode:\t\tB")

def getVersion():
    ver = mydll.GetVersion()
    return ver

def isConnected():
    iscon=mydll.IsConnected()
    return iscon
    
#calculate two's complement
def two_comp(phase_in):
    phase_tmp1 = phase_in.astype(np.uint16)
    phase_tmp2 = np.left_shift(phase_tmp1, 4)
    phase_tmp3 = phase_tmp2.astype(np.int16)
    phase_tmp4 = np.right_shift(phase_tmp3, 4)
    phase_out = phase_tmp4.astype(np.double)
    return phase_out

def reScale(pixArray,scale):
    super_threshold_indices = pixArray >= scale[1]
    pixArray[super_threshold_indices] = scale[1]-1
    super_threshold_indices = pixArray < scale[0]
    pixArray[super_threshold_indices] = scale[0]
    pixArray=pixArray-scale[0]
    pixArray=pixArray*(65536/(scale[1]-scale[0]))
    pixArray8b = (pixArray/256).astype('uint8')
    return pixArray8b
