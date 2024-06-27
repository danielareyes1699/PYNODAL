# %%
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline

from model.q import qo_ipr_compuesto, qo, qb, qo_darcy, qo_vogel
# %%

# IPR CURVE

def IPR_curve(q_test, pwf_test, pr, pwf: list, pb):
    # Creating Dataframe
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    df['Qo(bpd)'] = df['Pwf(psia)'].apply(
        lambda x: qo_ipr_compuesto(q_test, pwf_test, pr, x, pb))
    fig, ax = plt.subplots(figsize=(20, 10))
    x = df['Qo(bpd)']
    y = df['Pwf(psia)']
    # The following steps are used to smooth the curve
    X_Y_Spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), 500)
    Y_ = X_Y_Spline(X_)
    # Build the curve
    ax.plot(X_, Y_, c='g')
    ax.set_xlabel('Qo(bpd)', fontsize=14)
    ax.set_ylabel('Pwf(psia)', fontsize=14)
    ax.set_title('IPR', fontsize=18)
    ax.set(xlim=(0, df['Qo(bpd)'].max() + 10), ylim=(0, df['Pwf(psia)'][0] + 100))
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


# IPR Curve
def IPR_curve_methods(q_test, pwf_test, pr, pwf:list, pb, method, ef=1, ef2=None):
    # Creating Dataframe
    fig, ax = plt.subplots(figsize=(20, 10))
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    if method == 'Darcy':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_darcy(q_test, pwf_test, pr, x, pb))
    elif method == 'Vogel':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_vogel(q_test, pwf_test, pr, x, pb))
    elif method == 'IPR Compuesto':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_ipr_compuesto(q_test, pwf_test, pr, x, pb))
    # Stand the axis of the IPR plot
    x = df['Qo(bpd)']
    y = df['Pwf(psia)']
    # The following steps are used to smooth the curve
    X_Y_Spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), 500)
    Y_ = X_Y_Spline(X_)
    #Build the curve
    ax.plot(X_, Y_, c='g')
    ax.set_xlabel('Qo(bpd)')
    ax.set_ylabel('Pwf(psia)')
    ax.set_title('IPR')
    ax.set(xlim=(0, df['Qo(bpd)'].max() + 10), ylim=(0, df['Pwf(psia)'].max() + 100))
    # Arrow and Annotations
    plt.annotate(
        'Bubble Point', xy=(qb(q_test, pwf_test, pr, pb), pb),xytext=(qb(q_test, pwf_test, pr, pb) + 100, pb + 100) ,
    arrowprops=dict(arrowstyle='->',lw=1)
    )
    # Horizontal and Vertical lines at bubble point
    plt.axhline(y=pb, color='r', linestyle='--')
    plt.axvline(x=qb(q_test, pwf_test, pr, pb), color='r', linestyle='--')
    ax.grid()
    plt.show()


# IPR Curve
def IPR_Curve(q_test, pwf_test, pr, pwf: list, pb, ef=1, ef2=None, ax=None):
    # Creating Dataframe
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    df['Qo(bpd)'] = df['Pwf(psia)'].apply(
        lambda x: qo(q_test, pwf_test, pr, x, pb, ef, ef2))
    fig, ax = plt.subplots(figsize=(20, 10))
    x = df['Qo(bpd)']
    y = df['Pwf(psia)']
    # The following steps are used to smooth the curve
    X_Y_Spline = make_interp_spline(x, y)
    X_ = np.linspace(x.min(), x.max(), 500)
    Y_ = X_Y_Spline(X_)
    # Build the curve
    ax.plot(X_, Y_, c='g')
    ax.set_xlabel('Qo(bpd)', fontsize=14)
    ax.set_ylabel('Pwf(psia)', fontsize=14)
    ax.set_title('IPR', fontsize=18)
    ax.set(xlim=(0, df['Qo(bpd)'].max() + 10), ylim=(0, df['Pwf(psia)'][0] + 100))
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

