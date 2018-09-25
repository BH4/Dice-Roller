from platonic_solids import Cube

import pygame
from pygame.locals import DOUBLEBUF, OPENGL

from OpenGL.GL import GL_LINES, glTranslatef, glRotatef, glClear
from OpenGL.GL import GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT, glBegin
from OpenGL.GL import glVertex3fv, glEnd
from OpenGL.GLU import gluPerspective


def Draw_Shape(shape):
    glBegin(GL_LINES)
    verticies = shape.get_vertices()
    edges = shape.get_edges()
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


def main():
    pygame.init()
    display = (800, 600)
    pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

    gluPerspective(45, (display[0]/display[1]), 0.1, 50.0)

    glTranslatef(0.0, 0.0, -5)

    center1 = (1, 0, 0)
    center2 = (-1, 0, 0)

    t = 0
    w = .01
    shape1 = Cube(center1)
    shape2 = Cube(center2)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # glRotatef(1, 0, 0, 1)  # Rotates the perspective. Not the object.
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        Draw_Shape(shape1)
        Draw_Shape(shape2)

        pygame.display.flip()
        pygame.time.wait(10)

        t += 1
        shape1.rotate(w, (3, 1, 1))
        shape2.rotate(w, (1, 1, 0))


main()
