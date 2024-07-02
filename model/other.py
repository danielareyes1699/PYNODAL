
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# Friction factor (f) from darcy-weisbach equation

def f_darcy(q: float,
            id: float,
            c: float = 120):
    """

    :param q: Volumetric flow rate
    :param id: Pipe inner diameter
    :param c: Roughness coefficient
    :return: Friction factor
    """
    f = (2.083 * (((100 * q) / (34.3 * c)) ** 1.85 * (1 / id) ** 4.8655)) / 1000
    return f


# SGOil using API
def sg_oil(api: float):
    """

    :param api: Petroleum API Gravity
    :return: Specific gravity of oil
    """
    sg_oil_value = 141.5 / (131.5 + api)
    return sg_oil_value


# SG average of fluids
def sg_avg(api: float,
           wc: float,
           sg_h2o: float):
    """

    :param api: API gravity of oil
    :param wc: Water cut in the fluid
    :param sg_h2o: Specific gravity of water
    :return: Average specific gravity of fluids
    """
    sg_avg = wc * sg_h2o + (1 - wc) * sg_oil(api)
    return sg_avg


# Average Gradient using fresh water gradient (0.433 psi/ft)
def gradient_avg(api: float,
                 wc: float,
                 sg_h2o: float):
    """

    :param api: API gravity of oil
    :param wc: Fraction of water in the fluid
    :param sg_h2o: Specific gravity of water
    :return: Average gradient
    """
    g_avg = sg_avg(api, wc, sg_h2o) * 0.433
    return g_avg

