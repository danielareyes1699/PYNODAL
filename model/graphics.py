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
    # Ordenar los valores por 'Qo(bpd) para asegurarse de que x es una secuencia
    df = df.sort_values(by='Qo(bpd)')
    fig, ax = plt.subplots(figsize=(12, 6))
    x = df['Qo(bpd)']
    y = df['Pwf(psia)']
    # The following steps are used to smooth the curve
    x_y_spline = make_interp_spline(x, y)
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = x_y_spline(x_)
    # Build the curve
    ax.plot(x_, y_, c='g')
    ax.set_xlabel('Qo(bpd)', fontsize=14)
    ax.set_ylabel('Pwf(psia)', fontsize=14)
    ax.set_title('IPR', fontsize=18)
    ax.set_xlim(0, df['Qo(bpd)'].max() + 100)
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
pwf_test = 2000
pr = 3000
pwf = [3000, 2500, 2000, 1500,1000]
pb = 1500

IPR_curve(q_test, pwf_test, pr, pwf, pb)

#%%
# IPR Curve
def IPR_curve_methods(q_test, pwf_test, pr, pwf:list, pb, method, ef=1, ef2=None):
    # Creating Dataframe
    fig, ax = plt.subplots(figsize=(12, 6))
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    if method == 'Darcy':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_darcy(q_test, pwf_test, pr, x, pb))
    elif method == 'Vogel':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_vogel(q_test, pwf_test, pr, x, pb))
    elif method == 'IPR Compuesto':
        df['Qo(bpd)'] = df['Pwf(psia)'].apply(lambda x: qo_ipr_compuesto(q_test, pwf_test, pr, x, pb))
    # Stand the axis of the IPR plot
    df = df.sort_values(by='Qo(bpd)')
    x = df['Qo(bpd)']
    y = df['Pwf(psia)']
    # The following steps are used to smooth the curve
    x_y_spline = make_interp_spline(x, y)
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = x_y_spline(x_)
    #Build the curve
    ax.plot(x_, y_, c='g')
    ax.set_xlabel('Qo(bpd)', fontsize=14)
    ax.set_ylabel('Pwf(psia)', fontsize=15)
    ax.set_title('IPR', fontsize=18)
    ax.set_xlim(0, df['Qo(bpd)'].max() + 100)
    ax.set_ylim(0, df['Pwf(psia)'].max() + 100)
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

# Quicktest
q_test = 1000
pwf_test = 2000
pr = 3000
pwf = [3000, 2500, 2000, 1500, 1000]
pb = 1500

IPR_curve_methods(q_test, pwf_test, pr, pwf, pb, method='Darcy')
IPR_curve_methods(q_test, pwf_test, pr, pwf, pb, method='Vogel')
IPR_curve_methods(q_test, pwf_test, pr, pwf, pb, method='IPR Compuesto')


#%%
# IPR Curve
def IPR_Curve(q_test, pwf_test, pr, pwf: list, pb, ef=1, ef2=None, ax=None):
    # Creating Dataframe
    df = pd.DataFrame()
    df['Pwf(psia)'] = pwf
    df['Qo(bpd)'] = df['Pwf(psia)'].apply(
        lambda x: qo(q_test, pwf_test, pr, x, pb, ef, ef2))
    df = df.sort_values(by='Qo(bpd)')
    fig, ax = plt.subplots(figsize=(12, 6))
    x = df['Qo(bpd)']
    y = df['Pwf(psia)']
    # The following steps are used to smooth the curve
    x_y_spline = make_interp_spline(x, y)
    x_ = np.linspace(x.min(), x.max(), 500)
    y_ = x_y_spline(x_)
    # Build the curve
    ax.plot(x_, y_, c='g')
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

# Quicktest
q_test = 1000
pwf_test = 2000
pr = 3000
pwf = [3000, 2500, 2000, 1500, 1000]
pb = 1500


IPR_Curve(q_test, pwf_test, pr, pwf, pb)
