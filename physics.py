import numpy as np


gamma = .8  # Dissipation on bounce
slow_rotation = .1


class simulation():
    def __init__(self, shape_list):
        self.flag = True



        self.shapes = shape_list

        self.num_shapes = len(shape_list)

        self.velocities = np.zeros((self.num_shapes, 3))
        self.omegas = np.zeros((self.num_shapes, 3))

    def gravity(self, dt):
        for i, s in enumerate(self.shapes):
            a = np.array([0, -9.81, 0])  # Accelerate in -y direction
            v = self.velocities[i]

            lowestY = min([v[1] for v in s.vertices])
            if lowestY > 0:
                self.velocities[i] = v+a*dt
            s.translate(v*dt)

    def boundaries(self):
        bounced_list = []
        for i, s in enumerate(self.shapes):
            lowestY_ind = np.argmin([v[1] for v in s.vertices])
            lowestY = s.vertices[lowestY_ind][1]

            if lowestY <= 0:
                s.translate([0, -1*lowestY, 0])
                newv = self.velocities[i][1]*-1*gamma
                if newv < gamma**10:
                    newv = 0
                dv = newv-self.velocities[i][1]
                self.velocities[i][1] = newv

                bounced_list.append((s.vertices[lowestY_ind], [0, dv, 0]))
            else:
                bounced_list.append(None)

        return bounced_list

    def torque(self, dt, bounced_list):
        for i, s in enumerate(self.shapes):
            w = self.omegas[i]

            if bounced_list[i] is not None:
                """
                F = dp/dt
                tau = I dw/dt = rxF
                I dw = rxF dt
                dw = I^(-1) rXdp
                """
                MOI = s.MOI
                r = bounced_list[i][0]-s.center
                dv = bounced_list[i][1]
                print(r, dv, np.cross(r, dv))
                self.omegas[i] = slow_rotation*gamma*np.dot(s.mass*np.linalg.inv(MOI), np.cross(r, dv))

            theta = dt*np.sqrt(w[0]**2+w[1]**2+w[2]**2)
            if theta > 0:
                s.rotate(theta, w)

    def step(self, dt):
        self.gravity(dt)
        bounced_list = self.boundaries()
        self.torque(dt, bounced_list)
        # self.interactions()
