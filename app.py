#Import Python libraries

from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

st.set_option('deprecation.showPyplotGlobalUse', False)

from model.utilities import j, aof, qo, \
    IPR_curve_methods, pwf_darcy, pwf_vogel, f_darcy, sg_oil, sg_avg, gradient_avg

# Insert an icon
icon = Image.open("resources/Logo.png")

# state the design of the app
st.set_page_config(page_title="PYNODAL APP", page_icon=icon)

# Insert css codes to improve the design of the app

st.markdown(
    """
<style>
h1 {
    text-align: center;
}
[data-testid="stAppViewContainer"] {
    background-color: #ADD8E6; /* Azul claro */
}
[data-testid="stSidebar"] {
    background-color: #D3D3D3; /* Gris claro */
}
footer {
  display: none;
}
</style>""",
    unsafe_allow_html=True,
)
# Insert title of the app
st.title("PYNODAL App ®")

st.write("---")

# Add information of the app
st.markdown(""" This app is used to see production history, IPR graphs curve, nodal 
analysis for single phase flow and reservoir potential calculations.

***Python:*** Pandas, NumPy, Streamlit, PIL, Plotly.
""")

# Add additional information
expander = st.expander("Information")
expander.write("This is an open-source web app fully programmed in Python "
               "for calculating"
               " production parameters.")

# Insert image
image = Image.open("resources/img.png")
st.image(image, width=100, use_column_width=True)

# Write subheader
st.write("---")
st.subheader("**Fundamentals of the oil industry**")

# Insert caption
st.caption("*Video about Exploration and Production*")

# Our Logo
logo = Image.open("resources/Logo.png")
st.sidebar.image(logo)

# Creation of Menu
st.sidebar.title("⬇ Menu")
file = st.sidebar.file_uploader("Upload your csv file")

# Add sections of the app
with st.sidebar:
    options = option_menu(
        menu_title="Menu",
        options=["Home", "Data", "Plots", "Calculations", "Nodal Analysis", "Nodal Analisis Plots"],
        icons=["house", "tv-fill", "box", "calculator", "droplet", "bar-chart"], )


#Qo(bpd) @ all conditions
def plots(dataframe):
    st.write(dataframe)
    st.subheader("***Production History***")
    fig1, ax1 = plt.subplots()
    ax1.plot(list(dataframe['date']), list(dataframe['oil_rate']), color="red")
    st.title('Annual Oil Production')
    plt.xlabel('Years')
    plt.ylabel('Rate (BBL/D)')
    plt.grid()
    st.plotly_chart(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(list(dataframe['date']), list(dataframe['water_rate']), color="green")
    st.title('Annual Water Production')
    plt.xlabel('Years')
    plt.ylabel('Rate (BBL/D)')
    plt.grid()
    st.plotly_chart(fig2)

    fig3, ax3 = plt.subplots()
    aq = dataframe[['date', 'oil_rate', 'water_rate']]
    ax3.plot(list(aq['date']), list(aq['water_rate']), color="red", label="Water Production")
    ax3.plot(list(aq['date']), list(aq['oil_rate']), color="green", label="Oil Production")
    st.title('Annual Total Production')
    plt.xlabel('Years')
    plt.ylabel('Rate (BBL/D)')
    plt.grid()
    st.plotly_chart(fig3)


Data = namedtuple("Input", "q_test pwf_test pr pwf pf ef ef2")
Output = namedtuple("Output", "qo")

if file:
    df = pd.read_excel(file)
    df1 = pd.DataFrame(df)
    if options == "Data":
        df1
    elif options == "Plots":
        plots(df)
    elif options == "Nodal Analisis Plots":
        Data = namedtuple("Input", "THP WC SG_H2O API QT ID TVD MD C PR PB PWFT")
        st.subheader("**Enter input values**")
        THP = st.number_input("Enter THP value: ")
        WC = st.number_input("Enter WC test value: ")
        SG_H2O = st.number_input("Enter SG_H2O value: ")
        API = st.number_input("Enter API value")
        QT = st.number_input("Enter QT value")
        ID = st.number_input("Enter ID value")
        TVD = st.number_input("Enter TVD value")
        MD = st.number_input("Enter MD value")
        C = st.number_input("Enter C value")
        PR = st.number_input("Enter PR value")
        PB = st.number_input("Enter PB value")
        PWFT = st.number_input("Enter PWFT value")

        columns = ['q(bpd)', 'Pwf(psia)', 'THP(psia)', 'Pgravity(psia)', 'f', 'F(ft)',
                   'Pf(psia)', 'Po(psia)', 'Psys(psia)']
        df2 = pd.DataFrame(columns=columns)

        # Here the AOF is divided per 10 in order to evaluate the pwf for these 10 different flow rates
        df2[columns[0]] = df1["Q"].to_numpy()
        df2[columns[1]] = df2['q(bpd)'].apply(lambda x: pwf_darcy(QT, PWFT, x, PR, PB))
        df2[columns[2]] = THP
        df2[columns[3]] = gradient_avg(API, WC, SG_H2O) * TVD
        df2[columns[4]] = df2['q(bpd)'].apply(lambda x: f_darcy(x, ID, C))
        df2[columns[5]] = df2['f'] * MD
        df2[columns[6]] = gradient_avg(API, WC, SG_H2O) * df2['F(ft)']
        df2[columns[7]] = df2['THP(psia)'] + df2['Pgravity(psia)'] + df2['Pf(psia)']
        df2[columns[8]] = df2['Po(psia)'] - df2['Pwf(psia)']
        df2
        st.subheader("**Nodal Analysis Graphic**")

        fig4, ax4 = plt.subplots()
        pl = df2[['q(bpd)', 'Pwf(psia)', 'Po(psia)', 'Psys(psia)']]
        ax4.plot(list(pl['q(bpd)']), list(pl['Pwf(psia)']), color="red",
                 label="IPR")
        ax4.plot(list(pl['q(bpd)']), list(pl['Po(psia)']), color="green",
                 label="VLP")
        ax4.plot(list(pl['q(bpd)']), list(pl['Psys(psia)']), color="orange",
                 label="System Curve")
        st.title('Nodal Analysis')
        plt.xlabel('q(bpd)')
        plt.ylabel('Pwf(psia)')
        plt.grid()
        st.plotly_chart(fig4)

if options == "Calculations":
    if st.checkbox("Potential resevoir"):
        Data = namedtuple("Input", "q_test pwf_test pr pwf pb ef ef2")
        st.subheader("**Enter input values**")
        q_test = st.number_input("Enter q_test value: ")
        pwf_test = st.number_input("Enter pw_test value: ")
        pr = st.number_input("Enter pr value: ")
        pwf = st.number_input("Enter pwf value")
        pb = st.number_input("Enter pb value")
        ef = st.number_input("Enter ef value")
        ef2 = st.number_input("Enter ef2 value")
        st.subheader("**Show results**")
        qo = qo(q_test, pwf_test, pr, pwf, pb, ef=1, ef2=None)
        st.success(f"{'Qo'} -> {qo:.3f} scf/Dia ")
        Qmax = aof(q_test, pwf_test, pr, pb, ef=1, ef2=None)
        st.success(f"{'Caudal maximo'} -> {Qmax:.3f} scf/Dia ")
        idp = j(q_test, pwf_test, pr, pb, ef=1, ef2=None)
        st.success(f"{'Indice de productividad'} -> {idp:.3f}  ")

    elif st.checkbox("IPR Curve"):
        st.subheader("**Select method**")
        method = st.selectbox("Method", ("Darcy", "Vogel", "IPR Compuesto"))
        Data = namedtuple("Input", "q_test pwf_test pr pwf pb")
        st.subheader("**Enter input values**")
        q_test = st.number_input("Enter q_test value: ")
        pwf_test = st.number_input("Enter pw_test value: ")
        pr = st.number_input("Enter pr value: ")
        pb = st.number_input("Enter pb value")
        pwf = []
        for i in range(0, int(pr + 100), 100):
            pwf.append(i)
        pwf.reverse()
        arr_pwf = np.array(pwf, dtype=int)
        q = IPR_curve_methods(q_test, pwf_test, pr, arr_pwf, pb, method)
        st.pyplot(q)

if options == "Nodal Analysis":
    Data = namedtuple("Input", "q_test pwf_test q pr pb sg_h2o API Q ID c wc")
    st.subheader("**Enter input values**")
    q_test = st.number_input("Enter q_test Value: ")
    pwf_test = st.number_input("Enter pwf test value: ")
    sg_h2o = st.number_input("Enter sg_h20 value: ")
    API = st.number_input("Enter API value")
    Q = st.number_input("Enter Q value")
    ID = st.number_input("Enter ID value")
    q = st.number_input("Enter q value")
    pr = st.number_input("Enter pr value")
    c = st.number_input("Enter c value")
    pb = st.number_input("Enter pb value")
    wc = st.number_input("Enter wc value")
    st.subheader("**Show results**")
    if pr > pb:
        pw_darcy = pwf_darcy(q_test, pwf_test, q, pr, pb)
        st.success(f"{'Pwf Darcy'} -> {pw_darcy:.3f} psi ")
    else:
        pw_vogel = pwf_vogel(q_test, pwf_test, q, pr, pb)
        st.success(f"{'Pwf Vogel'} -> {pw_vogel:.3f} psi ")

    fric = f_darcy(Q, ID, C=120)
    st.success(f"{'Friccion'} -> {fric:.3f}  ")
    sg_oil = sg_oil(API)
    st.success(f"{'Sg Oil'} -> {sg_oil:.3f}  ")
    sg_f = sg_avg(API, wc, sg_h2o)
    st.success(f"{'Sg fluids'} -> {sg_f:.3f}  ")
    gra = gradient_avg(API, wc, sg_h2o)
    st.success(f"{'Average Gradient'} -> {gra:.3f} psi/ft ")

st.caption("Developed by Reyes Elsie")
