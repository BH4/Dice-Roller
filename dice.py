from platonic_solids import Cube, Tetrahedron, Octahedron, Dodecahedron, Icosahedron
from physics import simulation

import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from OpenGL.GL import GL_LINES, glTranslatef, glClear
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glBegin
from OpenGL.GL import glVertex3fv, glEnd
from OpenGL.GLU import gluPerspective

from random import random


def Draw_Shape(shape):
    glBegin(GL_LINES)
    vertices = shape.get_vertices()
    edges = shape.get_edges()
    for edge in edges:
        for vertex in edge:
            glVertex3fv(vertices[vertex])
    glEnd()


# Useful for troubleshooting shape creation
def minimal_show_shapes(shape_list, angle, rot_vector):
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Change perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, -2.0, -5)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw Shapes
        for shape in shape_list:
            Draw_Shape(shape)
            shape.rotate(angle, rot_vector, shape.center)

        pygame.display.flip()
        pygame.time.wait(10)


def run(shape_list):
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    # Change perspective
    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)
    glTranslatef(0.0, -2.0, -5)

    # Initialize the simulation
    sim = simulation(shape_list)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw Shapes
        for shape in shape_list:
            Draw_Shape(shape)

        pygame.display.flip()
        pygame.time.wait(10)

        sim.step(.01)


def main():
    center1 = (-4, 4, -5)
    center2 = (-2, 4, -7)
    center3 = (0, 4, -3)
    center4 = (2, 4, -7)
    center5 = (4, 4, -5)

    x, y, z = (random(), random(), random())
    print(x, y, z)

    # Make shapes
    shape1 = Cube(center1, angle=.1, rot_vector=(x, y, z))
    shape5 = Icosahedron(center2, angle=.1, rot_vector=(x, y, z))
    shape3 = Octahedron(center3, angle=.1, rot_vector=(x, y, z))
    shape4 = Dodecahedron(center4, angle=.1, rot_vector=(x, y, z))
    shape2 = Tetrahedron(center5, angle=.1, rot_vector=(x, y, z))

    shape_list = [shape1, shape2, shape3, shape4, shape5]

    run(shape_list)


"""
center = (0, 4, -5)
shape_list = [Icosahedron(center, angle=0, rot_vector=(1, 0, 0))]
print(shape_list[0].vertices[0])
print(shape_list[0].vertices[1])
minimal_show_shapes(shape_list, .006, (0, 1, 0))
"""
main()
