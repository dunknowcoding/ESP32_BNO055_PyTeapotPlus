"""
PyTeapot module for drawing rotating cube using OpenGL as per
quaternion or yaw, pitch, roll angles received over serial port and UDP.
"""

import pygame
import math
import sys
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *
from pywavefront import Wavefront, visualization

# User Configurations
# --------------------------------------------------------------------------------------------------------------------------------
useSerial = True  # set True for using serial for data transmission, False for wifi
useQuat = True   # set True for using quaternions, False for using y,p,r angles
DISPLAY_SIZE = (640, 480)  # Configuration
OBJ_FILE = "PyTeapotPlus\\alfa147.obj" # Use a simple obj file, ensure you have one in the same directory
COLOR = (0.1, 0.3, 0.1)

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
    pygame.init()
    pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("PyTeapot IMU orientation visualization")
    resizewin(640, 480)
    model = init()
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
            draw(model, w, nx, ny, nz)
        else:
            draw(model, 1, yaw, pitch, roll)
        frames += 1
        pygame.display.flip()
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
    gluPerspective(45, width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)


def init():
    glEnable(GL_DEPTH_TEST)
    #enable lighting
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0) # or other lights
    glEnable(GL_COLOR_MATERIAL) # Allows current color to affect material properties
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE) # Apply color to ambient/diffuse
    # Define light color and position
    light_ambient = [0.1, 0.2, 0.1, 0.1] # Adjust ambient light intensity
    light_diffuse = [0.1, 0.3, 0.3, 0.3]
    light_position = [50, 50, 0, 10] # Adjust position as needed
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    # Position the light (do this before model transformations)
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    # Load the model
    try:
        scene = Wavefront(OBJ_FILE, collect_faces=True, create_materials=True)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have a 'model.obj' file in the script directory.")
        sys.exit()
    glColor3f(*COLOR) # Set current color to white
    return scene


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


def draw(scene, w, nx, ny, nz):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0, 0.0, -10.0) # Move scene back
    INITIAL_SCALE = 0.04 # Adjust this value based on the size of your model
    glScalef(INITIAL_SCALE, INITIAL_SCALE, INITIAL_SCALE)

    if(useQuat):
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        print(f"Yaw={yaw:.4f}, Pitch={pitch:.4f}, Roll={roll:.4f}")
    else:
        yaw = nx
        pitch = ny
        roll = nz
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
    
    # for the 'car' model only
    glRotatef(yaw, 0.00, 0.00, 1.00)
    glRotatef(pitch, 1.00, 0.00, 0.00)
    glRotatef(-roll, 0.00, 1.00, 0.00)
    visualization.draw(scene)


def drawText(position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tobytes(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)
    

def quat_to_ypr(q):
    # Default conversion method
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= -180.0 / math.pi
    yaw   *= 180.0 / math.pi
    roll  *= 180.0 / math.pi
    # return [yaw, pitch, roll]
    # customized orientation
    yaw -= 40.2381
    pitch += 7.4261
    roll += 0.6765
    return [yaw, pitch, roll]  # For BNO055
    

if __name__ == '__main__':
    main()
