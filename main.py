import os
import anthropic
import streamlit as st

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
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        client = anthropic.Anthropic(api_key=api_key)

        with st.spinner("Agent 1/3: Analysing adherence..."):
            analyst_response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": f"""You are an Adherence Analyst for fitness coaches. Analyse this client check-in brutally and honestly.

Client: {client_name}
Goal: {client_goal}
Last week's target: {last_weeks_target}

Check-in message:
{checkin_text}

Output a scorecard:
- Adherence score: X/10
- What they nailed:
- What they missed:
- Red flags (excuses, avoidance patterns):"""
                }]
            )
            scorecard = analyst_response.content[0].text

        with st.spinner("Agent 2/3: Building coaching strategy..."):
            strategist_response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": f"""You are a Coach Strategist. Based on this adherence scorecard for {client_name}, decide the ONE coaching focus for the reply.

Scorecard:
{scorecard}

Coaching style to match: {coaching_style}

Choose ONE focus from: accountability, encouragement, plan adjustment, mindset shift.
Give your chosen focus and a 1-sentence reason why."""
                }]
            )
            strategy = strategist_response.content[0].text

        with st.spinner("Agent 3/3: Writing your reply..."):
            writer_response = client.messages.create(
                model="claude-opus-4-5",
                max_tokens=300,
                messages=[{
                    "role": "user",
                    "content": f"""You are a Message Writer for fitness coaches. Write a reply from coach to {client_name}.

Coaching strategy: {strategy}
Coaching style: {coaching_style}
Client goal: {client_goal}

Original check-in:
{checkin_text}

Rules:
- Reference specific things they said in the check-in
- Match the coaching style exactly
- End with ONE clear action for next week
- Max 120 words
- No generic phrases like "great job" or "keep it up"

Write only the message, nothing else."""
                }]
            )
            reply = writer_response.content[0].text

        st.success("Analysis complete.")
        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Adherence Scorecard")
            st.markdown(scorecard)
            st.markdown("**Coaching Strategy:**")
            st.markdown(strategy)
        with col2:
            st.subheader("✉️ Ready-to-Send Reply")
            st.markdown(reply)
            st.code(reply, language=None)
