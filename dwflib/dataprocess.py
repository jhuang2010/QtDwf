#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Functions for data processing/analysing.
    Author:  Jinrui Huang
    Revision:  16-01-2024
    Requires:  Python 3.5
   
"""

from scipy.signal import find_peaks, butter, lfilter
from scipy.fft import fft, ifft #library structure varies for different versions (fft, ifft are either from scipy.fft or scipy)
from ctypes import *
import numpy as np
import os

# to get the coefficients for Butterworth filter
def butter_bandpass(lowcut, highcut, fs, order): 
    # lowcut, highcut and fs are all in Hz and order is set to 5th order by default but can be changed if necessary
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a
    
# to get the coefficients for the filter and then apply filter to data set
def butter_bandpass_filter(data, lowcut, highcut, fs, order):
    b, a = butter_bandpass(lowcut, highcut, fs, order)
    y = lfilter(b, a, data)
    return y
    
# to find the index of an element in an array that has the closest value to a target
def find(data,value):
    delta = np.zeros(len(data))
    for i in range(len(data)):
        delta[i] = abs(data[i]-value)
    index = np.nonzero(delta==min(delta))
    return index[0][0]
    
def signal_process(timevec, arData, Filter, UpSampling, nFreq): 
    # passing data vector
    proData = arData
    protimevec = timevec
    # from data get sampling frequency and data length
    nSampFreq = 1/(protimevec[1] - protimevec[0])
    nRecLength = len(proData)
    
    # apply filter if set true
    if Filter == True:
        ## 5th order Butterworth filter
        # apply filter to data and return filtered data
        filtData = butter_bandpass_filter(proData, 0.5*nFreq, 1.5*nFreq, nSampFreq, 5)
        proData = filtData
    
    # apply upsampling if set true
    if UpSampling == True:
        ## up-sample to 1GHz (1e9 samples per second)
        nUpSampFreq = 1e9
        fUpSamp = nUpSampFreq/nSampFreq
        nbin = int(fUpSamp*nRecLength)
        upData = np.zeros((nbin,),dtype=complex)
        fftData = fft(proData)
        for i in range(0,int(len(fftData)/2-1)):
            upData[i]=fftData[i]
        for i in range(len(upData),int(len(upData)-(len(fftData)/2)),-1):
            upData[i-1]=fftData[i-(len(upData)-len(fftData))-1]
        upData = np.real(ifft(upData))
        for i in range(len(upData)):
            upData[i]=upData[i]*fUpSamp
        uptimevec = (c_double*nbin)()
        # get time vector
        for i in range(len(upData)):
            uptimevec[i]=i/nUpSampFreq
        protimevec = uptimevec
        proData = upData
    
    return protimevec, proData

# calculation for UT properties from signal, e.g. velocity and attenuation of sound
def results_cal(protimevec,proData,nFreq,nCycles,timecutoff):
    pathlength = 0.015 #pathlength is 0.015m by default, the active area
    fac_thd = 0.1 #threshold for peak identification, 0.1 of the maximum amplitude of reflected signal
    
    # identify the 1st reflection
    nSampFreq = 1/(protimevec[1]-protimevec[0])
    indexcutoff = find(protimevec,timecutoff)
    indexpeaks,_ = find_peaks(proData[indexcutoff:len(proData)],height = fac_thd*max(proData[indexcutoff:]),distance = 3*nSampFreq*nCycles/nFreq)
    indexPeaks = np.zeros(len(indexpeaks),dtype=int)
    for i in range(0,len(indexpeaks)):
        indexPeaks[i] = indexpeaks[i]+indexcutoff
        
    # get the time of arrival for the 1st reflection and index with interpolation
    dT = protimevec[indexPeaks[0]]-protimevec[indexPeaks[0]-1]
    m1 = (proData[indexPeaks[0]]-proData[indexPeaks[0]-1])/dT
    m2 = (proData[indexPeaks[0]+1]-proData[indexPeaks[0]])/dT
    M = (m2-m1)/(2*dT)
    dT3= -1*m1/M
    Int_T1 = dT3+protimevec[indexPeaks[0]-1]
    indexPeak1 = indexPeaks[0]

    # identify the 2nd reflection
    timecutoff2 = protimevec[indexPeak1]+8e-6
    indexcutoff = find(protimevec,timecutoff2)
    indexend = find(protimevec,timecutoff2+3e-6)
    indexpeaks,_ = find_peaks(proData[indexcutoff:indexend],height = fac_thd*max(proData[indexcutoff:indexend]),distance = 3*nSampFreq*nCycles/nFreq)
    indexPeaks = np.zeros(len(indexpeaks),dtype=int)
    for i in range(0,len(indexpeaks)):
        indexPeaks[i] = indexpeaks[i]+indexcutoff

    # get the time of arrival for the 2nd reflection and index with interpolation
    m1 = (proData[indexPeaks[0]]-proData[indexPeaks[0]-1])/dT
    m2 = (proData[indexPeaks[0]+1]-proData[indexPeaks[0]])/dT
    M = (m2-m1)/(2*dT)
    dT3= -1*m1/M
    Int_T2 = dT3+protimevec[indexPeaks[0]-1]
    indexPeak2 = indexPeaks[0]

    # calculate velocity of sound
    TOF = Int_T2 - Int_T1
    vel = 2*pathlength/TOF
    Peak1 = proData[indexPeak1]
    Peak2 = proData[indexPeak2]
    # calculate attenuation/relative amplitude from time domain 
    atten = -1*np.log(Peak1/Peak2)/(2*pathlength)
       
    return Int_T1, Int_T2, Peak1, Peak2, vel, atten

# get density and viscosity of known samples depending on temperature
def rhofvu(temperature,type_sample):

    vu = 0
    rhof = 0

    if type_sample == 'S600':
        p_rhof = [-0.000590440403569401,0.858310527135024]
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3   
        p_nu = [8.09628403884733,7.40047695400422,-0.0624543915524598,0.000175851462028443]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3
    
    if type_sample == 'S60':
        p_rhof = [-0.000636193475467889,0.888793688383073];
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3   
        p_nu = [6.09426031336495,1.93903872633985,-0.0669305189350423,0.000240395048492693]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3
    
    if type_sample == 'N350':
        p_rhof = [-0.000589193302640659,0.885119170795794]
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3  
        p_nu = [7.77453937809582,8.95539541920474,-0.0688531041991786,0.000208226882730463]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3
    
    if type_sample == 'N35':
        p_rhof = [-0.000625639760998825,0.869224566278919];
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3  
        p_nu = [4.78514868686062,8.02834694098624,-0.0479235880493548,0.000142520951173293]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3
    
    if type_sample == 'S3S':
        p_rhof = [-0.000699195896992767,0.834173694916320]
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3  
        p_nu = [1.51274855245423,3.92003348585739,-0.0211267393546965,4.44591968497190e-05]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3

    if type_sample == 'S6S':
        p_rhof = [-0.000672928619079388,0.858228485657105]
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3  
        p_nu = [2.33742852670512,6.95924738065282,-0.0262433861993490,5.92404527473303e-05]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3

    if type_sample == 'S60S':
        p_rhof = [-0.0006154176610978536,0.8740448687350836]
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3  
        p_nu = [5.18619877,12.28192665,-0.04623777,0.00011475]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3

    if type_sample == 'S600S':
        p_rhof = [-0.000581334222815211,0.889698398932622]
        rhof = p_rhof[0]*temperature + p_rhof[1] #in g/cm3  
        p_nu = [8.13224726879007,14.6503135839463,-0.0662712860081032,0.000173827010406862]
        nu = np.exp(p_nu[0])*np.exp(p_nu[1]/temperature+p_nu[2]*temperature+p_nu[3]*temperature**2) #in mPa s
        vu = nu/rhof #in cSt    
        rhof = rhof*1e3 #in kg/m3
    
    return rhof, vu
