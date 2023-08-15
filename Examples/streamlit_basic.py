import streamlit as st

st.set_page_config(page_title="SRL Chatbot Demo", page_icon = ":robot:")
st.header("SRL Bot Demo")


col1, col2, col3 = st.columns(3)

with col1:
    st.write("col1")

with col2:
    st.write("col2")

with col3:
    st.write("col3")

input_text = st.text_area(label="", placeholder="Enter your prompt..", key="user_input")

if input_text:
    st.write("The user input text is " + input_text)