import streamlit as st
from src.agents.personal_assistant import PersonalAssistant

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Personal AI Assistant",
    page_icon="🤖",
    layout="wide"
)

# ---------------------------
# Load Agent
# ---------------------------
@st.cache_resource
def load_agent():
    return PersonalAssistant()

agent = load_agent()
USER_ID = "sushma"

# ---------------------------
# Session State
# ---------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Header
# ---------------------------
st.title("🤖 Personal AI Assistant")
st.caption("Mem0 + Classification Memory System")

# ---------------------------
# Chat History
# ---------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------
# Input
# ---------------------------
prompt = st.chat_input("Type something...")

if prompt:

    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = agent.chat(USER_ID, prompt)
            st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})

# ---------------------------
# Sidebar Memory UI
# ---------------------------
with st.sidebar:

    st.header("🧠 Memory Panel")

    if st.button("📚 Load Memories"):

        memories = agent.show_memories(USER_ID)

        memories_list = memories.get("results", memories) if isinstance(memories, dict) else memories

        semantic, preference, episodic = [], [], []

        for m in memories_list:

            metadata = m.get("metadata") or {}
            mtype = metadata.get("type", "unknown")

            if mtype == "semantic":
                semantic.append(m)
            elif mtype == "preference":
                preference.append(m)
            elif mtype == "episodic":
                episodic.append(m)

        st.metric("Total Memories", len(memories_list))
        st.metric("Semantic", len(semantic))
        st.metric("Preference", len(preference))
        st.metric("Episodic", len(episodic))

        st.divider()

        st.markdown("### 🧩 Semantic")
        for m in semantic:
            st.write("•", m.get("memory"))

        st.markdown("### ❤️ Preference")
        for m in preference:
            st.write("•", m.get("memory"))

        st.markdown("### 📖 Episodic")
        for m in episodic:
            st.write("•", m.get("memory"))

    if st.button("🔍 Raw Memory Dump"):
        st.json(agent.show_memories(USER_ID))

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()