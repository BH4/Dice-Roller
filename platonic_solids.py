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
    def __init__(self, center, angle=0, rot_vector=(1, 0, 0), size=1):
        self.center = np.array(center)

        self.angle = angle
        rot_vector = np.array(rot_vector)
        mag = np.sqrt(sum(rot_vector**2))
        self.rot_vector = rot_vector/mag

        self.size = size

        self.vertices = np.array([])
        self.edges = np.array([])

    # Assumes the object has already been translated to the center point
    def rotate(self, angle, vector):
        self.translate(-1*self.center)

        R = rotation_matrix(angle, vector)
        new_verts = []
        for v in self.vertices:
            newv = np.dot(v, R)
            new_verts.append(newv)

        self.vertices = new_verts

        self.translate(self.center)

    def translate(self, vector):
        self.vertices = self.vertices + vector

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges


class Cube(Solid):
    def __init__(self, center,  angle=0, rot_vector=(1, 0, 0), size=1):
        Solid.__init__(self, center, angle=angle, rot_vector=rot_vector, size=size)
        self.setup()

    def setup(self):
        verts = []
        for i in [-1, 1]:
            x = .5*i*self.size
            for j in [-1, 1]:
                y = .5*j*self.size
                for k in [-1, 1]:
                    z = .5*k*self.size

                    verts.append((x, y, z))
        self.vertices = verts

        self.edges = [(0, 1), (0, 2), (0, 4),
                      (3, 1), (3, 2), (3, 7),
                      (5, 1), (5, 4), (5, 7),
                      (6, 2), (6, 4), (6, 7)]

        self.translate(self.center)
        self.rotate(self.angle, self.rot_vector)


if __name__ == "__main__":
    R = rotation_matrix(1, (3, 1, 1))
    print(R)
    print(np.dot(R, R.T))
    print(np.linalg.det(R))
