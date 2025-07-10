
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import exp
from datetime import datetime
from io import StringIO

# Constants
Gsc = 0.0820  # MJ m-2 min-1
albedo = 0.23
lat = 36.5657  # Utsunomiya latitude

st.set_page_config(page_title="ET₀ Calculator", layout="wide")
st.title("📈 Hourly Reference Evapotranspiration (ET₀) Calculator")

uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    try:
        df['Datetime'] = pd.to_datetime(df['Date'] + ' ' + df['Hour'])
    except:
        st.error("Ensure the CSV includes 'Date' and 'Hour' columns.")

    if 'Elevation' not in df.columns:
        st.error("CSV must include an 'Elevation' column.")
    else:
        z = df['Elevation'].iloc[0]

        def calculate_eto(row):
            T = row['T_air']
            RH = row['RH']
            u2 = row['Wind_speed_2m']
            Rs = row['Solar_radiation']
            time = row['Datetime']

            es = 0.6108 * exp((17.27 * T) / (T + 237.3))
            ea = es * (RH / 100)
            delta = (4098 * es) / ((T + 237.3)**2)
            P = 101.3 * ((293 - 0.0065 * z)/293)**5.26
            gamma = 0.665e-3 * P
            Rns = (1 - albedo) * Rs
            Rnl = 0  # Simplified
            Rn = Rns - Rnl
            G = 0
            numerator = (0.408 * delta * (Rn - G)) + (gamma * (900 / (T + 273)) * u2 * (es - ea))
            denominator = delta + gamma * (1 + 0.34 * u2)
            eto = numerator / denominator
            return eto

        df['ET0'] = df.apply(calculate_eto, axis=1)

        st.success("ET₀ calculated successfully!")
        st.line_chart(df.set_index('Datetime')['ET0'])

        st.download_button("📥 Download ET₀ CSV", data=df.to_csv(index=False), file_name="eto_output.csv", mime="text/csv")
        st.dataframe(df.head())
