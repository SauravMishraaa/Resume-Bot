import streamlit as st
import requests
import os
import dotenv

dotenv.load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/query")
RESUME_URL = os.getenv("RESUME_URL")

st.set_page_config(page_title="Saurav's Resume Bot", page_icon="🤖", layout="centered")

st.title("🤖 Saurav Kumar's AI Resume Assistant")
st.write("Ask me anything about Saurav's skills, projects, and experience!")

st.markdown(
    f'<a href="{RESUME_URL}" target="_blank">'
    '<button style="background-color:#4CAF50; color:white; padding:10px 20px; border:none; border-radius:8px; cursor:pointer;">📄 View Resume</button>'
    '</a>',
    unsafe_allow_html=True
)

st.markdown("---")

user_query = st.text_input(
    "💬 Type your question here:", 
    placeholder="e.g., What projects has Saurav worked on?"
)

if st.button("Ask"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = requests.post(API_URL, json={"query": user_query})
                if response.status_code == 200:
                    answer = response.json().get("answer", "⚠️ No answer returned.")
                    st.markdown(f"### 📌 Answer:\n{answer}")
                elif response.status_code == 429 or response.status_code == 500:
                    st.error("Apologies! Something went wrong on the server 😔. You can still view my resume above.")
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"Failed to reach backend: {e}")
