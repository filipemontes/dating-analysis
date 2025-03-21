import streamlit as st
from message_analyzer import process_and_group_chat
import os
# Load HTML intro page
html_path = os.path.abspath("index.html")
with open(html_path, "r", encoding="utf-8") as f:
    html_content = f.read()

# Page Navigation using the new query_params
query_params = st.query_params
if "run" not in query_params:
    st.components.v1.html(html_content, height=600)
else:
    st.title("Relationship Message Analyzer")

    # File uploader
    uploaded_file = st.file_uploader("Upload your chat text file", type=["txt"])

    if uploaded_file is not None:
        chat_data = uploaded_file.read().decode("utf-8").splitlines()

        # Apply the combined function for processing and grouping
        df = process_and_group_chat(chat_data)

        # Message count per sender
        st.subheader("Messages Sent by Each Person")
        msg_count = df["Sender"].value_counts()
        st.bar_chart(msg_count)

        # Count occurrences of the word "amote"
        df["Amote Count"] = df["Message"].str.lower().str.count("amote")
        amote_count = df.groupby("Sender")["Amote Count"].sum()

        st.subheader("'Amote' Count per Person")
        st.bar_chart(amote_count)

    st.write("Upload a chat file to analyze messages!")
