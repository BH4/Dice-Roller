import numpy as np

# constants
PHI = (np.sqrt(5)+1)/2

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


# size is the side length of the cube
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

        self.rotate(angle, rot_vector, self.center)

    def moment_of_inertia(self):
        m = (self.mass/6)*self.size**2
        I = m*np.eye(3)
        return I


# A size s tetrahedron (with no rotation) fits perfectly inside a size s cube.
# Side length = sqrt(2)*size
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

        self.rotate(angle, rot_vector, self.center)

    def moment_of_inertia(self):
        m = (self.mass/10)*self.size**2
        I = m*np.eye(3)
        return I


# A size s octahedron (with no rotation) has each vertex at the center of each
# face of a size s cube.
# Side length = size/sqrt(2)
class Octahedron(Solid):
    def __init__(self, center,  angle=0, rot_vector=(1, 0, 0), size=1, mass=1):
        Solid.__init__(self, center, size=size, mass=mass)
        self.MOI = self.moment_of_inertia()
        self.setup(angle, rot_vector)

    def setup(self, angle, rot_vector):
        verts = []
        for i in [-1, 1]:
            x = .5*i*self.size

            verts.append(self.center+np.array((x, 0, 0)))
            verts.append(self.center+np.array((-x, 0, 0)))
            verts.append(self.center+np.array((0, x, 0)))
            verts.append(self.center+np.array((0, -x, 0)))
            verts.append(self.center+np.array((0, 0, x)))
            verts.append(self.center+np.array((0, 0, -x)))

        self.vertices = verts

        self.edges = []
        for i in range(4):
            start = i+1
            if i % 2 == 0:
                start += 1
            for j in range(start, 6):
                self.edges.append((i, j))

        self.rotate(angle, rot_vector, self.center)

    def moment_of_inertia(self):
        m = (self.mass/20)*self.size**2
        I = m*np.eye(3)
        return I


# A size s dodecahedron (with no rotation) contains all the vertices of a cube
# of size s with no rotation. Note this shape is not flat on bottom without
# rotation.
# Side length = (2/phi)*size = (sqrt(5)-1)*size
# I think rotation by pi/3 about (1, 0, 0) will result in a flat bottom.
class Dodecahedron(Solid):
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

        for i in [-1, 1]:
            for j in [-1, 1]:
                verts.append(self.center + np.array((0, i*PHI, j/PHI))/2)
                verts.append(self.center + np.array((j/PHI, 0, i*PHI))/2)
                verts.append(self.center + np.array((i*PHI, j/PHI, 0))/2)

        self.vertices = verts

        self.edges = [(8, 11), (8, 0), (8, 4), (11, 1), (11, 5),
                      (14, 17), (14, 2), (14, 6), (17, 3), (17, 7),
                      (9, 12), (9, 0), (9, 2), (12, 4), (12, 6),
                      (15, 18), (15, 1), (15, 3), (18, 5), (18, 7),
                      (10, 13), (10, 0), (10, 1), (13, 2), (13, 3),
                      (16, 19), (16, 4), (16, 5), (19, 6), (19, 7)]

        self.rotate(angle, rot_vector, self.center)

    def moment_of_inertia(self):
        m = ((39*PHI+28)/150)*(2/PHI)**2*self.mass*self.size**2
        I = m*np.eye(3)
        return I


# A size s icosahedron (with no rotation) is oriented... how?
# Side length = 2*size
# I think rotation by x about y will result in a flat bottom.
class Icosahedron(Solid):
    def __init__(self, center,  angle=0, rot_vector=(1, 0, 0), size=1, mass=1):
        Solid.__init__(self, center, size=size, mass=mass)
        self.MOI = self.moment_of_inertia()
        self.setup(angle, rot_vector)

    def setup(self, angle, rot_vector):
        verts = []

        for i in [-1, 1]:
            for j in [-1, 1]:
                verts.append((0, .5*self.size*j*1, .5*self.size*i*PHI))

        plane2 = []
        plane3 = []
        for v in verts:
            plane2.append((v[1], v[2], v[0]))
            plane3.append((v[2], v[0], v[1]))

        verts.extend(plane2)
        verts.extend(plane3)

        self.vertices = []
        for v in verts:
            self.vertices.append(self.center+np.array(v))

        self.edges = [(0, 4), (0, 5), (0, 8), (0, 10), (0, 1),
                      (1, 6), (1, 7), (1, 8), (1, 10),
                      (2, 4), (2, 5), (2, 9), (2, 11), (2, 3),
                      (3, 6), (3, 7), (3, 9), (3, 11),
                      (4, 8), (4, 9), (4, 5),
                      (5, 10), (5, 11),
                      (6, 8), (6, 9), (6, 7),
                      (7, 10), (7, 11),
                      (8, 9),
                      (10, 11)]

        self.rotate(angle, rot_vector, self.center)

    def moment_of_inertia(self):
        m = (4*PHI**2/10)*self.mass*self.size**2
        I = m*np.eye(3)
        return I


if __name__ == "__main__":
    center1 = (0, 0, 0)
    shape1 = Cube(center1, angle=.1, rot_vector=(1, 2, 3))
    shape1.rotate(-.1, (1, 2, 3), (1, 0, 0))
    print(shape1.get_vertices())
    print(shape1.center)
