# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHeaderView, QTableWidgetItem, QMessageBox
from PySide6.QtCore import QFile, Qt, Signal, Slot
from PySide6.QtUiTools import QUiLoader
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import (FigureCanvasQTAgg,NavigationToolbar2QT)
from dwflib.DWF import DWF
from dwflib.dataprocess import signal_process, results_cal, rhofvu
import numpy as np
import threading
import timeit
from datetime import datetime

class Widget(QWidget):
    message = Signal(str)
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = self.load_ui()
        self.line, self.axes, self.fig = self.load_chart()
        self.load_table()
        self.dwf = DWF()
        self.timevec = []
        self.arData = []
        self.vch2 = []
        self.gain = []
        self.nAverage = []
        self.temp = []
        self.sample = ''
        self.bSweep = False
        self.running = False
        self.recording = False
        self.createfolder = True
        self.pause = False
        self.flag = False
        self.runT = threading.Thread(target=None, args=())
        self.recordT = threading.Thread(target=None, args=())
        # self.stop = threading.Event()
        # self.stop.set()

    def load_ui(self):
        loader = QUiLoader()
        path = Path(__file__).resolve().parent / "form.ui"
        ui_file = QFile(path)
        ui_file.open(QFile.ReadOnly)
        ui = loader.load(ui_file, self)
        ui_file.close()
        ui.comboBox_freq.addItems(["1.5e6","2.0e6","2.5e6"])
        ui.comboBox_amp.addItems(["0.5","0.6","0.7","0.8","0.9","1"])
        ui.comboBox_cycles.addItems(["3","5","10"])
        ui.comboBox_avg.addItems(["1","40","100","400"])
        ui.comboBox_txgain.addItems(["Low","Medium","High","Very High"])
        ui.comboBox_rxgain.addItems(["Low","Medium","High","Very High"])
        return ui

    def load_chart(self):
        matplotlib.use('QTAgg')
        fig, axes = plt.subplots(ncols=1)
        self.protime = np.arange(0,8129)/50
        self.prosig = 0*self.protime
        line, = axes.plot(self.protime,self.prosig, 'b-', linewidth=1)
        axes.set_ylim([-25,25])
        axes.set_xlabel('Time,microseconds')
        axes.set_ylabel('Amplitude,volts')
        canvas = FigureCanvasQTAgg(fig)
        toolbar = NavigationToolbar2QT(canvas,self.ui)
        # self.ui.pushButton.clicked.connect(lambda: print("clicked"))
        layout = QVBoxLayout(self)
        layout.addWidget(canvas,Qt.AlignCenter)
        layout.addWidget(toolbar,Qt.AlignCenter)
        self.ui.tabSignal.setLayout(layout)
        return line, axes, fig

    def load_table(self):
        self.ui.tableData.setColumnCount(4)
        self.ui.tableData.setHorizontalHeaderLabels(["Timestamp", "Temperature", "PT1000 Voltage", "Relative Amplitude"])
        header = self.ui.tableData.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

    def clear_table(self):
        self.ui.tableData.clearContents()
        self.ui.tableData.setRowCount(0)

    def update_table(self,timestp,temp,pt1000,atten):
        rowIndex = self.ui.tableData.rowCount()
        item1 = QTableWidgetItem(timestp)
        item2 = QTableWidgetItem(temp)
        item3 = QTableWidgetItem(pt1000)
        item4 = QTableWidgetItem(atten)
        self.ui.tableData.insertRow(rowIndex)
        itemlist = [item1,item2,item3,item4]
        for item in itemlist:
            item.setTextAlignment(Qt.AlignCenter)
            self.ui.tableData.setItem(rowIndex,itemlist.index(item),item)

    @Slot(str)
    def showDialogWarning(self,message):
        QMessageBox.warning(self, 'Warning', message, QMessageBox.Ok)

    def showDialogCritical(self,message):
        QMessageBox.critical(self, 'Error', message, QMessageBox.Ok)

    def get_settings(self):
        val1 = self.ui.comboBox_freq.currentText()
        val2 = self.ui.comboBox_amp.currentText()
        val3 = self.ui.comboBox_cycles.currentText()
        val4 = self.ui.comboBox_avg.currentText()
        val5 = self.ui.comboBox_txgain.currentText()
        val6 = self.ui.comboBox_rxgain.currentText()

        if val1 == '':
            self.showDialogCritical("Error","Please Enter Frequency!")
            return
        if val2 == '':
            self.showDialogCritical("Error","Please Enter Amplitude!")
            return
        if val3 == '':
            self.showDialogCritical("Error","Please Enter Cycles!")
            return
        if val4 == '':
            self.showDialogCritical("Error","Please Enter Averages!")
            return
        if val5 == '':
            self.showDialogCritical("Error","Please Enter Tx Gain!")
            return
        if val6 == '':
            self.showDialogCritical("Error","Please Enter Rx Gain!")
            return

        if val5 == "Low":
            nTxGain1 = 0
            nTxGain2 = 0
        if val5 == "Medium":
            nTxGain1 = 1
            nTxGain2 = 0
        if val5 == "High":
            nTxGain1 = 0
            nTxGain2 = 1
        if val5 == "Very High":
            nTxGain1 = 1
            nTxGain2 = 1
        if val6 == "Low":
            nRxGain1 = 0
            nRxGain2 = 0
        if val6 == "Medium":
            nRxGain1 = 1
            nRxGain2 = 0
        if val6 == "High":
            nRxGain1 = 0
            nRxGain2 = 1
        if val6 == "Very High":
            nRxGain1 = 1
            nRxGain2 = 1

        self.dwf.nFreq = float(val1)
        self.dwf.nAmplitude = float(val2)
        self.dwf.nCycles = int(val3)
        self.nAverage = int(val4)
        self.gain = [nRxGain1,nRxGain2,nTxGain1,nTxGain2]

    def update_plot(self,xdata,ydata):
        self.line.set_xdata(xdata*1e6)
        self.line.set_ydata(ydata)

        if self.bSweep:
            self.axes.set_title(str(round(self.temp,3))+u'\N{DEGREE SIGN}C',fontsize = 10)
        else:
            self.axes.set_title('')

        self.fig.canvas.draw()
        # self.fig.canvas.flush_events()

    def open_ad2(self):
        self.get_settings()
        # try:
        if self.dwf.opendevice():
            self.dwf.setgain(self.gain)
            self.ui.label_Status.setText("Status: Connected!")
            self.flag = False
        else:
            self.running = False
            self.flag = True
            self.ui.label_Status.setText("Status: Not Connected...")
            # # self.showDialogWarning('Device Not Found!')
        # except Exception as e:
        #     print(e)

    def thread_run(self):

        protime = []
        prosig = []

        while True:
            # if self.stop.isSet():
            #     break
            # else:
            if self.running:
                try:
                    self.dwf.Filt = self.ui.checkBoxFilter.isChecked()
                    self.bSweep = self.ui.checkBoxSweep.isChecked()
                    # SNR_tick  = xb3.get()
                    # get temperature pre-data collection
                    temp1 = self.dwf.gettemp()

                    # collect data
                    [self.timevec, self.arData, self.vch2] = self.dwf.getsig2(self.nAverage)

                    # get temperature post-data collection and average
                    temp2 = self.dwf.gettemp()
                    self.temp = (temp1 + temp2) / 2

                    if self.dwf.Filt:
                        [protime,prosig] = signal_process(self.timevec,self.arData,self.dwf.Filt,False,self.dwf.nFreq)
                    else:
                        [protime,prosig] = [self.timevec,self.arData]

                    self.update_plot(protime,prosig)

                except Exception as e:
                    print(e)
                    self.running = False
                    break
                except KeyboardInterrupt:
                    self.running = False
                    break
            else:
                break

    def thread_record(self):
        count = 0
        atten_new = 0
        tic = timeit.default_timer()
        self.pause = False
        while True:
            if self.recording:
                self.ui.label_Status.setText("Status: Recording...")
                try:
                    if self.bSweep == True & self.pause == True:
                        toc = timeit.default_timer()
                        delta_t = toc - tic
                        if delta_t < self.dwf.tPause:
                            continue

                    if self.createfolder:
                        # file save path
                        # dirDefault = os.path.dirname(os.path.realpath(__file__))
                        if getattr(sys, 'frozen', False):
                            dirDefault = os.path.dirname(sys.executable)
                        else:
                            dirDefault = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
                        os.chdir(dirDefault)
                        dirName = 'data/'+datetime.today().strftime('%d-%m-%Y')
                        if not os.path.exists(dirName):
                            os.makedirs(dirName)
                            print("Directory",dirName,"created")
                        else:
                            print("Directory",dirName,"already exists")
                        os.chdir(dirName)
                        self.createfolder = False
                        self.clear_table()

                    # data processing (butterworth filter and up-sampling)
                    temp = self.temp
                    vch2 = self.vch2
                    arData = self.arData
                    timevec = self.timevec
                    (protimevec, proData) = signal_process(timevec, arData, self.dwf.Filt, self.dwf.UpSamp, self.dwf.nFreq)

                    # calculation for acoustic properties (velocity of sound and attenuation of sound)
                    toa1, toa2, peak1, peak2, vel, atten = results_cal(protimevec, proData, self.dwf.nFreq, self.dwf.nCycles, self.dwf.tCutoff)
                    (rhof, visc) = rhofvu(temp, self.sample)
                    # print('Temperature: '+str(temp))
                    # print('Sample: '+self.sample)
                    # print('Density: '+str(rhof)+' Viscosity: '+str(visc))

                    if not atten_new == atten:
                        atten_new = atten
                    else:
                        continue

                    # save signal and data collected, label with sample name, frequency, voltage and gain settings.
                    # print("Saving data...")
                    with open('Data_'+self.sample+'_'+str(self.dwf.nAmplitude)+'v_'+str(self.dwf.nFreq)+'hz_'+str(self.gain)+'.csv', 'a') as f2_append:
                        # np.savetxt(f2_append, np.c_[temp, vch2, atten], fmt=('%.18e,%.18e,%.18e'), delimiter=',')
                        np.savetxt(f2_append, np.c_[temp,toa1,toa2,peak1,peak2,vch2,atten,rhof,visc], fmt=('%.18e,%.18e,%.18e,%.18e,%.18e,%.18e,%.18e,%.18e,%.18e'), delimiter=',')
                    with open('Signal_'+self.sample+'_'+str(self.dwf.nAmplitude)+'v_'+str(self.dwf.nFreq)+'hz_'+str(self.gain)+'.csv','a') as f1_append:
                        np.savetxt(f1_append,[arData],delimiter = ',')

                    # print results in terminal
                    # self.dwf.printRow(temp, vch2, atten)
                    now = datetime.now()  # current date and time
                    strDate = now.strftime('%d-%m-%YT%H-%M-%S')
                    strTemp = ("%4.3f") % temp
                    strPt1000 = ("%4.5f") % vch2
                    strAtten = ("%4.3f") % atten
                    self.update_table(strDate,strTemp,strPt1000,strAtten)

                    # define break condition if temperature sweep (e.g. temperature drops to below min of range)
                    if self.bSweep == True:
                        tic = timeit.default_timer()
                        self.pause = True
                        # temp = 20
                        if temp < self.dwf.temp_min:
                            print("Data collection complete!")
                            self.recording = False
                            self.createfolder = True
                            self.ui.label_Status.setText("Status: Connected!")
                            self.message.emit("Data collection complete!")
                            # self.emit(self,SIGNAL("record_completed"))
                            # messagebox.showinfo('Info','Data Collection Completed!')
                            break

                    if self.bSweep == False:
                        count += 1
                        # collect 30 signal if no temperature sweep
                        if count == 30:
                            print("Data collection complete!")
                            self.recording = False
                            self.createfolder = True
                            self.ui.label_Status.setText("Status: Connected!")
                            self.message.emit("Data collection complete!")
                            # messagebox.showinfo('Info','Data Collection Completed!')
                            break

                except Exception as e:
                    print(e)
                    self.recording = False
                    self.createfolder = True
                    self.ui.label_Status.setText("Status: Connected!")
                    break
                except KeyboardInterrupt:
                    self.recording = False
                    self.createfolder = True
                    self.ui.label_Status.setText("Status: Connected!")
                    break

            else:
                break

    def run_test(self):
        # if self.stop.isSet():
        #     self.stop.clear()
        # else:
        #     self.stop.set()
        #     self.runT.join(timeout=2)
        # self.runT = threading.Thread(target=self.thread_run, args=())
        # self.runT.start()

        if  self.recording == True:
            self.showDialogCritical('Recording!')
            return

        if self.running == True:
            self.running = False
            if self.runT.is_alive():
                self.runT.join()
            self.dwf.closedevice()
        self.open_ad2()

        if self.flag:
            self.showDialogCritical('Device Not Found!')
            return

        self.running = True
        self.runT = threading.Thread(target=self.thread_run, args=())
        self.runT.start()

        # if self.running == True:
        #     self.running = False
        #     # self.dwf.closedevice()
        #     if self.runT.is_alive():
        #         self.runT.join()
        # self.runT = threading.Thread(target=self.thread_run, args=())
        # self.running = True
        # self.runT.start()

        # self.timer = QTimer()
        # self.timer.setInterval(100)
        # self.timer.timeout.connect(lambda: self.update_plot(self.protime,self.prosig))
        # self.timer.start()

    def stop_test(self):
        if self.running == True:
            self.running = False
            # self.stop.set()
            if self.runT.is_alive():
                self.runT.join()
            self.dwf.closedevice()

    def run_record(self):
        self.sample = self.ui.lineEditDataLabel.text()
        if  self.recording == True:
            self.showDialogCritical('Already recording!')
            return
        elif self.sample == '':
            self.showDialogCritical('Enter Data Label!')
            return
        self.recording = True
        self.recordT = threading.Thread(target=self.thread_record, args=())
        self.recordT.start()

    def stop_record(self):
        if self.recording == True:
            self.recording = False
            if self.recordT.is_alive():
                self.recordT.join()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Quit', 'Are you sure you want to quit?',
        QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.stop_record()
            self.stop_test()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Waveguide Tester Qt")
    widget = Widget()
    widget.show()
    widget.ui.pushButtonRun.clicked.connect(widget.run_test)
    widget.ui.pushButtonRecord.clicked.connect(widget.run_record)
    widget.message.connect(widget.showDialogWarning)
    # widget.ui.pushButtonRun.clicked.connect(lambda: widget.showDialogInfo("Cannot find device!"))
    sys.exit(app.exec())
