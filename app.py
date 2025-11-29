############################################
#  AI BY HER — NEON PREMIUM A2 DASHBOARD   #
#  Final single-file app.py (shap optional)
#  Folium (Leaflet) integrated — math import fixed
############################################

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

from twilio.rest import Client
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Optional SHAP
try:
    import shap
    import matplotlib.pyplot as plt
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

# Folium + streamlit_folium (may be missing in some envs -> handle gracefully)
try:
    import folium
    from streamlit_folium import st_folium
    from branca.colormap import linear
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

############################################
# PAGE CONFIG + GLOBAL NEON CSS
############################################

st.set_page_config(
    page_title="AI by Her — Women Safety",
    page_icon="🛡",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; background: #0b0f19; color: #e6eef8; }
.header-box { width:100%; padding:25px; border-radius:16px; margin-bottom:25px;
    background: linear-gradient(135deg, #6f00ff, #00c8ff);
    box-shadow: 0 0 25px rgba(111,0,255,0.35), 0 0 25px rgba(0,200,255,0.25); }
.neon-card { background: rgba(255,255,255,0.04); border-radius:18px; padding:25px; margin-bottom:30px;
    backdrop-filter: blur(12px); border:1px solid rgba(255,255,255,0.06); }
.stButton>button { background: linear-gradient(135deg,#6f00ff,#00c8ff); color:white; border-radius:10px; padding:0.6rem 1.2rem; border:none; font-weight:600; box-shadow:0 0 12px rgba(0,200,255,0.45); }
.stButton>button:hover { transform:scale(1.04); box-shadow:0 0 20px rgba(0,200,255,0.8); }
input, select, textarea { background: rgba(255,255,255,0.06) !important; color: white !important; }
[data-testid="stSidebar"] { background: rgba(255,255,255,0.03); backdrop-filter: blur(15px); border-right:1px solid rgba(255,255,255,0.08); }
.sidebar-title { color:#00eaff; font-size:22px; font-weight:600; padding-bottom:12px; border-bottom:1px solid rgba(255,255,255,0.12); }
.small { font-size:13px; color:#94a3b8; }
.muted { color:#9aa0a6; font-size:14px; }
.js-plotly-plot .plotly { border-radius:12px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

############################################
# TWILIO CONFIG (optional)
############################################

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

############################################
# LOAD DATA + MODEL
############################################

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

    model = joblib.load("safety_model.pkl")
    return df, model, crime_cols, feature_cols

df, model, crime_cols, feature_cols = load_all()

############################################
# HELPERS
############################################

def risk_from_score(score: float) -> str:
    if score < 40:
        return "High Risk"
    elif score < 70:
        return "Medium Risk"
    return "Safe"

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

@st.cache_data
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

############################################
# Folium (Leaflet) helper
############################################

def leaflet_state_heatmap(df, model, feature_cols, geojson, crime_col="Rape"):
    if not FOLIUM_AVAILABLE:
        st.warning("Folium or streamlit-folium not installed — folium map unavailable.")
        return None

    agg = df.groupby("State")[crime_col].sum().reset_index().rename(columns={crime_col: "crime_sum"})
    latest = int(df["Year"].max())
    scores = {}
    for st_name in df["State"].unique():
        row = df[(df["State"] == st_name) & (df["Year"] == latest)]
        if not row.empty:
            try:
                X = pd.DataFrame([row.iloc[0][feature_cols]])
                scores[st_name.lower()] = float(model.predict(X)[0])
            except Exception:
                scores[st_name.lower()] = None
        else:
            scores[st_name.lower()] = None
    agg["safety_score"] = agg["State"].str.lower().map(scores)

    vmin = float(agg["crime_sum"].min())
    vmax = float(agg["crime_sum"].max())
    if math.isclose(vmin, vmax):
        vmax = vmin + 1.0
    colormap = linear.YlOrRd_09.scale(vmin, vmax)

    sample_props = list(geojson["features"][0]["properties"].keys())
    name_prop = None
    for p in ["st_nm", "ST_NM", "STATE", "STATE_NAME", "name", "NAME"]:
        if p in sample_props:
            name_prop = p
            break
    if not name_prop:
        for p in sample_props:
            if isinstance(geojson["features"][0]["properties"][p], str):
                name_prop = p
                break
    if not name_prop:
        st.error("Could not detect state name property in GeoJSON.")
        return None

    def style_fn(feature):
        st_nm = feature["properties"].get(name_prop, "").strip()
        row = agg[agg["State"].str.lower() == st_nm.lower()]
        if not row.empty:
            value = float(row.iloc[0]["crime_sum"])
            return {"fillOpacity": 0.7, "weight": 0.6, "color": "#222", "fillColor": colormap(value)}
        else:
            return {"fillOpacity": 0.15, "weight": 0.4, "color": "#444", "fillColor": "#666666"}

    m = folium.Map(location=[22.0, 80.0], zoom_start=5, tiles="CartoDB dark_matter")

    folium.GeoJson(
        geojson,
        name="States",
        style_function=style_fn,
        highlight_function=lambda x: {"weight":2, "color":"#00ffff", "fillOpacity":0.9},
        tooltip=folium.GeoJsonTooltip(fields=[name_prop], aliases=["State:"], localize=True)
    ).add_to(m)

    for feat in geojson["features"]:
        st_nm = feat["properties"].get(name_prop, "").strip()
        try:
            geom = feat["geometry"]
            coords = []
            if geom["type"] == "Polygon":
                coords = geom["coordinates"][0]
            elif geom["type"] == "MultiPolygon":
                coords = geom["coordinates"][0][0]
            if coords:
                avg_lat = sum([c[1] for c in coords]) / len(coords)
                avg_lon = sum([c[0] for c in coords]) / len(coords)
                row = agg[agg["State"].str.lower() == st_nm.lower()]
                if not row.empty:
                    crime_v = int(row.iloc[0]["crime_sum"])
                    sc = row.iloc[0]["safety_score"]
                    sc_text = f"{sc:.1f}/100" if (sc is not None and not pd.isna(sc)) else "N/A"
                    wa_msg = urllib.parse.quote(f"EMERGENCY: Please help. Location: {st_nm}")
                    wa_link = f"https://wa.me/91XXXXXXXXXX?text={wa_msg}"
                    html = f"""<div style="font-family:Arial;color:#012"> <b>{st_nm}</b><br/> Crime (sum): <b>{crime_v}</b><br/> Safety Score: <b>{sc_text}</b><br/><a href="{wa_link}" target="_blank">Quick WhatsApp</a></div>"""
                else:
                    html = f"<div><b>{st_nm}</b><br/>No data</div>"
                folium.Marker(
                    location=[avg_lat, avg_lon],
                    icon=folium.DivIcon(html=f"""<div style="font-size:11px;color:#fff;background:rgba(0,0,0,0.45);padding:4px;border-radius:6px">{st_nm}</div>"""),
                    popup=folium.Popup(html, max_width=300)
                ).add_to(m)
        except Exception:
            continue

    # caption uses crime_col
    try:
        colormap.caption = f"{crime_col} (sum)"
        colormap.add_to(m)
    except Exception:
        pass

    return st_folium(m, width=900, height=700)

############################################
# SIDEBAR NAV
############################################

st.sidebar.markdown("<div class='sidebar-title'>🛡 AI by Her</div>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["Dashboard", "Existing Data", "What-If Simulation", "Trends", "Heatmap", "Recommendations", "SOS Assistant"])

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
# PAGES
############################################

if page == "Dashboard":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("📊 National Safety Overview")
    last_year = int(df["Year"].max())
    try:
        nat_scores = model.predict(df[df["Year"] == last_year][feature_cols])
        avg_score = float(pd.Series(nat_scores).mean())
        st.metric(f"Avg Safety Score ({last_year})", f"{avg_score:.2f}")
    except Exception:
        st.metric("Avg Safety Score", "—")
    st.write(f"States Covered: **{df['State'].nunique()}**")
    st.markdown("</div>", unsafe_allow_html=True)

if page == "Existing Data":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("📍 Existing Data — Safety Prediction")
    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("Select State", sorted(df["State"].unique()))
    with col2:
        year = st.selectbox("Select Year", sorted(df["Year"].unique()))
    if st.button("Predict Safety"):
        row = df[(df["State"] == state) & (df["Year"] == year)]
        if row.empty:
            st.error("No data for this selection.")
        else:
            row = row.iloc[0]
            X = pd.DataFrame([row[feature_cols]])
            try:
                score = float(model.predict(X)[0])
                risk = risk_from_score(score)
                st.metric("Safety Score", f"{score:.2f}")
                st.write(f"**Risk Level:** {risk}")
                if SHAP_AVAILABLE:
                    st.markdown("#### 🔎 Why this score? (SHAP)")
                    try:
                        bg = df[df["State"] == state][feature_cols]
                        if len(bg) < 5:
                            bg = df[feature_cols].sample(min(50, len(df)))
                        try:
                            explainer = shap.TreeExplainer(model)
                            shap_vals = explainer.shap_values(X)
                        except Exception:
                            explainer = shap.KernelExplainer(model.predict, bg)
                            shap_vals = explainer.shap_values(X, nsamples=100)
                        if isinstance(shap_vals, list):
                            shap_plot_vals = shap_vals[0]
                        else:
                            shap_plot_vals = shap_vals
                        try:
                            plt.figure(figsize=(7,3))
                            shap.summary_plot(shap_plot_vals, X, plot_type="bar", show=False)
                            st.pyplot(plt.gcf())
                            plt.clf()
                        except Exception:
                            feat_names = X.columns.tolist()
                            vals = shap_plot_vals[0] if getattr(shap_plot_vals, "shape", None) else shap_plot_vals
                            fig = px.bar(x=feat_names, y=vals, title="SHAP contributions")
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception:
                        st.info("SHAP explanation unavailable.")
                else:
                    st.info("SHAP not installed — install 'shap' to enable explainability.")
                tips_text = ""
                if risk == "High Risk":
                    tips_text = "\n".join(["Avoid isolated areas after sunset", "Share live location with trusted contacts", "Keep emergency contacts ready", "Prefer trusted transportation options"])
                elif risk == "Medium Risk":
                    tips_text = "\n".join(["Travel with company when possible", "Stay alert in crowded places", "Use safety apps and share ETA"])
                else:
                    tips_text = "\n".join(["Follow general precautions", "Avoid unnecessary late-night travel", "Keep phone charged and emergency contacts handy"])
                pdf_buffer = generate_pdf_report_text(state, year, score, risk, tips_text)
                st.download_button(label="📄 Download Safety Report (PDF)", data=pdf_buffer, file_name=f"{state}_{year}_safety_report.pdf", mime="application/pdf")
            except Exception as e:
                st.error("Prediction failed: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

if page == "What-If Simulation":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🧪 What-If Crime Simulation")
    sim_year = st.number_input("Simulation Year", min_value=2001, max_value=2025, value=2021, step=1)
    left, mid, right = st.columns(3)
    with left:
        rape = left.number_input("Rape", min_value=0, value=100)
        ka = left.number_input("Kidnapping & Abduction (K&A)", min_value=0, value=50)
        dd = left.number_input("Dowry Deaths (DD)", min_value=0, value=20)
    with mid:
        aow = mid.number_input("Assault on Women (AoW)", min_value=0, value=150)
        aom = mid.number_input("Assault on Minors (AoM)", min_value=0, value=30)
    with right:
        dv = right.number_input("Domestic Violence (DV)", min_value=0, value=80)
        wt = right.number_input("Women Trafficking (WT)", min_value=0, value=10)
    if st.button("Simulate Safety Score"):
        total = rape + ka + dd + aow + aom + dv + wt
        if total == 0:
            st.error("At least one crime count must be > 0.")
        else:
            X_sim = pd.DataFrame([{
                "Year": sim_year, "Rape": rape, "K&A": ka, "DD": dd, "AoW": aow,
                "AoM": aom, "DV": dv, "WT": wt,
                "Rape_ratio": rape/total, "K&A_ratio": ka/total, "DD_ratio": dd/total,
                "AoW_ratio": aow/total, "AoM_ratio": aom/total, "DV_ratio": dv/total, "WT_ratio": wt/total
            }])
            try:
                score = float(model.predict(X_sim)[0])
                risk = risk_from_score(score)
                st.metric("Predicted Safety Score", f"{score:.2f}/100")
                st.write(f"**Risk Level:** `{risk}`")
                pdf_buf = generate_pdf_report_text("Simulated", sim_year, score, risk, "Recommendations based on simulated score.")
                st.download_button("📄 Download Simulation Report (PDF)", pdf_buf, file_name=f"simulation_{sim_year}_report.pdf", mime="application/pdf")
            except Exception as e:
                st.error("Model prediction failed on simulated input: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

if page == "Trends":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("📈 Trends Over Years")
    col1, col2 = st.columns([1,3])
    with col1:
        t_state = st.selectbox("State", df["State"].unique(), key="trend_state")
        crime = st.selectbox("Crime Type", crime_cols, key="trend_crime")
        smoothing = st.checkbox("Show 3-year moving average", value=False)
    tdf = df[df["State"] == t_state].sort_values("Year")
    fig = px.line(tdf, x="Year", y=crime, markers=True, title=f"{crime} Trend — {t_state}")
    if smoothing:
        tdf["ma3"] = tdf[crime].rolling(3, center=True, min_periods=1).mean()
        fig.add_trace(go.Scatter(x=tdf["Year"], y=tdf["ma3"], mode="lines", name="3-year MA", line=dict(dash="dash")))
    fig.update_layout(height=450, margin=dict(t=40,b=20), paper_bgcolor='#0b0f19', plot_bgcolor='rgba(255,255,255,0.03)', font=dict(color='white'))
    col2.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if page == "Heatmap":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🗺 Heatmap — India (Leaflet / Folium)")
    hcrime = st.selectbox("Select Crime for Heatmap", crime_cols, key="heat_crime")
    st.markdown("<div class='small'>If Folium is not installed or network blocked, app will fallback to Plotly choropleth.</div>", unsafe_allow_html=True)
    geo = fetch_geojson()
    hdf = df.groupby("State")[hcrime].sum().reset_index()
    if geo and FOLIUM_AVAILABLE:
        try:
            leaflet_state_heatmap(df, model, feature_cols, geo, crime_col=hcrime)
        except Exception as e:
            st.error("Folium map failed: " + str(e))
            fig = px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds", title=f"{hcrime} (fallback)")
            st.plotly_chart(fig, use_container_width=True)
    else:
        if not geo:
            st.warning("Could not fetch GeoJSON — using fallback choropleth.")
        elif not FOLIUM_AVAILABLE:
            st.warning("Folium / streamlit-folium not installed — using fallback choropleth.")
        fig = px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds", title=f"{hcrime} (fallback)")
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

if page == "Recommendations":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🛡 Recommendations & Safety Tips")
    score_input = st.slider("Your Safety Score (example)", 0, 100, 50)
    if score_input < 40:
        st.error("🚨 High Risk — Follow these:")
        st.write("- Avoid isolated areas after sunset  \n- Share live location with someone trusted  \n- Keep emergency contacts and SOS ready")
    elif score_input < 70:
        st.warning("⚠ Medium Risk — Follow these:")
        st.write("- Travel with company when possible  \n- Stay alert in crowded places  \n- Use safety features on phone apps")
    else:
        st.success("✔ Safe Zone — Follow general precautions:")
        st.write("- Avoid late-night solo travel if avoidable  \n- Keep phone charged  \n- Keep emergency contacts handy")
    st.markdown("</div>", unsafe_allow_html=True)

if page == "SOS Assistant":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("🚨 SOS Assistant — Multi-contact")
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Name")
        user_area = st.text_input("Area / Landmark")
    with col2:
        maps_link = st.text_input("Google Maps Link (Optional)", placeholder="https://maps.app.goo.gl/...")
        send_via_twilio = st.checkbox("Attempt send via Twilio (requires Twilio secrets & verified numbers)", value=False)
    st.markdown("---")
    st.subheader("Trusted Contacts")
    if "contacts" not in st.session_state:
        st.session_state["contacts"] = []
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
                st.session_state["contacts"].append({"name": new_name, "number": new_number})
                st.success("Contact added.")
                st.rerun()
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
                link_num = num
                if len(link_num) == 10 and link_num.isdigit():
                    link_num = "91" + link_num
                wa_url = f"https://wa.me/{link_num}?text={encoded}"
                st.markdown(f"- [{nm.strip()}]({wa_url})")
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
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='small muted'>Tip: If Folium map does not appear, ensure 'folium' and 'streamlit-folium' are in requirements.txt and GeoJSON fetch is allowed by network.</div>", unsafe_allow_html=True)
