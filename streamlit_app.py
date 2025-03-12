import streamlit as st
import openai
import time

openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

st.title("Test My AI Assistant")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

def display_chat_history(messages):
    for msg in reversed(messages.data):
        role = msg.role.capitalize()
        content = msg.content[0].text.value
        st.write(f"**{role}:** {content}")

def call_assistant(user_input):
    try:
        if st.session_state.thread_id is None:
            response = openai.beta.threads.create_and_run(
                assistant_id=assistant_id,
                thread={"messages": [{"role": "user", "content": user_input}]},
                temperature=0.7,
                top_p=1.0
            )
            st.session_state.thread_id = response.thread_id
            return response.id, response.thread_id
        else:
            openai.beta.threads.messages.create(
                thread_id=st.session_state.thread_id,
                role="user",
                content=user_input
            )
            run = openai.beta.threads.runs.create(
                thread_id=st.session_state.thread_id,
                assistant_id=assistant_id,
                temperature=0.7,
                top_p=1.0
            )
            return run.id, st.session_state.thread_id
    except openai.OpenAIError as e:
        st.error(f"API Error: {str(e)}")
        return None, None

user_input = st.text_input("Type your message here:")
if st.button("Send"):
    if user_input:
        with st.spinner("Thinking..."):
            run_id, thread_id = call_assistant(user_input)
            if run_id and thread_id:
                while True:
                    run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                    if run_status.status == "completed":
                        break
                    time.sleep(1)
                messages = openai.beta.threads.messages.list(thread_id=thread_id)
                display_chat_history(messages)
if st.button("Clear Chat"):
    st.session_state.thread_id = None
    st.write("Chat cleared!")