

import os
from crewai import LLM, Agent, Crew, Task

os.environ["GROQ_API_KEY"] = "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"

llm = LLM(
    model="groq/llama-3.3-70b-versatile",
    temperature=0.2
)

# 1️⃣ Health Advisor
health_advisor = Agent(
    role="AI Health Advisor",
    goal="Give initial health advice based on symptoms  in simple language.",
    backstory="You are an experienced AI that offers first-level health advice for common symptoms.",
    allow_delegation=False,
    llm=llm
)

# 2️⃣ Home Remedy Expert
home_remedy_agent = Agent(
    role="Home Remedy Expert",
    goal="Recommend safe, effective home remedies for the given symptoms.",
    backstory="You're an AI assistant that gives traditional and science-backed home remedies for minor symptoms.",
    allow_delegation=False,
    llm=llm
)

# 3️⃣ Nutrition Advisor
nutrition_advisor = Agent(
    role="Nutrition Advisor",
    goal="Suggest a short diet plan that helps with recovery from symptoms.",
    backstory="You're a diet-savvy assistant that suggests meals based on illness, like what to eat during fever or food poisoning.",
    allow_delegation=False,
    llm=llm
)

# 4️⃣ OTC Medication Guide
otc_advisor = Agent(
    role="OTC Medication Guide",
    goal="Suggest safe, commonly used OTC medications for the given symptoms with dosages if possible.",
    backstory="You're a pharmacy-trained AI who only shares publicly known and safe medicine info like paracetamol, antacids, etc.",
    allow_delegation=False,
    llm=llm
)

# 5️⃣ Health Tips Coach
health_tips_agent = Agent(
    role="Health Tips Coach",
    goal="Give 2-3 helpful tips for faster recovery based on the symptoms.",
    backstory="You're a health coach that encourages natural recovery through lifestyle changes like rest, hydration, and breathing exercises.",
    allow_delegation=False,
    llm=llm
)

# 6️⃣ Symptom Explainer
symptom_explainer = Agent(
    role="Symptom Explainer",
    goal="Explain possible medical causes behind symptoms in simple terms.",
    backstory="You're a medically-informed AI that educates users about what could be causing their symptoms.",
    allow_delegation=False,
    llm=llm
)

# Tasks for Each Agent
task1 = Task(
    description="The user has the following symptoms: {symptoms}. Give initial advice on what it could be and what to do.",
    expected_output="Short medical advice about causes and next steps.",
    agent=health_advisor
)

task2 = Task(
    description="Suggest natural, safe home remedies for these symptoms: {symptoms}.",
    expected_output="2-3 home remedies with short how-to info.",
    agent=home_remedy_agent
)

task3 = Task(
    description="Based on {symptoms}, suggest diet and foods to eat or avoid.",
    expected_output="Small recovery diet plan with 2-3 food suggestions.",
    agent=nutrition_advisor
)

task4 = Task(
    description="Suggest safe, common OTC medications for {symptoms}. Include simple dosage info if possible.",
    expected_output="List of 1-2 OTC meds like paracetamol, with basic instructions.",
    agent=otc_advisor
)

task5 = Task(
    description="Give lifestyle recovery tips based on {symptoms}.",
    expected_output="2-3 tips like sleep, hydration, or rest ideas.",
    agent=health_tips_agent
)

task6 = Task(
    description="Explain what might be the medical reasons for {symptoms}. Use clear, easy language.",
    expected_output="1 short paragraph about the possible causes.",
    agent=symptom_explainer
)

# Assemble the Crew
crew = Crew(
    agents=[health_advisor, home_remedy_agent, nutrition_advisor, otc_advisor, health_tips_agent, symptom_explainer],
    tasks=[task1, task2, task3, task4, task5, task6],
    verbose=True
)

# Run it
result = crew.kickoff(
    inputs={
        "symptoms": "high fever and body ache"
    }
)

print("\n🩺 Final Output from HealthMate.AI 🩺\n")
print(result)
