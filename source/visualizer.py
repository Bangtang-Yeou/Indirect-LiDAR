import cv2
import threading
import sys
import numpy as np
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5 import QtWidgets
from PyQt5 import QtGui

import EVK.EVK_functions as EVK

AmplitudeScale=[0,1000]     # Tune amplitude when used
DistanceScale=[0,3700]      # Tune distance range

px_width = 640
px_height = 480

class imager(QWidget):
    
    def __init__(self, settings):
        super().__init__()
        
        self.OperatingM = settings.OperatingM
        self.ModF = settings.ModF
        self.close = False
        
        self.setWindowTitle('Visualizer')
        self.setWindowIcon(QtGui.QIcon('data\icon.png'))
        self.setGeometry(300, 300, 100, 100)
        
        self.amplitude = QLabel()
        self.distance = QLabel()

        self.initUI()
        self.show()
        self.start()
        
    def initUI(self):
        
        # HBOX
        label1 = QLabel('Amplitude');   label1.setAlignment(Qt.AlignCenter);    label1.setFont(QtGui.QFont('Arial', 14))
        label2 = QLabel('Distance');    label2.setAlignment(Qt.AlignCenter);    label2.setFont(QtGui.QFont('Arial', 14))
    
        hbox1 = QHBoxLayout()
        hbox1.addWidget(label1)
        hbox1.addWidget(label2)
        
        hbox2 = QHBoxLayout()
        hbox2.addWidget(self.amplitude)
        hbox2.addSpacing(20)
        hbox2.addWidget(self.distance)
        
        # VBOX
        vbox = QVBoxLayout()
        vbox.addLayout(hbox1)
        vbox.addSpacing(15)
        vbox.addLayout(hbox2)
        
        self.setLayout(vbox)
    
    def start(self):
        
        while(self.OperatingM==0x0000 or self.OperatingM==0x00D0 or self.OperatingM==0x00C0):
            
            channelStat = EVK.getFrame(3000)
            
            if self.OperatingM==0x0000 and channelStat==0: # distance amplitude
                amplitude = EVK.getAmplitudes()
                distance = EVK.getDistances()
                amp = np.resize(amplitude, (px_height, px_width))
                dist = np.resize(distance, (px_height, px_width))
                
            elif self.OperatingM==0x00C0 and channelStat==0: # raw phases
                p0 = EVK.getChannelData(0)
                p180 = EVK.getChannelData(1)
                p90 = EVK.getChannelData(2)
                p270 = EVK.getChannelData(3)
            
                phase0 = np.resize(p0, (px_height, px_width))
                phase180 = np.resize(p180, (px_height, px_width))
                phase90 = np.resize(p90, (px_height, px_width))
                phase270 = np.resize(p270, (px_height, px_width))
                
                phase0_two_comp=EVK.two_comp(phase0)
                phase180_two_comp=EVK.two_comp(phase180)
                phase90_two_comp=EVK.two_comp(phase90)
                phase270_two_comp=EVK.two_comp(phase270)
                
                I = np.subtract(phase0_two_comp, phase180_two_comp)
                Q = np.subtract(phase270_two_comp, phase90_two_comp)
                
                # Calculating the amplitude
                amp = np.sqrt(np.power(I,2) + np.power(Q,2))
                amp = np.resize(amp, (px_height, px_width))

                # Calculating the distance
                phase = np.arctan2(Q,I)
                unAmbiguousRange = (0.5*299792458)/(self.ModF*1000)
                coefRad = unAmbiguousRange / (2*np.pi)
                dist = (phase+np.pi)*coefRad
                dist = np.resize(dist, (px_height, px_width))
            
            elif self.OperatingM==0x00D0 and channelStat==0: # distance confidence
                distance = EVK.getDistances()
                amplitude = EVK.getConfidences()
                dist = np.resize(distance, (px_height, px_width))
                amp = np.resize(amplitude, (px_height, px_width))
            
            EVK.freeFrame()   
            
            #Rescale and display images
            if(self.OperatingM !=0x00D0): amp=EVK.reScale(amp,AmplitudeScale) #rescale to 8 bit data
            dist=EVK.reScale(dist,DistanceScale) #rescale to 8 bit data
            dist_RGB=cv2.applyColorMap(dist, cv2.COLORMAP_JET)
            
            qImg1 = QtGui.QImage(amp.data, px_width, px_height, QtGui.QImage.Format_Grayscale8)
            pixmap1 = QtGui.QPixmap.fromImage(qImg1)
            
            qImg2 = QtGui.QImage(dist_RGB.data, px_width, px_height, QtGui.QImage.Format_RGB888)
            pixmap2 = QtGui.QPixmap.fromImage(qImg2)
            
            self.amplitude.setPixmap(pixmap1)
            self.distance.setPixmap(pixmap2)
            
            if self.close:
                break
            
            cv2.waitKey(1)
            
    def closeEvent(self, event):
        print('Close window')
        self.close = True
               
        
        
        
        
if __name__ == '__main__':
    class a():
        def __init__(self):
            self.OperatingM = 'Test'
            self.ModF = 40
    settings = a()
    app = QApplication(sys.argv)
    ex = imager(settings)
    sys.exit(app.exec_())
    