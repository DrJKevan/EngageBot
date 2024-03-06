import ollama
import streamlit as st

# Streamlit Code
st.set_page_config(page_title="Sigma - Learning Mentor", page_icon=":robot:")

# Use consistent styling and layout
background_color = "#f4f4f6"
font_color = "#333"

st.markdown(
    f"""
    <style>
        body {{
            background-color: {background_color};
            color: {font_color};
        }}
    @keyframes typing {{
        0% {{ content: '.'; }}
        25% {{ content: '..'; }}
        50% {{ content: '...'; }}
        75% {{ content: '..'; }}
        100% {{ content: '.'; }}
    }}

    .typing-animation::before {{
        content: '...';
        animation: typing 1s steps(5, end) infinite;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Sigma - Learning Mentor")

# Chat Window Styling
chat_window_style = """
    border-radius: 10px;
    border: 1px solid #ddd;
    background-color: #fff;
    padding: 10px;
    height: 400px;
    overflow-y: auto;
    font-size: 16px;
    font-family: Arial, sans-serif;
"""

response_style = """
    border-radius: 5px;
    background-color: #e1f3fd;
    padding: 10px;
    margin: 10px 0;
    display: inline-block;
"""

# initialize history
if "messages" not in st.session_state:
    st.session_state["messages"] = []

def model_res_generator():
    stream = ollama.chat(
        model="llama2:latest",
        messages=st.session_state["messages"],
        stream=True,
    )
    for chunk in stream:
        yield chunk["message"]["content"]

# Display chat messages from history on app rerun
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What is up?"):
    # add latest message to history in format {role, content}
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message = st.write_stream(model_res_generator())
        st.session_state["messages"].append({"role": "assistant", "content": message})
