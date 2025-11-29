# app.py — robust single-file Streamlit app
# - Graceful model load (no crash on ModuleNotFoundError)
# - Fallback demo predictor when model not available
# - Folium & SHAP optional, handled gracefully
# BEFORE DEPLOY: make sure requirements.txt contains the libs you need (see comments)

import streamlit as st
import pandas as pd
import joblib
import urllib.parse
import requests
import io
import json
import plotly.express as px
import plotly.graph_objects as go
import math
import traceback

from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Optional: SHAP (best-effort)
try:
    import shap
    import matplotlib.pyplot as plt
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

# Optional: Folium (best-effort)
try:
    import folium
    from streamlit_folium import st_folium
    from branca.colormap import linear
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# Page config + minimal CSS
st.set_page_config(page_title="AI by Her — Women Safety", page_icon="🛡", layout="wide")
st.markdown("""
<style>
html, body, [class*="css"] { font-family: Inter, sans-serif; background:#0b0f19; color:#e6eef8; }
.neon-card { background: rgba(255,255,255,0.03); border-radius:12px; padding:18px; margin-bottom:18px; }
.stButton>button { background: linear-gradient(135deg,#6f00ff,#00c8ff); color:white; border-radius:8px; padding:6px 12px; font-weight:600; }
.small { font-size:13px; color:#94a3b8; }
</style>
""", unsafe_allow_html=True)

# Twilio config (optional)
TWILIO_SID = st.secrets.get("TWILIO_SID", None)
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH", None)
TWILIO_WHATSAPP = "whatsapp:+14155238886"
client = Client(TWILIO_SID, TWILIO_AUTH) if (TWILIO_SID and TWILIO_AUTH) else None

def send_whatsapp_sos(message, number):
    if not client:
        return False
    try:
        if len(number) == 10 and number.isdigit():
            number = "91" + number
        client.messages.create(from_=TWILIO_WHATSAPP, body=message, to=f"whatsapp:+{number}")
        return True
    except Exception:
        return False

# Helper: demo fallback predictor (deterministic)
def demo_predict_from_row(X_row):
    # X_row is a DataFrame row with crime counts; produce a 0-100 score:
    # heuristic: more total crimes -> lower score; scale with smoothing so extremes don't saturate
    counts = X_row[["Rape","K&A","DD","AoW","AoM","DV","WT"]].sum(axis=1).iloc[0]
    # scale: safety = 100 * (1 - (counts / (counts + 1000)))
    safety = 100.0 * (1.0 - (counts / (counts + 1000.0)))
    return float(max(0.0, min(100.0, safety)))

def risk_from_score(score: float) -> str:
    if score < 40: return "High Risk"
    if score < 70: return "Medium Risk"
    return "Safe"

# PDF generator
def generate_pdf_report_text(state, year, score, risk, tips_text):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "Women Safety Report — AI by Her")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 90, f"State: {state}")
    c.drawString(300, height - 90, f"Year: {year}")
    c.drawString(50, height - 110, f"Safety Score: {score:.2f}/100")
    c.drawString(300, height - 110, f"Risk Level: {risk}")
    c.line(50, height - 120, width - 50, height - 120)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(50, height - 150, "Recommendations")
    c.setFont("Helvetica", 11)
    y = height - 170
    for line in tips_text.split("\n"):
        if y < 80:
            c.showPage()
            y = height - 60
        c.drawString(60, y, "- " + line.strip())
        y -= 18
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

# Load CSV & model with robust error handling
@st.cache_data
def load_all():
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    crime_cols = ['Rape','K&A','DD','AoW','AoM','DV','WT']
    for c in crime_cols:
        if c not in df.columns:
            raise RuntimeError(f"Missing expected column in CSV: {c}")

    df["TotalCrimes"] = df[crime_cols].sum(axis=1).replace({0:1})
    for c in crime_cols:
        df[c + "_ratio"] = df[c] / df["TotalCrimes"]

    feature_cols = [
        'Year','Rape','K&A','DD','AoW','AoM','DV','WT',
        'Rape_ratio','K&A_ratio','DD_ratio','AoW_ratio',
        'AoM_ratio','DV_ratio','WT_ratio'
    ]

    model = None
    model_error = None
    try:
        model = joblib.load("safety_model.pkl")
    except Exception as e:
        model_error = traceback.format_exc()
        # print stack to server logs for debugging (not shown to end-user)
        print("=== model load error (traceback) ===")
        print(model_error)
    return df, model, crime_cols, feature_cols, model_error

# call loader
df, model, crime_cols, feature_cols, model_error = load_all()

# show header + model status
st.markdown("<div style='padding:14px;border-radius:10px;background:linear-gradient(90deg,#6f00ff,#00c8ff);margin-bottom:12px'><h1 style='color:white;margin:0'>Women Safety — AI by Her</h1></div>", unsafe_allow_html=True)

if model is None:
    st.warning("Model failed to load — app will run with a demo fallback predictor. Check logs for details.")
    # show small expandable area with a short note; do not print full traceback to UI (safety)
    with st.expander("Why this happened / how to fix"):
        st.write("Unpickling your model failed (likely missing Python package such as xgboost/lightgbm/catboost).")
        st.write("Add the missing package(s) to requirements.txt and redeploy. Use the server logs to see the full traceback.")
else:
    st.success("Model loaded successfully — full ML predictions enabled.")

# quick national metric using model or fallback
latest_year = int(df["Year"].max())
try:
    sample_X = df[df["Year"] == latest_year][feature_cols]
    if model is not None:
        nat_scores = model.predict(sample_X)
        nat_avg = float(pd.Series(nat_scores).mean())
    else:
        nat_avg = float(pd.Series([demo_predict_from_row(sample_X.iloc[[i]]) for i in range(len(sample_X))]).mean())
    st.metric(label=f"Avg Safety ({latest_year})", value=f"{nat_avg:.1f}/100")
except Exception:
    pass

# UI: simple tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Existing Data","What-if","Trends","Heatmap","Recommendations","SOS"])

# TAB 1: Existing
with tab1:
    st.subheader("Existing Data — check safety")
    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("State", sorted(df["State"].unique()))
    with col2:
        year = st.selectbox("Year", sorted(df["Year"].unique()))
    if st.button("Check Safety"):
        row = df[(df["State"]==state)&(df["Year"]==year)]
        if row.empty:
            st.error("No data.")
        else:
            X = pd.DataFrame([row.iloc[0][feature_cols]])
            if model is not None:
                try:
                    score = float(model.predict(X)[0])
                except Exception as e:
                    st.error("Model prediction failed; using demo fallback.")
                    print("Prediction error:", traceback.format_exc())
                    score = demo_predict_from_row(X)
            else:
                score = demo_predict_from_row(X)
            risk = risk_from_score(score)
            st.metric("Safety Score", f"{score:.2f}/100")
            st.write(f"Risk Level: **{risk}**")
            # PDF
            tips = ("Avoid isolated areas after sunset\nShare live location\nKeep emergency contacts ready") if risk=="High Risk" else ("Travel with company\nStay alert") if risk=="Medium Risk" else ("Follow general precautions")
            pdf_buf = generate_pdf_report_text(state, year, score, risk, tips)
            st.download_button("Download report (PDF)", pdf_buf, file_name=f"{state}_{year}_report.pdf", mime="application/pdf")

# TAB 2: What-if
with tab2:
    st.subheader("What-if simulation")
    sim_year = st.number_input("Year", 2001, 2025, value=2021)
    c1,c2,c3 = st.columns(3)
    with c1:
        rape = c1.number_input("Rape", 0, value=100)
        ka = c1.number_input("K&A", 0, value=50)
        dd = c1.number_input("DD", 0, value=20)
    with c2:
        aow = c2.number_input("AoW", 0, value=150)
        aom = c2.number_input("AoM", 0, value=30)
    with c3:
        dv = c3.number_input("DV", 0, value=80)
        wt = c3.number_input("WT", 0, value=10)
    if st.button("Simulate"):
        total = rape+ka+dd+aow+aom+dv+wt
        if total==0:
            st.error("At least one count > 0.")
        else:
            X_sim = pd.DataFrame([{
                "Year": sim_year, "Rape": rape, "K&A": ka, "DD": dd, "AoW": aow,
                "AoM": aom, "DV": dv, "WT": wt,
                "Rape_ratio": rape/total, "K&A_ratio": ka/total, "DD_ratio": dd/total,
                "AoW_ratio": aow/total, "AoM_ratio": aom/total, "DV_ratio": dv/total, "WT_ratio": wt/total
            }])
            if model is not None:
                try:
                    score = float(model.predict(X_sim)[0])
                except Exception:
                    st.error("Model prediction failed on simulated input; using fallback.")
                    score = demo_predict_from_row(X_sim)
            else:
                score = demo_predict_from_row(X_sim)
            risk = risk_from_score(score)
            st.metric("Predicted Safety Score", f"{score:.2f}/100")
            st.write(f"Risk Level: **{risk}**")
            pdf_buf = generate_pdf_report_text("Simulated", sim_year, score, risk, "Tips based on simulated score")
            st.download_button("Download simulation report (PDF)", pdf_buf, file_name=f"sim_{sim_year}_report.pdf", mime="application/pdf")

# TAB 3: Trends
with tab3:
    st.subheader("Trends")
    t_state = st.selectbox("State", df["State"].unique(), key="trend_state")
    crime = st.selectbox("Crime", crime_cols, key="trend_crime")
    tdf = df[df["State"]==t_state].sort_values("Year")
    fig = px.line(tdf, x="Year", y=crime, markers=True, title=f"{crime} - {t_state}")
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: Heatmap (folium optional)
with tab4:
    st.subheader("Heatmap (Folium optional)")
    hcrime = st.selectbox("Crime for heatmap", crime_cols, key="heat_crime")
    hdf = df.groupby("State")[hcrime].sum().reset_index()
    # Try folium if available & geojson fetched
    def fetch_geojson():
        urls = [
            "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
            "https://raw.githubusercontent.com/rajkumarpv/indian-states/master/india_states.geojson",
            "https://raw.githubusercontent.com/arcdata/india-admin/master/india_states.geojson"
        ]
        for u in urls:
            try:
                r = requests.get(u, timeout=8)
                if r.status_code==200:
                    return r.json()
            except Exception:
                continue
        return None

    geo = fetch_geojson()
    if FOLIUM_AVAILABLE and geo is not None:
        try:
            # simple folium choropleth
            m = folium.Map(location=[22.0,80.0], zoom_start=5, tiles="CartoDB dark_matter")
            folium.Choropleth(
                geo_data=geo,
                name="choropleth",
                data=hdf,
                columns=["State", hcrime],
                key_on="feature.properties.name" if "name" in geo["features"][0]["properties"] else "feature.properties.st_nm",
                fill_color="YlOrRd",
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name=hcrime
            ).add_to(m)
            st_folium(m, width=900, height=600)
        except Exception as e:
            st.error("Folium map failed — falling back to Plotly choropleth.")
            st.plotly_chart(px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime), use_container_width=True)
    else:
        if geo is None:
            st.info("GeoJSON not fetched — using fallback.")
        if not FOLIUM_AVAILABLE:
            st.info("Folium not installed — using Plotly fallback.")
        st.plotly_chart(px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime), use_container_width=True)

# TAB 5: Recommendations
with tab5:
    st.subheader("Recommendations")
    score = st.slider("Example Safety Score", 0, 100, 50)
    if score < 40:
        st.error("High Risk: Avoid isolated places, share location, keep contacts.")
    elif score < 70:
        st.warning("Medium Risk: Prefer company, stay alert.")
    else:
        st.success("Safe: General precautions.")

# TAB 6: SOS
with tab6:
    st.subheader("SOS Assistant")
    user_name = st.text_input("Your name")
    user_area = st.text_input("Your area/landmark")
    maps_link = st.text_input("Maps link (optional)")
    if "contacts" not in st.session_state:
        st.session_state["contacts"] = []
    contacts = st.session_state["contacts"]
    if contacts:
        contact_list = [f"{c['name']} ({c['number']})" for c in contacts]
        selected = st.multiselect("Select contacts", contact_list)
    else:
        st.info("No contacts yet")
        selected = []
    ca, cb, cc = st.columns([3,3,1])
    with ca:
        new_name = st.text_input("Add contact name", key="add_name")
    with cb:
        new_number = st.text_input("Add number", key="add_num")
    with cc:
        if st.button("Add Contact"):
            if not new_name or not new_number:
                st.error("Provide both")
            else:
                st.session_state["contacts"].append({"name": new_name, "number": new_number})
                st.success("Contact added")
                st.rerun()
    if st.button("Generate SOS"):
        if not user_name or not user_area:
            st.error("Enter name & area")
        elif len(selected)==0:
            st.error("Select at least one contact")
        else:
            sos_text = f"🚨 EMERGENCY ALERT 🚨\nI, {user_name}, am in danger at {user_area}.\nPlease reach me immediately."
            if maps_link:
                sos_text += f"\n📍 {maps_link}"
            st.code(sos_text)
            encoded = urllib.parse.quote(sos_text)
            for entry in selected:
                nm, num = entry.split("(")
                num = num.replace(")","").strip()
                link_num = num if not (len(num)==10 and num.isdigit()) else "91"+num
                st.markdown(f"- [{nm.strip()}](https://wa.me/{link_num}?text={encoded})")

# Footer: if model_error present, show small hint and server log contains full trace
if model_error:
    with st.expander("Model load error (dev info)"):
        st.write("Model failed to load. Full traceback was printed to server logs. Typical cause: missing package used in training (eg xgboost/lightgbm/catboost).")
        st.write("Add the missing package to requirements.txt and redeploy.")
        # do not print full traceback in UI for security, but allow dev to copy if they insist:
        if st.checkbox("Show full traceback (dev)"):
            st.text(model_error)

st.markdown("<div class='small' style='margin-top:14px'>Tip: If unpickling errors mention `ModuleNotFoundError`, add that package to requirements.txt (e.g. xgboost) and redeploy.</div>", unsafe_allow_html=True)
