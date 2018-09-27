import numpy as np


# assumes unit vector
def rotation_matrix(a, v):
    v = np.array(v)
    mag = np.sqrt(sum(v**2))
    v = v/mag

    R = np.zeros((3, 3))
    for j in range(3):
        for k in range(3):
            if j == k:
                R[j][k] = np.cos(a/2)**2 + np.sin(a/2)**2*(2*v[j]**2-1)
            else:
                R[j][k] = 2*v[j]*v[k]*np.sin(a/2)**2
                l = [0, 1, 2]
                l.remove(j)
                l.remove(k)
                l = l[0]
                if (j, k) == (0, 1) or (j, k) == (1, 2) or (j, k) == (2, 0):
                    lc = 1
                else:
                    lc = -1

                R[j][k] += lc*v[l]*np.sin(a)
    return R


class Solid():
    def __init__(self, center, size=1, mass=1):
        self.center = np.array(center)

        self.size = size
        self.mass = mass

        self.vertices = np.array([])
        self.edges = np.array([])

    # Assumes the object has already been translated to the center point
    def rotate(self, angle, vector):
        center_copy = np.array([x for x in self.center])
        self.translate(-1*center_copy)

        R = rotation_matrix(angle, vector)
        new_verts = []
        for v in self.vertices:
            newv = np.dot(v, R)
            new_verts.append(newv)

        self.vertices = new_verts

        self.translate(center_copy)

    def translate(self, vector):
        self.vertices = self.vertices + vector
        self.center = self.center + vector

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges


class Cube(Solid):
    def __init__(self, center,  angle=0, rot_vector=(1, 0, 0), size=1, mass=1):
        Solid.__init__(self, center, size=size, mass=mass)
        self.setup(angle, rot_vector)

    def setup(self, angle, rot_vector):
        verts = []
        for i in [-1, 1]:
            x = self.center[0]+.5*i*self.size
            for j in [-1, 1]:
                y = self.center[1]+.5*j*self.size
                for k in [-1, 1]:
                    z = self.center[2]+.5*k*self.size

                    verts.append((x, y, z))
        self.vertices = verts

        self.edges = [(0, 1), (0, 2), (0, 4),
                      (3, 1), (3, 2), (3, 7),
                      (5, 1), (5, 4), (5, 7),
                      (6, 2), (6, 4), (6, 7)]

        # self.translate(self.center)
        self.rotate(angle, rot_vector)

    def moment_of_inertia(self):
        I = np.zeros((3, 3))
        I[0][0] = (self.mass/6)*self.size**2
        I[1][1] = (self.mass/6)*self.size**2
        I[2][2] = (self.mass/6)*self.size**2
        return I


# A size s tetrahedron (with no rotation) fits perfectly inside a size s cube.
class Tetrahedron(Solid):
    def __init__(self, center,  angle=0, rot_vector=(1, 0, 0), size=1, mass=1):
        Solid.__init__(self, center, size=size, mass=mass)
        self.setup(angle, rot_vector)

    def setup(self, angle, rot_vector):
        verts = []
        for i in [-1, 1]:
            x = self.center[0]+.5*i*self.size
            for j in [-1, 1]:
                y = self.center[1]+.5*j*self.size
                for k in [-1, 1]:
                    if i*j*k == -1:
                        z = self.center[2]+.5*k*self.size

                        verts.append((x, y, z))

        self.vertices = verts

        self.edges = []
        for i in range(0, 3):
            for j in range(i+1, 4):
                self.edges.append((i, j))

        #self.translate(self.center)
        self.rotate(angle, rot_vector)

    def moment_of_inertia(self):
        print("Tetrahedron moment of inertia not implemented")
        I = np.zeros((3, 3))
        I[0][0] = (self.mass/20)*self.size**2
        I[1][1] = (self.mass/20)*self.size**2
        I[2][2] = (self.mass/20)*self.size**2
        return I


if __name__ == "__main__":
    center1 = (1, 5, -20)
    shape1 = Cube(center1)
    print(shape1.center)
