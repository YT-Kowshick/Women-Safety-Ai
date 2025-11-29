# app.py
# Full single-file Streamlit app — includes:
# - Existing safety prediction + What-if simulation
# - Trend charts (Plotly)
# - India GeoJSON heatmap (online fallback)
# - SOS assistant (WhatsApp links + Twilio send)
# - PDF report download (text + meta)
# - SHAP explainability (best-effort; disabled gracefully if shap not installed)
#
# Required packages (add to requirements.txt before deploying):
# streamlit
# pandas
# joblib
# plotly
# requests
# twilio
# reportlab
# shap
# matplotlib
#
# Notes:
# - Keep your model file 'safety_model.pkl' and data 'CrimesOnWomenData.csv' in app folder.
# - Put TWILIO credentials in Streamlit secrets: TWILIO_SID, TWILIO_AUTH
# - GeoJSON is fetched from an online source; if blocked, it falls back to the default choropleth.

import streamlit as st
import pandas as pd
import joblib
import urllib.parse
import requests
import io
import json
import math

# visualization
import plotly.express as px
import plotly.graph_objects as go

# Twilio
from twilio.rest import Client

# PDF
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# SHAP (optional; if not available app still runs)
try:
    import shap
    import matplotlib.pyplot as plt
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

# ------------------------------
# CONFIG / SECRETS / TWILIO
# ------------------------------
st.set_page_config(page_title="AI by Her — Women Safety", page_icon="🛡", layout="wide")

# Twilio settings (must exist in st.secrets)
TWILIO_SID = st.secrets.get("TWILIO_SID", None)
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH", None)
TWILIO_WHATSAPP = "whatsapp:+14155238886"
if TWILIO_SID and TWILIO_AUTH:
    client = Client(TWILIO_SID, TWILIO_AUTH)
else:
    client = None

def send_whatsapp_sos(message, user_phone):
    """Send WhatsApp message using Twilio (best-effort). user_phone should include country code or 10-digit Indian number."""
    if not client:
        return False
    try:
        # ensure phone includes country code, Twilio expects full E.164 for Whatsapp? we use whatsapp:+<number>
        if len(user_phone) == 10 and user_phone.isdigit():
            user_phone = "91" + user_phone
        client.messages.create(
            from_=TWILIO_WHATSAPP,
            body=message,
            to=f"whatsapp:+{user_phone}"
        )
        return True
    except Exception:
        return False

# ------------------------------
# DATA + MODEL LOADING
# ------------------------------
@st.cache_data
def load_data_model():
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    # standard crime columns expected
    crime_cols = ['Rape','K&A','DD','AoW','AoM','DV','WT']
    for c in crime_cols:
        if c not in df.columns:
            st.error(f"Data missing expected column: {c}")
            raise RuntimeError(f"Missing column {c}")

    # totals & ratios
    df["TotalCrimes"] = df[crime_cols].sum(axis=1)
    df["TotalCrimes"] = df["TotalCrimes"].replace({0: 1})
    for c in crime_cols:
        df[c + "_ratio"] = df[c] / df["TotalCrimes"]

    feature_cols = [
        'Year',
        'Rape','K&A','DD','AoW','AoM','DV','WT',
        'Rape_ratio','K&A_ratio','DD_ratio','AoW_ratio','AoM_ratio','DV_ratio','WT_ratio'
    ]

    model = joblib.load("safety_model.pkl")
    return df, model, crime_cols, feature_cols

df, model, crime_cols, feature_cols = load_data_model()

# ------------------------------
# Helper functions
# ------------------------------
def risk_from_score(score: float) -> str:
    if score < 40:
        return "High Risk"
    elif score < 70:
        return "Medium Risk"
    return "Safe"

def generate_pdf_report_text(state, year, score, risk, tips_text):
    """Return BytesIO PDF for download — simple professional text report."""
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    # header
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "Women Safety Report — AI by Her")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 90, f"State: {state}")
    c.drawString(250, height - 90, f"Year: {year}")
    c.drawString(50, height - 110, f"Safety Score: {score:.2f}/100")
    c.drawString(250, height - 110, f"Risk Level: {risk}")

    c.line(50, height - 120, width - 50, height - 120)

    # recommendations / tips
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

@st.cache_data
def fetch_geojson():
    """
    Fetch India states GeoJSON from a common online repo.
    If not available the function returns None and caller should fallback.
    """
    urls = [
        # common geojson sources — try a couple
        "https://raw.githubusercontent.com/geohacker/india/master/state/india_state.geojson",
        "https://raw.githubusercontent.com/rajkumarpv/indian-states/master/india_states.geojson",
        "https://raw.githubusercontent.com/arcdata/india-admin/master/india_states.geojson"
    ]
    for u in urls:
        try:
            r = requests.get(u, timeout=8)
            if r.status_code == 200:
                gj = r.json()
                return gj
        except Exception:
            continue
    return None

# SHAP helper (best-effort)
def compute_shap_for_row(model, X_df):
    """
    Returns (feature_names, shap_values) if possible.
    This function attempts to use shap.TreeExplainer for tree models first.
    If not available, tries KernelExplainer with a small background sample (slow).
    If SHAP not available or fails, returns (None, None).
    """
    if not SHAP_AVAILABLE:
        return None, None

    try:
        explainer = None
        # Try TreeExplainer first
        try:
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X_df)
            # For tree models shap_values might be list (for multiclass). We'll coerce to array for regression/regscore.
            if isinstance(shap_values, list):
                # pick first output
                shap_values = shap_values[0]
            return X_df.columns.tolist(), shap_values[0] if shap_values.shape[0] > 1 else shap_values
        except Exception:
            # fallback to KernelExplainer
            background = shap.sample(X_df, nsamples=min(50, len(X_df)))
            explainer = shap.KernelExplainer(model.predict, background)
            shap_values = explainer.shap_values(X_df, nsamples=100)
            return X_df.columns.tolist(), shap_values[0] if isinstance(shap_values, list) else shap_values
    except Exception:
        return None, None

# ------------------------------
# Page Header
# ------------------------------
st.markdown("<h1 style='margin-bottom:6px'>🛡 AI by Her — Women Safety Prediction</h1>", unsafe_allow_html=True)
st.markdown("<div style='color:#9aa0a6;margin-bottom:14px'>Predict Safety Score (0-100), run what-if scenarios, view trends and heatmap, generate reports and send SOS.</div>", unsafe_allow_html=True)

# show a quick national average metric (last year)
latest_year = int(df["Year"].max())
try:
    sample_X = df[df["Year"] == latest_year][feature_cols]
    nat_scores = model.predict(sample_X)
    nat_avg = float(pd.Series(nat_scores).mean())
    st.metric(label=f"Avg Safety ({latest_year})", value=f"{nat_avg:.1f}/100")
except Exception:
    # ignore quietly, show nothing
    pass

# ------------------------------
# Tabs
# ------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Existing Data", "What-if Simulation", "Trend Graphs", "Heatmap (India)", "Recommendations / PDF", "SOS Assistant"
])

# ------------------------------
# TAB 1 — Existing Data Safety Check
# ------------------------------
with tab1:
    st.header("📊 Existing Data Safety Check")
    c1, c2 = st.columns([2,1])
    with c1:
        state = st.selectbox("State", sorted(df["State"].unique()))
    with c2:
        year = st.selectbox("Year", sorted(df["Year"].unique()))
    if st.button("Check Safety for Selection"):
        row = df[(df["State"] == state) & (df["Year"] == year)]
        if row.empty:
            st.error("No data for this state/year.")
        else:
            row = row.iloc[0]
            X = pd.DataFrame([row[feature_cols]])
            try:
                score = float(model.predict(X)[0])
            except Exception as e:
                st.error("Model prediction failed: " + str(e))
                score = None
            if score is not None:
                risk = risk_from_score(score)
                st.metric("Safety Score", f"{score:.2f}/100")
                st.write(f"**Risk Level:** `{risk}`")
                if risk == "High Risk":
                    st.error("⚠ High Risk — avoid isolated areas and share live location.")
                elif risk == "Medium Risk":
                    st.warning("⚠ Medium Risk — be cautious.")
                else:
                    st.success("✅ Relatively safer region.")

                # SHAP explainability (best-effort)
                if SHAP_AVAILABLE:
                    st.markdown("#### 🔎 Why this score? (SHAP Explanation)")
                    try:
                        # compute shap for a small background - use rows for that state across years as background
                        bg = df[df["State"] == state][feature_cols]
                        if len(bg) < 5:
                            bg = df[feature_cols].sample(min(50, len(df)))
                        explainer = None
                        try:
                            explainer = shap.TreeExplainer(model)
                            shap_vals = explainer.shap_values(X)
                        except Exception:
                            explainer = shap.KernelExplainer(model.predict, bg)
                            shap_vals = explainer.shap_values(X, nsamples=100)
                        # shap_vals shape handling
                        if isinstance(shap_vals, list):
                            shap_plot_vals = shap_vals[0]
                        else:
                            shap_plot_vals = shap_vals
                        # bar plot of feature importance for the single sample
                        try:
                            # shap has bar plot
                            plt.figure(figsize=(7,3))
                            shap.summary_plot(shap_plot_vals, X, plot_type="bar", show=False)
                            st.pyplot(plt.gcf())
                            plt.clf()
                        except Exception:
                            # fallback: manual bar chart
                            import numpy as np
                            sv = shap_plot_vals[0] if shap_plot_vals.shape[0] > 0 else shap_plot_vals
                            feat_names = X.columns.tolist()
                            vals = sv
                            fig = px.bar(x=feat_names, y=vals, title="SHAP feature contributions (approx.)")
                            fig.update_layout(height=360, margin=dict(t=40,b=20))
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        st.info("SHAP explanation not available for this model or environment.")
                else:
                    st.info("SHAP not installed — install 'shap' to enable explainability (optional).")

                # provide PDF download (simple text report)
                tips_text = ""
                if risk == "High Risk":
                    tips_text = "\n".join([
                        "Avoid isolated areas after sunset",
                        "Share live location with trusted contacts",
                        "Keep emergency contacts ready",
                        "Prefer trusted transportation options"
                    ])
                elif risk == "Medium Risk":
                    tips_text = "\n".join([
                        "Travel with company when possible",
                        "Stay alert in crowded places",
                        "Use safety apps and share ETA"
                    ])
                else:
                    tips_text = "\n".join([
                        "Follow general precautions",
                        "Avoid unnecessary late-night travel",
                        "Keep phone charged and emergency contacts handy"
                    ])

                pdf_buffer = generate_pdf_report_text(state, year, score, risk, tips_text)
                st.download_button(
                    label="📄 Download Safety Report (PDF)",
                    data=pdf_buffer,
                    file_name=f"{state}_{year}_safety_report.pdf",
                    mime="application/pdf"
                )

# ------------------------------
# TAB 2 — What-if Simulation
# ------------------------------
with tab2:
    st.header("🧪 What-if Crime Scenario Simulation")
    sim_year = st.number_input("Simulation Year", min_value=2001, max_value=2025, value=2021, step=1)
    left, mid, right = st.columns(3)
    with left:
        rape = st.number_input("Rape", min_value=0, value=100)
        ka = st.number_input("Kidnapping & Abduction (K&A)", min_value=0, value=50)
        dd = st.number_input("Dowry Deaths (DD)", min_value=0, value=20)
    with mid:
        aow = st.number_input("Assault on Women (AoW)", min_value=0, value=150)
        aom = st.number_input("Assault on Minors (AoM)", min_value=0, value=30)
    with right:
        dv = st.number_input("Domestic Violence (DV)", min_value=0, value=80)
        wt = st.number_input("Women Trafficking (WT)", min_value=0, value=10)
    if st.button("Simulate Safety Score"):
        total = rape + ka + dd + aow + aom + dv + wt
        if total == 0:
            st.error("At least one crime count must be > 0.")
        else:
            X_sim = pd.DataFrame([{
                "Year": sim_year,
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
            try:
                score = float(model.predict(X_sim)[0])
                risk = risk_from_score(score)
                st.metric("Predicted Safety Score", f"{score:.2f}/100")
                st.write(f"**Risk Level:** `{risk}`")
                # offer PDF for simulation
                tips = ""
                if risk == "High Risk":
                    tips = "Avoid isolated areas; Share live location; Keep emergency contacts."
                elif risk == "Medium Risk":
                    tips = "Travel with company; Stay alert."
                else:
                    tips = "Follow general precautions."

                pdf_buf = generate_pdf_report_text("Simulated", sim_year, score, risk, tips)
                st.download_button("📄 Download Simulation Report (PDF)", pdf_buf, file_name=f"simulation_{sim_year}_report.pdf", mime="application/pdf")
            except Exception as e:
                st.error("Model prediction failed on simulated input: " + str(e))

# ------------------------------
# TAB 3 — Trend Graphs
# ------------------------------
with tab3:
    st.header("📈 Crime Trends (2001-2021)")
    col_ctrl, col_plot = st.columns([1,3])
    with col_ctrl:
        t_state = st.selectbox("Select State for Trend", df["State"].unique(), key="trend_state")
        crime = st.selectbox("Crime Type", crime_cols, key="trend_crime")
        smoothing = st.checkbox("Show 3-year moving average", value=False)
    tdf = df[df["State"] == t_state].sort_values("Year")
    fig = px.line(tdf, x="Year", y=crime, markers=True, title=f"{crime} Trend — {t_state}")
    if smoothing:
        tdf["ma3"] = tdf[crime].rolling(3, center=True, min_periods=1).mean()
        fig.add_trace(go.Scatter(x=tdf["Year"], y=tdf["ma3"], mode="lines", name="3-year MA", line=dict(dash="dash")))
    fig.update_layout(height=450, margin=dict(t=40,b=20))
    col_plot.plotly_chart(fig, use_container_width=True)

# ------------------------------
# TAB 4 — India GeoJSON Heatmap
# ------------------------------
with tab4:
    st.header("🗺 Heatmap — India (State boundaries)")

    hcrime = st.selectbox("Select Crime for Heatmap", crime_cols, key="heat_crime")

    st.markdown("Fetching GeoJSON for India states (online). If this fails, a fallback choropleth is used.")
    geo = fetch_geojson()
    hdf = df.groupby("State")[hcrime].sum().reset_index()

    if geo:
        try:
            # Attempt to match by state names — many geojson properties differ; this is best-effort.
            # Ensure the geojson feature property used for state names exists:
            # Try common properties: 'st_nm', 'STATE_NAME', 'name'
            sample_props = list(geo["features"][0]["properties"].keys())
            # find likely name property
            name_prop = None
            for p in ["st_nm", "ST_NM", "STATE", "STATE_NAME", "name", "NAME"]:
                if p in sample_props:
                    name_prop = p
                    break
            if not name_prop:
                # fallback to first string prop
                for p in sample_props:
                    if isinstance(geo["features"][0]["properties"][p], str):
                        name_prop = p
                        break

            # prepare a mapping from geo state name to feature id
            for i, feat in enumerate(geo["features"]):
                feat["id"] = feat["properties"].get(name_prop, feat["properties"].get(list(feat["properties"].keys())[0], f"id_{i}"))

            # create choropleth
            fig = px.choropleth_mapbox(
                hdf,
                geojson=geo,
                featureidkey="properties." + name_prop,
                locations="State",
                color=hcrime,
                mapbox_style="carto-positron",
                center={"lat": 22.0, "lon": 80.0},
                zoom=3.5,
                color_continuous_scale="Reds",
                title=f"India — {hcrime} (States)"
            )
            fig.update_layout(margin={"r":0,"t":40,"l":0,"b":0}, height=640)
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("GeoJSON mapping failed — falling back to simple choropleth.")
            fig = px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds", title=f"{hcrime} (fallback)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Could not fetch India GeoJSON — using fallback choropleth.")
        fig = px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds", title=f"{hcrime} (fallback)")
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# TAB 5 — Recommendations & Quick Tips
# ------------------------------
with tab5:
    st.header("🛡 Recommendations & Safety Tips")
    st.write("Use the slider to see recommended actions for a score band.")
    score_input = st.slider("Your Safety Score (example)", 0, 100, 50)
    if score_input < 40:
        st.error("🚨 High Risk — Recommended actions:")
        st.write("- Avoid isolated areas after sunset\n- Share live location with trusted contacts\n- Keep emergency contacts ready\n- Prefer verified transport")
    elif score_input < 70:
        st.warning("⚠ Medium Risk — Recommended actions:")
        st.write("- Travel with someone\n- Stay alert and avoid risky shortcuts\n- Use safety features & share ETA")
    else:
        st.success("✔ Safer area — general precautions:")
        st.write("- Avoid unnecessary late-night travel\n- Keep phone charged\n- Keep emergency contacts handy")

# ------------------------------
# TAB 6 — SOS Assistant
# ------------------------------
if "contacts" not in st.session_state:
    st.session_state["contacts"] = []

def add_contact(name, number):
    st.session_state["contacts"].append({"name": name, "number": number})

with tab6:
    st.header("🚨 SOS Assistant — Multi-contact")

    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Name")
        user_area = st.text_input("Area / Landmark")
    with col2:
        maps_link = st.text_input("Google Maps Link (Optional)", placeholder="https://maps.app.goo.gl/...")
        send_via_twilio = st.checkbox("Attempt send via Twilio (requires Twilio secrets & verified numbers)", value=False)

    st.markdown("---")
    st.subheader("Trusted Contacts")
    contacts = st.session_state["contacts"]
    if contacts:
        contact_list = [f"{c['name']} ({c['number']})" for c in contacts]
        selected = st.multiselect("Select contacts to alert", contact_list)
    else:
        st.info("No contacts yet. Add below.")
        selected = []

    ca, cb, cc = st.columns([3,3,1])
    with ca:
        new_name = st.text_input("Add contact name", key="add_name")
    with cb:
        new_number = st.text_input("Add WhatsApp number (10 digits or with code)", key="add_num")
    with cc:
        if st.button("Add Contact"):
            if not new_name or not new_number:
                st.error("Provide both name and number.")
            else:
                add_contact(new_name, new_number)
                st.success("Contact added.")
                st.experimental_rerun()

    st.markdown("---")
    if st.button("Generate & Show SOS Message"):
        if not user_name or not user_area:
            st.error("Enter your name and area.")
        elif len(selected) == 0:
            st.error("Select at least one contact.")
        else:
            sos_text = f"🚨 EMERGENCY ALERT 🚨\nI, {user_name}, am in danger at {user_area}.\nPlease reach me immediately."
            if maps_link:
                sos_text += f"\n📍 {maps_link}"
            st.code(sos_text)

            encoded = urllib.parse.quote(sos_text)
            st.markdown("### WhatsApp quick links (tap to open chat):")
            for entry in selected:
                nm, num = entry.split("(")
                num = num.replace(")", "").strip()
                # if 10-digit assume India
                link_num = num
                if len(link_num) == 10 and link_num.isdigit():
                    link_num = "91" + link_num
                wa_url = f"https://wa.me/{link_num}?text={encoded}"
                try:
                    st.markdown(f"- [{nm.strip()}]({wa_url})")
                except Exception:
                    st.write(f"- {nm.strip()} : {wa_url}")

            if send_via_twilio:
                st.info("Attempting Twilio sends (best-effort).")
                for entry in selected:
                    nm, num = entry.split("(")
                    num = num.replace(")", "").strip()
                    ok = send_whatsapp_sos(sos_text, num)
                    if ok:
                        st.success(f"Sent to {nm.strip()}")
                    else:
                        st.error(f"Failed to send to {nm.strip()} (Twilio).")

# ------------------------------
# Footer / helpful notes
# ------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div style='color:#94a3b8;font-size:13px'>Tip: If map or SHAP features do not display, ensure required packages are in your requirements.txt (see top of file). For GeoJSON, network access is required to fetch online file.</div>", unsafe_allow_html=True)
