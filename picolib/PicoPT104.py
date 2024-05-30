#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
   Python module for Pico PT104.
   Author:  Jinrui Huang
   Revision:  2020-11-03
   Requires:  Python 3.5, Pico SDK
    
"""

import ctypes
from picosdk.usbPT104 import usbPt104 as pt104
import time

class PT104(object):
    
    def __init__(self):
        self.handle = ctypes.c_int16()
        self.status = {}
    
    def openunit(self,DeviceSN):
        # convert device serial number
        DeviceSN = DeviceSN.encode()
        # open unit
        self.status = pt104.UsbPt104OpenUnit(ctypes.byref(self.handle),DeviceSN)
    
    def setmain(self):
        # set mains rejection to 50 Hz
        self.status = pt104.UsbPt104SetMains(self.handle,0)
        
    def setchannel(self,Channel,DataType,nWires,tWait):
        # set up channel， data/sensor type, number of wires and wait time for conversion
        self.status = pt104.UsbPt104SetChannel(self.handle, Channel, DataType, ctypes.c_int16(nWires))
        time.sleep(tWait) # wait for 2s for conversion
        
        # PT104_DATA_TYPE list
        # 'USBPT104_OFF':0
        # 'USBPT104_PT100':1
        # 'USBPT104_PT1000':2
        # 'USBPT104_RESISTANCE_TO_375R':3
        # 'USBPT104_RESISTANCE_TO_10K':4
        # 'USBPT104_DIFFERENTIAL_TO_115MV':5
        # 'USBPT104_DIFFERENTIAL_TO_2500MV':6
        # 'USBPT104_SINGLE_ENDED_TO_115MV':7
        # 'USBPT104_SINGLE_ENDED_TO_2500MV':8
        # 'USBPT104_MAX_DATA_TYPES':9
        # The following are used by default
        # DataType = 1 for PT100
        # nWires = 4 for probe type sensors
        # tWait = 2 for 2 seconds wait for conversion
    
    def getvalue(self,Channel):
        # get temperature reading
        temp = (ctypes.c_double*1)() #double type output
        temp_raw = (ctypes.c_int32*1)() #raw outputs from PT104 are int32 type
        self.status = pt104.UsbPt104GetValue(self.handle, Channel, ctypes.byref(temp_raw), True)
        temp = temp_raw[0]/1000 # scale the reading/conversion
        # print data
        # print("Channel "+str(Channel)+": "+str(temp))
        return temp
    
    def closeunit(self):
        # close unit
        self.status = pt104.UsbPt104CloseUnit(self.handle)
    
