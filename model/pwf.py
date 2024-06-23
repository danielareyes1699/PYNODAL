# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

from model.j import j
from model.q import aof

# %%

def pwf_darcy(q_test: float,
              pwf_test: float,
              q: float,
              pr: float,
              pb: float):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom pressure during test
    :param q: Current flow rate
    :param pr: Reservoir pressure
    :param pb: Bubble-point pressure
    :return: Flowing bottom pressure
    """
    pwf = pr - (q / j(q_test, pwf_test, pr, pb))
    return pwf


# Quicktest
q_test = 1000
pwf_test = 1500
q = 800
pr = 3000
pb = 2000

pwf = pwf_darcy(q_test, pwf_test, q, pr, pb)
print("The calculated Flowing pressure is:", pwf)


# %%

# Pwf when Pr < Pb (Saturated reservoir)

def pwf_vogel(q_test: float,
              pwf_test: float,
              q: float,
              pr: float,
              pb: float):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom pressure during test
    :param q: Current flow rate
    :param pr: Reservoir pressure
    :param pb: Bubble-point pressure
    :return: Flowing bottom pressure
    """
    pwf = 0.125 * pr * (-1 + np.sqrt(81 - 80 * q / aof(q_test, pwf_test, pr, pb)))
    return pwf


# Quicktest
q_test = 1000
pwf_test = 1500
q = 800
pr = 2500
pb = 3000

pwf = pwf_vogel(q_test, pwf_test, q, pr, pb)
print("The calculated flowing bottom pressure is:", pwf)