import numpy as np
# Productivity Index (darcy law)

def j_darcy(ko: float,
            h: float,
            bo: float,
            uo: float,
            re: float,
            rw: float,
            s: float,
            flow_regime: str = "pseudocontinue")-> float:
    """

    :param ko: oil permeability
    :param h: thickness of sand
    :param bo: oil volumetric factor
    :param uo: oil viscosity
    :param re: drainage radius
    :param rw: well radius
    :param s: skin
    :param flow_regime: flow regime
    :return: productivity Index (IP) of Darcy
    """
    if flow_regime == "pseudoncontinue":
        J_darcy = ko * h / (141.2 * bo * uo * (np.log(re / rw) - 0.75 + s))
    elif flow_regime == "continuo":
        J_darcy = ko * h / (141.2 * bo * uo * (np.log(re / rw) + s))
    return J_darcy

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
