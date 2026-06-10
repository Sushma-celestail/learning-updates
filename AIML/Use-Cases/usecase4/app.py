"""Streamlit chat UI for the Personal Research Assistant."""

import os
os.environ["USE_TAVILY"] = "false"
import uuid
import streamlit as st
from dotenv import load_dotenv
os.environ["USE_TAVILY"] = "false"

# Load environment variables FIRST
load_dotenv()

from agent.core import run_agent
from agent.callbacks import get_callbacks

    # Initialize iteration counter in session state if not present
if "iteration_counter" not in st.session_state:
    st.session_state.iteration_counter = 0
    st.set_page_config(page_title="Research Assistant", page_icon="🔍")
    st.title("🔍 Personal Research Assistant")
    st.caption("Powered by Groq (Llama 3.3 70B) with ReAct tool-calling")

# --- Session State ---
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Render Chat History ---
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# --- Handle User Input ---
if prompt := st.chat_input("Ask me anything..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        with st.spinner("Researching..."):
            callbacks = get_callbacks(st.session_state.thread_id)
            answer = run_agent(prompt, st.session_state.thread_id, callbacks)
            st.write(answer)
            # Increment iteration counter after each answer is produced
            st.session_state.iteration_counter += 1

        with st.expander("🔁 Iteration Counter"):
            st.write(f"Iterations used: {st.session_state.iteration_counter}")
        st.session_state.messages.append({"role": "assistant", "content": answer})
