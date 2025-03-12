import streamlit as st
import openai
import time

openai.api_key = st.secrets["OPENAI_API_KEY"]
assistant_id = st.secrets["ASSISTANT_ID"]

st.title("Test My AI Assistant")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None

import requests

def get_stock_price(ticker="ZSPC"):
    api_key = "45ITJ1V0GMTWDJHS"
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={api_key}"
    response = requests.get(url).json()
    try:
        price = response["Global Quote"]["05. price"]
        return f"The current stock price of {ticker} is ${price} USD (last updated {response['Global Quote']['07. latest trading day']})."
    except KeyError:
        return "Unable to fetch stock price at this time."

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
            run_id = response.id
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
            run_id = run.id

        while True:
            run_status = openai.beta.threads.runs.retrieve(thread_id=st.session_state.thread_id, run_id=run_id)
            if run_status.status == "completed":
                break
            elif run_status.status == "requires_action":
                tool_calls = run_status.required_action.submit_tool_outputs.tool_calls
                tool_outputs = []
                for tool_call in tool_calls:
                    if tool_call.function.name == "get_stock_price":
                        args = eval(tool_call.function.arguments) if tool_call.function.arguments else {}
                        ticker = args.get("ticker", "ZSPC")
                        result = get_stock_price(ticker)
                        tool_outputs.append({"tool_call_id": tool_call.id, "output": result})
                openai.beta.threads.runs.submit_tool_outputs(
                    thread_id=st.session_state.thread_id,
                    run_id=run_id,
                    tool_outputs=tool_outputs
                )
            time.sleep(1)
        return st.session_state.thread_id
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None

user_input = st.text_input("Type your message here:")
if st.button("Send"):
    if user_input:
        with st.spinner("Thinking..."):
            thread_id = call_assistant(user_input)
            if thread_id:
                messages = openai.beta.threads.messages.list(thread_id=thread_id)
                for msg in reversed(messages.data):
                    st.write(f"**{msg.role.capitalize()}:** {msg.content[0].text.value}")