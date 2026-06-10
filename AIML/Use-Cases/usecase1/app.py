from __future__ import annotations

import streamlit as st

from rag import answer_question, collection_count

st.set_page_config(page_title="Docs Buddy", layout="centered")
st.title("Docs Buddy")
st.caption("FastAPI documentation assistant")

try:
    count = collection_count()
except Exception as exc:
    count = 0
    st.warning(f"Vector store is not ready: {exc}")

if count == 0:
    st.info("Run `python ingest.py` before asking questions.")
else:
    st.caption(f"Indexed chunks: {count}")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

question = st.chat_input("Ask one FastAPI docs question")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching the documentation"):
            response = answer_question(question)
        st.markdown(response.answer)
        st.caption(f"Latency: {response.latency_seconds:.2f}s")

    st.session_state.messages.append({"role": "assistant", "content": response.answer})
