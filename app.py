############################################
#  AI BY HER — NEON PREMIUM A2 DASHBOARD   #
############################################
#  Full Neon UI + Sidebar Navigation
#  Glassmorphism Cards + Gradient Header
#  All original backend logic preserved
############################################

import streamlit as st
import pandas as pd
import joblib
import shap
import urllib.parse
import requests
import io
import json
import plotly.express as px
import plotly.graph_objects as go
from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import matplotlib.pyplot as plt

############################################
# PAGE CONFIG + GLOBAL NEON CSS
############################################

st.set_page_config(
    page_title="AI by Her — Women Safety",
    page_icon="🛡",
    layout="wide"
)

# ------ NEON THEME CSS -------- #
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
    background: #0b0f19;
}

/* Gradient Header */
.header-box {
    width: 100%;
    padding: 25px;
    border-radius: 16px;
    margin-bottom: 25px;
    background: linear-gradient(135deg, #6f00ff, #00c8ff);
    box-shadow: 0 0 25px rgba(111, 0, 255, 0.4),
                0 0 25px rgba(0, 200, 255, 0.3);
}

/* Section Cards (Glassmorphism) */
.neon-card {
    background: rgba(255,255,255,0.05);
    border-radius: 18px;
    padding: 25px;
    margin-bottom: 30px;
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 0 20px rgba(0, 200, 255, 0.15),
                inset 0 0 25px rgba(111, 0, 255, 0.05);
}

/* Neon Buttons */
.stButton>button {
    background: linear-gradient(135deg,#6f00ff,#00c8ff);
    color: white;
    border-radius: 10px;
    padding: 0.6rem 1.2rem;
    border: none;
    font-weight: 600;
    transition: 0.2s;
    box-shadow: 0 0 12px rgba(0,200,255,0.5);
}
.stButton>button:hover {
    transform: scale(1.04);
    box-shadow: 0 0 20px rgba(0,200,255,0.8);
}

/* Inputs */
input, select, textarea {
    background: rgba(255,255,255,0.07) !important;
    color: white !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: rgba(255, 255, 255, 0.03);
    backdrop-filter: blur(15px);
    border-right: 1px solid rgba(255,255,255,0.1);
}

.sidebar-title {
    color: #00eaff;
    font-size: 22px;
    font-weight: 600;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.15);
}

</style>
""", unsafe_allow_html=True)

############################################
# TWILIO CONFIG
############################################

TWILIO_SID = st.secrets.get("TWILIO_SID", None)
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH", None)
TWILIO_WHATSAPP = "whatsapp:+14155238886"

client = Client(TWILIO_SID, TWILIO_AUTH) if (TWILIO_SID and TWILIO_AUTH) else None

def send_whatsapp_sos(message, number):
    """Send via Twilio (best-effort)."""
    if not client: return False
    try:
        if len(number) == 10:
            number = "91" + number
        client.messages.create(
            from_=TWILIO_WHATSAPP,
            body=message,
            to=f"whatsapp:+{number}"
        )
        return True
    except:
        return False


############################################
# LOAD DATA + MODEL
############################################

@st.cache_data
def load_all():
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    crime_cols = ['Rape','K&A','DD','AoW','AoM','DV','WT']
    df["TotalCrimes"] = df[crime_cols].sum(axis=1).replace({0:1})
    for c in crime_cols:
        df[c + "_ratio"] = df[c] / df["TotalCrimes"]

    feature_cols = [
        'Year','Rape','K&A','DD','AoW','AoM','DV','WT',
        'Rape_ratio','K&A_ratio','DD_ratio','AoW_ratio',
        'AoM_ratio','DV_ratio','WT_ratio'
    ]

    model = joblib.load("safety_model.pkl")
    return df, model, crime_cols, feature_cols

df, model, crime_cols, feature_cols = load_all()


############################################
# SIDEBAR NAVIGATION
############################################

st.sidebar.markdown("<div class='sidebar-title'>🛡 AI by Her</div>", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Existing Data", "What-If Simulation",
     "Trends", "Heatmap", "Recommendations", "SOS Assistant"]
)


############################################
# HEADER
############################################
st.markdown("""
<div class='header-box'>
    <h1 style='color:white;margin:0;font-weight:700;'>Women Safety — AI by Her</h1>
    <p style='color:white;margin:0;opacity:0.88;font-size:16px;'>
        Neon Dashboard • Safety Score Prediction • Geo Heatmaps • SOS Alerts
    </p>
</div>
""", unsafe_allow_html=True)


############################################
# PAGE 1 : MAIN DASHBOARD
############################################

if page == "Dashboard":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)

    st.subheader("📊 National Safety Overview")
    last_year = df["Year"].max()
    avg_score = float(model.predict(df[df["Year"] == last_year][feature_cols]).mean())

    colA, colB = st.columns(2)
    colA.metric(f"Avg Safety Score ({last_year})", f"{avg_score:.2f}")
    colB.metric("Total States Covered", df["State"].nunique())

    st.markdown("</div>", unsafe_allow_html=True)


############################################
# PAGE 2 : EXISTING DATA CHECK
############################################

if page == "Existing Data":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("📍 Existing Data — Safety Prediction")

    col1, col2 = st.columns(2)
    state = col1.selectbox("Select State", sorted(df["State"].unique()))
    year = col2.selectbox("Select Year", sorted(df["Year"].unique()))

    if st.button("Predict Safety"):
        row = df[(df["State"] == state) & (df["Year"] == year)].iloc[0]
        X = pd.DataFrame([row[feature_cols]])
        score = float(model.predict(X)[0])

        risk = "High Risk" if score < 40 else "Medium Risk" if score < 70 else "Safe"

        st.metric("Safety Score", f"{score:.2f}")
        st.write(f"Risk Level: **{risk}**")

    st.markdown("</div>", unsafe_allow_html=True)


############################################
# PAGE 3 : WHAT-IF SIMULATION
############################################

if page == "What-If Simulation":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🧪 What-If Crime Simulation")

    year_sim = st.number_input("Simulation Year", 2001, 2025, 2021)

    col1, col2, col3 = st.columns(3)
    rape = col1.number_input("Rape", 0, 100)
    ka   = col1.number_input("Kidnapping & Abduction", 0, 100)
    dd   = col2.number_input("Dowry Deaths", 0, 100)
    aow  = col2.number_input("Assault on Women", 0, 200)
    aom  = col3.number_input("Assault on Minors", 0, 100)
    dv   = col3.number_input("Domestic Violence", 0, 200)
    wt   = col3.number_input("Women Trafficking", 0, 50)

    if st.button("Simulate Score"):
        total = rape + ka + dd + aow + aom + dv + wt
        if total == 0:
            st.error("Values cannot be all zero")
        else:
            Xsim = pd.DataFrame([{
                "Year": year_sim,
                "Rape": rape, "K&A": ka, "DD": dd, "AoW": aow,
                "AoM": aom, "DV": dv, "WT": wt,
                "Rape_ratio": rape/total,
                "K&A_ratio": ka/total,
                "DD_ratio": dd/total,
                "AoW_ratio": aow/total,
                "AoM_ratio": aom/total,
                "DV_ratio": dv/total,
                "WT_ratio": wt/total
            }])

            score = float(model.predict(Xsim)[0])
            st.metric("Predicted Score", f"{score:.2f}")

    st.markdown("</div>", unsafe_allow_html=True)


############################################
# PAGE 4 : TRENDS
############################################

if page == "Trends":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("📈 Trends Over Years")

    col1, col2 = st.columns(2)
    st_sel = col1.selectbox("State", df["State"].unique())
    crime = col2.selectbox("Crime Type", crime_cols)

    tdf = df[df["State"] == st_sel].sort_values("Year")
    fig = px.line(tdf, x="Year", y=crime, markers=True, height=450)
    fig.update_layout(
        paper_bgcolor='#0b0f19',
        plot_bgcolor='rgba(255,255,255,0.03)',
        font=dict(color='white')
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)


############################################
# PAGE 5 : HEATMAP
############################################

if page == "Heatmap":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🗺 India Heatmap (Online GeoJSON)")

    crime = st.selectbox("Crime Type", crime_cols)

    try:
        geo = requests.get(
            "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson"
        ).json()

        hdf = df.groupby("State")[crime].sum().reset_index()

        fig = px.choropleth_mapbox(
            hdf,
            geojson=geo,
            locations="State",
            featureidkey="properties.st_nm",
            color=crime,
            color_continuous_scale="Inferno",
            mapbox_style="carto-darkmatter",
            center={"lat": 22, "lon": 80},
            zoom=3.5,
            opacity=0.7,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)

    except:
        st.error("GeoJSON fetch failed. Try again.")

    st.markdown("</div>", unsafe_allow_html=True)


############################################
# PAGE 6 : RECOMMENDATIONS
############################################

if page == "Recommendations":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🛡 Safety Recommendations")

    score = st.slider("Your Score", 0, 100, 50)

    if score < 40:
        st.error("High Risk — Avoid isolated areas, share live location.")
    elif score < 70:
        st.warning("Medium Risk — Travel with someone & stay alert.")
    else:
        st.success("Safe Zone — Follow basic precautions.")

    st.markdown("</div>", unsafe_allow_html=True)


############################################
# PAGE 7 : SOS ASSISTANT
############################################

if page == "SOS Assistant":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🚨 SOS Alert Assistant")

    col1, col2 = st.columns(2)
    name = col1.text_input("Your Name")
    area = col1.text_input("Your Area / Landmark")
    maps = col2.text_input("Google Maps Link", "")
    send_twilio = col2.checkbox("Send via Twilio")

    # Contacts
    st.markdown("### 🔗 Trusted Contacts")
    if "contacts" not in st.session_state:
        st.session_state.contacts = []

    contacts = st.session_state.contacts
    display = [f"{c['name']} ({c['number']})" for c in contacts]

    selected = st.multiselect("Select contacts", display)

    # Add new contact
    st.markdown("### ➕ Add Contact")
    ca, cb, cc = st.columns([3,3,1])
    new_n = ca.text_input("Name", key="nn")
    new_p = cb.text_input("Number", key="np")

    if cc.button("Add"):
        if new_n and new_p:
            st.session_state.contacts.append({"name": new_n, "number": new_p})
            st.success("Added!")
            st.rerun()
        else:
            st.error("Enter valid details")

    st.markdown("---")

    if st.button("Generate SOS"):
        if not name or not area or len(selected)==0:
            st.error("Fill all details")
        else:
            msg = f"🚨 EMERGENCY ALERT 🚨\nI, {name}, am in danger at {area}."
            if maps: msg += f"\nLocation: {maps}"

            st.code(msg)

            enc = urllib.parse.quote(msg)
            st.markdown("### WhatsApp Links")

            for entry in selected:
                nm, num = entry.split("(")
                num = num.replace(")", "").strip()
                if len(num)==10: num = "91"+num
                st.markdown(f"- [{nm.strip()}](https://wa.me/{num}?text={enc})")

                if send_twilio:
                    ok = send_whatsapp_sos(msg, num)
                    if ok: st.success(f"Sent to {nm.strip()}")
                    else: st.error(f"Failed → {nm.strip()}")

    st.markdown("</div>", unsafe_allow_html=True)
