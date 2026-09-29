import asyncio
from concurrent.futures import ThreadPoolExecutor

import streamlit as st

from agent import build_agent, get_final_text


st.set_page_config(
    page_title="AI School Operations Agent",
    page_icon="🎓",
    layout="wide",
)


def _run_in_fresh_loop(coro_factory):
    """
    Streamlit reruns can trigger multiple async agent calls across the app
    lifecycle. Each call must own its own event loop; do not reuse a loop
    that may already be closed by a previous rerun or async client session.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro_factory())

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(asyncio.run, coro_factory())
        return future.result()


def chat_response(messages):
    agent = build_agent()

    async def _invoke_agent():
        response = await agent.ainvoke(
            {"messages": messages},
            config={"recursion_limit": 6},
        )
        final_message = response["messages"][-1]
        return get_final_text(final_message.content)

    return _run_in_fresh_loop(_invoke_agent)


if "messages" not in st.session_state:
    st.session_state.messages = []


st.title("AI School Operations Agent")
st.caption("School operations assistant for attendance and student information.")

with st.sidebar:
    st.markdown("### About")
    st.write(
        "This UI uses the existing LangChain agent and EDAP toolchain without changing the backend logic."
    )
    st.write("No secrets or credentials are hard-coded here.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask about attendance, student details, or school operations...")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = chat_response(st.session_state.messages)
            st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})
    except Exception as exc:
        error_message = f"Sorry, I hit an error: {exc}"
        with st.chat_message("assistant"):
            st.error(error_message)
        st.session_state.messages.append({"role": "assistant", "content": error_message})
