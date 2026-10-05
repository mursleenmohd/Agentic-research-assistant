import uuid
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Agentic Research Assistant", layout="wide",)


if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

if "research_plan" not in st.session_state:
    st.session_state.research_plan = []

if "research_topic" not in st.session_state:
    st.session_state.research_topic = ""

if "approval_required" not in st.session_state:
    st.session_state.approval_required = False

if "final_answer" not in st.session_state:
    st.session_state.final_answer = ""

if "status" not in st.session_state:
    st.session_state.status = ""


st.title("Agentic Research Assistant")
st.write("Research using LangGraph, MCP, FastAPI and Human-in-the-Loop.")


with st.sidebar:
    st.header("Agent Architecture")
    st.markdown(
        """
        **Workflow**
        1. Planner
        2. Human Approval
        3. MCP Research
        4. Synthesis
        5. Final Answer
        """
    )

    st.divider()
    st.caption("Smart Search With Workflow")

st.subheader("Research Topic")
topic = st.text_area("Enter your research topic", placeholder="Example: What are AI agents?",height=120,)

if st.button("Start Research",type="primary",use_container_width=True,):
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        thread_id = str(uuid.uuid4())
        st.session_state.thread_id = thread_id
        st.session_state.research_topic = topic
        st.session_state.research_plan = []
        st.session_state.final_answer = ""
        st.session_state.approval_required = False
        st.session_state.status = ""
        try:
            with st.spinner("Creating research plan..."):
                response = requests.post(
                    f"{API_URL}/research/start",
                    json={
                        "message": topic,
                        "thread_id": thread_id,
                    },
                    timeout=120,
                )
            if response.status_code != 200:
                st.error(f"Backend error: {response.text}")
            else:
                data = response.json()
                st.session_state.status = data.get("status","",)
                if data.get("status") == "approval_required":
                    st.session_state.approval_required = True
                    st.session_state.research_plan = (data.get("research_plan",[],))
                    st.rerun()
                else:
                    st.session_state.final_answer = (
                        data.get("response","",))
                    st.rerun()

        except requests.exceptions.RequestException as e:
            st.error(f"Could not connect to FastAPI: {e}")

if st.session_state.approval_required:
    st.divider()
    st.subheader("Human Approval Required")
    st.info("The agent created the following research plan. " "Review it before allowing the research to continue.")
    st.markdown("### Research Plan")
    for index, question in enumerate(st.session_state.research_plan,start=1,):
        st.write(f"**{index}.** {question}")
    st.divider()
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Approve & Continue",type="primary",use_container_width=True,):
            try:
                with st.spinner("Agent is researching..."):
                    response = requests.post(f"{API_URL}/research/resume",
                        json={
                            "thread_id": (
                                st.session_state.thread_id
                            ),
                            "approved": True,
                        },
                        timeout=180,
                    )
                if response.status_code != 200:
                    st.error(f"Backend error: {response.text}")
                else:
                    data = response.json()
                    st.session_state.status = data.get("status","",)
                    st.session_state.final_answer = (
                        data.get("response","",))
                    st.session_state.approval_required = False
                    st.rerun()

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to FastAPI: {e}")

    with col2:
        if st.button("Reject Research",use_container_width=True,):
            try:
                with st.spinner("Stopping research..."):
                    response = requests.post(f"{API_URL}/research/resume",
                        json={
                            "thread_id": (
                                st.session_state.thread_id
                            ),
                            "approved": False,
                        },
                        timeout=60,
                    )

                if response.status_code != 200:
                    st.error(f"Backend error: {response.text}")
                else:
                    data = response.json()
                    st.session_state.status = data.get("status","",)
                    st.session_state.final_answer = (data.get("response","",))
                    st.session_state.approval_required = False
                    st.rerun()
            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to FastAPI: {e}")

if st.session_state.final_answer:
    st.divider()
    st.subheader("Final Research Answer")
    st.markdown(st.session_state.final_answer)

if st.session_state.status:
    st.divider()
    st.caption(f"Agent Status: {st.session_state.status}")