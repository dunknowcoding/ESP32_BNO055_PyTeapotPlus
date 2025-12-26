"""
A 3D viewer to read .obj models
"""

import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from pywavefront import Wavefront, visualization
import sys

# Configuration
DISPLAY_SIZE = (800, 600)
# Use a simple obj file, ensure you have one in the same directory
OBJ_FILE = "PyTeapotPlus\\alfa147.obj"
COLOR = (0.1, 0.3, 0.1)


def draw():
    pygame.init()
    pygame.display.set_mode(DISPLAY_SIZE, DOUBLEBUF | OPENGL)
    pygame.display.set_caption("OpenGL Model Viewer")

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

    # Setup OpenGL perspective
    gluPerspective(45, (DISPLAY_SIZE[0] / DISPLAY_SIZE[1]), 1.0, 30.0)
    glPushMatrix()

    # Initial camera/model position and rotation variables
    glTranslatef(0.0, 0.0, -10.0) # Move scene back
    INITIAL_SCALE = 0.03 # Adjust this value based on the size of your model
    INITIAL_POSITION = (0, 0, 1.0) # X, Y, Z coordinates

    # 1. Apply scaling (must happen before translation if scaling relative to origin)
    glScalef(INITIAL_SCALE, INITIAL_SCALE, INITIAL_SCALE)
    # 2. Apply translation (positioning)
    # Note: the translation values are also scaled if applied after glScalef
    glTranslatef(INITIAL_POSITION[0] / INITIAL_SCALE, 
                 INITIAL_POSITION[1] / INITIAL_SCALE, 
                 INITIAL_POSITION[2] / INITIAL_SCALE)

    # Enable depth testing for proper 3D rendering
    glEnable(GL_DEPTH_TEST)

    # Load the model
    try:
        scene = Wavefront(OBJ_FILE, collect_faces=True, create_materials=True)
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure you have a 'model.obj' file in the script directory.")
        sys.exit()
    glColor3f(*COLOR) # Set current color

    # Initial mouse state
    drag = False
    mouse_pos = None

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # --- Zoom In/Out ---
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 4: # Wheel up (zoom in)
                    glScalef(1.05, 1.05, 1.05)
                elif event.button == 5: # Wheel down (zoom out)
                    glScalef(0.95, 0.95, 0.95)
                elif event.button == 1: # Left button down (start drag rotation)
                    drag = True
                    mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1: # Left button up (stop drag rotation)
                    drag = False

            # --- Rotate using mouse ---
            elif event.type == pygame.MOUSEMOTION:
                if drag:
                    current_mouse_pos = event.pos

                    # Calculate mouse movement
                    dx = current_mouse_pos[0] - mouse_pos[0]
                    dy = current_mouse_pos[1] - mouse_pos[1]
                    mouse_pos = current_mouse_pos

                    # Apply rotation: X-axis rotation around the Y global axis, Y-axis rotation around X global axis
                    # glRotatef applies the rotation *after* any previous transformations (like initial translation)
                    glRotatef(dx * 0.5, 0, 1, 0) # Rotate around Y-axis based on horizontal drag
                    glRotatef(dy * 0.5, 1, 0, 0) # Rotate around X-axis based on vertical drag
                    
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw the model
        visualization.draw(scene)

        # Update the display
        pygame.display.flip()
        pygame.time.wait(10)


if __name__ == '__main__':
    draw()
