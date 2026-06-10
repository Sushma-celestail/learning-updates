import streamlit as st

def render_interrupt(interrupt):
    st.warning("human approval required")
    st.json(interrupt)

    decision=st.selectBox(
        "Decision",
        options=["approve","edit","reject"]
    )

    edited_args=None
    if decision=="edit":
        edited_args=st.text_area("Modified tool arguments (JSON format)")

    reviewer=st.text_input("Reviewer ")
    
    return {
            "reviewer": reviewer,
            "decision": decision,
            "edited_args": edited_args
        }