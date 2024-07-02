
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

from model.j import j


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
    qb_value = j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)
    return qb_value


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

    if ef == 1 and ef2 is None: # Darcy and Vogel
        if pr > pb:  # Undersaturated reservoir
            if pwf_test >= pb:
                aof_value = j(q_test, pwf_test, pr, pb) * pr
            elif pwf_test < pb:
                aof_value = qb(q_test, pwf_test, pr, pb, ef=1) + (
                    (j(q_test, pwf_test, pr, pb) / 1.8))
        else:  # Saturated reservoir
            aof_value = q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)

    elif ef < 1 and ef2 is None:  # Standing
        if pr > pb:
            if pwf_test >= pb:
                aof_value = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                aof_value = qb(q_test, pwf_test, pr, pb, ef) + (
                        (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                                    1.8 - 0.8 * ef)
        else:
            aof_value = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                                1.8 * ef - 0.8 * ef ** 2)

    elif ef > 1 and ef2 is None: # Darcy and Standing
        if pr > pb:
            if pwf_test >= pb:
                aof_value = j(q_test, pwf_test, pr, pb, ef) * pr
            elif pwf_test < pb:
                aof_value = qb(q_test, pwf_test, pr, pb, ef) + (
                        (j(q_test, pwf_test, pr, pb, ef) * pb) / 1.8) * (
                                    0.624 + 0.376 * ef)
        else:
            aof_value = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                                0.624 + 0.376 * ef)

    elif ef < 1 and ef2 >= 1:  # Darcy and Standing
        if pr > pb:
            if pwf_test >= pb:
                aof_value = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                aof_value = qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                        j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                                    0.624 + 0.376 * ef2)
        else:
            aof_value = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                                0.624 + 0.376 * ef2)

    elif (ef > 1 and ef2 <= 1):
        if pr > pb:
            if pwf_test >= pb:
                aof_value = j(q_test, pwf_test, pr, pb, ef, ef2) * pr
            elif pwf_test < pb:
                aof_value = qb(q_test, pwf_test, pr, pb, ef, ef2) + (
                        j(q_test, pwf_test, pr, pb, ef, ef2) * pb / 1.8) * (
                                    1.8 - 0.8 * ef2)
        else:
            aof_value = (q_test / (1.8 * ef * (1 - pwf_test / pr) - 0.8 * ef ** 2 * (
                    1 - pwf_test / pr) ** 2)) * (
                                1.8 * ef - 0.8 * ef ** 2)
    return aof_value


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


# Qo (bpd) @ Vogel Conditions
def qo_ipr_compuesto(q_test: float,
                     pwf_test: float,
                     pr: float,
                     pwf: float,
                     pb: float):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom-hole pressure during test
    :param pr: Reservoir Pressure
    :param pwf: Flowing bottom-hole pressure
    :param pb: Bubble-point pressure
    :return: Oil Production rate
    """

    if pr > pb:  # Saturated reservoir
        if pwf >= pb:
            qo = qo_darcy(q_test, pwf_test, pr, pwf, pb)
        elif pwf < pb:
            qo = qb(q_test, pwf_test, pr, pb) + \
                 ((j(q_test, pwf_test, pr, pb) * pb) / 1.8) * \
                 (1 - 0.2 * (pwf / pb) - 0.8 * (pwf / pb) ** 2)

    elif pr <= pb:  # Undersaturated reservoir
        qo = aof(q_test, pwf_test, pr, pb) * \
             (1 - 0.2 * (pwf / pr) - 0.8 * (pwf / pr) ** 2)
    return qo


# Qo (bpd) @ Standing Conditions
def qo_standing(q_test: float,
                pwf_test: float,
                pr: float,
                pwf: float,
                pb: float,
                ef: float = 1,
                ef2: float = None):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom hole pressure during test
    :param pr: Reservoir pressure
    :param pwf: Flowing bottom-hole pressure
    :param pb: Bubble-point pressure
    :param ef: Efficiency factor
    :param ef2: Additional efficiency factor (optional)
    :return: Oil Production rate
    """

    qo = aof(q_test, pwf_test, pr, pb, ef=1) * (
            1.8 * ef * (1 - pwf / pr) - 0.8 * ef ** 2 * (1 - pwf / pr) ** 2)
    return qo


# Qo (bpd) @ all conditions
def qo(q_test: float,
       pwf_test: float,
       pr: float,
       pwf: float,
       pb: float,
       ef: float = 1,
       ef2: float = None):
    """
    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom hole pressure during test
    :param pr: Reservoir pressure
    :param pwf: Flowing bottom-hole pressure
    :param pb: Bubble-point pressure
    :param ef: Efficiency factor
    :param ef2: Additional efficiency factor (optional)
    :return: Oil Production rate
    """

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

