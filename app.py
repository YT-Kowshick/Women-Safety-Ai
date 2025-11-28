import streamlit as st
import pandas as pd
import joblib
from twilio.rest import Client

# Load Twilio credentials safely
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
    except Exception as e:
        return False


# ---------- LOAD DATA & MODEL ----------

@st.cache_data
def load_data_and_model():
    df = pd.read_csv("CrimesOnWomenData.csv")
    if "Unnamed: 0" in df.columns:
        df = df.drop(columns=["Unnamed: 0"])

    crime_cols = ['Rape','K&A','DD','AoW','AoM','DV','WT']
    df["TotalCrimes"] = df[crime_cols].sum(axis=1)

    for c in crime_cols:
        df[c + "_ratio"] = df[c] / df["TotalCrimes"]

    feature_cols = [
        'Year',
        'Rape','K&A','DD','AoW','AoM','DV','WT',
        'Rape_ratio','K&A_ratio','DD_ratio','AoW_ratio','AoM_ratio','DV_ratio','WT_ratio'
    ]

    model = joblib.load("safety_model.pkl")
    # scaler = joblib.load("scaler.pkl")  # now not used, but kept for future

    return df, model, crime_cols, feature_cols

df, model, crime_cols, feature_cols = load_data_and_model()

def risk_from_score(score: float) -> str:
    if score < 40:
        return "High Risk"
    elif score < 70:
        return "Medium Risk"
    return "Safe"

# ---------- STREAMLIT UI ----------

st.set_page_config(page_title="Women Safety AI", page_icon="🛡", layout="centered")

st.title("🛡 AI-based Women Safety Prediction")
st.write(
    "This app uses **crimes against women data (2001–2021)** "
    "and a Machine Learning model to estimate a **Safety Score (0–100)** "
    "and Risk Level for each state and year in India."
)

tab1, tab2, tab3 = st.tabs([
    "📊 Existing Data Safety Check",
    "🧪 What-if Simulation",
    "🚨 SOS Assistant"
])

# ---------- TAB 1: EXISTING DATA ----------

with tab1:
    st.subheader("📊 Check Safety for Existing State & Year")

    col1, col2 = st.columns(2)
    with col1:
        state = st.selectbox("Select State", sorted(df["State"].unique()))
    with col2:
        year = st.selectbox("Select Year", sorted(df["Year"].unique()))

    if st.button("Check Safety", key="existing"):
        row = df[(df["State"] == state) & (df["Year"] == year)]
        if row.empty:
            st.error("No data for this state & year.")
        else:
            row = row.iloc[0]

            x = pd.DataFrame([{
                "Year": row["Year"],
                "Rape": row["Rape"],
                "K&A": row["K&A"],
                "DD": row["DD"],
                "AoW": row["AoW"],
                "AoM": row["AoM"],
                "DV": row["DV"],
                "WT": row["WT"],
                "Rape_ratio": row["Rape_ratio"],
                "K&A_ratio": row["K&A_ratio"],
                "DD_ratio": row["DD_ratio"],
                "AoW_ratio": row["AoW_ratio"],
                "AoM_ratio": row["AoM_ratio"],
                "DV_ratio": row["DV_ratio"],
                "WT_ratio": row["WT_ratio"],
            }])

            score = float(model.predict(x)[0])
            risk = risk_from_score(score)

            st.markdown(f"### 🔍 Result for **{state} – {int(year)}**")
            st.metric("Predicted Safety Score", f"{score:.2f}")
            st.write(f"**Risk Level:** `{risk}`")

            if risk == "High Risk":
                st.error("⚠ High Risk area – avoid travelling alone, especially at night. Share live location with trusted contacts.")
            elif risk == "Medium Risk":
                st.warning("⚠ Medium Risk – be cautious and prefer travelling with company.")
            else:
                st.success("✅ Relatively safer region – still follow standard safety practices.")

# ---------- TAB 2: WHAT-IF SIMULATION ----------

with tab2:
    st.subheader("🧪 What-if Crime Scenario Simulation")
    st.write("Adjust the crime numbers to see how the Safety Score changes.")

    sim_year = st.number_input("Year", min_value=2001, max_value=2025, value=2021, step=1)

    c1, c2, c3 = st.columns(3)
    with c1:
        rape = st.number_input("Rape", min_value=0, value=100)
        ka = st.number_input("Kidnapping & Abduction (K&A)", min_value=0, value=50)
    with c2:
        dd = st.number_input("Dowry Deaths (DD)", min_value=0, value=20)
        aow = st.number_input("Assault on Women (AoW)", min_value=0, value=150)
    with c3:
        aom = st.number_input("Assault on Minors (AoM)", min_value=0, value=30)
        dv = st.number_input("Domestic Violence (DV)", min_value=0, value=80)
        wt = st.number_input("Women Trafficking (WT)", min_value=0, value=10)

    if st.button("Simulate Safety Score", key="simulate"):
        total = rape + ka + dd + aow + aom + dv + wt
        if total == 0:
            st.error("At least one crime count must be > 0.")
        else:
            rape_r = rape / total
            ka_r = ka / total
            dd_r = dd / total
            aow_r = aow / total
            aom_r = aom / total
            dv_r = dv / total
            wt_r = wt / total

            x_sim = pd.DataFrame([{
                "Year": sim_year,
                "Rape": rape,
                "K&A": ka,
                "DD": dd,
                "AoW": aow,
                "AoM": aom,
                "DV": dv,
                "WT": wt,
                "Rape_ratio": rape_r,
                "K&A_ratio": ka_r,
                "DD_ratio": dd_r,
                "AoW_ratio": aow_r,
                "AoM_ratio": aom_r,
                "DV_ratio": dv_r,
                "WT_ratio": wt_r,
            }])

            score = float(model.predict(x_sim)[0])
            risk = risk_from_score(score)

            st.markdown("### 🔍 Simulation Result")
            st.metric("Predicted Safety Score", f"{score:.2f}")
            st.write(f"**Risk Level:** `{risk}`")

# ---------- TAB 3: SOS ASSISTANT ----------

# ---------- TAB 3: SOS ASSISTANT ----------

with tab3:
    st.subheader("🚨 SOS Message Assistant (WhatsApp Enabled)")
    st.write("Send a real-time SOS alert to your verified WhatsApp number.")

    name = st.text_input("Your Name")
    location = st.text_input("Your Current Location")
    user_phone = st.text_input("Your WhatsApp Number (+91xxxxxxxxxx)")

    if st.button("Send WhatsApp SOS 🚨", key="real_sos"):
        if not name or not location or not user_phone:
            st.error("Please fill all fields.")
        else:
            sos_msg = (
                f"🚨 *EMERGENCY ALERT* 🚨\n"
                f"Name: {name}\n"
                f"Location: {location}\n"
                f"I feel unsafe. Please contact me immediately."
            )

            ok = send_whatsapp_sos(sos_msg, user_phone)

            if ok:
                st.success("WhatsApp SOS sent successfully! 🚨 Check your phone.")
            else:
                st.error("Failed to send WhatsApp SOS ❌")

