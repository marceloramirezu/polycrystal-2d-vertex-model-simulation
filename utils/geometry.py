from tkinter.tix import TCL_WINDOW_EVENTS
from scipy.spatial import distance
import math 
import numpy as np



def wrap_distances(vi, vf):
    xi = vi[0]
    yi = vi[1]
    xf = vf[0]
    yf = vf[1]
    dist_x = np.absolute(xf-xi)
    dist_y = np.absolute(yf-yi)
    x_dist_wrap = dist_x > 0.5
    y_dist_wrap = dist_y > 0.5
    wrap = False

    if(x_dist_wrap and xi <= 0.5):
        xf = xf-1
        dist_x = np.absolute(xf-xi)
        wrap = True
    elif(x_dist_wrap and xi > 0.5):
        xf = xf+1
        dist_x = np.absolute(xf-xi)
        wrap = True
    else:
        pass

    if(y_dist_wrap and yi <= 0.5):
        yf = yf-1
        dist_y = np.absolute(yf-yi)
        wrap = True
    elif(y_dist_wrap and yi > 0.5):
        yf = yf+1
        dist_y = np.absolute(yf-yi)
        wrap = True
    else:
        pass
    
    arc_len = np.sqrt( np.power(dist_x, 2) + np.power(dist_y, 2) )
    dict_return = {
        "xi":[xi,yi],
        "xf":[xf,yf],
        "wrap":wrap,
        "dist_x":dist_x,
        "dist_y":dist_y,
        "delta_x": (xf-xi),
        "delta_y": (yf-yi),
        "arc_len":arc_len
    }
    return dict_return


def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy