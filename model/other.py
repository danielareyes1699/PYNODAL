# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

# %%

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


# Quicktest
q = 500
id = 6
c = 120

f = f_darcy(q, id, c)
print("The calculated friction factor is:", f)


# %%

# SGOil using API
def sg_oil(api: float):
    """

    :param api: Petroleum API Gravity
    :return: Specific gravity of oil
    """
    sg_oil_value = 141.5 / (131.5 + api)
    return sg_oil_value


# Quicktest
api_test = 30

sg_value = sg_oil(api_test)
print("The Specific Gravity of petroleum is:", sg_value)


# %%

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


# Quicktest
api = 30
wc = 0.2
sg_h20 = 1.0

sg_average = sg_avg(api, wc, sg_h20)
print("The average specific gravity of fluids is:", sg_average)


# %%

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


# Quick test
api = 30
wc = 0.2
sg_h20 = 1.0

g_average = gradient_avg(api, wc, sg_h20)
print("The average Gradient is:", g_average)
