import streamlit as st
import pandas as pd
import sqlite3
import os
import folium
from streamlit_folium import st_folium
import google.generativeai as genai

# ======================
# PAGE CONFIG
# ======================

st.set_page_config(
    page_title="GeoShield AI Pink Edition",
    page_icon="💖",
    layout="wide"
)

# ======================
# 💖 PINK FUTURISTIC UI
# ======================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #1a001a, #2b002b, #3d003d);
    color: white;
}

.block-container {
    padding-top: 2rem;
}

/* Titles */
h1, h2, h3 {
    color: #ff4fd8;
    text-shadow: 0px 0px 10px #ff4fd8;
}

/* Metrics */
[data-testid="metric-container"] {
    background: rgba(255, 0, 150, 0.15);
    border: 1px solid #ff4fd8;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0px 0px 15px #ff4fd8;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #1a001a;
    border-right: 2px solid #ff4fd8;
}

/* Buttons */
.stButton button {
    background: linear-gradient(90deg, #ff4fd8, #ff007f);
    color: white;
    border-radius: 10px;
    border: none;
    padding: 8px 16px;
    box-shadow: 0px 0px 10px #ff4fd8;
}

.stButton button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px #ff4fd8;
}

/* Progress */
.stProgress > div > div > div > div {
    background-color: #ff4fd8;
}

</style>
""", unsafe_allow_html=True)

# ======================
# GEMINI API
# ======================

GEMINI_API_KEY = "API_KEY"

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ======================
# SQLITE SAFE
# ======================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "reports.db")

conn = sqlite3.connect(DB_PATH, check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS reports(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    location TEXT,
    category TEXT,
    description TEXT,
    severity TEXT
)
""")

conn.commit()

def add_report(loc, cat, desc, sev):
    cur.execute(
        "INSERT INTO reports(location,category,description,severity) VALUES (?,?,?,?)",
        (loc, cat, desc, sev)
    )
    conn.commit()

def get_reports():
    cur.execute("SELECT * FROM reports")
    return cur.fetchall()

# ======================
# STABLE DATASET
# ======================

@st.cache_data
def load_data():

    data = []

    for i in range(100):

        data.append({
            "District": f"District_{i+1}",
            "Lat": 11.0 + (i * 0.01),
            "Lon": 78.0 + (i * 0.01),
            "Fraud": (i * 3) % 150,
            "Cyber": (i * 2) % 60,
            "Counterfeit": (i * 1) % 25
        })

    df = pd.DataFrame(data)
    df["Total"] = df["Fraud"] + df["Cyber"] + df["Counterfeit"]

    return df

crime_data = load_data()

# ======================
# RISK ENGINE
# ======================

def risk_level(v):
    if v > 200:
        return "🔴 HIGH"
    elif v > 120:
        return "🟠 MEDIUM"
    return "🟢 LOW"

crime_data["Risk"] = crime_data["Total"].apply(risk_level)

# ======================
# MENU
# ======================

menu = st.sidebar.selectbox(
    "💖 GeoShield AI",
    ["Dashboard", "Report Incident", "AI Detector", "Crime Map"]
)

# ======================
# DASHBOARD
# ======================

if menu == "Dashboard":

    st.title("💖 GeoShield AI - Pink Command Center")

    col1, col2, col3 = st.columns(3)

    col1.metric("Fraud", int(crime_data["Fraud"].sum()))
    col2.metric("Cyber", int(crime_data["Cyber"].sum()))
    col3.metric("Counterfeit", int(crime_data["Counterfeit"].sum()))

    high_risk = len(crime_data[crime_data["Risk"] == "🔴 HIGH"])

    score = 100 - (high_risk * 2)
    score = max(score, 0)

    st.subheader("🧠 Safety Index")
    st.progress(score)
    st.success(f"Safety Score: {score}/100")

# ======================
# REPORT INCIDENT
# ======================

elif menu == "Report Incident":

    st.title("🚨 Citizen Crime Reporting")

    loc = st.text_input("Location")

    cat = st.selectbox(
        "Category",
        ["Fraud", "Cyber Crime", "Digital Arrest Scam", "Counterfeit"]
    )

    sev = st.selectbox("Severity", ["Low", "Medium", "High"])

    desc = st.text_area("Description")

    if st.button("Submit Report"):

        add_report(loc, cat, desc, sev)
        st.success("💖 Report Sent Successfully")

# ======================
# AI DETECTOR
# ======================

elif menu == "AI Detector":

    st.title("🤖 AI Scam Detection Engine")

    msg = st.text_area("Paste suspicious message")

    if st.button("Analyze"):

        prompt = f"""
        Detect scam risk:
        - Risk Level
        - Explanation
        - Action

        Message:
        {msg}
        """

        res = model.generate_content(prompt)
        st.write(res.text)

# ======================
# 🗺️ CRIME MAP
# ======================

elif menu == "Crime Map":

    st.title("🗺️ Pink Geospatial Intelligence Map")

    st.caption("💖 Stable AI-powered crime hotspot visualization")

    m = folium.Map(
        location=[11.0, 78.5],
        zoom_start=7,
        tiles="CartoDB dark_matter"
    )

    for _, row in crime_data.iterrows():

        if row["Risk"] == "🔴 HIGH":
            color = "red"
        elif row["Risk"] == "🟠 MEDIUM":
            color = "orange"
        else:
            color = "green"

        folium.CircleMarker(
            location=[row["Lat"], row["Lon"]],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['District']} | {row['Risk']}"
        ).add_to(m)

    st_folium(m, width=1000, height=600)