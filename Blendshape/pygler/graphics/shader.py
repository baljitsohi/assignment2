
from OpenGL import GL

import os
import OpenGL.GL as gl
import ctypes



class ShaderException(Exception):
   
    pass

class ShaderVertexException(ShaderException):
    
    pass

class ShaderFragmentException(ShaderException):
   
    pass

class ShaderLinkException(ShaderException):
    
    pass



class Shader:
   

    def __init__(self, vertex_code = None, fragment_code = None):
      

        self.uniforms = {}
        self._vertex_code = vertex_code
        self._fragment_code = fragment_code

        # create the program handle
        self.handle = gl.glCreateProgram()

        # we are not linked yet
        self.linked = False

        # create the vertex shader
        self._build_shader(vertex_code, gl.GL_VERTEX_SHADER)

        # create the fragment shader
        self._build_shader(fragment_code, gl.GL_FRAGMENT_SHADER)

        # the geometry shader will be the same, once pyglet supports the
        # extension self.createShader(frag, GL_GEOMETRY_SHADER_EXT) attempt to
        # link the program
        self._link()



    def _build_shader(self, strings, shader_type):
       

        count = len(strings)
        # if we have no source code, ignore this shader
        if count < 1:
            return

        # create the shader handle
        shader = gl.glCreateShader(shader_type)

        # Upload shader code
        gl.glShaderSource(shader, strings)

        # compile the shader
        gl.glCompileShader(shader)

        # retrieve the compile status
        status = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)

        # if compilation failed, raise exception and print the log
        if not status:
            if shader_type == gl.GL_VERTEX_SHADER:
                raise ShaderException, \
                    'Vertex compilation: ' + gl.glGetShaderInfoLog(shader)
            elif shader_type == gl.GL_FRAGMENT_SHADER:
                raise ShaderException, \
                    'Fragment compilation:' + gl.glGetShaderInfoLog(shader)
            else:
                raise ShaderException, \
                    gl.glGetShaderInfoLog(shader)
        else:
            # all is well, so attach the shader to the program
            gl.glAttachShader(self.handle, shader)

    def _link(self):
        ''' Link the program '''

        gl.glLinkProgram(self.handle)
        # retrieve the link status
        temp = ctypes.c_int(0)
        gl.glGetProgramiv(self.handle, gl.GL_LINK_STATUS, ctypes.byref(temp))

        # if linking failed, print the log
        if not temp:
            # retrieve the log length
            gl.glGetProgramiv(self.handle,
                              gl.GL_INFO_LOG_LENGTH, ctypes.byref(temp))

            # create a buffer for the log
            log = gl.glGetProgramInfoLog(self.handle) #, temp, None, buffer)

            raise ShaderException, 'Linking: '+ log
        else:
            # all is well, so we are linked
            self.linked = True

    def bind(self):
        ''' Bind the program, i.e. use it. '''
        gl.glUseProgram(self.handle)

    def unbind(self):
       
        gl.glUseProgram(0)

    def uniformf(self, name, *vals):
    

        loc = self.uniforms.get(name,
                                gl.glGetUniformLocation(self.handle,name))
        #if loc < 0:
        #    raise ShaderException, \
        #        '''Unknow uniform location '%s' ''' % name
        self.uniforms[name] = loc

        # Check there are 1-4 values
        if len(vals) in range(1, 5):
            # Select the correct function
            { 1 : gl.glUniform1f,
              2 : gl.glUniform2f,
              3 : gl.glUniform3f,
              4 : gl.glUniform4f
              # Retrieve uniform location, and set it
            }[len(vals)](loc, *vals)

    def uniformi(self, name, *vals):
     

        loc = self.uniforms.get(name,
                                gl.glGetUniformLocation(self.handle,name))
        #if loc < 0:
        #    raise ShaderException, \
        #        '''Unknow uniform location '%s' ''' % name
        self.uniforms[name] = loc

        # Checks there are 1-4 values
        if len(vals) in range(1, 5):
            # Selects the correct function
            { 1 : gl.glUniform1i,
              2 : gl.glUniform2i,
              3 : gl.glUniform3i,
              4 : gl.glUniform4i
              # Retrieves uniform location, and set it
            }[len(vals)](loc, *vals)


    def uniform_matrixf(self, name, mat):

        loc = self.uniforms.get(name,
                                gl.glGetUniformLocation(self.handle,name))
        #if loc < 0:
        #    raise ShaderException, \
        #        '''Unknow uniform location '%s' ''' % name
        self.uniforms[name] = loc

        # Upload the 4x4 floating point matrix
        gl.glUniformMatrix4fv(loc, 1, False, (ctypes.c_float * 16)(*mat))


    def getAttributeLocation(self, attributeName):
        return GL.glGetAttribLocation(self.handle, attributeName)

    def get_vertex_code(self, lineno=True):
        code = ''
        for lineno,line in enumerate(self._vertex_code.split('\n')):
            code += '%3d: ' % (lineno+1) + line + '\n'
        return code

    def get_fragment_code(self,lineno=True):
        code = ''
        for lineno,line in enumerate(self._fragment_code.split('\n')):
            code += '%3d: ' % (lineno+1) + line + '\n'
        return code

