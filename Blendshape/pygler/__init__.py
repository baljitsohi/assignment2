'''
Python - OpenGL - Viewer (PyGLer)

'''



VertexShaderCode = \



in vec4 vcolor;
in vec4 vposition;
out vec4 fragColor;
out vec4 fragPos;

void main() {
    fragColor = vcolor;
    fragPos = vposition;
}




