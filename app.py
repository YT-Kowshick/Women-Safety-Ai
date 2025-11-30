# app.py — AI by Her (final robust single-file Streamlit app)
#
# Minimal requirements (add to requirements.txt):
# streamlit pandas joblib plotly requests reportlab
# Optional (enable these for extra features): folium streamlit-folium branca twilio shap matplotlib
#
# Usage: put CrimesOnWomenData.csv and optionally safety_model.pkl in app folder.
# Run: streamlit run app.py

import streamlit as st
import pandas as pd
import joblib
import urllib.parse
import requests
import io
import traceback
import plotly.express as px
import plotly.graph_objects as go
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Optional libs (import with try/except so the app never crashes)
try:
    from twilio.rest import Client
    TWILIO_AVAILABLE = True
except Exception:
    TWILIO_AVAILABLE = False

try:
    import shap
    import matplotlib.pyplot as plt
    SHAP_AVAILABLE = True
except Exception:
    SHAP_AVAILABLE = False

try:
    import folium
    from streamlit_folium import st_folium
    from branca.colormap import linear
    FOLIUM_AVAILABLE = True
except Exception:
    FOLIUM_AVAILABLE = False

# ----------------------------
# Safe rerun helper (handles different Streamlit versions)
# ----------------------------
def safe_rerun():
    try:
        st.experimental_rerun()
        return
    except Exception:
        pass
    try:
        st.rerun()
        return
    except Exception:
        return

# ----------------------------
# Page config + Neon-ish CSS
# ----------------------------
st.set_page_config(page_title="AI by Her — Women Safety", page_icon="🛡", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: Poppins, sans-serif; background: #061021; color:#e6eef8; }
.header { padding:18px; border-radius:12px; background: linear-gradient(135deg,#7b2cff,#00d4ff); box-shadow:0 12px 40px rgba(0,0,0,0.6); margin-bottom:20px;}
.neon-card { background: rgba(255,255,255,0.02); border-radius:12px; padding:16px; margin-bottom:16px; border:1px solid rgba(255,255,255,0.03); }
.small { font-size:13px; color:#94a3b8; }
.stButton>button { background: linear-gradient(90deg,#7b2cff,#00d4ff); color:white; border-radius:8px; padding:8px 12px; font-weight:700; }
.muted { color:#9aa0a6; }
a { color:#00eaff; }
</style>
""", unsafe_allow_html=True)

# ----------------------------
# Twilio setup (optional)
# ----------------------------
TWILIO_SID = st.secrets.get("TWILIO_SID", None)
TWILIO_AUTH = st.secrets.get("TWILIO_AUTH", None)
TWILIO_WHATSAPP = "whatsapp:+14155238886"
twilio_client = None
if TWILIO_AVAILABLE and TWILIO_SID and TWILIO_AUTH:
    try:
        twilio_client = Client(TWILIO_SID, TWILIO_AUTH)
    except Exception:
        twilio_client = None

def send_whatsapp_via_twilio(txt, number):
    if not twilio_client:
        return False
    try:
        if len(number) == 10 and number.isdigit():
            number = "91" + number
        twilio_client.messages.create(from_=TWILIO_WHATSAPP, body=txt, to=f"whatsapp:+{number}")
        return True
    except Exception:
        return False

# ----------------------------
# Helpers: PDF export, risk conversion, fallback predictor
# ----------------------------
def generate_pdf_report(state, year, score, risk, tips):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 60, "Women Safety Report — AI by Her")
    c.setFont("Helvetica", 11)
    c.drawString(50, height - 90, f"State: {state}")
    c.drawString(320, height - 90, f"Year: {year}")
    c.drawString(50, height - 110, f"Safety Score: {score:.2f}/100")
    c.drawString(320, height - 110, f"Risk Level: {risk}")
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

def fallback_predict(df_row):
    expected = ["Rape","K&A","DD","AoW","AoM","DV","WT"]
    for c in expected:
        if c not in df_row.columns:
            return 50.0
    total = df_row[expected].sum(axis=1).iloc[0]
    score = 100.0 * (1.0 - (total / (total + 1000.0)))
    return float(max(0.0, min(100.0, score)))

# ----------------------------
# Load CSV robustly & optional model load helper
# ----------------------------
@st.cache_data
def load_csv(path="CrimesOnWomenData.csv"):
    df = pd.read_csv(path)
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
    return df, expected, feature_cols

def try_load_model(path_or_file):
    try:
        # joblib.load accepts file-like objects too in this usage
        return joblib.load(path_or_file), None
    except Exception:
        return None, traceback.format_exc()

# initial load
csv_error = None
try:
    df, crime_cols, feature_cols = load_csv("CrimesOnWomenData.csv")
except Exception as e:
    df = None
    crime_cols = None
    feature_cols = None
    csv_error = traceback.format_exc()

# attempt to auto-load model file (if present)
model = None
model_error = None
try:
    model, model_error = try_load_model("safety_model.pkl")
except Exception:
    model = None
    model_error = traceback.format_exc()

# ----------------------------
# Sidebar: navigation and upload options
# ----------------------------
st.sidebar.markdown("<div style='font-weight:700;color:#00eaff;font-size:20px'>AI by Her</div>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigate", ["Dashboard","Existing","What-If","Trends","Heatmap","Leaderboard","Recommendations","SOS","Model"])

st.sidebar.markdown("---")
if st.sidebar.button("Refresh (data & model)"):
    safe_rerun()

st.sidebar.markdown("### Upload / Replace")
uploaded_model = st.sidebar.file_uploader("Upload safety_model.pkl (optional)", type=["pkl","joblib"])
if uploaded_model is not None:
    m, err = try_load_model(uploaded_model)
    if m:
        model = m
        model_error = None
        st.sidebar.success("Model uploaded and loaded successfully.")
    else:
        model = None
        model_error = err
        st.sidebar.error("Model upload failed (check model format).")

uploaded_csv = st.sidebar.file_uploader("Upload Crimes CSV (optional)", type=["csv"])
if uploaded_csv is not None:
    try:
        df_new, crime_cols_new, feature_cols_new = load_csv(uploaded_csv)
        df, crime_cols, feature_cols = df_new, crime_cols_new, feature_cols_new
        st.sidebar.success("CSV uploaded and loaded.")
        safe_rerun()
    except Exception as e:
        st.sidebar.error("CSV upload failed: check columns & format.")

# ----------------------------
# Header & status
# ----------------------------
st.markdown("""
<div class='header'>
  <h1 style='margin:0'>SheShield AI — Women Safety</h1>
  <div class='small muted' style='margin-top:6px'>Predictive safety scores • Heatmaps • What-if simulation • SOS Alerts</div>
</div>
""", unsafe_allow_html=True)

if csv_error:
    st.error("Data load error: missing or invalid 'CrimesOnWomenData.csv'. Upload correct CSV via sidebar.")
    with st.expander("Data load error (dev)"):
        st.code(csv_error)

if model is None:
    st.warning("ML model not loaded. The app will use a safe deterministic fallback predictor.")
    with st.expander("Model guidance"):
        st.write("If your model uses libraries like xgboost/lightgbm/catboost, add those to requirements.txt and redeploy, or upload model via sidebar.")
else:
    st.success("ML model loaded — predictions enabled.")

# ----------------------------
# Dashboard
# ----------------------------
if page == "Dashboard":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("National Overview")
    if df is None:
        st.info("No data available. Upload CSV in sidebar.")
    else:
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
        st.write(f"States: **{df['State'].nunique()}** • Years: **{df['Year'].nunique()}**")
        # show 5 lowest-scoring states
        ldf = df[df["Year"] == last_year].copy()
        if model is not None:
            try:
                ldf["score"] = list(model.predict(ldf[feature_cols]))
            except Exception:
                ldf["score"] = [fallback_predict(ldf.iloc[[i]][feature_cols]) for i in range(len(ldf))]
        else:
            ldf["score"] = [fallback_predict(ldf.iloc[[i]][feature_cols]) for i in range(len(ldf))]
        worst = ldf.sort_values("score").head(5)[["State","score"]]
        st.write("Top 5 lowest safety (latest year):")
        st.table(worst.reset_index(drop=True))
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Existing Data page
# ----------------------------
if page == "Existing":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Existing Data — Safety Prediction")
    if df is None:
        st.info("Upload CSV to use this page.")
    else:
        col1, col2 = st.columns([2,1])
        with col1:
            state = st.selectbox("Select State", sorted(df["State"].unique()))
        with col2:
            year = st.selectbox("Select Year", sorted(df["Year"].unique()))
        if st.button("Predict Safety"):
            row = df[(df["State"] == state) & (df["Year"] == year)]
            if row.empty:
                st.error("No data for selection.")
            else:
                X = pd.DataFrame([row.iloc[0][feature_cols]])
                if model is not None:
                    try:
                        score = float(model.predict(X)[0])
                    except Exception:
                        st.warning("Model prediction failed — using fallback.")
                        score = fallback_predict(X)
                else:
                    score = fallback_predict(X)
                risk = risk_from_score(score)
                st.metric("Safety Score", f"{score:.2f}/100")
                st.write(f"**Risk Level:** {risk}")
                # downloads
                st.download_button("Download state CSV", data=row.to_csv(index=False).encode('utf-8'), file_name=f"{state}_{year}.csv", mime="text/csv")
                tips = ""
                if risk == "High Risk":
                    tips = "Avoid isolated areas after sunset\nShare live location\nKeep emergency contacts ready\nPrefer verified transport"
                elif risk == "Medium Risk":
                    tips = "Travel with company\nStay alert\nUse safety apps"
                else:
                    tips = "Follow general precautions\nKeep phone charged and emergency contacts handy"
                pdf_buf = generate_pdf_report(state, year, score, risk, tips)
                st.download_button("Download Safety Report (PDF)", pdf_buf, file_name=f"{state}_{year}_report.pdf", mime="application/pdf")
                # SHAP (optional)
                if SHAP_AVAILABLE and model is not None:
                    with st.expander("SHAP explanation (optional)"):
                        try:
                            bg = df[feature_cols].sample(min(50, len(df)))
                            explainer = shap.TreeExplainer(model)
                            shap_vals = explainer.shap_values(X)
                            shap.summary_plot(shap_vals, X, plot_type="bar", show=False)
                            st.pyplot(plt.gcf())
                            plt.clf()
                        except Exception:
                            st.info("SHAP explanation unavailable for this model type or environment.")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# What-If Simulation page
# ----------------------------
if page == "What-If":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("What-If Crime Scenario")
    sim_year = st.number_input("Simulation Year", min_value=2001, max_value=2025, value=2021)
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
            if model is not None:
                try:
                    score = float(model.predict(X_sim)[0])
                except Exception:
                    st.warning("Model prediction failed — using fallback.")
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
# Trends page
# ----------------------------
if page == "Trends":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Trends Over Years")
    if df is None:
        st.info("Upload CSV to show trends.")
    else:
        t_state = st.selectbox("State", df["State"].unique(), key="trend_state")
        crime = st.selectbox("Crime", crime_cols, key="trend_crime")
        smoothing = st.checkbox("Show 3-year moving average", value=False)
        tdf = df[df["State"] == t_state].sort_values("Year")
        fig = px.line(tdf, x="Year", y=crime, markers=True, title=f"{crime} Trend — {t_state}")
        if smoothing:
            tdf["ma3"] = tdf[crime].rolling(3, center=True, min_periods=1).mean()
            fig.add_trace(go.Scatter(x=tdf["Year"], y=tdf["ma3"], mode="lines", name="3-year MA", line=dict(dash="dash")))
        fig.update_layout(height=420, margin=dict(t=40), paper_bgcolor="#061021", plot_bgcolor="rgba(255,255,255,0.02)", font=dict(color="white"))
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Heatmap (Folium/Leaflet) with Plotly fallback
# ----------------------------
if page == "Heatmap":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Heatmap — India (Leaflet / Folium)")
    if df is None:
        st.info("Upload CSV to show heatmap.")
    else:
        hcrime = st.selectbox("Select crime for heatmap", crime_cols, key="heat_crime")
        st.markdown("<div class='small'>If Folium or GeoJSON fail, app uses Plotly fallback.</div>", unsafe_allow_html=True)

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
                m = folium.Map(location=[22.0,80.0], zoom_start=5, tiles="CartoDB dark_matter")
                data_map = {r["State"].strip().lower(): r[hcrime] for _, r in hdf.iterrows()}
                maxv = hdf[hcrime].max() if not hdf.empty else 1
                minv = hdf[hcrime].min() if not hdf.empty else 0
                colormap = linear.YlOrRd_09.scale(minv, maxv)
                def style_fn(feature):
                    nm = str(feature["properties"].get(name_prop, "")).strip().lower()
                    val = data_map.get(nm, None)
                    if val is None:
                        return {"fillColor":"#222222","color":"#444444","weight":0.3,"fillOpacity":0.06}
                    return {"fillColor": colormap(val), "color":"#222", "weight":0.3, "fillOpacity":0.7}
                folium.GeoJson(geo, style_function=style_fn, tooltip=folium.GeoJsonTooltip(fields=[name_prop], aliases=["State:"])).add_to(m)
                colormap.caption = f"{hcrime} (sum)"
                colormap.add_to(m)
                # add centroids
                for feat in geo["features"]:
                    try:
                        nm = str(feat["properties"].get(name_prop, "")).strip()
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
                            folium.CircleMarker(location=[avg_lat, avg_lon], radius=4, color="#00eaff", fill=True, fill_opacity=0.9, popup=popup_html).add_to(m)
                    except Exception:
                        continue
                st_folium(m, width=980, height=640)
            except Exception as e:
                st.error("Folium map error — falling back to Plotly choropleth.")
                st.plotly_chart(px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds"), use_container_width=True)
        else:
            if not geo:
                st.info("Could not fetch GeoJSON — using Plotly fallback.")
            if not FOLIUM_AVAILABLE:
                st.info("Folium or streamlit-folium not installed — using Plotly fallback.")
            st.plotly_chart(px.choropleth(hdf, locationmode="country names", locations="State", color=hcrime, color_continuous_scale="Reds"), use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Leaderboard page
# ----------------------------
if page == "Leaderboard":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Leaderboard — Lowest Safety Scores (latest year)")
    if df is None:
        st.info("Upload CSV to enable leaderboard.")
    else:
        latest_year = int(df["Year"].max())
        ldf = df[df["Year"] == latest_year].copy()
        if model is not None:
            try:
                ldf["score"] = list(model.predict(ldf[feature_cols]))
            except Exception:
                ldf["score"] = [fallback_predict(ldf.iloc[[i]][feature_cols]) for i in range(len(ldf))]
        else:
            ldf["score"] = [fallback_predict(ldf.iloc[[i]][feature_cols]) for i in range(len(ldf))]
        top = ldf.sort_values("score").head(10)[["State","score"]].reset_index(drop=True)
        st.table(top)
        st.download_button("Download Leaderboard CSV", top.to_csv(index=False).encode('utf-8'), file_name="leaderboard.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Recommendations page
# ----------------------------
if page == "Recommendations":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Recommendations & Quick Tips")
    score_input = st.slider("Example Safety Score", 0, 100, 50)
    if score_input < 40:
        st.error("High risk — recommended actions:")
        st.write("- Avoid isolated areas after sunset\n- Share live location with trusted contacts\n- Keep emergency contacts ready\n- Prefer verified transport")
    elif score_input < 70:
        st.warning("Medium risk — recommended actions:")
        st.write("- Travel with company\n- Stay alert\n- Use safety apps and share ETA")
    else:
        st.success("Safer area — general precautions:")
        st.write("- Avoid unnecessary late-night travel\n- Keep phone charged\n- Keep emergency contacts handy")
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# SOS Assistant
# ----------------------------
if page == "SOS":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("SOS Assistant — Multi-contact (WhatsApp)")
    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your name")
        user_area = st.text_input("Area / Landmark")
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
                safe_rerun()
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
            st.markdown("WhatsApp quick links (tap):")
            for entry in selected:
                nm, num = entry.split("(")
                num = num.replace(")","").strip()
                link_num = num if not (len(num) == 10 and num.isdigit()) else "91"+num
                wa = f"https://wa.me/{link_num}?text={encoded}"
                st.markdown(f"- [{nm.strip()}]({wa})")
            st.write("")  # spacing
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
# Model page (diagnostics & optional traceback)
# ----------------------------
if page == "Model":
    st.markdown("<div class='neon-card'>", unsafe_allow_html=True)
    st.subheader("Model & Diagnostics")
    if model is None:
        st.warning("No ML model loaded. Upload via sidebar or add 'safety_model.pkl' to app folder.")
    else:
        st.success("ML model loaded.")
    if model_error:
        with st.expander("Model load error (dev)"):
            st.code(model_error)
    if df is not None:
        st.write("Run a quick diagnostic prediction:")
        s_state = st.selectbox("Select state for diagnostic", df["State"].unique(), key="diag_state")
        s_year = st.selectbox("Select year", sorted(df["Year"].unique()), key="diag_year")
        if st.button("Run diagnostic"):
            row = df[(df["State"]==s_state)&(df["Year"]==s_year)]
            if row.empty:
                st.error("No row found.")
            else:
                X = pd.DataFrame([row.iloc[0][feature_cols]])
                try:
                    s = float(model.predict(X)[0]) if model is not None else fallback_predict(X)
                    st.metric("Predicted safety score", f"{s:.2f}/100")
                    st.write("Risk:", risk_from_score(s))
                except Exception as e:
                    st.error("Prediction failed: " + str(e))
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------
# Footer: tips
# ----------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<div class='small muted'>Tip: Add optional packages to requirements.txt if you want maps (folium & streamlit-folium), SHAP plots (shap & matplotlib), or Twilio sends (twilio).</div>", unsafe_allow_html=True)
