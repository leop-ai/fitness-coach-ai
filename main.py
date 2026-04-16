import os
import streamlit as st
from crewai import Agent, Task, Crew, LLM

st.set_page_config(page_title="Check-In Analyser", page_icon="💪", layout="wide")

with st.sidebar:
    st.title("Coach Settings")

    style_options = ["Direct and no-nonsense", "Motivational and energetic", "Empathetic and supportive", "Other (type below)"]
    coaching_style_select = st.selectbox("Your coaching style:", style_options)
    if coaching_style_select == "Other (type below)":
        coaching_style = st.text_input("Describe your style:", placeholder="e.g. Tough love but always positive")
    else:
        coaching_style = coaching_style_select

    goal_options = ["Fat loss", "Muscle gain", "Performance / strength", "General fitness", "Other (type below)"]
    client_goal_select = st.selectbox("Client goal:", goal_options)
    if client_goal_select == "Other (type below)":
        client_goal = st.text_input("Describe the goal:", placeholder="e.g. Marathon training, mobility improvement")
    else:
        client_goal = client_goal_select

    client_name = st.text_input("Client name:", placeholder="e.g. Sarah")
    last_weeks_target = st.text_area("What was their target last week?", placeholder="e.g. 5 workouts, stay under 2000 calories, no alcohol", height=100)

st.title("💪 Client Check-In Analyser")
st.caption("Paste a client check-in. Get an adherence score, strategy, and a ready-to-send reply.")

checkin_text = st.text_area("Paste the client check-in message:", placeholder="e.g. Hey coach, had a decent week. Hit 3 of 5 workouts, nutrition was ok but had a bad weekend...", height=200)
run_button = st.button("Analyse Check-In", type="primary", use_container_width=True)

if run_button:
    if not client_name or not checkin_text or not coaching_style or not client_goal:
        st.warning("Fill in all fields in the sidebar before running.")
    else:
        with st.spinner("3 agents analysing... 30-60 seconds..."):
            api_key = st.secrets["ANTHROPIC_API_KEY"]
            claude = LLM(model="claude-opus-4-5", api_key=api_key)
            analyst = Agent(role="Adherence Analyst", goal="Score client adherence with brutal honesty", backstory=f"You analyse fitness client check-ins. You compare what they did vs what they were supposed to do. You spot excuses disguised as reasons. You output a structured scorecard. The client goal is {client_goal}.", llm=claude, verbose=False)
            strategist = Agent(role="Coach Strategist", goal="Decide the single most important coaching focus for this reply", backstory=f"You understand behaviour change. You decide whether this client needs accountability, encouragement, a plan tweak, or a mindset shift. Coaching style to match: {coaching_style}.", llm=claude, verbose=False)
            writer = Agent(role="Message Writer", goal="Write a personalised coach reply the coach can send immediately", backstory=f"You write coach replies that feel personal and human. You always reference specific things the client said, never generic praise. Style: {coaching_style}. Always end with ONE clear action for next week. Max 120 words.", llm=claude, verbose=False)
            analyse = Task(description=f"Client: {client_name}. Goal: {client_goal}. Last week target: {last_weeks_target}.\n\nCheck-in:\n{checkin_text}\n\nOutput a scorecard:\n- Adherence score: X/10\n- What they nailed:\n- What they missed:\n- Red flags (excuses, avoidance patterns):", expected_output="A structured scorecard with score, positives, gaps, and red flags.", agent=analyst)
            strategise = Task(description=f"Based on {client_name}'s scorecard, decide the ONE focus for the reply. Choose from: accountability, encouragement, plan adjustment, mindset shift. Give a 1-sentence reason.", expected_output="Coaching focus + 1-sentence reason.", agent=strategist)
            write = Task(description=f"Write a reply from coach to {client_name}. Reference specific things they said. Match this style: {coaching_style}. End with one clear action for next week. Max 120 words. No generic phrases like great job or keep it up.", expected_output="A ready-to-send coach reply under 120 words.", agent=writer)
            crew = Crew(agents=[analyst, strategist, writer], tasks=[analyse, strategise, write], verbose=False)
            result = crew.kickoff()

        st.success("Analysis complete.")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Adherence Scorecard")
            st.markdown(str(result)[:len(str(result))//2])
        with col2:
            st.subheader("✉️ Ready-to-Send Reply")
            reply = str(result)[len(str(result))//2:]
            st.markdown(reply)
            st.code(reply, language=None)
