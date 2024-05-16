import numpy as np

# Productivity Index (darcy law)

def j_darcy(ko: float,
            h: float,
            bo: float,
            uo: float,
            re: float,
            rw: float,
            s: float,
            flow_regime: str = "pseudocontinue") -> float:
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


# Productivity Index

def j(q_test: float,
      pwf_test: float,
      pr: float,
      pb: float,
      ef: float = 1,
      ef2: float = None) -> float:
    """

    :param q_test:  production rate
    :param pwf_test: bottom pressure
    :param pr: reservoir pressure
    :param pb: bubble pressure
    :param ef: efficiency 1
    :param ef2: efficiency 2
    :return: Productivity Index
    """
    if ef == 1:
        if pwf_test >= pb:
            J = q_test / (pr - pwf_test)
        else:
            J = q_test / ((pr - pb) + (pb / 1.8) * \
                          (1 - 0.2 * (pwf_test / pb) - 0.8 * (pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is None:
        if pwf_test >= pb:
            J = q_test / (pr - pwf_test)
        else:
            J = q_test / ((pr - pb) + (pb / 1.8) * \
                          (1.8 * (1 - pwf_test / pb) - 0.8 * ef * (1 - pwf_test / pb) ** 2))
    elif ef != 1 and ef2 is not None:
        if pwf_test >= pb:
            J = ((q_test / (pr - pwf_test)) / ef) * ef2
        else:
            J = ((q_test / (pr - pb) + (pb / 1.8) * \
                  (1.8 * (1 - pwf_test / pb) - 0.8 * \
                   ef * (1 - pwf_test / pb) ** 2)) / ef) * ef2
    return J

# Quicktest
# Case 1: ef = 1 (default), pwf_test >= pb
q_test = 1000
pwf_test = 200
pr = 1500
pb = 500

productivity_index = J(q_test, pwf_test, pr, pb)
print("Productivity Index (ef=1, pwf_test >= pb): ", productivity_index)


# Bottom hole flow rate
# Q(bpd) @ Pb

def Qb(q_test: float,
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


# Absolute Open Flow
# Maximum production capacity
# AOF(bpd)
# j was calculated above

def aof(q_test: float,
        pwf_test: float,
        pr: float,
        pb: float,
        ef: float = 1,
        ef2: float = None):
    """

    :param q_test:  production rate
    :param pwf_test: bottom pressure
    :param pr: reservoir pressure
    :param pb: bubble pressure
    :param ef: efficiency 1
    :param ef2: efficiency 2
    :return: Absolute Open Flow
    """
    if (ef == 1 and ef2 is None):
        if pr > pb:  # Undersaturated reservoir
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef=1) + (
                    (j(q_test, pwf_test, pr, pb) / 1.8))
        else:  # Saturated reservoir
            AOF = q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)

    elif (ef < 1 and ef2 is None):
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb ,ef) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef) + (
                        (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                        1.8 - 0.8 * ef)
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                1 - pwf_test / pr) ** 2)) * (
                1.8 * ef - 0.8 * ef ** 2)

    elif (ef > 1 and ef2 is None):
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef) + (
                    (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                    0.624 + 0.376 * ef)
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                1 - pwf_test / pr) ** 2)) * (
                0.624 + 0.376 * ef)

    elif (ef < 1 and ef2 >= 1):
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                    j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                    0.624 + 0.376 * ef2)
        else:
            AOF = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                1 - pwf_test / pr) ** 2)) * (
                0.624 + 0.376 * ef2)

    elif (ef > 1 and ef2 <= 1):
        if pr > pb:
            if pwf_test >= pb:
                AOF = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                AOF = Qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                    j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                    1.8 - 0.8 * ef2)
        else:
            AOF = (q_test / (1.8 * ef * (1- pwf_test / pr) - 0.8 * ef ** 2 * (
                1- pwf_test / pr) ** 2)) * (
                1.8 * ef - 0.8 * ef ** 2)
    return AOF

# Quicktest with hypothetical values
q_test_val = 100
pwf_test_val = 2000
pr_val = 3000
pb_val = 1000

# Try with ef = 1 (default efficiency)
aof_result = aof(q_test_val, pwf_test_val, pr_val, pb_val)
print("AOF (ef=1): ", aof_result)
