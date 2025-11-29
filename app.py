import streamlit as st
import pandas as pd
import joblib
from twilio.rest import Client
import urllib.parse


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

if "contacts" not in st.session_state:
    st.session_state["contacts"] = []   # list of {"name":..., "number":...}


def get_contacts():
    """Load contacts from session."""
    return st.session_state["contacts"]


def add_contact(name, number):
    """Add new contact to session."""
    contacts = st.session_state["contacts"]
    contacts.append({"name": name, "number": number})
    st.session_state["contacts"] = contacts


# ---------------------------------------------
# TAB 3 - SOS Assistant (Multi Contact)
# ---------------------------------------------
with tab3:

    st.header("🚨 SOS Message Assistant (Multi-Contact + Location Enabled)")

    st.write(
        "Send your real-time SOS alert to **multiple trusted contacts** "
        "with your details + Google Maps location link on WhatsApp."
    )

    # ---------------------------
    # 1️⃣ USER DETAILS
    # ---------------------------
    st.subheader("1️⃣ Your Details")

    col1, col2 = st.columns(2)
    with col1:
        user_name = st.text_input("Your Name")
        user_area = st.text_input("Your Area / City")
    with col2:
        maps_link = st.text_input(
            "Google Maps Location Link (Optional)",
            placeholder="Paste Maps → Share → Copy link"
        )

    st.markdown("---")

    # ---------------------------
    # 2️⃣ TRUSTED CONTACTS
    # ---------------------------
    st.subheader("2️⃣ Trusted Contacts")

    contacts = get_contacts()

    if len(contacts) == 0:
        st.warning("⚠ No contacts saved yet.")
        selected = []
    else:
        contact_list = [
            f"{c['name']} ({c['number']})" for c in contacts
        ]
        selected = st.multiselect(
            "Select contacts to send alert:",
            contact_list
        )

    # ---------------------------
    # ➕ ADD NEW CONTACT
    # ---------------------------
    st.markdown("### ➕ Add New Contact")

    col_a, col_b, col_c = st.columns([3, 3, 2])
    with col_a:
        new_name = st.text_input("Name", key="new_contact_name")
    with col_b:
        new_number = st.text_input(
            "WhatsApp Number (10 digits)",
            key="new_contact_num",
            placeholder="Eg: 8220827025"
        )
    with col_c:
        if st.button("Add"):
            if not new_name or not new_number:
                st.error("Enter both name and number.")
            elif not new_number.isdigit() or len(new_number) != 10:
                st.error("Number must be 10 digits (only numbers).")
            else:
                add_contact(new_name, new_number)
                st.success(f"Added {new_name}!")
                st.rerun()

    st.markdown("---")

    # ---------------------------
    # 3️⃣ GENERATE SOS MESSAGE
    # ---------------------------
    st.subheader("3️⃣ Generate SOS Message")

    if st.button("Generate SOS 🚨"):

        if not user_name or not user_area:
            st.error("Fill your name & area.")
        elif len(selected) == 0:
            st.error("Select at least one contact.")
        else:
            sos_text = (
                f"🚨 EMERGENCY ALERT 🚨\n"
                f"I, {user_name}, am feeling unsafe at {user_area}.\n"
                f"Please contact me immediately."
            )

            if maps_link.strip():
                sos_text += f"\n\n📍 Location: {maps_link.strip()}"

            st.success("✔ SOS Message Generated:")
            st.code(sos_text, language="text")

            st.markdown("### 📤 Send to Contacts")

            encoded = urllib.parse.quote(sos_text)

            for entry in selected:
                name, number = entry.split("(")
                number = number.replace(")", "").strip()

                wa_url = f"https://wa.me/91{number}?text={encoded}"
                st.link_button(f"Send to {name.strip()} 📲", wa_url)
