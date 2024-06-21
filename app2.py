#Import Python libraries
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

st.set_option('deprecation.showPyplotGlobalUse', False)

from model.utilities import j, aof, qo, IPR_curve_methods, pwf_darcy, pwf_vogel, f_darcy, sg_oil, sg_avg, gradient_avg

# Insert an icon
icon = Image.open("resources/Logo.png")

# State the design of the app
st.set_page_config(page_title="PYNODAL APP", page_icon=icon)

# Insert CSS codes to improve the design of the app
st.markdown(
    """
<style>
body {
    font-family: Arial, sans-serif;
    background-color: #98ff98;
    color: #fff;
}

header {
    background-color: #0000ff; 
    height: 2cm;
    display: flex;
    align-items: center;
    padding: 0 1rem;
}

header .logo {
    height: 100%;
    margin-right: 1rem;
}

header h1 {
    font-size: 1.5rem;
    margin: 0;
}

footer {
    background-color: #0000ff; /* Color azul */
    height: 2cm;
    display: flex;
    justify-content: center;
    align-items: center;
    position: fixed;
    width: 100%;
    bottom: 0;
}

footer p {
    margin: 0;
}
</style>
""",
    unsafe_allow_html=True,
)

# Insert title of the app
st.title("PYNODAL App ®")

# Add navigation bar
selected = option_menu(
    menu_title=None,  # required
    options=["Home", "Data", "Plots", "Calculations", "Nodal Analysis Plots"],  # required
    icons=["house", "table", "bar-chart", "calculator", "graph-up"],  # optional
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
)

# Display selected option
if selected == "Home":
    st.write("Welcome to the Home Page")
    st.write(
        "Web application that will visually present the IPR (Well Productivity Index Curve) and demand curves, allowing the user to evaluate the well's capacity based on the data he has provided.")
    home_image = Image.open("resources/img.png")
    st.image(home_image, caption='IPR and Demand Curves', use_column_width=True)
elif selected == "Data":
    file = st.file_uploader("Upload your csv file")
    if file:
        df = pd.read_excel(file)
        st.write(df)
elif selected == "Plots":
    file = st.file_uploader("Upload your csv file")
    if file:
        df = pd.read_excel(file)
        df1 = pd.DataFrame(df)
        st.write(df)
elif selected == "Calculations":
    if st.checkbox("Potential reservoir"):
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

elif selected == "Nodal Analysis Plots":
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

    # Asegúrate de tener una columna 'Q' en el dataframe
    df2["q(bpd)"] = np.linspace(0, 10000, 100)  # Ejemplo de datos
    df2["Pwf(psia)"] = df2['q(bpd)'].apply(lambda x: pwf_darcy(QT, PWFT, x, PR, PB))
    df2["THP(psia)"] = THP
    df2["Pgravity(psia)"] = gradient_avg(API, WC, SG_H2O) * TVD
    df2["f"] = df2['q(bpd)'].apply(lambda x: f_darcy(x, ID, C))
    df2["F(ft)"] = df2['f'] * MD
    df2["Pf(psia)"] = gradient_avg(API, WC, SG_H2O) * df2['F(ft)']
    df2["Po(psia)"] = df2['THP(psia)'] + df2['Pgravity(psia)'] + df2['Pf(psia)']
    df2["Psys(psia)"] = df2['Po(psia)'] - df2['Pwf(psia)']
    st.write(df2)

    st.subheader("**Nodal Analysis Graphic**")

    fig4, ax4 = plt.subplots()
    pl = df2[['q(bpd)', 'Pwf(psia)', 'Po(psia)', 'Psys(psia)']]
    ax4.plot(list(pl['q(bpd)']), list(pl['Pwf(psia)']), color="red", label="IPR")
    ax4.plot(list(pl['q(bpd)']), list(pl['Po(psia)']), color="green", label="VLP")
    ax4.plot(list(pl['q(bpd)']), list(pl['Psys(psia)']), color="orange", label="System Curve")
    st.title('Nodal Analysis')
    plt.xlabel('q(bpd)')
    plt.ylabel('Pwf(psia)')
    plt.grid()
    st.pyplot(fig4)

# Footer
st.markdown(
    """
<footer>
    <p>PYNODAL 2024 BY REYES ELSIE</p>
</footer>
""",
    unsafe_allow_html=True,
)

# Qo(bpd) @ all conditions
def plots(dataframe):
    st.write(dataframe)
    st.subheader("***Production History***")
    fig1, ax1 = plt.subplots()
    ax1.plot(list(dataframe['date']), list(dataframe['oil_rate']), color="red")
    st.title('Annual Oil Production')
    plt.xlabel('Years')
    plt.ylabel('Rate (BBL/D)')
    plt.grid()
    st.pyplot(fig1)

    fig2, ax2 = plt.subplots()
    ax2.plot(list(dataframe['date']), list(dataframe['water_rate']), color="green")
    st.title('Annual Water Production')
    plt.xlabel('Years')
    plt.ylabel('Rate (BBL/D)')
    plt.grid()
    st.pyplot(fig2)

    fig3, ax3 = plt.subplots()
    aq = dataframe[['date', 'oil_rate', 'water_rate']]
    ax3.plot(list(aq['date']), list(aq['water_rate']), color="red", label="Water Production")
    ax3.plot(list(aq['date']), list(aq['oil_rate']), color="green", label="Oil Production")
    st.title('Annual Total Production')
    plt.xlabel('Years')
    plt.ylabel('Rate (BBL/D)')
    plt.grid()
    st.pyplot(fig3)


