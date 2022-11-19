from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QIntValidator
import time
import sys

from source.functions import *
from source.visualizer import *
from source.pointcloud import *

# import the EVK source
import EVK.EVK_functions as EVK


class secondwindow(QWidget):
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Indierct LiDAR (ver.2022)')
        self.setWindowIcon(QIcon('data\icon.png'))
        self.setGeometry(300, 300, 500, 500)
        self.setFixedSize(500, 500)
        
        self.initUI()
        self.show()
        
    def initUI(self):
        
        tab1 = self.tab1_settings()
        tab2 = self.tab2_visualizer()
        tab3 = self.tab3_pointcloud()
        
        tabs = QTabWidget()
        tabs.addTab(tab1, 'Settings')
        tabs.addTab(tab2, 'Visualizer')
        tabs.addTab(tab3, 'PointCloud')

        vbox = QVBoxLayout()
        vbox.addWidget(tabs)
        
        self.setLayout(vbox)
        self.load_btn_released()
        self.OperatingM_widget.setCurrentText('Raw phases')
        self.save_btn_released()


#####################################################
#                   Tab1 Settings                   #
#####################################################

    def tab1_settings(self):
        
        grid = QGridLayout()
        
        # Groupbox 1
        groupbox = QGroupBox('MLX75027 Settings')
        main_layout = QFormLayout()

        self.IntT_widget = QLineEdit()
        self.ModF_widget = QLineEdit()
        self.FrameR_widget = QLineEdit() 
        self.IllP_widget = QLineEdit()
        
        self.IntT_widget.setValidator(QIntValidator())
        self.ModF_widget.setValidator(QIntValidator())
        self.FrameR_widget.setValidator(QIntValidator())
        self.IllP_widget.setValidator(QIntValidator())

        # Save & Load Button
        save_cancel_layout = QHBoxLayout()
        save_button = QPushButton("Save")
        cancel_button = QPushButton("Load")
        
        save_button.released.connect(self.save_btn_released)
        cancel_button.released.connect(self.load_btn_released)
        
        save_cancel_layout.addWidget(save_button)
        save_cancel_layout.addWidget(cancel_button)

        main_layout.addRow("Integration Time (us): ", self.IntT_widget)
        main_layout.addRow("Modulation Frequency (MHz): ", self.ModF_widget)
        main_layout.addRow("Frame Rate (FPS): ", self.FrameR_widget)
        main_layout.addRow("Illumination Power (%): ", self.IllP_widget)
        main_layout.addRow("", save_cancel_layout)

        groupbox.setLayout(main_layout)
        grid.addWidget(groupbox, 0, 0)


        # Groupbox 2
        groupbox = QGroupBox('Advanced Settings')
        main_layout = QFormLayout()
        
        self.OutputM_widget = QComboBox()
        self.OperatingM_widget = QComboBox()

        # register addr = 0x8828 / 0 = A-B,  1 = A+B,  2 = A,  3 = B
        self.OutputM_widget.addItem('A-B')
        self.OutputM_widget.addItem('A+B')
        self.OutputM_widget.addItem('A')
        self.OutputM_widget.addItem('B')
        
        # register addr = 0x0004 / 0x0000: distance Amplitude / 0x00C0: raw phases / 0x00D0: distance confidence
        self.OperatingM_widget.addItem('Raw phases')
        self.OperatingM_widget.addItem('Distance Amplitude')
        self.OperatingM_widget.addItem('Distance confidence')
        
        main_layout.addRow("Output Mode: ", self.OutputM_widget)
        main_layout.addRow("Operating Mode: ", self.OperatingM_widget)

        
        groupbox.setLayout(main_layout)
        grid.addWidget(groupbox, 1, 0)
        
        # widget
        widget = QWidget()
        widget.setLayout(grid)
        return widget
    
    def save_btn_released(self):
        print('save')
        self.IntT = int(self.IntT_widget.text())
        self.ModF = int(self.ModF_widget.text())
        self.FrameR = int(self.FrameR_widget.text())
        self.IllP = int(self.IllP_widget.text())
        self.OutputM = Outputmode2value(self.OutputM_widget.currentText())
        self.OperatingM = Operatingmode2value(self.OperatingM_widget.currentText())
        
        error = False
        
        # Check the input value range
        if self.IntT >1000 or self.IntT <1:
            QMessageBox.warning(self,'Warning','Please enter an integration time between 1us and 1000us')
            error = True

        if self.ModF <4 or self.ModF >100:
            QMessageBox.warning(self,'Warning','Please enter a modulation frequency between 4Mhz and 100MHz')
            error = True

        if self.FrameR <1 or self.FrameR >15:
            QMessageBox.warning(self,'Warning','Please enter a frame rate between 1 and 15')
            error = True

        if self.IllP <0 or self.IllP >100:
            QMessageBox.warning(self,'Warning','Please enter an illumination power between 0% and 100%')
            error = True

        if self.OutputM <0 and self.OutputM >3:
            QMessageBox.warning(self,'Warning','Please enter a valid output mode ')
            error = True
            
        if error:
            return 0
        
        # Write register
        EVK.ChangeMLX75027Settings(self.IntT, self.ModF, self.FrameR, self.IllP, self.OutputM)
        EVK.writeRegister(0x0004, self.OperatingM)  
    
    def load_btn_released(self):
        print('Load')
        
        # Load register from MLX75027
        self.IntT_widget.setText(str(EVK.readRegister(0x0005)))
        self.ModF_widget.setText(str(int(EVK.readRegister(0x0009)/100)))
        self.FrameR_widget.setText(str(EVK.readRegister(0x000A)))
        self.IllP_widget.setText(str(EVK.readRegister(0x0159)))
        self.OutputM_widget.setCurrentText(Value2outputmode(EVK.readRegister(0x8828)))
        self.OperatingM_widget.setCurrentText(Value2operatingmode(EVK.readRegister(0x0004)))
        
        
#####################################################
#                  Tab2 Visualizer                  #
#####################################################

    def tab2_visualizer(self):
        
        btn = QPushButton('Visualizer')
        btn.setFixedSize(300,80)
        font = btn.font()
        font.setPointSize(18)
        font.setFamily('Arial')
        btn.setFont(font)
        
        btn.released.connect(self.vis_btn_released)
        
        # HBOX
        hbox = QHBoxLayout()
        hbox.addWidget(btn)
        
        # VBOX
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        
        # widget
        widget = QWidget()
        widget.setLayout(vbox)
        
        return widget
    
    def vis_btn_released(self):
        time.sleep(3)
        self.visualizer = imager(self)
        self.hide
    
    
#####################################################
#                  Tab3 PointCloud                  #
#####################################################

    def tab3_pointcloud(self):
        
        btn = QPushButton('PointCloud')
        btn.setFixedSize(300,80)
        font = btn.font()
        font.setPointSize(18)
        font.setFamily('Arial')
        btn.setFont(font)
        
        btn.released.connect(self.pcd_btn_released)
        
        # HBOX
        hbox = QHBoxLayout()
        hbox.addWidget(btn)
        
        # VBOX
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        
        # widget
        widget = QWidget()
        widget.setLayout(vbox)
        
        return widget
    
    def pcd_btn_released(self):
        self.pointcloud = pointcloud(self)
        self.hide
        
              
        
if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = secondwindow()
   sys.exit(app.exec_())