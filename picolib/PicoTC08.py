#
# Copyright (C) 2019 Pico Technology Ltd. See LICENSE file for terms.
#
# TC-08 SINGLE MODE EXAMPLE


import ctypes
from picosdk.usbtc08 import usbtc08 as tc08

class PicoTC08(object):
    
    def __init__(self):
        self.handle = ctypes.c_int16()
        self.status = {}

    def openunit(self,channel,type):
        # open unit
        self.status["open_unit"] = tc08.usb_tc08_open_unit()
        self.handle = self.status["open_unit"]
        # set mains rejection to 50 Hz
        self.status["set_mains"] = tc08.usb_tc08_set_mains(self.handle,0)
        # set up channel
        # therocouples types and int8 equivalent
        # B=66 , E=69 , J=74 , K=75 , N=78 , R=82 , S=83 , T=84 , ' '=32 , X=88 

        if type == 'typeB':
            type_int = ctypes.c_int8(66) 
        if type == 'typeE':
            type_int = ctypes.c_int8(69) 
        if type == 'typeJ':
            type_int = ctypes.c_int8(74) 
        if type == 'typeK':
            type_int = ctypes.c_int8(75) 
        if type == 'typeN':
            type_int = ctypes.c_int8(78) 
        if type == 'typeR':
            type_int = ctypes.c_int8(82) 
        if type == 'typeS': 
            type_int = ctypes.c_int8(83) 
        if type == 'typeT':
            type_int = ctypes.c_int8(84)      
            
        self.status["set_channel"] = tc08.usb_tc08_set_channel(self.handle, channel, type_int)
        # get minimum sampling interval in ms
        self.status["get_minimum_interval_ms"] = tc08.usb_tc08_get_minimum_interval_ms(self.handle)

    def getvalue(self,channel):
        # get single temperature reading
        temp = (ctypes.c_float * 9)()
        overflow = ctypes.c_int16(0)
        units = tc08.USBTC08_UNITS["USBTC08_UNITS_CENTIGRADE"]
        self.status["get_single"] = tc08.usb_tc08_get_single(self.handle,ctypes.byref(temp), ctypes.byref(overflow), units)
        # assert_pico2000_ok(status["get_single"])
        return temp[channel]
    
    def closeunit(self):
        # close unit
        self.status["close_unit"] = tc08.usb_tc08_close_unit(self.handle)