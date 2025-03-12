import streamlit as st
import openai

# Load API key from secrets (no hardcoding)
openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]  # Optional: Store Assistant ID too

st.title("Test My AI Assistant")

# Chat interface
user_input = st.text_input("Type your message here:")
if st.button("Send"):
    if user_input:
        with st.spinner("Thinking..."):
            # Call OpenAI Assistants API
            response = openai.beta.threads.create_and_run(
                assistant_id=assistant_id,
                thread={"messages": [{"role": "user", "content": user_input}]}
            )
            # Poll for completion (simplified for brevity)
            run_id = response["id"]
            thread_id = response["thread_id"]
            while True:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                if run_status["status"] == "completed":
                    break
            messages = openai.beta.threads.messages.list(thread_id=thread_id)
            assistant_response = messages["data"][0]["content"][0]["text"]["value"]
            st.write(f"**Assistant:** {assistant_response}")
    else:
        st.write("Please enter a message.")