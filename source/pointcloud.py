import open3d as o3d
import numpy as np
import cv2
import time

import EVK.EVK_functions as EVK

px_width = 640
px_height = 480
DistanceScale=[0,3700]

xyz_range = np.array([[0, -1700, 3700], [0, 1700, 3700], [2000, -1700, 3700], [2000, 1700, 3700], [1000, 0, 1000]])
# ModF 40MHz 기준

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class PCG:                          # PointCloud Generation from 2D Depth Camera
    def __init__(self, ModF):
        self.s_sz = [4.8, 6.4]      # Sensor size [Vertical,Horizontal] (mm)
        self.px_sz = 0.01           # Sensor pixel size                 (mm)
        self.FOV = 135              # Field of View                     (Degree)
        self.cal_parameter()
        self.ModF = ModF
        
    def set_parameter(self, sensor_sz, sensor_px_sz, FOV):
        self.s_sz = sensor_sz
        self.px_sz = sensor_px_sz
        self.FOV = FOV
        self.cal_parameter()
    
    def cal_parameter(self):
        self.px = (int(self.s_sz[0]/self.px_sz), int(self.s_sz[1]/self.px_sz))
        self.s_d = (self.s_sz[0]**2 + self.s_sz[1]**2)**0.5                 # senosr digonal
        self.VFOV = self.FOV*self.s_sz[0]/self.s_d
        self.HFOV = self.FOV*self.s_sz[1]/self.s_d
        self.fl = self.s_d/(2*np.tan(np.pi*(self.VFOV/360)))                # focus length
        
        
        self.abs_h = np.zeros((self.px[0], self.px[1]))                     # absolute height
        self.abs_w = np.zeros((self.px[0], self.px[1]))                     # absolute width
        self.sign = np.ones((self.px[0], self.px[1]))
        
        for i in range(self.px[0]):
            for j in range(self.px[1]):
                self.abs_h[i, j] = (i+0.5-self.px[0]/2)*self.px_sz
                self.abs_w[i, j] = (j+0.5-self.px[1]/2)*self.px_sz
                if j>320:
                    self.sign[i ,j] = -1
                
        self.px_b = (self.fl**2 + self.abs_w**2)**0.5       # pixel base
        self.px_ang = np.arctan(self.abs_h/self.px_b)       # pixel angle
        self.px_f = (self.px_b**2 + self.abs_h**2)**0.5     # pixel focus
        self.px_bang = np.arcsin(self.fl/self.px_b)         # pixel baseAngle
    
    def depth2pcd(self, arr):
        
        y = -(arr + self.px_f)*self.abs_h/self.px_f
        actual_pxB = (arr**2 + self.px_f**2 - y**2 )**0.5 - self.px_b
        z = np.sin(self.px_bang)*actual_pxB
        x = self.sign*np.cos(self.px_bang)*actual_pxB + self.abs_w
        
        tmp = np.stack((x,y,z), axis=0)
        tmp = np.where((arr < 500*40/self.ModF) | (arr > 3600*40/self.ModF), 0*tmp, tmp)
        tmp = np.swapaxes(tmp, 2,0)
        tmp = np.reshape(tmp, (640*480, 3))
        
        del_list = np.where(np.sum(tmp,axis=1)==0)
        tmp = np.delete(tmp, del_list,axis=0)
        
        return tmp      
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
class pointcloud:
    def __init__(self, settings):
        
        self.OperatingM = settings.OperatingM
        self.ModF = settings.ModF
        
        self.pcg = PCG(self.ModF)
        
        self.vis = o3d.visualization.Visualizer()
        self.vis.create_window()
        
        self.pcd = o3d.geometry.PointCloud()
        self.pcd.points = o3d.utility.Vector3dVector(xyz_range*40/self.ModF)
        self.vis.add_geometry(self.pcd)
        
        # View Control (default : frontview)
        ctr = self.vis.get_view_control()
        ctr.set_up([0,1,0])
        ctr.set_front([0,0,-1])
        ctr.set_lookat([0,0,1])
        
        self.start()
            
        self.vis.destroy_window()
        
    def visualizer(self, xyz):
        self.pcd.points = o3d.utility.Vector3dVector(xyz)
        self.vis.update_geometry(self.pcd)
        self.vis.poll_events()
        self.vis.update_renderer()
        
    def start(self):
        
        while(self.OperatingM==0x0000 or self.OperatingM==0x00D0 or self.OperatingM==0x00C0):
            
            channelStat = EVK.getFrame(3000)
            
            if self.OperatingM==0x0000 and channelStat==0: # distance amplitude
                distance = EVK.getDistances()
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

                # Calculating the distance
                phase = np.arctan2(Q,I)
                unAmbiguousRange = (0.5*299792458)/(self.ModF*1000)
                coefRad = unAmbiguousRange / (2*np.pi)
                dist = (phase+np.pi)*coefRad
                dist = np.resize(dist, (px_height, px_width))
            
            elif self.OperatingM==0x00D0 and channelStat==0: # distance confidence
                distance = EVK.getDistances()
                dist = np.resize(distance, (px_height, px_width))
            
            EVK.freeFrame()
            xyz=self.pcg.depth2pcd(dist)
            self.visualizer(xyz)
            
            if not self.vis.poll_events():
                print('Close Window')
                break
            
        
        
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

if __name__ == "__main__":
    
    class a():
        def __init__(self):
            self.OperatingM = 'Test'
            self.ModF = 40
            
    pointcloud(a())