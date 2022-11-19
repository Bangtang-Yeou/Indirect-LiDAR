import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QCoreApplication
from ctypes import *

# import second window
from source.second_window import *

# import the EVK source
import EVK.EVK_functions as EVK


class MyApp(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Indierct LiDAR (ver.2022)')
        self.setWindowIcon(QIcon('data\icon.png'))
        self.setGeometry(300, 300, 350, 200)
        self.setFixedSize(350, 200)
        
        self.initUI()
        self.show()

    def initUI(self):
        
        # HBOX
        hbox1 = QHBoxLayout()
        hbox1.addWidget(self.connect_btn())
        
        hbox2 = QHBoxLayout()
        hbox2.addStretch(1)
        hbox2.addWidget(self.dev_ip_lbl())
        hbox2.addStretch(1)
        hbox2.addWidget(self.dev_ip_qle())
        hbox2.addStretch(1)
        
        # VBOX
        vbox = QVBoxLayout()
        vbox.addStretch(1)   
        vbox.addLayout(hbox1)
        vbox.addStretch(1)
        vbox.addLayout(hbox2)
        vbox.addStretch(1)
        
        self.setLayout(vbox)
        
    def connect_btn(self):
        self.cnt_btn = QPushButton('Connect', self)
        btn = self.cnt_btn
        
        btn.pressed.connect(self.connect_btn_pressed)
        btn.released.connect(self.connect_btn_released)
    
        font = btn.font()
        font.setPointSize(15)
        font.setFamily('Arial')
        btn.setFont(font)
        btn.setFixedSize(300,80)
        
        return btn
    
    def connect_btn_pressed(self):
        self.cnt_btn.setText('Connecting...')
    
    def connect_btn_released(self):
        
        txt = self.ip.text()
        txt = txt.split('.')
        txt = [int(i) for i in txt]
                    
        EVK.initAndOpen(c_uint8(txt[0]),c_uint8(txt[1]),c_uint8(txt[2]),c_uint8(txt[3]))
        
        self.cnt_btn.setText('Connected!')       
        self.second = secondwindow()
        QCoreApplication.instance().quit
        
    
    def dev_ip_lbl(self):
        
        lbl = QLabel('Device IP address:', self)
        
        font = lbl.font()
        font.setPointSize(10)
        font.setFamily('Arial')
        lbl.setFont(font)
        
        return lbl
    
    def dev_ip_qle(self):
        
        self.ip = QLineEdit(self)
        self.ip.setAlignment(Qt.AlignRight)
        self.ip.setInputMask('000.000.000.000;')
        
        # IP address 192.168.0.10
        self.ip.setText('192168  0 10')
        self.ip.setFixedSize(150,20)
        
        return self.ip
            

if __name__ == '__main__':
   app = QApplication(sys.argv)
   ex = MyApp()
   sys.exit(app.exec_())