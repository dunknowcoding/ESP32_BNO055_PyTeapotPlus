"""
PyTeapot module for drawing rotating cube using OpenGL as per
quaternion or yaw, pitch, roll angles received over serial port and UDP.
"""

import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *


# User Configurations
# --------------------------------------------------------------------------------------------------------------------------------
useSerial = True  # set True for using serial for data transmission, False for wifi
useQuat = True   # set True for using quaternions, False for using y,p,r angles

if(useSerial):
    import serial
    ser = serial.Serial('COM19', 115200, dsrdtr=False, timeout=1)  # set 'COM' if you are using Windows, otherwise as '/dev/ttyUSB0'
else:
    import socket
    # Modify these two varibles acording to your UDP settings
    UDP_IP = "192.168.1.2"
    UDP_PORT = 5555
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
# --------------------------------------------------------------------------------------------------------------------------------
# User Configurations ends here


def main():
    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("PyTeapot IMU orientation visualization")
    resizewin(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if(useQuat):
            [w, nx, ny, nz] = read_data()
        else:
            [yaw, pitch, roll] = read_data()
        if(useQuat):
            draw(w, nx, ny, nz)
        else:
            draw(1, yaw, pitch, roll)
        pygame.display.flip()
        frames += 1
    print("fps: %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    if(useSerial):
        ser.close()


def resizewin(width, height):
    """
    For resizing window
    """
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)


def cleanSerialBegin():
    if(useQuat):
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            w = float(line.split('w')[1])
            nx = float(line.split('a')[1])
            ny = float(line.split('b')[1])
            nz = float(line.split('c')[1])
        except Exception:
            pass
    else:
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '') 
            roll = float(line.split('y')[1])
            pitch = float(line.split('p')[1])
            yaw = float(line.split('r')[1])
        except Exception:
            pass


def read_data():
    if(useSerial):
        ser.reset_input_buffer()
        cleanSerialBegin()
        line = ser.readline().decode('UTF-8').replace('\n', '')
        print(line)
    else:
        # Waiting for data from udp port 5555
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        line = data.decode('UTF-8').replace('\n', '')
        # print(line)
            
    if(useQuat):
        try:
            w = float(line.split('w')[1])
            nx = float(line.split('a')[1])
            ny = float(line.split('b')[1])
            nz = float(line.split('c')[1])
            return [w, nx, ny, nz]
        except Exception:
            return [0, 0, 0, 1]
    else:
        try:
            yaw = float(line.split('y')[1])
            pitch = float(line.split('p')[1])
            roll = float(line.split('r')[1])
            print(f"Roll={roll:.4f}, Pitch={pitch:.4f}, Yaw={yaw:.4f}")
            return [yaw, pitch, roll]
        except Exception:
            return [0, 0, 0]


def draw_arrow_tips(length, size):
    """
    Draws simple line-based arrow tips for the axes.
    """
    glBegin(GL_LINES)

    # Y arrow tip (blue)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-length, 0.0, 0.0)
    glVertex3f(-length + size, 0.0, size)
    glVertex3f(-length, 0.0, 0.0)
    glVertex3f(-length + size, 0.0, -size)

    # Z arrow tip (green)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, length, 0.0)
    glVertex3f(size, length - size, 0.0)
    glVertex3f(0.0, length, 0.0)
    glVertex3f(-size, length - size, 0.0)

    # X arrow tip (red)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, -length - 0.5)
    glVertex3f(0.0, size, size - length - 0.5)
    glVertex3f(0.0, 0.0, -length - 0.5)
    glVertex3f(0.0, -size, size - length - 0.5)

    glEnd()


def draw_axes(length=2, line_width=3.0, arrow_width=2.0, arrow_size=0.2):
    """
    Draws the X, Y, and Z axes at the origin (0, 0, 0).
    For BNO055's absolute orientation
    X axis is red, Y axis is blue, Z axis is green.
    """
    glLineWidth(line_width)
    glBegin(GL_LINES)

    # Y axis (blue)
    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(-length, 0.0, 0.0) # Line to y=-2

    # Z axis (green)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, length, 0.0) # Line to z=2

    # X axis (red)
    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, 0.0)
    glVertex3f(0.0, 0.0, -length-0.5) # Line to x=-2.5
    glEnd()
    
    glLineWidth(arrow_width)
    draw_arrow_tips(length, arrow_size)

    
    
    
def draw_surface():
    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    
    glEnd()


def draw(w, nx, ny, nz):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    drawText((-2.6, 1.8, 2), "PyTeapotPlus", 18)
    drawText((-2.6, 1.6, 2), "Module to visualize quaternion or Euler angles data", 16)
    drawText((-2.6, -2, 2), "Press Escape to exit.", 16)

    if(useQuat):
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        print(f"Yaw={yaw:.4f}, Pitch={pitch:.4f}, Roll={roll:.4f}")
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(2 * math.acos(w) * 180.00/math.pi, -ny, nz, -nx)
    else:
        yaw = nx
        pitch = ny
        roll = nz
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(-roll, 0.00, 0.00, 1.00)
        glRotatef(pitch, 1.00, 0.00, 0.00)
        glRotatef(yaw, 0.00, 1.00, 0.00)
    draw_axes()
    draw_surface()



def drawText(position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tobytes(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def quat_to_ypr(q):
    ## Default conversion method
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= -180.0 / math.pi
    yaw   *= 180.0 / math.pi
    roll  *= 180.0 / math.pi
    # yaw   -= -0.13  # Declination at Chandrapur, Maharashtra is - 0 degress 13 min
    # return [yaw, pitch, roll]
    yaw -= 40.2381
    pitch += 7.4261
    roll += 0.6765
    return [yaw, pitch, roll]  # For BNO055
    yaw 
    


    


if __name__ == '__main__':
    main()
