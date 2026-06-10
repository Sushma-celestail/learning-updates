import streamlit as st
from graph.builder import run_graph, initial_state

# Page Config
st.set_page_config(
    page_title="Customer Support Chatbot",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 Customer Support Chatbot")

# Initialize state
if "state" not in st.session_state:
    st.session_state.state = initial_state()
    st.session_state.state["customer_context"] = {
        "user_id": "usr_a4f2c"
    }

# Display chat history
for msg in st.session_state.state.get("messages", []):

    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])

    else:
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Chat input
if prompt := st.chat_input("Type your message..."):

    # Add user message
    st.session_state.state.setdefault("messages", []).append(
        {
            "role": "user",
            "content": prompt
        }
    )

    # Run graph
    st.session_state.state = run_graph(
        st.session_state.state
    )

    st.rerun()