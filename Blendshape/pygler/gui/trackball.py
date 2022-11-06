

import math
import OpenGL.GL as gl
from OpenGL.GL import GLfloat
import numpy as np

def _v_add(v1, v2):
    return [v1[0]+v2[0], v1[1]+v2[1], v1[2]+v2[2]]
def _v_sub(v1, v2):
    return [v1[0]-v2[0], v1[1]-v2[1], v1[2]-v2[2]]
def _v_mul(v, s):
    return [v[0]*s, v[1]*s, v[2]*s]
def _v_dot(v1, v2):
    return v1[0]*v2[0]+v1[1]*v2[1]+v1[2]*v2[2]
def _v_cross(v1, v2):
    return [(v1[1]*v2[2]) - (v1[2]*v2[1]),
            (v1[2]*v2[0]) - (v1[0]*v2[2]),
            (v1[0]*v2[1]) - (v1[1]*v2[0])]
def _v_length(v):
    return math.sqrt(_v_dot(v,v))
def _v_normalize(v):
    try:                      return _v_mul(v,1.0/_v_length(v))
    except ZeroDivisionError: return v


def _q_add(q1,q2):
    t1 = _v_mul(q1, q2[3])
    t2 = _v_mul(q2, q1[3])
    t3 = _v_cross(q2, q1)
    tf = _v_add(t1, t2)
    tf = _v_add(t3, tf)
    tf.append(q1[3]*q2[3]-_v_dot(q1,q2))
    return tf
def _q_mul(q, s):
    return [q[0]*s, q[1]*s, q[2]*s, q[3]*s]
def _q_dot(q1, q2):
    return q1[0]*q2[0] + q1[1]*q2[1] + q1[2]*q2[2] + q1[3]*q2[3]
def _q_length(q):
    return math.sqrt(_q_dot(q,q))
def _q_normalize(q):
    try:                      return _q_mul(q,1.0/_q_length(q))
    except ZeroDivisionError: return q
def _q_from_axis_angle(v, phi):
    q = _v_mul(_v_normalize(v), math.sin(phi/2.0))
    q.append(math.cos(phi/2.0))
    return q
def _q_rotmatrix(q):
    m = [0.0]*16
    m[0*4+0] = 1.0 - 2.0*(q[1]*q[1] + q[2]*q[2])
    m[0*4+1] = 2.0 * (q[0]*q[1] - q[2]*q[3])
    m[0*4+2] = 2.0 * (q[2]*q[0] + q[1]*q[3])
    m[0*4+3] = 0.0
    m[1*4+0] = 2.0 * (q[0]*q[1] + q[2]*q[3])
    m[1*4+1] = 1.0 - 2.0*(q[2]*q[2] + q[0]*q[0])
    m[1*4+2] = 2.0 * (q[1]*q[2] - q[0]*q[3])
    m[1*4+3] = 0.0
    m[2*4+0] = 2.0 * (q[2]*q[0] - q[1]*q[3])
    m[2*4+1] = 2.0 * (q[1]*q[2] + q[0]*q[3])
    m[2*4+2] = 1.0 - 2.0*(q[1]*q[1] + q[0]*q[0])
    m[3*4+3] = 1.0
    return m



class Trackball(object):
    

    def __init__(self, theta=0, phi=0):
        

        self._rotation = [0,0,0,1]
        self._count = 0
        self._RENORMCOUNT = 97
        self._TRACKBALLSIZE = 0.8
        self.setOrientation(theta,phi)

    def dragTo (self, x, y, dx, dy):
        
        viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)
        width,height = float(viewport[2]), float(viewport[3])
        x  = (x*2.0 - width)/width
        dx = (2.*dx)/width
        y  = (y*2.0 - height)/height
        dy = (2.*dy)/height
        q = self._rotate(x,y,dx,dy)
        self._rotation = _q_add(q,self._rotation)
        self._count += 1
        if self._count > self._RENORMCOUNT:
            self._rotation = _q_normalize(self._rotation)
            self._count = 0
        
        return _q_rotmatrix(self._rotation)
        
    def getRotMat(self):
        '''
        Returns a 4x4 Rotation matrix as a np.array of float32. (row major)
        '''
        return np.array(_q_rotmatrix(self._rotation),dtype=np.float32).reshape(4,4).transpose()


    def setRotation(self,quat):
        self._rotation = quat

    def getRotation(self):
        return self._rotation

    def getOrientation(self):
        

        q0,q1,q2,q3 = self._rotation
        ax = math.atan(2*(q0*q1+q2*q3)/(1-2*(q1*q1+q2*q2)))*180.0/math.pi
        az = math.atan(2*(q0*q3+q1*q2)/(1-2*(q2*q2+q3*q3)))*180.0/math.pi
        return -az,ax

    def setOrientation(self, theta, phi):
      

        self._theta = theta
        self._phi = phi
        angle = self._theta*(math.pi/180.0)
        sine = math.sin(0.5*angle)
        xrot = [1*sine, 0, 0, math.cos(0.5*angle)]
        angle = self._phi*(math.pi/180.0)
        sine = math.sin(0.5*angle);
        zrot = [0, 0, sine, math.cos(0.5*angle)]
        self._rotation = _q_add(xrot, zrot)


    def _project(self, r, x, y):
       

        d = math.sqrt(x*x + y*y)
        if (d < r * 0.70710678118654752440):    # Inside sphere
            z = math.sqrt(r*r - d*d)
        else:                                   # On hyperbola
            t = r / 1.41421356237309504880
            z = t*t / d
        return z


    def _rotate(self, x, y, dx, dy): 
      

        if not dx and not dy:
            return [ 0.0, 0.0, 0.0, 1.0]
        last = [x, y,       self._project(self._TRACKBALLSIZE, x, y)]
        new  = [x+dx, y+dy, self._project(self._TRACKBALLSIZE, x+dx, y+dy)]
        a = _v_cross(new, last)
        d = _v_sub(last, new)
        t = _v_length(d) / (2.0*self._TRACKBALLSIZE)
        if (t > 1.0): t = 1.0
        if (t < -1.0): t = -1.0
        phi = 2.0 * math.asin(t)
        return _q_from_axis_angle(a,phi)

