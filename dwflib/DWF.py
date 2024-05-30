#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
	Python module for ViscoPro software, defining all API functions used for calibration/monitoring mode. 
	Author:Jinrui Huang
	Revision:16-01-2024
	Requires:Python 3.5, Digilent WaveForms SDK, PicoSDK
 
"""

import sys
import time
from datetime import datetime
import numpy as np
import os
from dwflib.dataprocess import *
from dwflib.dwfconstants import *
from picolib.PicoPT104 import PT104
from picolib.PicoTC08 import PicoTC08

# load DWF library
if sys.platform.startswith("win"):
	dwf = cdll.dwf
elif sys.platform.startswith("darwin"):
	dwf = cdll.LoadLibrary("/Library/Frameworks/dwf.framework/dwf")
else:
	dwf = cdll.LoadLibrary("libdwf.so")

class DWF(object):

	def __init__(self):

		self.h = c_int()
		self.sts = c_byte()

		self.gain = [[0,1,0,0]] # amplifier gain for the test
		self.freq = [1.5e6,2e6,2.5e6] # ultrasonic signal frequency for the test
		self.volt = [0.5] # ultrasonic signal amplitude for the test
		self.dirCal = '/home/piotr/SmartVisco/DWF/data' # the directory for data storage
		# self.running = True
		# self.recording = False
		# self.createfolder = False

		# The following are the default values for the inputs of the API functions.
		self.nWG = 1  # wave generator channel to use
		self.nCH = 1  # oscilloscope channel to use
		self.nFreq = 2e6  # transmitted wave frequency in Hz
		self.nAmplitude = 0.5  # transmitted wave amplitude in V
		self.nCycles = 5  # number of cycles per signal
		self.nSampFreq = 50e6  # sampling frequency in Hz, e.g. how many data points collected per second
		self.nRecLength = 8192  # length of recording, e.g. how many data points to collect	
		self.tCutoff = 1.10e-4 # starting point in the time domain to identify the reflections in the signal
		self.tc08cn = 1 # channel to use if tc08 is used
		self.tc08tp = 'typeT' # thermistor type for tc08
		self.PicoSN = 'GQ840/141' # serial number for pt104
		self.nPT = 1  # channel to use if pt104 is used
		self.tPT = 2  # time for pt104 to convert output in seconds, increase if reads zero
		self.typePT = 1  # 1 for PT100 and 2 for PT100 used with pt104
		self.tPause = 60  # time interval between data collection in seconds
		self.temp_min = 25  # minimum of temperature for calibration in degrees Celsius
		self.temp_max = 150  # maximum of temperature for calibration in degrees Celsius
		self.order_temp = 2  # 2nd order polynomial fit for temperature
		self.order_atten = 5  # 5th order polynomial fit for attenuation
		# self.order_vel = 2  # 2nd order polymonial fit for velocity correction
		# self.nAmpMax = 20  # amplifier signal max output in V, must be < oscilloscope range (25V)
		self.Filt = True # set True to use digital filter for the signal 
		self.UpSamp = True # set True to use up sampling for the signal
		# constants required for calculation of temperature and viscosity
		# self.H = 0.00048  # thickness of the waveguide in m
		self.H = 0.0005  # thickness of the waveguide in m		
		self.rhos = 2690  # density of the waveguide in kg/m^3
		self.G = 26.34e9  # shear modulus of the waveguide in Pa
		self.rhof = 850  # assumed density of the oil sample in kg/m^3
		self.CalSample = 'S3S'  # name of calibration sample, e.g. 'S3S' for Paragon Viscosity Standard S3S

	def opendevice(self):
		# This function opens the AD2, configure the waveform generator to send a 5-cycle tone-burst at 2.0MHz frequency and 5V peak amplitude.
		print("Loading amplifier gain setting...")
		# go to the desired directory and create one if not exists
		if not os.path.exists(self.dirCal):
			os.makedirs(self.dirCal)
		os.chdir(self.dirCal)
		# create gain settings csv file if not found
		if not os.path.isfile(self.dirCal + '/GainSet.csv'):
			with open('GainSet.csv', 'w') as f1_write:
				np.savetxt(f1_write, [1, 1, 1, 1], fmt='%i', delimiter=',')
			print("Not found... Max gain used...")
		# load gain settings csv file
		with open('GainSet.csv', 'r') as f1_read:
			Gain = np.loadtxt(f1_read, dtype='int', delimiter=',')

		# calculate the pulse length and the repeat frequency
		nLag = int(500)
		nPulse = int(self.nSampFreq * self.nCycles / self.nFreq)
		nTrigger = nPulse + 2 * nLag
		hzFreq = self.nSampFreq / nTrigger

		# define vectors for data
		Pulse = (c_double * nPulse)()
		rgdSamples = (c_double * nTrigger)()

		# define arbitrary waveform, values should be normalised to +-1
		for i in range(0, len(Pulse)):
			Pulse[i] = np.sin(1.0 * i / nPulse * self.nCycles * 2 * np.pi) * 0.5 * (
					1 - np.cos(2 * np.pi * 1.0 * i / (nPulse - 1)))
		for i in range(0, len(Pulse)):
			rgdSamples[nLag + i] = Pulse[i]

		# # display version of hardware
		# version = create_string_buffer(16)
		# dwf.FDwfGetVersion(version)
		# print("DWF Version: "+str(version.value))

		# discover and open device
		print("Opening AD2...")
		dwf.FDwfDeviceOpen(c_int(-1), byref(self.h))
		# # 2nd configuration for Analog Disocovery with 16k analog-in buffer
		# dwf.FDwfDeviceConfigOpen(c_int(-1), c_int(1), byref(self.h))

		if self.h.value == hdwfNone.value:
			szError = create_string_buffer(512)
			dwf.FDwfGetLastErrorMsg(szError)
			print("Error: Failed To Open AD2! \n" + str(szError.value))
			return False
			# quit()
		else:  
			# define channels to send signal
			channel = c_int(self.nWG - 1)  # 0 for channel 1
			channel2 = c_int(self.nWG)  # 1 for channel 2
			# configure waveform generator
			# Awg 1 Carrier
			dwf.FDwfAnalogOutNodeEnableSet(self.h, channel, AnalogOutNodeCarrier, c_bool(True))  # turn on AFG
			dwf.FDwfAnalogOutNodeFunctionSet(self.h, channel, AnalogOutNodeCarrier,
											funcCustom)  # turn on customisation of waveform
			dwf.FDwfAnalogOutNodeDataSet(self.h, channel, AnalogOutNodeCarrier, rgdSamples,
										c_int(nTrigger))  # load defined waveform
			dwf.FDwfAnalogOutNodeFrequencySet(self.h, channel, AnalogOutNodeCarrier,
											c_double(hzFreq))  # set repeating frequency
			dwf.FDwfAnalogOutNodeAmplitudeSet(self.h, channel, AnalogOutNodeCarrier,
											c_double(self.nAmplitude))  # set amplitude
			dwf.FDwfAnalogOutRunSet(self.h, channel, c_double(1.0 / hzFreq))  # run for 1 period for pulse only
			dwf.FDwfAnalogOutWaitSet(self.h, channel, c_double(
				5 * self.nRecLength / self.nSampFreq))  # hold on till at least one recording period (This needs to be properly defined)
			dwf.FDwfAnalogOutRepeatSet(self.h, channel, c_int())  # repeat continuously until device closed
			dwf.FDwfDeviceTriggerSet(self.h, c_int(0),
									trigsrcAnalogOut1)  # activate t1 when w1 is activated, 0 = T1 , 7 = trigsrcAnalogOut
			dwf.FDwfAnalogOutConfigure(self.h, channel, c_bool(True))  # activate w1

			# Awg 2 Carrier
			dwf.FDwfAnalogOutNodeEnableSet(self.h, channel2, AnalogOutNodeCarrier, c_bool(True))  # turn on AFG	
			dwf.FDwfAnalogOutNodeFunctionSet(self.h, channel2, AnalogOutNodeCarrier,
											funcDC)  # turn on DC waveform
			dwf.FDwfAnalogOutNodeAmplitudeSet(self.h, channel2, AnalogOutNodeCarrier,
											c_double(1))  # set amplitude to 1
			dwf.FDwfAnalogOutNodeOffsetSet(self.h, channel2, AnalogOutNodeCarrier,
											c_double(4))  # set offset to 4 
			dwf.FDwfAnalogOutRunSet(self.h, channel2, c_double(1.0 / hzFreq))  # run for 1 period for pulse only
			dwf.FDwfAnalogOutRepeatSet(self.h, channel2, c_int())  # repeat continuously until device closed
			dwf.FDwfAnalogOutConfigure(self.h, channel2, c_bool(True))  # activate w2		

			# define digital IO channels (DIO) to send triggers to set transmit/receive amplifier gain
			# set up DIO0
			dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(0), c_int(Gain[0]),
											c_int(Gain[0]))  # channel number, high or low represented by one or zero
			dwf.FDwfDigitalOutEnableSet(self.h, c_int(0), c_int(1))  # channel number, integer 1 to turn on
			# set up DIO1
			dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(1), c_int(Gain[1]), c_int(Gain[1]))  # channel number, high or low represented by one or zero
			dwf.FDwfDigitalOutEnableSet(self.h, c_int(1), c_int(1))  # channel number, integer 1 to turn on
			# set up DIO2
			dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(2), c_int(Gain[2]), c_int(Gain[2]))  # channel number, high or low represented by one or zero
			dwf.FDwfDigitalOutEnableSet(self.h, c_int(2), c_int(1))  # channel number, integer 1 to turn on
			# set up DIO3
			dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(3), c_int(Gain[3]), c_int(Gain[3]))  # channel number, high or low represented by one or zero
			dwf.FDwfDigitalOutEnableSet(self.h, c_int(3), c_int(1))  # channel number, integer 1 to turn on

			# activate DIO channels
			dwf.FDwfDigitalOutConfigure(self.h, c_int(1))

			# define oscilloscope channels to receive signal
			channel = c_int(self.nCH - 1)  # 0 for channel 1
			channel2 = c_int(self.nCH)  # 1 for channel 2
			# configure oscilloscope
			# print("Setting up acquisition and trigger...")
			dwf.FDwfAnalogInFrequencySet(self.h, c_double(self.nSampFreq))  # acquisition sampling frequency
			dwf.FDwfAnalogInBufferSizeSet(self.h, c_int(self.nRecLength))  # acquisition buffer size, number of points per acquisition
			dwf.FDwfAnalogInChannelEnableSet(self.h, channel, c_bool(True))  # activate channel 1
			dwf.FDwfAnalogInChannelRangeSet(self.h, channel,
											c_double(25))  # acquisition amplitude range set to 20V peak to peak for channel 1
			dwf.FDwfAnalogInChannelEnableSet(self.h, channel2, c_bool(True))  # activate channel 2
			dwf.FDwfAnalogInChannelRangeSet(self.h, channel2,
											c_double(25))  # acquisition amplitude range set to 20V peak to peak for channel 2

			# set up trigger (location in signal to record data)
			dwf.FDwfAnalogInTriggerAutoTimeoutSet(self.h, c_double(0))  # disable auto trigger
			dwf.FDwfAnalogInTriggerSourceSet(self.h, trigsrcAnalogOut1)  # trigger when w1 is active
			dwf.FDwfAnalogInTriggerTypeSet(self.h, trigtypeEdge)  # trigger type - edge
			dwf.FDwfAnalogInTriggerConditionSet(self.h, trigcondRisingPositive)  # trigger type - rising positive edge
			dwf.FDwfAnalogInTriggerChannelSet(self.h, channel)  # ch1 linked to trigger
			dwf.FDwfAnalogInTriggerLevelSet(self.h, c_double(0))  # trigger level 0V
			dwf.FDwfAnalogInTriggerHysteresisSet(self.h, c_double(0.5))  # trigger hysteresis 0.5V
			dwf.FDwfAnalogInTriggerPositionSet(self.h, c_double(
				(self.nRecLength - 1) / self.nSampFreq / 2))  # set trigger position to half the recording window

			# wait at least 2 seconds with Analog Discovery for the offset to stabilize, before the first reading after device open or offset/range change
			time.sleep(2)

			# start data acquisitions
			# print("Starting repeated acquisitions...")
			dwf.FDwfAnalogInConfigure(self.h, c_bool(False), c_bool(True))  # activate oscilloscope channels
			print("AD2 initialsed!")
			return True

	def setgain(self, Gain):
		# define digital IO channels (DIO) to send triggers to set transmit/receive amplifier gain
		# set up DIO0
		dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(0), c_int(Gain[0]),
										 c_int(Gain[0]))  # channel number, high or low represented by one or zero
		dwf.FDwfDigitalOutEnableSet(self.h, c_int(0), c_int(1))  # channel number, integer 1 to turn on
		# set up DIO1
		dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(1), c_int(Gain[1]), c_int(Gain[1]))  # channel number, high or low represented by one or zero
		dwf.FDwfDigitalOutEnableSet(self.h, c_int(1), c_int(1))  # channel number, integer 1 to turn on
		# set up DIO2
		dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(2), c_int(Gain[2]), c_int(Gain[2]))  # channel number, high or low represented by one or zero
		dwf.FDwfDigitalOutEnableSet(self.h, c_int(2), c_int(1))  # channel number, integer 1 to turn on
		# set up DIO3
		dwf.FDwfDigitalOutCounterInitSet(self.h, c_int(3), c_int(Gain[3]), c_int(Gain[3]))  # channel number, high or low represented by one or zero
		dwf.FDwfDigitalOutEnableSet(self.h, c_int(3), c_int(1))  # channel number, integer 1 to turn on

		# activate DIO channels
		dwf.FDwfDigitalOutConfigure(self.h, c_int(1))

	def getsig(self, nAverage):
		# To get a signal with n number of acquisition (100 by default), higher nAverage for better SNR but will slow down measurements
		# define vectors for data
		rxData = (c_double * self.nRecLength)()
		arData = (c_double * self.nRecLength)()
		timevec = (c_double * self.nRecLength)()

		# print("Collecting signal...")
		for iTrigger in range(nAverage):
			# new acquisition is started automatically after done state
			while True:
				dwf.FDwfAnalogInStatus(self.h, c_bool(True), byref(self.sts))
				# print(self.sts.value)
				# print(DwfStateDone.value)
				if self.sts.value == DwfStateDone.value:
					break
				time.sleep(0.001)
			# define channel to receive data
			channel = c_int(self.nCH - 1)
			# pass data to vector
			dwf.FDwfAnalogInStatusData(self.h, channel, rxData, self.nRecLength)  # get channel 1 data
			# overlapping data
			if iTrigger == 0:
				arData = rxData
			else:
				arData = np.add(arData, rxData)
		# averaging data
		arData = np.divide(arData, nAverage)
		# get time vector
		timevec = np.arange(0, self.nRecLength / self.nSampFreq, 1 / self.nSampFreq)

		return timevec, arData
	
	def getsig2(self, nAverage):
		# To get a signal with n number of acquisition (100 by default), higher nAverage for better SNR but will slow down measurements
		# Including channel 2 for voltage reading from pt1000
		# define vectors for data
		rxData1 = (c_double * self.nRecLength)()
		arData1 = (c_double * self.nRecLength)()
		rxData2 = (c_double * self.nRecLength)()
		arData2 = (c_double * self.nRecLength)()		
		timevec = (c_double * self.nRecLength)()

		# print("Collecting signal...")
		for iTrigger in range(nAverage):
			# new acquisition is started automatically after done state
			while True:
				dwf.FDwfAnalogInStatus(self.h, c_bool(True), byref(self.sts))
				# print(self.sts.value)
				# print(DwfStateDone.value)
				if self.sts.value == DwfStateDone.value:
					break
				time.sleep(0.001)
			# define channel to receive data
			channel = c_int(self.nCH - 1)
			channel2 = c_int(self.nCH)
			# pass data to vector
			dwf.FDwfAnalogInStatusData(self.h, channel, rxData1, self.nRecLength)  # get channel 1 data
			dwf.FDwfAnalogInStatusData(self.h, channel2, rxData2, self.nRecLength)  # get channel 2 data
			# overlapping data
			if iTrigger == 0:
				arData1 = rxData1
				arData2 = rxData2
			else:
				arData1 = np.add(arData1, rxData1)
				arData2 = np.add(arData2, rxData2)
		# averaging data
		arData1 = np.divide(arData1, nAverage)
		arData2 = np.divide(arData2, nAverage)
		# get time vector
		timevec = np.arange(0, self.nRecLength / self.nSampFreq, 1 / self.nSampFreq)

		return timevec, arData1, np.mean(arData2)	

	# def gettemp(self):
	# 	# Set up temperature logger and get temperature from channel specified
	# 	# initialise and open PT104
	# 	pt104 = PT104()
	# 	pt104.openunit(self.PicoSN)
	# 	if pt104.handle == 0:
	# 		print("Error: Temperature Logger Not Found!")
	# 		quit()
	# 	else:
	# 		pt104.setmain()
	# 		# print("nPT: %d, typePT: %d, tPT: %d" % (self.nPT, self.typePT, self.tPT))
	# 		pt104.setchannel(self.nPT, self.typePT, 4, self.tPT)
	# 		temp = pt104.getvalue(self.nPT)
	# 		pt104.closeunit()

	# 	return temp

	# def gettemp2(self):
	# 	# Set up temperature logger and get temperature from channel specified
	# 	# initialise and open TC08
	# 	tc08 = PicoTC08()
	# 	if tc08.handle == 0:
	# 		print("Error: TC08 Not Found!")
	# 		quit()
	# 	else:
	# 		tc08.openunit(self.tc08cn,self.tc08tp)
	# 		temp = tc08.getvalue(self.tc08cn)
	# 		tc08.closeunit()

	# 	return temp
	
	def gettemp(self):
		# Set up temperature logger and get temperature from channel specified
		# initialise and open PT104
		temp = 0
		temp_pt104 = 0
		temp_tc08 = 0
		try: 
			pt104 = PT104()
			pt104.openunit(self.PicoSN)
			pt104.setmain()
			# print("nPT: %d, typePT: %d, tPT: %d" % (self.nPT, self.typePT, self.tPT))
			pt104.setchannel(self.nPT, self.typePT, 4, self.tPT)
			temp_pt104 = pt104.getvalue(self.nPT)
			pt104.closeunit()
			if not temp_pt104 == 0:
				temp = temp_pt104
			else: 
				tc08 = PicoTC08()
				tc08.openunit(self.tc08cn,self.tc08tp)
				temp_tc08 = tc08.getvalue(self.tc08cn)
				tc08.closeunit()
				if not temp_tc08 == 0:
					temp = temp_tc08
		except Exception as e:
			pass
		
		return temp


	def printSerialHeader(self):
		# Print data header
		BOLD = '\033[1m'
		END = '\033[0m'
		# # Now clear the stream
		os.system('clear')
		print(
			"{}|{:<19}|{:<12}|{:<12}|{:<12}|{}".format(BOLD, 'Date and Time', 'Temperature', 'Voltage', 'Attenuation',
		 											   END))
		print('-' * 59)

	def printRow(self, temp, tof, Peak):
		# Print data in rows
		now = datetime.now()  # current date and time
		strDate = now.strftime('%d-%m-%YT%H-%M-%S')
		strTemp = ("%4.2f") % temp
		strTof = ("%4.5f") % tof
		strPeak = ("%4.5f") % Peak
		print("|{:<19}|{:<12}|{:<12}|{:<12}|".format(strDate, strTemp, strTof, strPeak))
		print('-' * 59)

	def getdata(self, nAverage, sample, bSweep):
		# Collect signal with averages and calculate acoustic properties from it
		# check if data folder exists
		print("Locating folder to store calibration data...")
		if not os.path.exists(self.dirCal):
			print("Error: Folder Not Found!")
			quit()
		else:
			# print("Folder",dirCal,"found")
			os.chdir(self.dirCal)
			print("Data collection initiated...")

			# define vectors for data
			temp = c_double()
			atten = c_double()
			arData = (c_double * self.nRecLength)()
			timevec = (c_double * self.nRecLength)()
			vch2 = c_double()
			peak1 = c_double()
			peak2 = c_double()	
			toa1 = c_double()	
			toa2 = c_double()	

			self.printSerialHeader()
			count = 0

			# loop data collection until conditions are met
			# collect data with multiple frequency, voltage and gain settings as defined
			while True:
				count += 1
				for j in range(len(self.freq)):
					for i in range(len(self.volt)): 
						self.nFreq = self.freq[j]
						self.nAmplitude = self.volt[i]
						self.closedevice()
						self.opendevice()
						for k in range(len(self.gain)):
							self.setgain(self.gain[k])

							# get temperature pre-data collection
							temp = self.gettemp()

							# collect data
							[timevec, arData, vch2] = self.getsig2(nAverage)

							# get temperature post-data collection and average
							temp1 = self.gettemp()				
							temp = (temp + temp1) / 2

							# get density and viscosity data if sample known
							(rhof,visc) = rhofvu(temp,sample)

							# data processing (butterworth filter and up-sampling)
							(protimevec, proData) = signal_process(timevec, arData, self.Filt, self.UpSamp, self.nFreq)

							# calculation for acoustic properties (velocity of sound and attenuation of sound)
							toa1, toa2, peak1, peak2, vel, atten = results_cal(protimevec, proData, self.nFreq, self.nCycles, self.tCutoff)

							# save signal and data collected, label with sample name, frequency, voltage and gain settings. 
							# print("Saving data...")
							with open('Data_'+sample+'_'+str(self.nAmplitude)+'v_'+str(self.nFreq)+'hz_'+str(self.gain[k])+'.csv', 'a') as f2_append:
								# np.savetxt(f2_append, np.c_[temp, vch2, atten], fmt=('%.18e,%.18e,%.18e'), delimiter=',')
								np.savetxt(f2_append, np.c_[temp,toa1,toa2,peak1,peak2,vch2,atten,rhof,visc], fmt=('%.18e,%.18e,%.18e,%.18e,%.18e,%.18e,%.18e,%.18e,%.18e'), delimiter=',')
							with open('Signal_'+sample+'_'+str(self.nAmplitude)+'v_'+str(self.nFreq)+'hz_'+str(self.gain[k])+'.csv','a') as f1_append:
								np.savetxt(f1_append,[arData],delimiter = ',')

							# print results in terminal
							self.printRow(temp, vch2, atten)

				# define break condition if temperature sweep (e.g. temperature drops to below min of range)
				if temp < self.temp_min and bSweep == True:
					print("Data collection complete!")
					break

				# pause between data collection (wait for temperature to change) if temperature sweep
				if bSweep == True:
					time.sleep(self.tPause)

				# collect 30 signal if no temperature sweep
				if count == 30 and bSweep == False: 
					print("Data collection complete!")
					break

	def closedevice(self):
		# This functions closes the AD2
		# define channel to close
		channel = c_int(self.nWG - 1)  # input = channel number -1
		# disconnect device and close it
		dwf.FDwfAnalogOutConfigure(self.h, channel, c_bool(False))
		dwf.FDwfDeviceCloseAll()
		print('AD2 closed!')
