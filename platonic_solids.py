import numpy as np


# assumes unit vector
def rotation_matrix(a, v):
    v = np.array(v)
    mag = np.sqrt(sum(v**2))

    if mag == 0:
        return np.eye(3)

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

    def rotate(self, angle, vector, rotation_point):
        rotation_point_copy = np.array([x for x in rotation_point])
        self.translate(-1*rotation_point_copy)

        R = rotation_matrix(angle, vector)
        new_verts = []
        for v in self.vertices:
            newv = np.dot(v, R)
            new_verts.append(newv)

        self.vertices = new_verts

        self.center = np.dot(self.center, R)
        # Note: MOI for platonic solids is proportional to identity so this
        # does nothing, but may want to add more complex objects later.
        self.MOI = np.dot(R, np.dot(self.MOI, R.T))

        self.translate(rotation_point_copy)

    def translate(self, vector):
        self.vertices = self.vertices + vector
        self.center = self.center + vector

    def get_vertices(self):
        return self.vertices

    def get_edges(self):
        return self.edges

    # currently only gets lever arm wrt the ground and only for convex shapes.
    def get_lever_arm(self):
        tol = .0001
        num = 0
        tot = np.array([0.0, 0.0, 0.0])
        for v in self.vertices:
            if -1*tol < v[1] < tol:
                tot += v
                num += 1

        if num > 0:
            return tot/num-self.center

        lowestY = min([v[1] for v in self.vertices])
        for v in self.vertices:
            if -1*tol+lowestY < v[1] < tol+lowestY:
                tot += v
                num += 1

        return tot/num-self.center

    def parralel_axis(self, d):
        # d is the vector from the center of mass to the new reference point
        d_M = np.array([[0, -d[2], d[1]],
                        [d[2], 0, -d[0]],
                        [-d[1], d[0], 0]])
        return self.MOI-self.mass*np.dot(d_M, d_M)


class Cube(Solid):
    def __init__(self, center,  angle=0, rot_vector=(1, 0, 0), size=1, mass=1):
        Solid.__init__(self, center, size=size, mass=mass)
        self.MOI = self.moment_of_inertia()
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
        self.rotate(angle, rot_vector, self.center)

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
        self.MOI = self.moment_of_inertia()
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
        self.rotate(angle, rot_vector, self.center)

    def moment_of_inertia(self):
        I = np.zeros((3, 3))
        I[0][0] = (self.mass/10)*self.size**2
        I[1][1] = (self.mass/10)*self.size**2
        I[2][2] = (self.mass/10)*self.size**2
        return I


if __name__ == "__main__":
    center1 = (0, 0, 0)
    shape1 = Cube(center1, angle=.1, rot_vector=(1, 2, 3))
    shape1.rotate(-.1, (1, 2, 3), (1, 0, 0))
    print(shape1.get_vertices())
    print(shape1.center)
