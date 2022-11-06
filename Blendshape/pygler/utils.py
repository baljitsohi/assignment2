

import numpy as np
from pygler.model import PyGLerModel,Geometry

def normalize_Nx3(arr):
    
    lens = np.sqrt( arr[:,0]**2 + arr[:,1]**2 + arr[:,2]**2 )
    arr[:,0] /= lens
    arr[:,1] /= lens
    arr[:,2] /= lens                
    return arr

def ComputeNormals(vertices, faces):
    
    norm = np.zeros( vertices.shape, dtype=vertices.dtype )
   
    tris = vertices[faces]
               
    n = np.cross( tris[::,1 ] - tris[::,0]  , tris[::,2 ] - tris[::,0] )

    k = normalize_Nx3(n)
     norm[ faces[:,1] ] += k
    norm[ faces[:,2] ] += k
    r = normalize_Nx3(norm)
        
    return r;


def CreateAxisModel(name="axis",thickness=0.01,length=1.0,colorX=[255,0,0],colorY=[0,255,0],colorZ=[0,0,255],alpha=1.0):
   
    
    s = thickness/2.0
    lr = length / s
    
    cubeV = np.array([-s, s, s,
                       s, s, s,
                       s,-s, s,
                      -s,-s, s,
                      -s,-s,-s,
                      -s, s,-s,
                       s, s,-s,
                       s,-s,-s],dtype='f').reshape(-1,3)
    
    cubeF = np.array([0,1,2, 2,3,0, # front
                      2,3,4, 4,7,2, # bottom
                      0,5,4, 4,3,0, # left
                      7,2,1, 1,6,7, # right 
                      5,6,7, 7,4,5, # back
                      0,5,6, 6,1,0  # top 
                                    ],dtype=np.uint32)

    
    
    axisV = np.empty((24,3),dtype=np.float32)
    axisF = np.empty((36*3),dtype=np.uint32) 
    
    Xaxis = np.copy(cubeV)
    Xaxis[[1,2,6,7],0] *= lr

    Yaxis = np.copy(cubeV)
    Yaxis[[0,1,5,6],1] *= lr
    
    Zaxis = np.copy(cubeV)
    Zaxis[[0,1,2,3],2] *= lr
    
    for i,ax in enumerate((Xaxis,Yaxis,Zaxis)):
        axisV[i*8:(i+1)*8] = ax
        axisF[(i*36):((i+1)*36)] = np.copy(cubeF) + i*8 
    
    # colours.
    colors = np.empty((24,3),dtype=np.ubyte)
    colors[0*8:1*8] = colorX
    colors[1*8:2*8] = colorY
    colors[2*8:3*8] = colorZ
    
    return PyGLerModel(name, geometry=Geometry(axisV, axisF, colors=colors,alpha=alpha,autoScale=False,bgrColor=False),modelM=np.eye(4,dtype=np.float32))
    

def CreateCubeModel(name="cube",side=1.0,scale=[1.0,1.0,1.0],colors=[0,255,0],alpha=0.9):
    
    
    s = side/2.0
    cubeV = np.array([-s, s, s,
                       s, s, s,
                       s,-s, s,
                      -s,-s, s,
                      -s,-s,-s,
                      -s, s,-s,
                       s, s,-s,
                       s,-s,-s],dtype='f').reshape(-1,3)
    
    cubeF = np.array([0,1,2, 2,3,0, # front 
                      2,3,4, 4,7,2, # bottom
                      0,5,4, 4,3,0, # left
                      7,2,1, 1,6,7, # right 
                      5,6,7, 7,4,5, # back
                      0,5,6, 6,1,0  # top 
                                    ],dtype=np.uint32)

    
    cubeV *= scale
        
    colors = np.array(colors,dtype=np.ubyte)
    
    return PyGLerModel(name, geometry=Geometry(cubeV, cubeF, colors=colors,autoScale=False,alpha=alpha),modelM=np.eye(4,dtype=np.float32))


class CameraParams(object):
   
    
    def __init__(self,width=640,height=480,cx=320,cy=240,fx=575.81573,fy=575.81573,znear=1.0,zfar=10000.0,unit=1.0):
        
        self._width = width
        self._height = height
        self._cx = cx
        self._cy = cy
        self._fx = fx
        self._fy = fy
        
        self._unit=unit
        self._zfar=zfar
        self._znear=znear
            
      
        intr = np.zeros((4,4),dtype=np.float32); 
        intr[0][0] = (2.0 * fx) / width;
        intr[0][1] = 0;
        intr[0][2] = -1 + (2 * cx) / width;
        
        intr[1][1] = -(2 * fy) / height 
            
        intr[1][2] = 1 - (2 * cy) / height
        intr[2][2] = 1;
        intr[3][3] = unit; 
        cpm = np.zeros((4,4),dtype=np.float32) 
        cpm[0][0] = 1;
        cpm[1][1] = 1;
        cpm[2][2] = zfar/(zfar - znear);
        cpm[2][3] = (-((zfar*znear)/(zfar - znear))) / unit;
        cpm[3][2] = 1;
        

            
        projectionMat = cpm.dot(intr)
        
        self._projectionMat = projectionMat.transpose()

    @property
    def projectionMat(self):
        return self._projectionMat
    
    
