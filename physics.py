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

        self.acc = np.array([0, -9.81, 0])  # Accelerate in -y direction

    def gravity(self, dt):
        for i, s in enumerate(self.shapes):
            a = self.acc
            v = self.velocities[i]

            lowestY = min([vert[1] for vert in s.vertices])
            if lowestY > 0:
                self.velocities[i] = v+a*dt

            s.translate(v*dt)

    def boundaries(self, dt):
        bounce_limit = gamma**7
        tol = .01
        for i, s in enumerate(self.shapes):
            w = self.omegas[i]
            lowestY_ind = np.argmin([v[1] for v in s.vertices])
            lowestY = s.vertices[lowestY_ind][1]

            if lowestY <= 0:
                # Move back above boundary, reverse velocity, apply damping
                s.translate([0, -1*lowestY, 0])
                newv = -1*self.velocities[i][1]*gamma
                if newv < bounce_limit:
                    newv = 0

                dv = newv-self.velocities[i][1]
                self.velocities[i][1] = newv

                # Torque due to impacting the floor
                if newv > bounce_limit:
                    """
                    F = dp/dt
                    tau = I dw/dt = rxF
                    I dw = rxF dt
                    dw = I^(-1) rXdp
                    """
                    MOI = s.MOI
                    r = s.get_lever_arm()
                    self.omegas[i] = slow_rotation*gamma*np.dot(s.mass*np.linalg.inv(MOI), np.cross(r, [0, dv, 0]))

            if lowestY < tol:
                r = s.get_lever_arm()
                MOI = s.parralel_axis(r)
                F = s.mass*self.acc
                dw = np.dot(np.linalg.inv(MOI), np.cross(-1*r, F)*dt)
                self.omegas[i] = (gamma*self.omegas[i]+dw)

                # Rotation about contact
                w = self.omegas[i]

                theta = dt*np.sqrt(w[0]**2+w[1]**2+w[2]**2)
                if theta > 0:
                    s.rotate(theta, w, r+s.center)
            else:
                # Rotation about center
                w = self.omegas[i]

                theta = dt*np.sqrt(w[0]**2+w[1]**2+w[2]**2)
                if theta > 0:
                    s.rotate(theta, w, s.center)

    def step(self, dt):
        self.gravity(dt)
        self.boundaries(dt)
        # self.interactions()
