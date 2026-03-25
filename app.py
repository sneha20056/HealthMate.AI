
import streamlit as st
from crewai import LLM, Agent, Crew, Task
import os, json, hashlib, random
from dotenv import load_dotenv
from datetime import datetime


load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

import random

# 🔑 Secret Key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# 🎨 Page Styling
st.set_page_config(page_title="HealthMate.AI", page_icon="🩺", layout="wide")

st.markdown("""
<style>
body { font-family: 'Segoe UI', sans-serif; }
.main { background-color: #f0f8ff; }
.box {
    background-color: #ffffff; color: #000000;
    padding: 20px; border-radius: 12px; margin: 10px 0;
    border: 1px solid #ddd; font-size: 16px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.title { font-size: 32px; color: #0a9396; font-weight: bold; text-shadow: 1px 1px #ccc; }
.tip {
    background-color: #e0fbfc; color: #000000;
    font-size: 16px; font-weight: 500; padding: 10px 15px;
    border-radius: 8px; margin-top: 20px;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
}
</style>
""", unsafe_allow_html=True)

# ─── Helper Functions ───────────────────────────────────────────
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def signup(username, password):
    users = load_users()
    if username in users:
        return False, "❌ Username already exists!"
    users[username] = {"password": hash_password(password), "history": []}
    save_users(users)
    return True, "✅ Account created! Please log in."

def login(username, password):
    users = load_users()
    if username not in users:
        return False, "❌ Username not found!"
    if users[username]["password"] != hash_password(password):
        return False, "❌ Wrong password!"
    return True, "✅ Logged in!"

def save_history(username, symptoms, agent_name, result):
    users = load_users()
    if username not in users:
        return
    users[username]["history"].append({
        "date": datetime.now().strftime("%d %b %Y, %I:%M %p"),
        "symptoms": symptoms,
        "agent": agent_name,
        "result": str(result)
    })
    save_users(users)

def get_history(username):
    users = load_users()
    return users.get(username, {}).get("history", [])

# ─── Session State ──────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# ─── Login / Signup Page ────────────────────────────────────────
if not st.session_state.logged_in:
    col1, col2 = st.columns([1, 5])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=70)
    with col2:
        st.markdown('<div class="title">HealthMate.AI</div>', unsafe_allow_html=True)
        st.caption("Your friendly AI-powered health advisor 🩺")

    st.markdown("---")
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])

    with tab1:
        st.subheader("Welcome back!")
        login_user = st.text_input("Username", key="login_user")
        login_pass = st.text_input("Password", type="password", key="login_pass")
        if st.button("Login", use_container_width=True):
            success, msg = login(login_user, login_pass)
            if success:
                st.session_state.logged_in = True
                st.session_state.username = login_user
                st.rerun()
            else:
                st.error(msg)

    with tab2:
        st.subheader("Create an account")
        new_user = st.text_input("Choose Username", key="new_user")
        new_pass = st.text_input("Choose Password", type="password", key="new_pass")
        if st.button("Sign Up", use_container_width=True):
            success, msg = signup(new_user, new_pass)
            if success:
                st.success(msg)
            else:
                st.error(msg)

# ─── Main App ───────────────────────────────────────────────────
else:
    col1, col2, col3 = st.columns([1, 5, 1])
    with col1:
        st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=70)
    with col2:
        st.markdown('<div class="title">HealthMate.AI</div>', unsafe_allow_html=True)
        st.caption(f"Welcome, **{st.session_state.username}** 👋")
    with col3:
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()

    st.sidebar.title("HealthMate.AI")
    page = st.sidebar.radio("Navigate", ["🩺 Get Advice", "📋 My History"])

    # ── Get Advice Page ─────────────────────────────────────────
    if page == "🩺 Get Advice":
        user_input = st.sidebar.text_input("Enter your symptoms",
                                           placeholder="e.g. high fever and body ache")
        agent_choice = st.sidebar.radio("Select Agent", [
            "AI Health Advisor", "Home Remedy Expert",
            "Nutrition Advisor", "OTC Medication Guide",
            "Health Tips Coach", "Symptom Explainer"
        ])
        run_button = st.sidebar.button("Get Health Advice")

        llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.2)

        agents = {
            "AI Health Advisor": Agent(
                role="AI Health Advisor",
                goal="Give initial health advice based on symptoms in simple language.",
                backstory="You are an experienced AI that offers first-level health advice for common symptoms.",
                allow_delegation=False, llm=llm
            ),
            "Home Remedy Expert": Agent(
                role="Home Remedy Expert",
                goal="Recommend safe, effective home remedies for the given symptoms.",
                backstory="You're an AI assistant that gives traditional and science-backed home remedies.",
                allow_delegation=False, llm=llm
            ),
            "Nutrition Advisor": Agent(
                role="Nutrition Advisor",
                goal="Suggest a short diet plan that helps with recovery from symptoms.",
                backstory="You're a diet-savvy assistant that suggests meals based on illness.",
                allow_delegation=False, llm=llm
            ),
            "OTC Medication Guide": Agent(
                role="OTC Medication Guide",
                goal="Suggest safe, commonly used OTC medications for the given symptoms.",
                backstory="You're a pharmacy-trained AI who shares publicly known and safe medicine info.",
                allow_delegation=False, llm=llm
            ),
            "Health Tips Coach": Agent(
                role="Health Tips Coach",
                goal="Give 2-3 helpful tips for faster recovery based on the symptoms.",
                backstory="You're a health coach encouraging natural recovery through lifestyle changes.",
                allow_delegation=False, llm=llm
            ),
            "Symptom Explainer": Agent(
                role="Symptom Explainer",
                goal="Explain possible medical causes behind symptoms in simple terms.",
                backstory="You're a medically-informed AI that educates users about their symptoms.",
                allow_delegation=False, llm=llm
            )
        }

        if run_button and user_input.strip():
            with st.spinner("🧠 Generating your health report..."):
                task = Task(
                    description=f"The user has the following symptoms: {user_input}. Provide advice.",
                    expected_output="Relevant advice",
                    agent=agents[agent_choice]
                )
                crew = Crew(agents=[agents[agent_choice]], tasks=[task], verbose=False)
                result = crew.kickoff(inputs={"symptoms": user_input})

            save_history(st.session_state.username, user_input, agent_choice, result)

            st.markdown(f"## 🩺 {agent_choice}")
            st.markdown(f'<div class="box">{result}</div>', unsafe_allow_html=True)

            tips = [
                "💧 Stay hydrated! Aim for at least 8 glasses of water a day.",
                "😴 Rest is medicine. Don't skip sleep while you're sick.",
                "🥦 Eat light, nourishing food like khichdi or soup.",
                "🧘 Breathe deeply – relaxation helps healing too."
            ]
            st.markdown(f'<div class="tip">💡 Tip of the Day: {random.choice(tips)}</div>',
                        unsafe_allow_html=True)

        elif not run_button:
            st.info("👈 Enter your symptoms, select an agent, and click 'Get Health Advice'.")

    # ── My History Page ─────────────────────────────────────────
    elif page == "📋 My History":
        st.markdown("## 📋 Your Health History")
        history = get_history(st.session_state.username)

        if not history:
            st.info("No history yet! Ask your first health question to get started.")
        else:
            for item in reversed(history):
                with st.container():
                    st.markdown(f"📅 **{item['date']}**")
                    st.markdown(f"🤒 **Symptoms:** {item['symptoms']}")
                    st.markdown(f"🤖 **Agent:** {item['agent']}")
                    with st.expander("View Advice"):
                        st.write(item['result'])
                    st.divider()

            if st.button("🗑️ Clear My History"):
                users = load_users()
                users[st.session_state.username]["history"] = []
                save_users(users)
                st.success("History cleared!")
                st.rerun()