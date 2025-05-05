
import numpy as np
import pdb

import math
import pickle


class Dimensions:
    def __init__(self, l, w, il, iw, d2ex, d2ey, gs, gd, cmr, f_il):
        self.fl = int(f_il)
        self.hs = f_il/(2*d2ex+il)
        self.l = int(l)
        self.w = int(w)
        self.d2ex = int(d2ex*self.hs) # distance from LED to edge (x axis)
        self.d2ey = int(d2ey*self.hs) # distance from LED to edge (y axis)
        self.il = self.fl-2*self.d2ex # inner length (between LEDs)
        self.iw = int(iw*self.hs) # inner width (between LEDs)
        self.fw = 2*self.d2ey+self.iw
        self.gs = int(gs*self.hs) # goal size
        self.gd = int(gd*self.hs) # goal depth
        self.pr = int(cmr*self.hs) # puck radius

    def save_to_file(self, filename):
        with open(filename, 'wb') as file:
            pickle.dump(self, file)

    @staticmethod
    def load_from_file(filename):
        with open(filename, 'rb') as file:
            return pickle.load(file)


def get_dimensions(nat_res_x, nat_res_y, final_res_x):

    dim = Dimensions(nat_res_x, nat_res_y, 288, 174, 76, 56, 90, 10, 20, final_res_x)
    return dim


def get_shapes(dim, vis_scale):

    # pdb.set_trace()

    tl = [(0)*vis_scale, (0)*vis_scale]
    tr = [(dim.fl-1)*vis_scale, (0)*vis_scale]
    bl = [(0)*vis_scale, (dim.fw-1)*vis_scale]
    br = [(dim.fl-1)*vis_scale, (dim.fw-1)*vis_scale]

    field = [bl, tl, tr, br]

    line = [(int(dim.fl/2)*vis_scale, (0)*vis_scale), (int(dim.fl/2)*vis_scale, (dim.fw-1)*vis_scale)]

    c1 = [(dim.d2ex)*vis_scale, (dim.d2ey+dim.iw)*vis_scale]
    c2 = [(dim.d2ex)*vis_scale, (dim.d2ey)*vis_scale]
    c3 = [(dim.d2ex+dim.il)*vis_scale, (dim.d2ey)*vis_scale]
    c4 = [(dim.d2ex+dim.il)*vis_scale, (dim.d2ey+dim.iw)*vis_scale]
    c5 = [(dim.d2ex+int(dim.il/2))*vis_scale, (dim.d2ey+int(dim.iw/2))*vis_scale]

    circles = [c1, c2, c3, c4, c5]
    radius = dim.cmr*vis_scale

    # Coordinates of rectangles that define the goals
    gu = int((dim.fw-dim.gs)/2)*vis_scale
    gb = gu + dim.gs*vis_scale
    gl_l = (0)*vis_scale
    gl_r = (dim.gd)*vis_scale
    gr_l = (dim.fl-dim.gd)*vis_scale
    gr_r = (dim.fl-1)*vis_scale
    goal_1 = [[gl_l,gu], [gl_r, gu], [gl_r, gb], [gl_l, gb]]
    goal_2 = [[gr_l,gu], [gr_r, gu], [gr_r, gb], [gr_l, gb]]
    goals = [goal_1, goal_2]

    # pdb.set_trace()
    return field, line, goals, circles, radius


def get_test_resolutions(x, y, k):

    idx = 0
    resolutions = []
    for d in np.linspace(1, 0.1, 30):
        a = (x - k) * (y - k)
        b = k * (x + y - 2 * k)
        c = k * k - x * y * d

        e = (-b + math.sqrt(b * b - 4 * a * c)) / (2 * a)

        new_x = int((x - k) * e + k)
        new_y = int((y - k) * e + k)
        resolutions.append((new_x, new_y))
        idx += 1
    return resolutions

def get_max_res_and_k_size():

    dim = Dimensions.load_from_file('../common/homdim.pkl')
    np_kernel = np.load(f"../common/fast_kernel.npy")
    k_sz = len(np_kernel)

    return dim.fl, dim.fw, k_sz