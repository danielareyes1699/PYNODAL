# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline


# %%

# Productivity Index using Darcy's Law
def j_darcy(
        ko: float,
        h: float,
        bo: float,
        uo: float,
        re: float,
        rw: float,
        s: float,
        flow_regime: str = "pseudocontinue"
) -> float:
    """

    :param ko: Oil permeability
    :param h: Thickness of sand
    :param bo: Oil volumetric factor
    :param uo: Oil viscosity
    :param re: Drainage radius
    :param rw: Well radius
    :param s: Skin
    :param flow_regime: flow regime
    :return: Productivity Index (IP) of Darcy
    """
    if flow_regime == "pseudocontinue":
        j_darcy = ko * h / (141.2 * bo * uo * (np.log(re / rw) - 0.75 + s))
        return j_darcy
    elif flow_regime == "continuo":
        j_darcy = ko * h / (141.2 * bo * uo * (np.log(re / rw) + s))
        return j_darcy
    else:
        print("There is not flow regime.")


# Quicktest
# Case 1: Pseudocontinue
ko = 100
h = 50
bo = 1.2
uo = 0.5
re = 500
rw = 5
s = 1
flow_regime = "pseudocontinue"

J = j_darcy(ko, h, bo, uo, re, rw, s, flow_regime)
print("Productivity Index: ", J)


# %%
# Productivity Index

def j(
        q_test: float,
        pwf_test: float,
        pr: float,
        pb: float,
        ef: float = 1,
        ef2: float = None
) -> float:
    """

    :param q_test:  Production rate
    :param pwf_test: Bottom pressure
    :param pr: Reservoir pressure
    :param pb: Bubble pressure
    :param ef: Efficiency 1
    :param ef2: Efficiency 2
    :return: Productivity Index
    """

    if ef == 1:
        if pwf_test >= pb:
            j_value = q_test / (pr - pwf_test)
        else:
            j_value = q_test / ((pr - pb) + (pb / 1.8) *
                                (1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is None:
        if pwf_test >= pb:
            j_value = q_test / (pr - pwf_test)
        else:
            j_value = q_test / ((pr - pb) + (pb / 1.8) *
                                (1.8 * (1 - pwf_test / pb) - 0.8 * ef * (1 - pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is not None:
        if pwf_test >= pb:
            j_value = ((q_test / (pr - pwf_test)) / ef) * ef2
        else:
            j_value = ((q_test / (pr - pb) + (pb / 1.8) *
                        (1.8 * (1 - pwf_test / pb) - 0.8 *
                         ef * (1 - pwf_test / pb) ** 2)) / ef) * ef2
    return j_value


# Quicktest
# Case 1: ef = 1 (default), pwf_test >= pb
q_test = 1000
pwf_test = 200
pr = 1500
pb = 500

productivity_index = j(q_test, pwf_test, pr, pb)
print("Productivity Index (ef=1, pwf_test >= pb): ", productivity_index)