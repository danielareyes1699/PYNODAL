# Import Python libraries
from collections import namedtuple
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_option_menu import option_menu

st.set_option('deprecation.showPyplotGlobalUse', False)

from model.j import j
from model.q import aof, qo
from model.graphics import IPR_curve_methods
from model.pwf import pwf_darcy, pwf_vogel
from model.other import f_darcy, sg_oil, sg_avg, gradient_avg

# Insert an icon
icon = Image.open("resources/Logo.png")

# State the design of the app
st.set_page_config(page_title="PYNODAL APP", page_icon=icon)

# Insert CSS codes to improve the design of the app
st.markdown(
    """
    <style>
    body {
        background-color: #98ff98; /* Light green */
        color: #fff; /* White text */
        margin: 0;
        padding: 0;
    }
    header {
        background-color: #0000ff; /* Blue */
        color: #fff; /* White text */
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1rem;
    }
    header h1 {
        font-size: 1.5rem;
        margin: 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown(
    """
    <header>
        <div class="logo">
            <img src="resources/Logo.png" style="height: 100%;" alt="Logo">
        </div>
        <h1>PYNODAL App ®</h1>
    </header>
    """,
    unsafe_allow_html=True,
)

# Our Logo
#logo = Image.open("resources/Logo.png")
# Creation of Menu


# Add navigation bar
selected = option_menu(
    menu_title="Menu",  # required
    options=["Home", "Data", "Plots", "Calculations", "Nodal Analysis Plots"],  # required
    icons=["house", "table", "bar-chart", "calculator", "graph-up"],  # optional
    menu_icon="cast",  # optional
    default_index=0,  # optional
    orientation="horizontal",
)


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

if selected == "Home":
    st.write("**Welcome to the Home Page**")
    st.write(
        "Web application that will visually present the IPR (Well Productivity Index Curve) and demand curves, "
        "allowing the user to evaluate the well's capacity based on the data he has provided."
    )
    animation_path = "resources/analisis_nodal.gif"
    st.image(animation_path, caption='IPR and Demand Curves', use_column_width=True)
    st.write("It is commonly accepted that wells are drilled and equipped for the primary purpose of extracting "
             "oil or gas from reservoirs. The movement of these fluids from the accumulations to and through the"
             " wellbore requires energy to compensate for frictional losses and bring them to the surface. "
             "The fluids initially travel through the reservoir, enter the wellbore, flow to the surface, pass "
             "through the pipeline system and are finally processed in the fluid separators located at the flow "
             "stations (Marcelo Hirschfeldt, 2009). (Marcelo Hirschfeldt, 2009)")

if selected == "Data":
    st.write("In this section you must first upload your file containing the oil production with the respective dates.")
    file = st.file_uploader("Upload your csv file with oil and water rate")
    df = pd.read_excel(file)
    df1 = pd.DataFrame(df)
    df1

elif (selected
      == "Plots"):
    st.write("In this section you get the respective graph with the data entered in the Data section.")
    file = st.file_uploader("Upload your csv file with oil and water rate")
    df = pd.read_excel(file)
    df1 = pd.DataFrame(df)
    plots(df1)

if selected == "Calculations":
    st.write("This section is used to obtain the reservoir potential. Also, in the IPR Curve option you must load a "
             "file containing pwf data. To obtain the IPR curve by different methods.")
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
        file2 = st.file_uploader("Upload your csv file to Calculations/IPR CURVE")
        df_e = pd.read_excel(file2)
        df3 = pd.DataFrame(df_e)
        st.subheader("**Select method**")
        method = st.selectbox("Method", ("Darcy", "Vogel", "IPR Compuesto"))
        Data = namedtuple("Input", "q_test pwf_test pr pwf pb")
        st.subheader("**Enter input values**")
        q_test = st.number_input("Enter q_test value: ")
        pwf_test = st.number_input("Enter pw_test value: ")
        pr = st.number_input("Enter pr value: ")
        pb = st.number_input("Enter pb value")
        pwf = df3["pwf"].tolist()
        pwf.sort(reverse=True)
        arr_pwf = np.array(pwf, dtype=float)
        q = IPR_curve_methods(q_test, pwf_test, pr, arr_pwf, pb, method)
        st.pyplot(q)

elif selected == "Nodal Analysis":
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

elif selected == "Nodal Analysis Plots":
    st.write("This section is used to obtain the IPR and VLP curves, it is necessary to enter production data for a "
             "certain time of the well to be analysed.")
    file3 = st.file_uploader("Upload your csv file to Nodal Analysis")
    df_nodal = pd.read_excel(file3)
    df1_a_n = pd.DataFrame(df_nodal)
    Data = namedtuple("Input", "THP WC SG_H2O API QT ID TVD MD C PR PB PWFT NVL")
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
    NVL = st.number_input("Enter Fluid Level (ft) value")

    columns = ['q(bpd)', 'Pwf(psia)', 'THP(psia)', 'Pgravity(psia)', 'f', 'F(ft)',
               'Pf(psia)', 'Po(psia)', 'Psys(psia)']
    df2 = pd.DataFrame(columns=columns)

    # Here the AOF is divided per 10 in order to evaluate the pwf for these 10 different flow rates
    df2[columns[0]] = df1_a_n["oil_rate"].to_numpy()
    df2[columns[1]] = df2['q(bpd)'].apply(lambda x: pwf_darcy(QT, PWFT, x, PR, PB))
    df2[columns[2]] = THP
    df2[columns[3]] = gradient_avg(API, WC, SG_H2O) * (TVD - NVL)
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
