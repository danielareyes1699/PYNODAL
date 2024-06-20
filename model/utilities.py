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
    qb_value = j(q_test, pwf_test, pr, pb, ef, ef2) * (pr - pb)
    return qb_value


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
                aof_value = j(q_test, pwf_test, pr, pb) * pr
            elif pwf_test < pb:
                aof_value = qb(q_test, pwf_test, pr, pb, ef=1) + (
                    (j(q_test, pwf_test, pr, pb) / 1.8))
        else:  # Saturated reservoir
            aof_value = q_test / (1 - 0.2 * (pwf_test / pr) - 0.8 * (pwf_test / pr) ** 2)

    elif ef < 1 and ef2 is None:
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

    elif ef > 1 and ef2 is None:
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

    elif ef < 1 and ef2 >= 1:
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
ef = 0.8
ef2 = 1.2
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


# Quicktest

q_test = 500
pwf_test = 2500
pr = 3000
pwf = 1500
pb = 2800

qo = qo_ipr_compuesto(q_test, pwf_test, pr, pwf, pb)
print("Oil Production rate (Qo):", qo)


# %%
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


# Quicktest

q_test = 500
pwf_test = 2500
pr = 3000
pwf = 1550
pb = 2800
ef = 1

qo = qo_standing(q_test, pwf_test, pr, pwf, pb, ef)
print("Oil Production rate (Qo):", qo)


# %%
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


# Quicktest

q_test = 500
pwf_test = 2500
pr = 3000
pwf = 1500
pb = 2800
ef = 1
ef2 = None

qo_result = qo(q_test, pwf_test, pr, pwf, pb, ef, ef2)
print("Oil Production rate (Qo):", qo_result)


# %%

# IPR CURVE

def IPR_curve(q_test: float,
              pwf_test: float,
              pr: float,
              pwf: list,
              pb: float):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom hole pressure during test
    :param pr: Reservoir pressure
    :param pwf: List of flowing bottom pressures
    :param pb: Bubble-point pressure
    :return: None
    """

    # Creating Dataframe
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    df['Qo(bpd)'] = df['Pwf(psia)'].apply(
        lambda x: qo_ipr_compuesto(q_test, pwf_test, pr, x, pb))

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(20, 10))
    x = df['Qo(bpd)'].sort_values()
    y = df['Pwf(psia)'].iloc[x.index]

    # The following steps are used to smooth the curve
    x_y_spline = make_interp_spline(x, y)
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = x_y_spline(x_)

    # Build the curve
    ax.plot(x_, y_, c='g')
    ax.set_xlabel('Qo(bpd)', fontsize=14)
    ax.set_ylabel('Pwf(psia)', fontsize=14)
    ax.set_title('IPR', fontsize=18)
    ax.set_xlim(0, df['Qo(bpd)'].max() + 10)
    ax.set_ylim(0, df['Pwf(psia)'].max() + 100)

    # Arrow and Annotations
    plt.annotate(
        'Bubble Point', xy=(qb(q_test, pwf_test, pr, pb), pb),
        xytext=(qb(q_test, pwf_test, pr, pb) + 100, pb + 100),
        arrowprops=dict(arrowstyle='->', lw=1)
    )

    # Horizontal and Vertical lines at bubble point
    plt.axhline(y=pb, color='r', linestyle='--')
    plt.axvline(x=qb(q_test, pwf_test, pr, pb), color='r', linestyle='--')

    ax.grid()
    plt.show()


# Quicktest
q_test = 1000
pwf_test = 1500
pr = 3000
pb = 2000
pwf = [1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000]

IPR_curve(q_test, pwf_test, pr, pwf, pb)


# %%

# IPR CURVE

def IPR_curve_methods(q_test: float,
                      pwf_test: float,
                      pr: float,
                      pwf: list,
                      pb: float,
                      method: str,
                      ef: float = 1,
                      ef2: float = None):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom hole pressure during test
    :param pr: Reservoir pressure
    :param pwf: List of flowing bottom pressures
    :param pb: Bubble-point pressure
    :param method: Method for calculating Qo
    :param ef: Efficiency factor
    :param ef2: Additional efficiency factor
    :return: None
    """

    # Creating dataframe
    fig, ax = plt.subplots(figsize=(20, 10))
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf

    if method == 'Darcy':
        df['Qo(bpd'] = df['Pwf(psia)'].apply(lambda x: qo_darcy(q_test, pwf_test, pr, x, pb))
    elif method == 'Vogel':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_vogel(q_test, pwf_test, pr, x, pb))
    elif method == 'IPR Compuesto':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_ipr_compuesto(q_test, pwf_test, pr, x, pb))

    # Stand the axis of the IPR plot
    x = df['Qo(bpd)'].sort_values()
    y = df['Pwf(psia)'].iloc[x.index]

    # The following steps are used to smooth the curve
    x_y_spline = make_interp_spline(x, y)
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = x_y_spline(x_)

    # Build the curve
    ax.plot(x_, y_, c='g')
    ax.set_xlabel('Qo(bpd)')
    ax.set_ylabel('Pwf(psia)')
    ax.set_title('IPR')
    ax.set_xlim(0, df['Qo(bpd)'].max() + 10)
    ax.set_ylim(0, df['Pwf(psia)'].max() + 100)

    # Arrow and Annotations
    plt.annotate(
        'Bubble Point', xy=(qb(q_test, pwf_test, pr, pb), pb),
        xytext=(qb(q_test, pwf_test, pr, pb) + 100, pb + 100),
        arrowprops=dict(arrowstyle='->', lw=1)
    )

    # Horizontal and Vertical lines at bubble point
    plt.axhline(y=pb, color='r', linestyle='--')
    plt.axvline(x=qb(q_test, pwf_test, pr, pb), color='r', linestyle='--')

    ax.grid()
    plt.show()


# Quicktest
q_test = 1000
pwf_test = 1500
pr = 3000
pb = 2000
pwf = [1000, 1200, 1400, 1600, 1800, 2000, 2200, 2400, 2600, 2800, 3000]

IPR_curve_methods(q_test, pwf_test, pr, pwf, pb, method='IPR Compuesto')


# %%

# IPR Curve

def IPR_Curve(q_test: float,
              pwf_test: float,
              pr: float,
              pwf: list,
              pb: float,
              ef: float = 1,
              ef2: float = None,
              ax: float = None):
    """

    :param q_test: Test flow rate
    :param pwf_test: Flowing bottom hole pressure during test
    :param pr: Reservoir pressure
    :param pwf: List of flowing bottom pressures
    :param pb: Bubble-point pressure
    :param ef: Efficiency factor
    :param ef2: Additional efficiency factor
    :param ax: Optional axis for graph
    :return: None
    """

    # Creating Dataframe
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    df['Qo(bpd)'] = df['Pwf(psia)'].apply(
        lambda x: qo(q_test, pwf_test, pr, x, pb))

    # Create figure and axis
    fig, ax = plt.subplots(figsize=(20, 10))
    x = df['Qo(bpd)'].sort_values()
    y = df['Pwf(psia)'].iloc[x.index]

    # The following steps are used to smooth the curve
    x_y_spline = make_interp_spline(x, y)
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = x_y_spline(x_)

    # Build the curve
    ax.plot(x_, y_, c='g')
    ax.set_xlabel('Qo(bpd)', fontsize=14)
    ax.set_ylabel('Pwf(psia)', fontsize=14)
    ax.set_title('IPR', fontsize=18)
    ax.set_xlim(0, df['Qo(bpd)'].max() + 10)
    ax.set_ylim(0, df['Pwf(psia)'].max() + 100)

    # Arrow and Annotations
    plt.annotate(
        'Bubble Point', xy=(qb(q_test, pwf_test, pr, pb), pb),
        xytext=(qb(q_test, pwf_test, pr, pb) + 100, pb + 100),
        arrowprops=dict(arrowstyle='->', lw=1)
    )

    # Horizontal and Vertical lines at bubble point
    plt.axhline(y=pb, color='r', linestyle='--')
    plt.axvline(x=qb(q_test, pwf_test, pr, pb), color='r', linestyle='--')
    ax.grid()
    plt.show()


# Quicktest
q_test = 1000
pwf_test = 1500
pr = 3000
pb = 2000
pwf = [1000, 1200, 1400, 1600, 800, 2000, 2200, 2400, 2600, 2800, 3000]

IPR_Curve(q_test, pwf_test, pr, pwf, pb)


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
