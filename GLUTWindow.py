#!/usr/bin/env python

import sys

try:
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *
except:
    raise ImportError, 'PyOpenGL not installed properly.'

__timerN = 0
__timers = {}
def addTimer( callback, delay ):
    global __timerN, __timers
    
    __timerN += 1
    
    __timers[ __timerN ] = (callback, delay)
    glutTimerFunc( delay, timerFunc, __timerN )
    return __timerN

def removeTimer( n ):
    global __timers
    
    if __timers.has_key( n ): del __timers[ n ]

def timerFunc( n ):
    if not __timers.has_key( n ): return
    
    callback, delay = __timers[ n ]
    callback()
    
    if __timers.has_key( n ):
        glutTimerFunc( delay, timerFunc, n )

class GLUTWindow( object ):
    def __init__( self, size = (512, 512), title = None ):
        self.size = size
        self.timerN = 0
        self.background_color = (.5, .6, .9 )
        self.screen_capture_count = 0
        self.full_screen_data = None
        
        glutInitWindowSize( self.size[0], self.size[1] )
        self.id = glutCreateWindow( 'scraps' )
        
        self.title = title
        if not self.title:
            self.title = 'Window #%d' % (self.id,)
        glutSetWindowTitle( self.title )
        
        self.reshapeFunc( *size )
        
        glutReshapeFunc( self.reshapeFunc )
        glutKeyboardFunc( self.keyboardFunc )
        glutSpecialFunc( self.specialFunc )
        glutMouseFunc( self.mouseFunc )
        glutMotionFunc( self.motionFunc )
        glutPassiveMotionFunc( self.passiveMotionFunc )
        glutDisplayFunc( self.displayFuncWrapper )
    
    def setWindow( self ):
        glutSetWindow( self.id )
    
    def postRedisplay( self ):
        glutSetWindow( self.id )
        glutPostRedisplay()
    
    def setWindowTitle( self, title ):
        glutSetWindow( self.id )
        self.title = title
        glutSetWindowTitle( self.title )
    
    def getWindowTitle( self ):
        glutSetWindow( self.id )
        return self.title
    
    def reshapeWindow( self, size ):
        glutSetWindow( self.id )
        glutReshapeWindow( *size )
    
    def getWindowShape( self ):
        glutSetWindow( self.id )
        return ( glutGet( GLUT_WINDOW_WIDTH ), glutGet( GLUT_WINDOW_HEIGHT ) )
    
    def positionWindow( self, pos ):
        glutSetWindow( self.id )
        glutPositionWindow( *pos )
    
    def getWindowPosition( self ):
        glutSetWindow( self.id )
        return ( glutGet( GLUT_WINDOW_X ), glutGet( GLUT_WINDOW_Y ) )
    
    def reshapeFunc( self, w, h ):
        glutReshapeWindow( w, h )
        self.size = (w,h)
        
        glViewport(0, 0, w, h)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        if(w <= h):
            gluOrtho2D(0.0, 1.0, 0.0, float(h)/w)
        else:
            gluOrtho2D(0.0, float(w)/h, 0.0, 1.0)
        glMatrixMode(GL_MODELVIEW)
    
    def displayFuncWrapper( self ):
        self.displayFunc()
        glutSwapBuffers()
        
    def displayFunc( self ):
        col = self.background_color
        
        glClearColor( col[0], col[1], col[2], 1.0 )
        glClear( GL_COLOR_BUFFER_BIT )
    
    def specialFunc( self, key, x, y ):
        print 'special key:', key
    
    def keyboardFunc( self, key, x, y ):
        print 'key:', ord(key), key
        if key == 'q' or key == 'Q': sys.exit(0)
        if key == 'c': self.captureScreen()
        if key == '\\': self.toggleFullScreen()
        
        print self.getWindowPosition()
    
    def mouseFunc( self, button, state, x, y ):
        print 'mouse button %d state %d at ( %d, %d )' % (button, state, x, y )
    
    def motionFunc( self, x, y ):
        print 'mouse motion at ( %d, %d ):' % (x,y)
    
    def passiveMotionFunc( self, x,y ):
        print 'mouse passive motion at ( %d, %d )' % (x,y)
    
    def timerFunc( self ):
        self.displayFunc()
    
    def startPeriodicTimer( self, delay ):
        self.stopPeriodicTimer()
        self.timerN = addTimer( self.__timerFuncWrapper, delay )
    
    def stopPeriodicTimer( self ):
        removeTimer( self.timerN )
    
    def __timerFuncWrapper( self ):
        glutSetWindow( self.id )
        self.timerFunc()
    
    def captureScreen( self ):
        glutSetWindow( self.id )
        try:
            import ctypes as C
            png_saver = C.cdll.LoadLibrary( 'libpng_saver.dylib' )
            save_png = png_saver.save_png
            save_png.argtypes = [ C.POINTER( C.c_char ), C.c_int, C.c_int, C.c_void_p, C.c_int ]
            
            view = glGetIntegerv( GL_VIEWPORT )
            width = view[2]
            height = view[3]
            
            glReadBuffer( GL_FRONT )
            data = glReadPixels( view[0], view[1], view[2], view[3], GL_RGBA, GL_UNSIGNED_BYTE )
            glReadBuffer( GL_BACK )
            
            fname = 'screen_capture-%s-%d.png' % (self.getWindowTitle(), self.screen_capture_count)
            self.screen_capture_count += 1
            save_png( fname, width, height, data, True )
            print 'Captured window \"' + self.getWindowTitle() + '\" to file', fname
        except:
            print >> sys.stderr, "Error saving screen capture (ctypes? missing png_saver library?)"
    
    def toggleFullScreen( self ):
        glutSetWindow( self.id )
        if self.full_screen_data:
            self.reshapeWindow( self.full_screen_data[0] )
            self.positionWindow( self.full_screen_data[1] )
            # on OS X the window title gets lost, so I must re-set it:
            self.setWindowTitle( self.getWindowTitle() )
            self.full_screen_data = None
        else:
            self.full_screen_data = ( tuple( self.size ), tuple( self.getWindowPosition() ) )
            glutFullScreen()


def test():
    glutInit( sys.argv )
    glutInitDisplayMode( GLUT_DOUBLE | GLUT_RGB )
    
    class PulseWindow( GLUTWindow ):
        def __init__( self ):
            GLUTWindow.__init__( self )
            self.startPeriodicTimer( 16 )
        
        def timerFunc( self ):
            from math import sin
            self.background_color = ( sin( glutGet( GLUT_ELAPSED_TIME ) / 1000. )**2, self.background_color[1], self.background_color[2] )
            self.displayFunc()
    
    window = GLUTWindow()
    window = PulseWindow()
    
    glutMainLoop()


# call main() if the script is being run
if __name__ == '__main__':
    test()
