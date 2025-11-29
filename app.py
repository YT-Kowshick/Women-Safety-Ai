# app.py
# AI by Her — final single-file Streamlit app
# - Robust model-loading (no crash on ModuleNotFoundError)
# - Folium (Leaflet) heatmap, with Plotly fallback
# - Neon-styled UI, PDF export, SOS assistant
#
# Make sure requirements.txt includes folium + streamlit-folium and any model libs (xgboost/lightgbm/etc.)

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
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Optional: Twilio
from twilio.rest import Client

# Optional: SHAP/Matplotlib (we keep optional)
try:
    import shap
    import matplotlib.pyplot as plt
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

# Optional: Folium + streamlit_folium (Leaflet)
try:
    import folium
    from streamlit_folium import st_folium
    from branca.colormap import linear
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# ----------------------------
# Page config + CSS
# ----------------------------
st.set_page_config(page_title="AI by Her — Women Safety", page_icon="🛡", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; background: #0b0f19; color:#e6eef8; }
.header { padding:18px; border-radius:12px; background: linear-gradient(90deg,#6f00ff,#00c8ff); box-shadow:0 12px 30px rgba(0,0,0,0.5); margin-bottom:18px;}
.neon-card { background: rgba(255,255,255,0.03); border-radius:12px; padding:18px; margin-bottom:18px; }
.small { font-size:13px; color:#94a3b8; }
.metric-box { display:flex; gap:12px; align-items:center; }
.stButton>button { background: linear-gradient(135deg,#6f00ff,#00c8ff); color:white; border-radius:8px; padding:8px 14px; font-weight:600; }
.input { background: rgba(255,255,255,0.04) !important; color:white !important; }
[data-testid="stSidebar"] { background: rgba(255,255,255,0.02); }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Twilio config (optional)
# ----------------------------
TWILIO_SID = st.secrets.get("TWILIO_SID", None)
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH", None)
TWILIO_WHATSAPP = "whatsapp:+14155238886"
client = Client(TWILIO_SID, TWILIO_AUTH) if (TWILIO_SID and TWILIO_AUTH) else None

def send_whatsapp_via_twilio(txt, number):
    if not client:
        return False
    try:
        if len(number) == 10 and number.isdigit():
            number = "91" + number
        client.messages.create(from_=TWILIO_WHATSAPP, body=txt, to=f"whatsapp:+{number}")
        return True
    except Exception:
        return False

# ----------------------------
# Helper functions
# ----------------------------
def generate_pdf_report(state, year, score, risk, tips):
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
    for line in tips.split("\n"):
        if y < 80:
            c.showPage()
            y = height - 60
        c.drawString(60, y, "- " + line.strip())
        y -= 18
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer

def risk_from_score(score):
    if score < 40: return "High Risk"
    if score < 70: return "Medium Risk"
    return "Safe"

# deterministic fallback predictor (simple, deterministic & safe)
def fallback_predict(df_row):
    # Accepts a DataFrame of one row with crime counts, returns 0-100 score
    counts = df_row[["Rape","K&A","DD","AoW","AoM","DV","WT"]].sum(axis=1).iloc[0]
    score = 100.0 * (1.0 - (counts / (counts + 1000.0)))  # smoothly maps counts -> lower score
    return float(max(0.0, min(100.0, score)))

# ----------------------------
# Load CSV + model (robust)
# ----------------------------
@st.cache_data
def load_all():
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    expected = ['Rape','K&A','DD','AoW','AoM','DV','WT']
    for c in expected:
        if c not in df.columns:
            raise RuntimeError(f"Missing column in CSV: {c}")

    df["TotalCrimes"] = df[expected].sum(axis=1).replace({0:1})
    for c in expected:
        df[c + "_ratio"] = df[c] / df["TotalCrimes"]

    feature_cols = ['Year'] + expected + [c + "_ratio" for c in expected]

    # Attempt to load model; if it fails we return model=None and model_error text
    model = None
    model_error = None
    try:
        model = joblib.load("safety_model.pkl")
    except Exception:
        model_error = traceback.format_exc()
        print("=== Model load traceback ===")
        print(model_error)
    return df, model, expected, feature_cols, model_error

df, model, crime_cols, feature_cols, model_error = load_all()

# ----------------------------
# UI Layout (sidebar navigation)
# ----------------------------
st.sidebar.markdown("<div style='font-weight:700;color:#00eaff;font-size:20px'>AI by Her</div>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["Dashboard","Existing","What-if","Trends","Heatmap","Recommendations","SOS"])

# Header
st.markdown("<div class='header'><h1 style='margin:0'>Women Safety — AI by Her</h1><div style='opacity:0.9;margin-top:6px' class='small'>Neon dashboard • Safety predictions • Map (Leaflet) • SOS alerts</div></div>", unsafe_allow_html=True)

# show model status
if model is None:
    st.warning("Model failed to load — app uses a safe fallback predictor. (Check logs for traceback)")
    with st.expander("Model load guidance"):
        st.write("If you trained your model using XGBoost / LightGBM / CatBoost or used a custom class, add the required package(s) to requirements.txt and redeploy.")
        st.write("Server logs (printed) contain the full traceback. If you want, upload the safety_model.pkl here and I can inspect which package is missing.")
else:
    st.success("Model loaded — full ML predictions enabled.")

# ----------------------------
# DASHBOARD page
# ----------------------------
if page == "Dashboard":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("National Overview")
    last_year = int(df["Year"].max())
    sample = df[df["Year"] == last_year][feature_cols]
    if model is not None:
        try:
            nat_scores = model.predict(sample)
            avg_score = float(pd.Series(nat_scores).mean())
        except Exception:
            avg_score = float(pd.Series([fallback_predict(sample.iloc[[i]]) for i in range(len(sample))]).mean())
    else:
        avg_score = float(pd.Series([fallback_predict(sample.iloc[[i]]) for i in range(len(sample))]).mean())
    st.metric(f"Average Safety ({last_year})", f"{avg_score:.1f}/100")
    st.write(f"States covered: **{df['State'].nunique()}**")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# EXISTING DATA page
# ----------------------------
if page == "Existing":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Check safety for an existing State & Year")
    c1, c2 = st.columns([2,1])
    with c1:
        state = st.selectbox("State", sorted(df["State"].unique()))
    with c2:
        year = st.selectbox("Year", sorted(df["Year"].unique()))
    if st.button("Run Prediction"):
        row = df[(df["State"]==state)&(df["Year"]==year)]
        if row.empty:
            st.error("No data found for selection.")
        else:
            X = pd.DataFrame([row.iloc[0][feature_cols]])
            if model is not None:
                try:
                    score = float(model.predict(X)[0])
                except Exception:
                    st.warning("Model prediction failed for this input — using fallback.")
                    print("Prediction error:", traceback.format_exc())
                    score = fallback_predict(X)
            else:
                score = fallback_predict(X)
            risk = risk_from_score(score)
            st.metric("Safety Score", f"{score:.2f}/100")
            st.write(f"**Risk Level:** {risk}")
            tips = ""
            if risk == "High Risk":
                tips = "Avoid isolated areas after sunset\nShare live location with trusted contacts\nKeep emergency contacts ready\nPrefer verified transport"
            elif risk == "Medium Risk":
                tips = "Travel with company\nStay alert in crowded places\nUse safety apps"
            else:
                tips = "Follow general precautions\nKeep phone charged and emergency contacts handy"
            pdf_buf = generate_pdf_report(state, year, score, risk, tips)
            st.download_button("Download Safety Report (PDF)", pdf_buf, file_name=f"{state}_{year}_report.pdf", mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# WHAT-IF page
# ----------------------------
if page == "What-if":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("What-if Crime Scenario Simulation")
    sim_year = st.number_input("Simulation Year", 2001, 2025, value=2021)
    left, mid, right = st.columns(3)
    with left:
        rape = left.number_input("Rape", 0, value=100)
        ka = left.number_input("Kidnapping & Abduction", 0, value=50)
        dd = left.number_input("Dowry Deaths", 0, value=20)
    with mid:
        aow = mid.number_input("Assault on Women", 0, value=150)
        aom = mid.number_input("Assault on Minors", 0, value=30)
    with right:
        dv = right.number_input("Domestic Violence", 0, value=80)
        wt = right.number_input("Women Trafficking", 0, value=10)

    if st.button("Simulate Score"):
        total = rape+ka+dd+aow+aom+dv+wt
        if total == 0:
            st.error("At least one crime count must be > 0.")
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
                    st.warning("Model failed to predict on simulated input — using fallback.")
                    score = fallback_predict(X_sim)
            else:
                score = fallback_predict(X_sim)
            risk = risk_from_score(score)
            st.metric("Simulated Safety Score", f"{score:.2f}/100")
            st.write(f"**Risk Level:** {risk}")
            pdf_buf = generate_pdf_report("Simulated", sim_year, score, risk, "Recommendations based on simulated score.")
            st.download_button("Download Simulation Report (PDF)", pdf_buf, file_name=f"simulation_{sim_year}_report.pdf", mime="application/pdf")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# TRENDS page
# ----------------------------
if page == "Trends":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Crime Trends")
    t_state = st.selectbox("State for trend", df["State"].unique(), key="trend_state")
    crime = st.selectbox("Crime type", crime_cols, key="trend_crime")
    smoothing = st.checkbox("Show 3-year moving average", value=False)
    tdf = df[df["State"]==t_state].sort_values("Year")
    fig = px.line(tdf, x="Year", y=crime, markers=True, title=f"{crime} Trend — {t_state}")
    if smoothing:
        tdf["ma3"] = tdf[crime].rolling(3, center=True, min_periods=1).mean()
        fig.add_trace(go.Scatter(x=tdf["Year"], y=tdf["ma3"], mode="lines", name="3-year MA", line=dict(dash="dash")))
    fig.update_layout(height=420, margin=dict(t=40), paper_bgcolor="#0b0f19", plot_bgcolor="rgba(255,255,255,0.03)", font=dict(color="white"))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# HEATMAP page (Leaflet / Folium)
# ----------------------------
if page == "Heatmap":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Heatmap — India (Leaflet / Folium)")

    hcrime = st.selectbox("Select crime for heatmap", crime_cols, key="heat_crime")
    st.markdown("<div class='small'>Map uses Folium (Leaflet). If Folium or GeoJSON fetch fails, app falls back to Plotly choropleth.</div>", unsafe_allow_html=True)

    # Fetch geojson
    def fetch_geojson():
        urls = [
            "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
            "https://raw.githubusercontent.com/rajkumarpv/indian-states/master/india_states.geojson",
            "https://raw.githubusercontent.com/arcdata/india-admin/master/india_states.geojson"
        ]
        for u in urls:
            try:
                r = requests.get(u, timeout=8)
                if r.status_code == 200:
                    return r.json()
            except Exception:
                continue
        return None

    geo = fetch_geojson()
    hdf = df.groupby("State")[hcrime].sum().reset_index()

    if geo and FOLIUM_AVAILABLE:
        try:
            # detect name property in geojson
            sample_props = list(geo["features"][0]["properties"].keys())
            name_prop = None
            for p in ["st_nm","ST_NM","STATE","STATE_NAME","name","NAME"]:
                if p in sample_props:
                    name_prop = p
                    break
            if not name_prop:
                for p in sample_props:
                    if isinstance(geo["features"][0]["properties"].get(p, None), str):
                        name_prop = p
                        break
            # create choropleth
            m = folium.Map(location=[22.0,80.0], zoom_start=5, tiles="CartoDB dark_matter")
            # create a mapping from state name property to crime sum (lowercase)
            data_map = {r["State"].strip().lower(): r[hcrime] for _, r in hdf.iterrows()}
            # simple choropleth style function
            maxv = hdf[hcrime].max() if not hdf.empty else 1
            minv = hdf[hcrime].min() if not hdf.empty else 0
            colormap = linear.YlOrRd_09.scale(minv, maxv)
            def style_fn(feature):
                nm = str(feature["properties"].get(name_prop, "")).strip().lower()
                val = data_map.get(nm, None)
                if val is None:
                    return {"fillColor":"#222222","color":"#444444","weight":0.4,"fillOpacity":0.1}
                return {"fillColor": colormap(val), "color":"#222", "weight":0.4, "fillOpacity":0.7}
            folium.GeoJson(geo, style_function=style_fn, tooltip=folium.GeoJsonTooltip(fields=[name_prop], aliases=["State:"])).add_to(m)
            colormap.caption = f"{hcrime} (sum)"
            colormap.add_to(m)
            # small markers: place a marker at centroid for each feature with popup including score (fallback/model)
            for feat in geo["features"]:
                try:
                    props = feat["properties"]
                    nm = str(props.get(name_prop, "")).strip()
                    geom = feat.get("geometry", {})
                    coords = None
                    if geom.get("type") == "Polygon":
                        coords = geom["coordinates"][0]
                    elif geom.get("type") == "MultiPolygon":
                        coords = geom["coordinates"][0][0]
                    if coords:
                        avg_lat = sum([c[1] for c in coords]) / len(coords)
                        avg_lon = sum([c[0] for c in coords]) / len(coords)
                        row = hdf[hdf["State"].str.lower() == nm.lower()]
                        crime_sum = int(row[hcrime].iloc[0]) if not row.empty else "N/A"
                        # compute safety score for latest year if model available
                        latest_year = int(df["Year"].max())
                        score_text = "N/A"
                        rrow = df[(df["State"].str.lower() == nm.lower()) & (df["Year"] == latest_year)]
                        if not rrow.empty:
                            Xr = pd.DataFrame([rrow.iloc[0][feature_cols]])
                            if model is not None:
                                try:
                                    s = float(model.predict(Xr)[0])
                                    score_text = f"{s:.1f}/100"
                                except Exception:
                                    score_text = f"{fallback_predict(Xr):.1f}/100"
                            else:
                                score_text = f"{fallback_predict(Xr):.1f}/100"
                        popup_html = f"<b>{nm}</b><br>Crime sum: {crime_sum}<br>Safety (latest): {score_text}"
                        folium.Marker(location=[avg_lat, avg_lon], popup=popup_html, icon=folium.DivIcon(html=f"""<div style="padding:4px;background:rgba(0,0,0,0.45);color:#fff;border-radius:6px;font-size:11px">{nm}</div>""")).add_to(m)
                except Exception:
                    continue
            st_data = st_folium(m, width=980, height=640)
        except Exception as e:
            st.error("Folium map error — falling back to Plotly choropleth. Error: " + str(e))
            st.plotly_chart(px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds"), use_container_width=True)
    else:
        if not geo:
            st.info("Could not fetch GeoJSON — using Plotly fallback.")
        if not FOLIUM_AVAILABLE:
            st.info("Folium / streamlit-folium not installed — using Plotly fallback.")
        st.plotly_chart(px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds"), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# RECOMMENDATIONS page
# ----------------------------
if page == "Recommendations":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Safety Recommendations")
    score_input = st.slider("Example Safety Score", 0, 100, 50)
    if score_input < 40:
        st.error("High risk — recommended actions:")
        st.write("- Avoid isolated areas after sunset\n- Share live location with trusted contacts\n- Keep emergency contacts ready\n- Prefer verified transport")
    elif score_input < 70:
        st.warning("Medium risk — recommended actions:")
        st.write("- Travel with company\n- Stay alert in crowded places\n- Use safety apps and share ETA")
    else:
        st.success("Safer area — general precautions:")
        st.write("- Avoid late-night solo travel when possible\n- Keep phone charged\n- Keep emergency contacts handy")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# SOS page
# ----------------------------
if page == "SOS":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("SOS Assistant — Multi-contact (WhatsApp)")
    col1,col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your name")
        user_area = st.text_input("Your area / landmark")
    with col2:
        maps_link = st.text_input("Google Maps link (optional)")
        send_twilio = st.checkbox("Attempt to send via Twilio (requires Twilio secrets)", value=False)
    st.markdown("---")
    if "contacts" not in st.session_state:
        st.session_state["contacts"] = []
    contacts = st.session_state["contacts"]
    if contacts:
        contact_list = [f"{c['name']} ({c['number']})" for c in contacts]
        selected = st.multiselect("Select contacts to alert", contact_list)
    else:
        st.info("No contacts yet. Add below.")
        selected = []

    ca,cb,cc = st.columns([3,3,1])
    with ca:
        new_name = st.text_input("Add contact name", key="add_name")
    with cb:
        new_number = st.text_input("Add WhatsApp number (10 digits or with code)", key="add_number")
    with cc:
        if st.button("Add Contact"):
            if not new_name or not new_number:
                st.error("Provide both name and number.")
            else:
                st.session_state["contacts"].append({"name": new_name, "number": new_number})
                st.success("Contact added.")
                st.rerun()

    st.markdown("---")
    if st.button("Generate SOS and Links"):
        if not user_name or not user_area:
            st.error("Enter your name & area.")
        elif len(selected) == 0:
            st.error("Select at least one contact.")
        else:
            sos = f"🚨 EMERGENCY ALERT 🚨\nI, {user_name}, am in danger at {user_area}.\nPlease reach me immediately."
            if maps_link:
                sos += f"\n📍 {maps_link}"
            st.code(sos)
            encoded = urllib.parse.quote(sos)
            st.markdown("WhatsApp quick links:")
            for entry in selected:
                nm, num = entry.split("(")
                num = num.replace(")","").strip()
                link_num = num if not (len(num)==10 and num.isdigit()) else "91"+num
                wa = f"https://wa.me/{link_num}?text={encoded}"
                st.markdown(f"- [{nm.strip()}]({wa})")
            if send_twilio:
                st.info("Attempting Twilio sends...")
                for entry in selected:
                    nm, num = entry.split("(")
                    num = num.replace(")","").strip()
                    ok = send_whatsapp_via_twilio(sos, num)
                    if ok:
                        st.success(f"Sent to {nm.strip()}")
                    else:
                        st.error(f"Failed to send to {nm.strip()} (Twilio).")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Footer: show model error expander (dev)
# ----------------------------
if model_error:
    with st.expander("Model load error — developer info (click to reveal)"):
        st.write("Model failed to load during startup. Full traceback printed to server logs.")
        if st.checkbox("Show full traceback in UI (dev only)"):
            st.code(model_error)

st.markdown("<div class='small' style='margin-top:12px'>Tip: If you see ModuleNotFoundError when unpickling, add that package (e.g. xgboost) to requirements.txt and redeploy.</div>", unsafe_allow_html=True)
