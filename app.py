# app.py - visually upgraded professional UI (keeps your model & Twilio logic intact)
import streamlit as st
import pandas as pd
import joblib
from twilio.rest import Client
import urllib.parse
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------
# TWILIO (unchanged)
# ------------------------------
TWILIO_SID = st.secrets["TWILIO_SID"]
TWILIO_AUTH = st.secrets["TWILIO_AUTH"]
TWILIO_WHATSAPP = "whatsapp:+14155238886"
client = Client(TWILIO_SID, TWILIO_AUTH)


def send_whatsapp_sos(message, user_phone):
    try:
        msg = client.messages.create(
            from_=TWILIO_WHATSAPP,
            body=message,
            to=f"whatsapp:{user_phone}"
        )
        return True
    except:
        return False


# ------------------------------
# LOAD DATA + MODEL (unchanged)
# ------------------------------
@st.cache_data
def load_data_and_model():
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    crime_cols = ['Rape','K&A','DD','AoW','AoM','DV','WT']
    df["TotalCrimes"] = df[crime_cols].sum(axis=1)

    # avoid division by zero - safer
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


df, model, crime_cols, feature_cols = load_data_and_model()


# ------------------------------
# RISK LABEL
# ------------------------------
def risk_from_score(score: float) -> str:
    if score < 40:
        return "High Risk"
    elif score < 70:
        return "Medium Risk"
    return "Safe"


# ------------------------------
# STYLES (modern card + spacing)
# ------------------------------
st.set_page_config(page_title="Women Safety AI", page_icon="🛡", layout="wide")

# Minimal modern CSS — small, safe, enhances readability
st.markdown(
    """
    <style>
    /* Font + background tuning */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    html, body, [class*="css"]  {
        font-family: "Inter", sans-serif;
    }
    .app-header {
        padding: 18px 12px;
        border-radius: 12px;
        margin-bottom: 18px;
    }
    .card {
        background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(255,255,255,0.01));
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 6px 18px rgba(2,6,23,0.35);
        margin-bottom: 16px;
    }
    .muted { color: #9aa0a6; font-size: 14px; }
    .metric-title { font-weight:600; font-size:14px; color:#cbd5e1; }
    .small-note { color:#94a3b8; font-size:13px; }
    .btn-space { margin-top: 8px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------
# HEADER
# ------------------------------
with st.container():
    st.markdown("<div class='app-header'>", unsafe_allow_html=True)
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("### 🛡 AI-based Women Safety Prediction")
        st.markdown(
            "<div class='muted'>Estimate Safety Score (0–100) for each Indian state & year using ML — explore scenarios, trends and send SOS alerts.</div>",
            unsafe_allow_html=True
        )
    with c2:
        # quick global metric: national average last year
        latest_year = int(df["Year"].max())
        nat_df = df[df["Year"] == latest_year]
        nat_total = []
        # compute safety score using your model on aggregated state rows then average
        try:
            sample_X = nat_df[feature_cols]
            nat_scores = model.predict(sample_X)
            nat_avg = float(nat_scores.mean())
            st.metric(label=f"Avg Safety ({latest_year})", value=f"{nat_avg:.1f}/100")
        except Exception:
            st.metric(label=f"Avg Safety ({latest_year})", value="—")
    st.markdown("</div>", unsafe_allow_html=True)


# ------------------------------
# TABS
# ------------------------------
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Existing Data Safety Check",
    "🧪 What-if Simulation",
    "📈 Trend Graphs",
    "🗺 Heatmap",
    "🛡 Recommendations",
    "🚨 SOS Assistant"
])


# ============================================================== #
# TAB 1: EXISTING DATA (clean card layout)
# ============================================================== #
with tab1:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📊 Check Safety for Existing State & Year")
    st.markdown("<div class='small-note'>Select a state & year to see the model prediction and quick safety tips.</div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        state = st.selectbox("State", sorted(df["State"].unique()))
    with col2:
        year = st.selectbox("Year", sorted(df["Year"].unique()))
    with col3:
        st.write("")  # spacing
        if st.button("Check Safety", key="existing", help="Run prediction for selected state & year"):
            row = df[(df["State"] == state) & (df["Year"] == year)]
            if row.empty:
                st.error("No data available for the selection.")
            else:
                row = row.iloc[0]
                x = pd.DataFrame([row[feature_cols]])
                score = float(model.predict(x)[0])
                risk = risk_from_score(score)

                # show results in neat columns
                m1, m2, m3 = st.columns([1, 1, 2])
                m1.metric("Safety Score", f"{score:.2f}/100")
                m2.metric("Risk Level", risk)
                with m3:
                    if risk == "High Risk":
                        st.error("⚠ High Risk – Avoid travelling alone at late nights.")
                    elif risk == "Medium Risk":
                        st.warning("⚠ Medium Risk – Stay cautious.")
                    else:
                        st.success("✔ Relatively safer region. Follow normal precautions.")

    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================== #
# TAB 2: WHAT-IF SIMULATION (improved spacing + quick compare)
# ============================================================== #
with tab2:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🧪 What-if Crime Scenario Simulation")

    st.markdown("<div class='small-note'>Adjust counts and simulate predicted safety score. Use the Compare button to quickly compare with an existing state/year.</div>", unsafe_allow_html=True)

    sim_year = st.number_input("Simulation Year", 2001, 2025, 2021)

    # grouped inputs with clearer labels
    left, middle, right = st.columns(3)
    with left:
        rape = st.number_input("Rape", 0, value=100)
        ka = st.number_input("Kidnapping & Abduction (K&A)", 0, value=50)
        dd = st.number_input("Dowry Deaths (DD)", 0, value=20)
    with middle:
        aow = st.number_input("Assault on Women (AoW)", 0, value=150)
        aom = st.number_input("Assault on Minors (AoM)", 0, value=30)
    with right:
        dv = st.number_input("Domestic Violence (DV)", 0, value=80)
        wt = st.number_input("Women Trafficking (WT)", 0, value=10)

    # action row
    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        if st.button("Simulate Safety Score", key="simulate"):
            total = rape + ka + dd + aow + aom + dv + wt
            if total == 0:
                st.error("Crime numbers cannot be all zero.")
            else:
                x_sim = pd.DataFrame([{
                    "Year": sim_year,
                    "Rape": rape, "K&A": ka, "DD": dd, "AoW": aow,
                    "AoM": aom, "DV": dv, "WT": wt,
                    "Rape_ratio": rape/total,
                    "K&A_ratio": ka/total,
                    "DD_ratio": dd/total,
                    "AoW_ratio": aow/total,
                    "AoM_ratio": aom/total,
                    "DV_ratio": dv/total,
                    "WT_ratio": wt/total,
                }])

                score = float(model.predict(x_sim)[0])
                risk = risk_from_score(score)

                st.markdown("### 🔍 Simulation Result")
                c1, c2 = st.columns([1, 2])
                c1.metric("Predicted Score", f"{score:.2f}/100")
                c2.write(f"**Risk Level:** {risk}")
    with action_col2:
        st.write("")  # placeholder for symmetry

    # optional: quick compare with existing selection
    with st.expander("Compare with an existing state/year"):
        comp_state = st.selectbox("Compare State", sorted(df["State"].unique()), key="comp_state")
        comp_year = st.selectbox("Compare Year", sorted(df["Year"].unique()), key="comp_year")
        if st.button("Run Compare", key="compare_button"):
            comp_row = df[(df["State"] == comp_state) & (df["Year"] == comp_year)]
            if comp_row.empty:
                st.error("No data for compare selection.")
            else:
                comp_row = comp_row.iloc[0]
                comp_X = pd.DataFrame([comp_row[feature_cols]])
                comp_score = float(model.predict(comp_X)[0])
                st.markdown(f"**{comp_state} ({comp_year})** — Score: **{comp_score:.2f}/100**")


    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================== #
# TAB 3: TREND GRAPH (bigger chart, clearer title)
# ============================================================== #
with tab3:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📈 Crime Trend Over the Years")

    controls_col, plot_col = st.columns([1, 3])
    with controls_col:
        t_state = st.selectbox("Select State", df["State"].unique(), key="trend_state")
        crime_type = st.selectbox("Crime Type", crime_cols, key="trend_crime")
        smoothing = st.checkbox("Show 3-year moving average", value=False)

    tdf = df[df["State"] == t_state].sort_values("Year")
    fig = px.line(tdf, x="Year", y=crime_type, markers=True, title=f"{crime_type} Trend in {t_state}")
    fig.update_layout(height=420, margin=dict(t=40, b=20, l=20, r=20))
    if smoothing:
        tdf["ma3"] = tdf[crime_type].rolling(3, center=True, min_periods=1).mean()
        fig.add_trace(go.Scatter(x=tdf["Year"], y=tdf["ma3"], mode="lines", name="3-year MA", line=dict(dash="dash")))

    with plot_col:
        st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================== #
# TAB 4: HEATMAP (with clearer colorbar)
# ============================================================== #
with tab4:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🗺 Crime Heatmap Across India")

    hcrime = st.selectbox("Select Crime Type for Heatmap", crime_cols, key="heat_crime")

    hdf = df.groupby("State")[hcrime].sum().reset_index()
    # Ensure location names match Plotly's expectations (country names mode)
    fig = px.choropleth(
        hdf,
        locationmode="country names",
        locations="State",
        color=hcrime,
        color_continuous_scale="Reds",
        title=f"India Heatmap – {hcrime}",
    )
    fig.update_layout(height=560, margin=dict(t=40, b=10, l=10, r=10))
    st.plotly_chart(fig, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================== #
# TAB 5: SAFETY RECOMMENDATIONS (card + dynamic tips)
# ============================================================== #
with tab5:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🛡 AI-Based Safety Recommendations")
    st.markdown("<div class='small-note'>Use your score (or simulated score) to get tailored safety suggestions.</div>", unsafe_allow_html=True)

    score_input = st.slider("Your Safety Score", 0, 100, 50)

    if score_input < 40:
        st.error("🚨 High Risk – Follow these:")
        st.write("""
- Avoid isolated areas after sunset  
- Share live location with someone trusted  
- Keep emergency contacts and SOS ready  
- Prefer verified transportation platforms  
""")
    elif score_input < 70:
        st.warning("⚠ Medium Risk – Follow these:")
        st.write("""
- Travel with company when possible  
- Stay alert and keep belongings secure  
- Use safety features on phones/apps  
""")
    else:
        st.success("✔ Safe Zone – Follow general precautions:")
        st.write("""
- Avoid late-night solo travel if avoidable  
- Keep phone charged and emergency contacts close  
- Trust your instincts and avoid risky situations  
""")
    st.markdown("</div>", unsafe_allow_html=True)


# ============================================================== #
# TAB 6: SOS ASSISTANT (visual improvements)
# ============================================================== #
if "contacts" not in st.session_state:
    st.session_state["contacts"] = []


def get_contacts():
    return st.session_state["contacts"]


def add_contact(name, number):
    st.session_state["contacts"].append({"name": name, "number": number})


with tab6:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.header("🚨 SOS Message Assistant (Multi Contact)")

    st.markdown("<div class='small-note'>Prepare a WhatsApp SOS message (links generated) or send using Twilio (if configured).</div>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Name")
        user_area = st.text_input("Your Area / Landmark")
    with col2:
        maps_link = st.text_input("Google Maps Link (Optional)", placeholder="https://maps.app.goo.gl/...")
        send_direct = st.checkbox("Attempt to send via Twilio WhatsApp (requires Twilio & verified numbers)", value=False)

    st.markdown("---")
    st.subheader("Trusted Contacts")
    contacts = get_contacts()
    if len(contacts) == 0:
        st.info("No contacts added yet. Add below.")
        selected = []
    else:
        contact_list = [f"{c['name']} ({c['number']})" for c in contacts]
        selected = st.multiselect("Select Contacts to alert", contact_list)

    # Add contact row
    ca, cb, cc = st.columns([3, 3, 1])
    with ca:
        new_name = st.text_input("Name", key="new_name")
    with cb:
        new_number = st.text_input("WhatsApp Number (10 digits)", key="new_number")
    with cc:
        if st.button("Add", key="add_contact_btn"):
            if not new_name or not new_number:
                st.error("Provide both name and number.")
            elif not new_number.isdigit() or len(new_number) not in (10, 12):
                st.error("Enter valid digits (10 or 12 if country code).")
            else:
                add_contact(new_name, new_number)
                st.success("Contact added.")
                st.experimental_rerun()

    st.markdown("---")

    # Generate & Send
    if st.button("Generate & Show SOS Message"):
        if not user_name or not user_area:
            st.error("Enter name & area.")
        elif len(selected) == 0:
            st.error("Select at least one contact.")
        else:
            sos_msg = f"🚨 EMERGENCY ALERT 🚨\nI, {user_name}, am in danger at {user_area}.\nPlease reach me immediately."
            if maps_link:
                sos_msg += f"\n📍 {maps_link}"

            st.markdown("**SOS Message**")
            st.code(sos_msg)

            encoded = urllib.parse.quote(sos_msg)
            st.markdown("**Send Links (tap to open WhatsApp chat)**")
            for entry in selected:
                name, number = entry.split("(")
                number = number.replace(")", "").strip()
                wa_url = f"https://wa.me/91{number}?text={encoded}"
                # link button (Streamlit >= certain versions support link_button)
                try:
                    st.link_button(f"Send to {name.strip()} via WhatsApp", wa_url)
                except Exception:
                    st.markdown(f"- [{name.strip()}]({wa_url})")

            if send_direct:
                st.info("Attempting to send via Twilio...")
                # attempt Twilio sends (best-effort)
                for entry in selected:
                    name, number = entry.split("(")
                    number = number.replace(")", "").strip()
                    # ensure number has country code
                    num = number
                    if len(num) == 10:
                        num = f"91{num}"
                    ok = send_whatsapp_sos(sos_msg, num)
                    if ok:
                        st.success(f"Sent to {name.strip()}")
                    else:
                        st.error(f"Failed to send to {name.strip()} (Twilio).")

    st.markdown("</div>", unsafe_allow_html=True)
