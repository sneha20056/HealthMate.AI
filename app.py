
import streamlit as st
from crewai import LLM, Agent, Crew, Task
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

import random

# 🔑 Secret Key
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")

# 🎨 Page Styling
st.set_page_config(page_title="HealthMate.AI", page_icon="🩺", layout="wide")

st.markdown("""
<style>
body {
    font-family: 'Segoe UI', sans-serif;
}
.main {
    background-color: #f0f8ff;
}
.box {
    background-color: #ffffff;
    color: #000000;
    padding: 20px;
    border-radius: 12px;
    margin: 10px 0;
    border: 1px solid #ddd;
    font-size: 16px;
    box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
}
.title {
    font-size: 32px;
    color: #0a9396;
    font-weight: bold;
    text-shadow: 1px 1px #ccc;
}
.tip {
    background-color: #e0fbfc;
    color: #000000; /* Make text black */
    font-size: 16px;
    font-weight: 500;
    padding: 10px 15px;
    border-radius: 8px;
    margin-top: 20px;
    box-shadow: 1px 1px 5px rgba(0,0,0,0.1);
}

</style>
""", unsafe_allow_html=True)

# 🧠 Header
col1, col2 = st.columns([1, 5])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/387/387561.png", width=70)
with col2:
    st.markdown('<div class="title">HealthMate.AI</div>', unsafe_allow_html=True)
    st.caption("Your friendly AI-powered health advisor 🩺")

# 🔷 Sidebar
st.sidebar.title("HealthMate.AI")
user_input = st.sidebar.text_input("Enter your symptoms", placeholder="e.g. high fever and body ache")

agent_choice = st.sidebar.radio(
    "Select Agent",
    [
        "AI Health Advisor",
        "Home Remedy Expert",
        "Nutrition Advisor",
        "OTC Medication Guide",
        "Health Tips Coach",
        "Symptom Explainer"
    ]
)

run_button = st.sidebar.button("Get Health Advice")

# 🧠 LLM setup
llm = LLM(model="groq/llama-3.3-70b-versatile", temperature=0.2)

# 👨‍⚕ Agents
agents = {
    "AI Health Advisor": Agent(
        role="AI Health Advisor",
        goal="Give initial health advice based on symptoms in simple language.",
        backstory="You are an experienced AI that offers first-level health advice for common symptoms.",
        allow_delegation=False,
        llm=llm
    ),
    "Home Remedy Expert": Agent(
        role="Home Remedy Expert",
        goal="Recommend safe, effective home remedies for the given symptoms.",
        backstory="You're an AI assistant that gives traditional and science-backed home remedies for minor symptoms.",
        allow_delegation=False,
        llm=llm
    ),
    "Nutrition Advisor": Agent(
        role="Nutrition Advisor",
        goal="Suggest a short diet plan that helps with recovery from symptoms.",
        backstory="You're a diet-savvy assistant that suggests meals based on illness, like what to eat during fever or food poisoning.",
        allow_delegation=False,
        llm=llm
    ),
    "OTC Medication Guide": Agent(
        role="OTC Medication Guide",
        goal="Suggest safe, commonly used OTC medications for the given symptoms with dosages if possible.",
        backstory="You're a pharmacy-trained AI who only shares publicly known and safe medicine info.",
        allow_delegation=False,
        llm=llm
    ),
    "Health Tips Coach": Agent(
        role="Health Tips Coach",
        goal="Give 2-3 helpful tips for faster recovery based on the symptoms.",
        backstory="You're a health coach that encourages natural recovery through lifestyle changes.",
        allow_delegation=False,
        llm=llm
    ),
    "Symptom Explainer": Agent(
        role="Symptom Explainer",
        goal="Explain possible medical causes behind symptoms in simple terms.",
        backstory="You're a medically-informed AI that educates users about what could be causing their symptoms.",
        allow_delegation=False,
        llm=llm
    )
}

# 🚀 Run
if run_button and user_input.strip() != "":
    with st.spinner("🧠 Thinking... Generating your health report..."):
        task = Task(
            description=f"The user has the following symptoms: {user_input}. Provide advice.",
            expected_output="Relevant advice",
            agent=agents[agent_choice]
        )
        crew = Crew(agents=[agents[agent_choice]], tasks=[task], verbose=False)
        result = crew.kickoff(inputs={"symptoms": user_input})

    # 💡 Displaying Results
    st.markdown(f"## 🩺 {agent_choice}")
    st.markdown(f'<div class="box">{result}</div>', unsafe_allow_html=True)

    # 💬 Daily Tip
    tips = [
        "💧 Stay hydrated! Aim for at least 8 glasses of water a day.",
        "😴 Rest is medicine. Don’t skip sleep while you're sick.",
        "🥦 Eat light, nourishing food like khichdi or soup.",
        "🧘‍♂ Breathe deeply – relaxation helps healing too."
    ]
    st.markdown(f'<div class="tip">💡 **Tip of the Day:** {random.choice(tips)}</div>', unsafe_allow_html=True)

elif not run_button:
    st.info("👈 Enter your symptoms, select an agent, and click 'Get Health Advice' in the sidebar.")
