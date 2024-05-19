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
            j = q_test / (pr - pwf_test)
        else:
            j = q_test / ((pr - pb) + (pb / 1.8) *
                          (1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is None:
        if pwf_test >= pb:
            j = q_test / (pr - pwf_test)
        else:
            j = q_test / ((pr - pb) + (pb / 1.8) *
                          (1.8 * (1 - pwf_test / pb) - 0.8 * ef * (1 - pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is not None:
        if pwf_test >= pb:
            j = ((q_test / (pr - pwf_test)) / ef) * ef2
        else:
            j = ((q_test / (pr - pb) + (pb / 1.8) *
                  (1.8 * (1 - pwf_test / pb) - 0.8 *
                   ef * (1 - pwf_test / pb) ** 2)) / ef) * ef2
    return j


# Quicktest
# Case 1: ef = 1 (default), pwf_test >= pb
q_test = 1000
pwf_test = 200
pr = 1500
pb = 500

productivity_index = j(q_test, pwf_test, pr, pb)
print("Productivity Index (ef=1, pwf_test >= pb): ", productivity_index)


# %%

# Calculate the Bottom hole flow rate
# Q(bpd) @ Pb

def qb(
    q_test: float,
    pwf_test: float,
    pr: float,
    pb: float,
    ef: float = 1,
    ef2: float = None):
    """

    :param q_test: production rate
    :param pwf_test: bottom pressure
    :param pr: reservoir pressure
    :param pb:  bubble pressure
    :param ef: efficiency 1
    :param ef2: efficiency 2
    :return: Bottom hole flow rate
    """
    qb = j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)
    return qb

# Quicktest
# Example values for testing
q_test = 1000
pwf_test = 200
pr = 1500
pb = 500
ef = 1
ef2 = None

bottom_hole_flow_rate = qb(q_test, pwf_test, pr, pb, ef, ef2)
print("Bottom hole flow rate:", bottom_hole_flow_rate)


# %%
# Calculate the Absolute Open Flow
# Maximum production capacity
# AOF(bpd)
# j was calculated above

def aof(
    q_test: float,
    pwf_test: float,
    pr: float,
    pb: float,
    ef: float = 1,
    ef2: float = None
) -> float:
    """

    :param q_test:  production rate
    :param pwf_test: bottom pressure
    :param pr: reservoir pressure
    :param pb: bubble pressure
    :param ef: efficiency 1
    :param ef2: efficiency 2
    :return: Absolute Open Flow
    """
    if ef == 1 and ef2 is None:
        if pr > pb:  # Undersaturated reservoir
            if pwf_test >= pb:
                aof = j(q_test, pwf_test, pr, pb) * pr
            elif pwf_test < pb:
                aof = qb(q_test, pwf_test, pr, pb, ef=1) + (
                    (j(q_test, pwf_test, pr, pb) / 1.8))
        else:  # Saturated reservoir
            aof = q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)

    elif ef < 1 and ef2 is None:
        if pr > pb:
            if pwf_test >= pb:
                aof = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                aof = qb(q_test, pwf_test, pr, pb, ef) + (
                        (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                              1.8 - 0.8 * ef)
        else:
            aof = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                          1.8 * ef - 0.8 * ef ** 2)

    elif ef > 1 and ef2 is None:
        if pr > pb:
            if pwf_test >= pb:
                aof = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                aof = qb(q_test, pwf_test, pr, pb, ef) + (
                        (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                              0.624 + 0.376 * ef)
        else:
            aof = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                          0.624 + 0.376 * ef)

    elif ef < 1 and ef2 >= 1:
        if pr > pb:
            if pwf_test >= pb:
                aof = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                aof = qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                        j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                              0.624 + 0.376 * ef2)
        else:
            aof = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                          0.624 + 0.376 * ef2)

    elif (ef > 1 and ef2 <= 1):
        if pr > pb:
            if pwf_test >= pb:
                aof = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                aof = qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                        j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                              1.8 - 0.8 * ef2)
        else:
            aof = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                          1.8 * ef - 0.8 * ef ** 2)
    return aof


# Quicktest
# Example values for testing

q_test_val = 1000
pwf_test_val = 200
pr_val = 1500
pb_val = 500

# Case 1: ef = 1, ef2 = None
ef = 1
ef2 = None
aof_value = aof(q_test, pwf_test, pr, pb, ef, ef2)
print("Absolute Open Flow (ef=1, ef2=None):", aof_value)

# Case 2: ef < 1, ef2= None
ef = 0.8
aof_value = aof(q_test, pwf_test, pr, pb, ef, ef2)
print("Absolute Open Flow (ef=0,8, ef2=None):", aof_value)

# Case 3: ef > 1, ef2= None
ef = 1.2
aof_value = aof(q_test, pwf_test, pr, pb, ef, ef2)
print("Absolute Open Flow (ef=1.2, ef2=None):", aof_value)

# Case 4: ef < 1, ef2 >= 1
ef= 0.8
ef2: 1.2
aof_value = aof(q_test, pwf_test, pr, pb, ef, ef2)
print("Absolute Open Flow (ef=0.8, ef2=1.2):", aof_value)

# Case 5: ef > 1, ef2 <= 1
ef = 1.2
ef2 = 0.8
aof_value = aof(q_test, pwf_test, pr, pb, ef, ef2)
print("Absolute Open Flow (ef=1.2, ef2=0.8):", aof_value)


# %%

# Calculate the oil flow rate under Darcy conditions.
# Qo (bpd) @ Darcy Conditions

def qo_darcy(
    q_test: float,
    pwf_test: float,
    pr: float,
    pwf: float,
    pb: float,
    ef: float = 1,
    ef2: float = None
) -> float:
    """

    :param q_test: Production rate
    :param pwf_test: Bottom pressure during test
    :param pr: Reservoir pressure
    :param pwf: Bottom hole flowing pressure
    :param pb: Bubble pressure
    :param ef: Efficiency 1 (default is 1)
    :param ef2: Efficiency 2 (optional)
    :return: Oil flow rate under Darcy conditions
    """
    qo = j(q_test, pwf_test, pr, pb) * (pr - pwf)
    return qo

# Quicktest
# Example values for testing
q_test = 1000
pwf_test = 200
pr = 1500
pwf = 300
pb = 500

# Case 1: ef = 1, ef2= None
ef = 1
ef2 = None
qo_value = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Darcy conditions (ef=1, ef2=None):", qo_value)

# Case 2: ef < 1, ef2 = None
ef = 0.8
qo_value = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Darcy conditions (ef=0.8, ef2=None):", qo_value)

# Case 3: ef > 1, ef2 = None
ef = 1.2
qo_value = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Darcy conditions (ef=1.2, ef2=None):", qo_value)

# Case 4: ef < 1, ef2 = 1
ef = 0.8
ef2 = 1.2
qo_value = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Darcy conditions (ef=0.8, ef2=1.2):", qo_value)

# Case 5: ef > 1, ef2 <= 1
ef = 1.2
ef2 = 0.8
qo_value = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Darcy conditions (ef=1.2, ef2=0.8):", qo_value)


# %%

# Qo (bpd) @ Vogel Conditions
def qo_vogel(
    q_test: float,
    pwf_test: float,
    pr: float,
    pwf: float,
    pb: float,
    ef: float = 1,
    ef2: float = None
) -> float:
    """

    :param q_test: Production rate during test
    :param pwf_test: Bottom hole flowing pressure during test
    :param pr: Reservoir pressure
    :param pwf: Bottom hole flowing pressure
    :param pb: Bubble point pressure
    :param ef:  Efficiency 1 (default 1)
    :param ef2: Efficiency 2 (optional)
    :return: Oil flow rate under Vogel conditions
    """
    qo = aof(q_test, pwf_test, pr, pb) * \
         (1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr) ** 2)
    return qo


# Quicktest
# Example values for testing
q_test = 1000
pwf_test = 200
pr = 1500
pwf = 300
pb = 500


# Case 1: ef = 1, ef2= None
ef = 1
ef2 = None
qo_value = qo_vogel(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Vogel conditions (ef=1, ef2=None):", qo_value)

# Case 2: ef < 1, ef2 = None
ef = 0.8
qo_value = qo_vogel(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Vogel conditions (ef=0.8, ef2=None):", qo_value)

# Case 3: ef > 1, ef2 = None
ef = 1.2
qo_value = qo_vogel(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Vogel conditions (ef=1.2, ef2=None):", qo_value)

# Case 4: ef < 1, ef2 = 1
ef = 0.8
ef2 = 1.2
qo_value = qo_vogel(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Vogel conditions (ef=0.8, ef2=1.2):", qo_value)

# Case 5: ef > 1, ef2 <= 1
ef = 1.2
ef2 = 0.8
qo_value = qo_vogel(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil flow rate under Vogel conditions (ef=1.2, ef2=0.8):", qo_value)


# %%
# Qo (bpd) @ Vogel Conditions
def qo_ipr_compuesto(q_test, pwf_test, pr, pwf, pb):
    if pr > pb:  # Saturated reservoir
        if pr >= pb:
            qo = qb(q_test, pwf_test, pr, pb) + \
                 ((j(q_test, pwf_test, pr, pb) * pb) / 1.8) * \
                 (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)

    elif pr <= pb:  # Undersaturated reservoir
        qo = aof(q_test, pwf_test, pr, pb) * \
             (1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr) ** 2)
    return qo


# %%
# Qo (bpd) @ Standing Conditions
def qo_standing(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    qo = aof(q_test, pwf_test, pr, pb, ef=1) * (
            1.8 * ef * (1 - pwf / pr) - 0.8 * ef ** 2 * (1 - pwf / pr) ** 2)
    return qo


# %%
# Qo (bpd) @ all conditions
def qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None):
    if ef == 1 and ef2 is None:
        if pr > pb:  # Saturated reservoir
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb)
            elif pwf < pb:
                qo = qb(q_test, pwf_test, pr, pb) + \
                     ((j(q_test, pwf_test, pr, pb) * pb) / 1.8) * \
                     (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)
        else:  # Subsaturated reservoir
            qo = qo_vogel(q_test, pwf_test, pr, pwf, pb)

    elif ef != 1 and ef2 is None:
        if pr > pb:  # Subsaturated reservoir
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
            elif pwf < pb:
                qo = qb(q_test, pwf_test, pwf, pb, ef) + \
                     ((j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * \
                     (1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb) ** 2)
        else:  # Saturated reservoir
            qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef)

    elif ef != 1 and ef2 is not None:
        if pr > pb:  # Subsaturated reservoir
            if pwf >= pb:
                qo = qo_darcy(q_test, pwf_test, pr, pwf, pb, ef, ef2)
            elif pwf < pb:
                qo = qb(q_test, pwf_test, pr, pb, ef, ef2) + \
                     ((j(q_test, pwf_test, pr, pb, ef, ef2) * pb) / 1.8) * \
                     (1.8 * (1 - pwf / pb) - 0.8 * ef * (1 - pwf / pb) ** 2)
            else:  # Saturated reservoir
                qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef, ef2)
    return qo



# IPR CURVE

