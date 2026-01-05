import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
from scipy.optimize import fsolve

import streamlit as st

def check_password():
    """Zwraca True, jeśli użytkownik wpisał poprawne hasło."""
    if "password_correct" not in st.session_state:
        # Wyświetl pole do wpisania hasła
        st.text_input("Wpisz hasło firmowe:", type="password", on_change=password_entered, key="password")
        return False
    return st.session_state["password_correct"]

def password_entered():
    if st.session_state["password"] == "Innowacyjny2026":
        st.session_state["password_correct"] = True
    else:
        st.error("Błędne hasło")

if not check_password():
    st.stop()  # Zatrzymaj aplikację tutaj

# --- KONFIGURACJA ---
st.set_page_config(page_title="Innowacyjny Dom - Dobór Pompy Ciepła", layout="centered")

# --- PEŁNA BAZA DANYCH (Zintegrowana ze wszystkich arkuszy) ---
DANE_POMP = {
    "ACOND": {
        "GRANDIS N": {"35": {"pts": [[-20, 3.8], [-15, 4.3], [-10, 4.9], [-5, 5.7], [0, 6.6], [5, 7.4], [10, 8.1]]}, "55": {"pts": [[-20, 3.6], [-15, 4.1], [-10, 4.6], [-5, 5.3], [0, 6.0], [5, 6.7], [10, 7.4]]}},
        "GRANDIS R": {"35": {"pts": [[-20, 8.7], [-15, 10.2], [-10, 11.6], [-5, 13.0], [0, 14.8], [5, 16.2], [10, 17.8]]}, "55": {"pts": [[-20, 8.4], [-15, 9.7], [-10, 11.0], [-5, 12.4], [0, 13.7], [5, 15.2], [10, 16.6]]}}
        },
    "CTC": {
        "ECOAIR 708M": {"35": {"pts": [[-15.0, 4.13], [-7.0, 5.51], [2.0, 5.66], [7.0, 6.96], [12.0, 8.71]]}, "55": {"pts": [[-15.0, 3.83], [-7.0, 4.84], [2.0, 5.58], [7.0, 7.41], [12.0, 8.43]]}},
        "ECOAIR 712M": {"35": {"pts": [[-15.0, 6.24], [-7.0, 7.11], [2.0, 7.36], [7.0, 9.04], [12.0, 11.23]]}, "55": {"pts": [[-15.0, 5.79], [-7.0, 7.32], [2.0, 7.56], [7.0, 8.7], [12.0, 10.65]]}},
        "ECOAIR 720M": {"35": {"pts": [[-15.0, 12.01], [-7.0, 13.57], [-2.0, 14.32], [2.0, 15.49], [7.0, 18.2], [12.0, 21.82]]}, "55": {"pts": [[-15.0, 11.66], [-7.0, 14.24], [-2.0, 14.51], [2.0, 15.47], [7.0, 17.28], [12.0, 20.28]]}}
    },
    "Kołton": {
        "AIRADAPT 3-12": {"35": {"pts": [[-25.0, 4.7], [-20.0, 5.86], [-15.0, 7.24], [-10.0, 8.16], [-5.0, 9.37], [0.0, 10.42], [5.0, 11.43]]}, "55": {"pts": [[-25.0, 5.15], [-20.0, 5.69], [-15.0, 7.06], [-10.0, 8.04], [-5.0, 9.6], [0.0, 10.7], [5.0, 11.83]]}},
        "AIRADAPT 4-16": {"35": {"pts": [[-25.0, 6.2], [-20.0, 7.37], [-15.0, 9.28], [-10.0, 10.56], [-5.0, 12.27], [0.0, 13.9], [5.0, 15.46]]}, "55": {"pts": [[-25.0, 7.0], [-20.0, 7.79], [-15.0, 9.37], [-10.0, 10.43], [-5.0, 12.34], [0.0, 13.64], [5.0, 14.88]]}},
        "AIRADAPT 4-20": {"35": {"pts": [[-25.0, 7.9], [-20.0, 10.0], [-15.0, 11.77], [-10.0, 13.42], [-5.0, 15.36], [0.0, 17.45], [5.0, 19.6]]}, "55": {"pts": [[-25.0, 8.33], [-20.0, 9.41], [-15.0, 11.32], [-10.0, 13.07], [-5.0, 14.9], [0.0, 16.35], [5.0, 18.5]]}}
    },
    "Mitsubishi (Zubadan)": {
        "ZUBADAN 6kW": {"35": {"pts": [[-25, 4.7], [-20, 6.0], [-15, 7.3], [-10, 8.0], [-7, 8.3], [2, 7.0], [7, 8.3]]}, "55": {"pts": [[-15, 5.8], [-10, 6.5], [-7, 6.9], [2, 6.0], [7, 6.9]], "limit": -15}},
        "ZUBADAN 8kW": {"35": {"pts": [[-25, 5.6], [-20, 7.6], [-15, 8.8], [-10, 9.7], [-7, 10.0], [2, 9.5], [7, 8.9]]}, "55": {"pts": [[-15, 7.4], [-10, 8.4], [-7, 8.8], [2, 8.4], [7, 7.5]], "limit": -15}},
        "ZUBADAN 10kW": {"35": {"pts": [[-25, 8.0], [-20, 9.4], [-15, 10.7], [-10, 12.0], [-7, 13.2], [2, 12.4], [7, 10.9]]}, "55": {"pts": [[-15, 9.2], [-10, 10.0], [-7, 10.9], [2, 10.4], [7, 9.2]], "limit": -15}},
        "ZUBADAN 12kW": {"35": {"pts": [[-25, 9.6], [-20, 11.0], [-15, 12.3], [-10, 13.6], [-7, 14.9], [2, 13.2], [7, 12.9]]}, "55": {"pts": [[-15, 11.2], [-10, 12.0], [-7, 12.4], [2, 12.0], [7, 11.2]], "limit": -15}},
        "ZUBADAN 14kW": {"35": {"pts": [[-25, 10.4], [-20, 12.0], [-15, 13.7], [-10, 15.0], [-7, 16.2], [2, 14.8], [7, 14.2]]}, "55": {"pts": [[-15, 12.5], [-10, 13.5], [-7, 14.0], [2, 13.5], [7, 12.5]], "limit": -15}}
    },
    "Mitsubishi (Eco Inverter)": {
        "ECO INVERTER 4kW": {"35": {"pts": [[-25, 1.8], [-20, 2.7], [-15, 3.5], [-10, 4.2], [-7, 4.1], [2, 4.4], [7, 5.4]]}, "55": {"pts": [[-7, 3.3], [2, 4.0], [7, 4.8]], "limit": -7}},
        "ECO INVERTER 6kW": {"35": {"pts": [[-25, 2.3], [-20, 3.4], [-15, 4.3], [-10, 5.2], [-7, 6.5], [2, 5.6], [7, 6.7]]}, "55": {"pts": [[-15, 3.1], [-10, 3.6], [-7, 4.0], [2, 4.8], [7, 5.5]], "limit": -15}},
        "ECO INVERTER 8kW": {"35": {"pts": [[-25, 4.8], [-20, 6.0], [-15, 7.0], [-10, 8.0], [-7, 8.0], [2, 8.4], [7, 10.1]]}, "55": {"pts": [[-15, 5.9], [-10, 6.3], [-7, 6.6], [2, 7.5], [7, 8.2]], "limit": -15}},
        "ECO INVERTER 10kW": {"35": {"pts": [[-25, 4.8], [-20, 6.0], [-15, 7.0], [-10, 8.0], [-7, 9.0], [2, 9.2], [7, 11.7]]}, "55": {"pts": [[-15, 5.9], [-10, 6.3], [-7, 6.8], [2, 8.5], [7, 9.5]], "limit": -15}}
    },
    "LG (R32 Mono)": {
        "MONOBLOC R32 5kW": {"35": {"pts": [[-25, 5.5], [-20, 5.5], [-15, 5.5], [-10, 5.5], [-7, 5.5], [2, 5.5], [7, 5.5]]}, "55": {"pts": [[-15, 5.23], [-7, 5.5], [2, 5.5], [7, 5.5]], "limit": -15}},
        "MONOBLOC R32 7kW": {"35": {"pts": [[-25, 5.85], [-20, 6.43], [-15, 7.0], [-7, 7.0], [2, 7.0], [7, 7.0]]}, "55": {"pts": [[-15, 6.6], [-7, 7.0], [2, 7.0], [7, 7.0]], "limit": -15}},
        "MONOBLOC R32 9kW": {"35": {"pts": [[-25, 6.5], [-20, 7.5], [-15, 8.5], [-10, 9.0], [-7, 9.0], [2, 9.0], [7, 9.0]]}, "55": {"pts": [[-25, 5.2], [-20, 6.4], [-15, 7.8], [-7, 9.0], [2, 9.0], [7, 9.0]]}},
        "MONOBLOC R32 12kW": {"35": {"pts": [[-25, 8.5], [-20, 10.2], [-15, 12.0], [-10, 12.0], [-7, 12.0], [2, 12.0], [7, 12.0]]}, "55": {"pts": [[-15, 11.5], [-7, 12.0], [2, 12.0], [7, 12.0]], "limit": -15}},
        "MONOBLOC R32 14kW": {"35": {"pts": [[-25, 10.0], [-20, 12.0], [-15, 14.0], [-10, 14.0], [-7, 14.0], [2, 14.0], [7, 14.0]]}, "55": {"pts": [[-15, 13.3], [-7, 14.0], [2, 14.0], [7, 14.0]], "limit": -15}},
        "MONOBLOC R32 16kW": {"35": {"pts": [[-25, 12.0], [-20, 14.0], [-15, 16.0], [-10, 16.0], [-7, 16.0], [2, 16.0], [7, 16.0]]}, "55": {"pts": [[-15, 15.2], [-7, 16.0], [2, 16.0], [7, 16.0]], "limit": -15}}
    },
    "LG Mały split": {
        "MAŁY SPLIT 4kW": {"35": {"pts": [[-20, 4.0], [-15, 4.0], [-7, 4.0], [-4, 4.0], [-2, 4.0], [2, 4.0], [7, 4.0]]}, "55": {"pts": [[-7, 4.0], [2, 4.0], [7, 4.0]], "limit": -7}},
        "MAŁY SPLIT 6kW": {"35": {"pts": [[-20, 6.0], [-15, 6.0], [-7, 6.0], [-4, 6.0], [-2, 6.0], [2, 6.0], [7, 6.0]]}, "55": {"pts": [[-7, 6.0], [2, 6.0], [7, 6.0]], "limit": -7}}
    },
    "LG split": {
        "SPLIT 5kW": {"35": {"pts": [[-20, 5.5], [-15, 5.5], [-7, 5.5], [-4, 5.5], [-2, 5.5], [2, 5.5], [7, 5.5]]}, "55": {"pts": [[-7, 5.5], [2, 5.5], [7, 5.5]], "limit": -7}},
        "SPLIT 7kW": {"35": {"pts": [[-20, 7.0], [-15, 7.0], [-7, 7.0], [-4, 7.0], [-2, 7.0], [2, 7.0], [7, 7.0]]}, "55": {"pts": [[-7, 7.0], [2, 7.0], [7, 7.0]], "limit": -7}},
        "SPLIT 9kW": {"35": {"pts": [[-20, 9.0], [-15, 9.0], [-7, 9.0], [-4, 9.0], [-2, 9.0], [2, 9.0], [7, 9.0]]}, "55": {"pts": [[-7, 9.0], [2, 9.0], [7, 9.0]], "limit": -7}}
    },
    "LG (R290 Mono)": {
        "THERMA V R290 7kW": {"35": {"pts": [[-25, 5.85], [-20, 6.5], [-15, 7.0], [-7, 7.0], [2, 7.0], [7, 7.0]]}, "55": {"pts": [[-25, 4.2], [-20, 5.4], [-15, 6.6], [-7, 7.0], [2, 7.0], [7, 7.0]]}},
        "THERMA V R290 9kW": {"35": {"pts": [[-25, 6.4], [-20, 7.6], [-15, 8.8], [-7, 9.0], [2, 9.0], [7, 9.0]]}, "55": {"pts": [[-25, 5.1], [-20, 6.5], [-15, 7.8], [-7, 9.0], [2, 9.0], [7, 9.0]]}},
        "THERMA V R290 12kW": {"35": {"pts": [[-25, 8.14], [-20, 9.47], [-15, 11.4], [-7, 12.0], [2, 12.0], [7, 12.0]]}, "55": {"pts": [[-25, 5.95], [-20, 7.61], [-15, 9.94], [-7, 12.0], [2, 12.0], [7, 12.0]]}},
        "THERMA V R290 14kW": {"35": {"pts": [[-25, 8.57], [-20, 9.97], [-15, 11.99], [-7, 14.0], [2, 14.0], [7, 14.0]]}, "55": {"pts": [[-25, 6.37], [-20, 8.27], [-15, 10.76], [-7, 12.58], [2, 14.0], [7, 14.0]]}},
        "THERMA V R290 16kW": {"35": {"pts": [[-25, 9.0], [-20, 10.47], [-15, 12.59], [-7, 16.0], [2, 16.0], [7, 16.0]]}, "55": {"pts": [[-25, 6.79], [-20, 8.93], [-15, 11.58], [-7, 13.16], [2, 16.0], [7, 16.0]]}}
    },
    "Hegam": {
        "HEGAM 6kW": {"35": {"pts": [[-25, 3.88], [-20, 4.44], [-15, 5.1], [-10, 5.87], [-7, 6.75], [-2, 7.76], [2, 7.91], [7, 9.1]]}, "55": {"pts": [[-25, 3.46], [-20, 3.98], [-15, 4.57], [-10, 5.26], [-7, 6.05], [-2, 6.96], [2, 7.1], [7, 8.16]]}},
        "HEGAM 10kW": {"35": {"pts": [[-25, 6.44], [-20, 7.41], [-15, 8.52], [-10, 9.8], [-7, 11.27], [2, 13.22], [7, 15.2]]}, "55": {"pts": [[-25, 6.17], [-20, 7.09], [-15, 8.16], [-10, 9.38], [-7, 10.79], [2, 12.65], [7, 14.55]]}},
        "HEGAM 16kW": {"35": {"pts": [[-25, 9.33], [-20, 10.47], [-15, 12.08], [-10, 13.92], [-7, 16.03], [2, 18.84], [7, 21.7]]}, "55": {"pts": [[-25, 8.51], [-20, 9.61], [-15, 11.02], [-10, 12.69], [-7, 14.59], [2, 17.15], [7, 19.8]]}}
    }
}

# --- 1. GÓRA: EDYCJA DANYCH ---
st.title("🏡 Dobór Pompy Ciepła - Innowacyjny Dom")

st.subheader("⚙️ Parametry wejściowe")
c1, c2 = st.columns(2)

with c1:
    demand = st.number_input("Zapotrzebowanie przy -20°C [kW]:", min_value=1.0, value=10.0, step=0.1, key="demand_widget")
    s_temp = st.selectbox("Zasilanie instalacji [°C]:", ["35", "55"], index=0, key="supply_widget")

with c2:
    prod = st.selectbox("Producent:", sorted(list(DANE_POMP.keys())), key="prod_widget")
    model = st.selectbox("Model pompy:", sorted(list(DANE_POMP[prod].keys())), key="model_widget")

# --- OBLICZENIA (BEZPOŚREDNIO W GŁÓWNYM NURCIE) ---
try:
    konf_data = DANE_POMP[prod][model][s_temp]
    t_v, p_v = zip(*konf_data["pts"])
    f_pump = interp1d(t_v, p_v, kind='linear', fill_value="extrapolate")
    
    # Funkcja budynku
    def f_house(t):
        m = -demand / 40
        c = demand / 2
        return m * t + c

    # Wyznaczanie punktu biwalentnego
    pb_calculated = float(fsolve(lambda t: f_pump(t) - f_house(t), x0=-10.0)[0])
    pb_power = f_house(pb_calculated)

    # --- 2. ŚRODEK: WYNIKI (ZAWSZE REAKTYWNE) ---
    st.write("---")
    st.subheader("📍 Wynik analizy")
    
    # Wyświetlamy konfigurację i PB używając zmiennych obliczonych w tej samej klatce
    st.markdown(f"**Konfiguracja:** :blue[{prod}] | :blue[{model}] | :blue[{s_temp}°C]")
    st.info(f"**Punkt biwalentny:** {pb_calculated:.2f} °C")
    
    if pb_calculated < -7:
        st.success("✅ pompa ciepła ma odpowiednio dużą moc")
    else:
        st.error("❌ pompa ciepła ma zbyt niską moc")

    if s_temp == "55" and "limit" in konf_data:
        st.warning(f"⚠️ Osiągnięcie temperatury 55st.C poniżej {konf_data['limit']} °C zawsze wymaga grzałki.")

    # --- 3. DÓŁ: WYKRES ---
    st.write("---")
    fig, ax = plt.subplots(figsize=(10, 5))
    t_axis = np.linspace(-25, 20, 500)
    
    ax.plot(t_axis, f_pump(t_axis), label=f'Maks. moc pompy ({s_temp}°C)', color='#1f77b4', linewidth=3)
    ax.plot(t_axis, [f_house(t) for t in t_axis], label=f'Zapotrzebowanie budynku ({demand}kW)', color='#d62728', linestyle='--')
    
    ax.scatter(pb_calculated, pb_power, color='black', s=150, zorder=5, label=f'PB: {pb_calculated:.2f}°C')
    ax.axvline(-7, color='green', linestyle=':', alpha=0.7, label='Wymóg -7°C')
    
    ax.set_xlabel('Temperatura zewnętrzna [°C]')
    ax.set_ylabel('Moc [kW]')
    ax.grid(True, which='both', linestyle='--', alpha=0.4)
    ax.legend()
    st.pyplot(fig)

except Exception as e:
    st.error("Wybrany model nie posiada danych charakterystyki dla zadanej temperatury zasilania.")

