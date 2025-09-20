import streamlit as st
import requests
import os
import dotenv
import smtplib
from email.mime.text import MIMEText

dotenv.load_dotenv()

API_URL = os.getenv("API_URL", "http://localhost:8000/query")
RESUME_URL = os.getenv("RESUME_URL")

EMAIL_SENDER = os.getenv("EMAIL_SENDER")       
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")   
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")   

def send_error_email(error_message):
    try:
        msg = MIMEText(error_message)
        msg['Subject'] = "Resume Bot Backend Error"
        msg['From'] = EMAIL_SENDER
        msg['To'] = EMAIL_RECEIVER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
    except Exception as e:
        st.warning(f"Failed to send error email: {e}")

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
                elif response.status_code in [429, 500]:
                    st.error("Apologies! Something went wrong on the server 😔. You can still view my resume.")
                    send_error_email(f"Backend returned error {response.status_code} for query: {user_query}")
                else:
                    st.error("Apologies! Something went wrong on the server 😔. You can still view my resume.")
                    send_error_email(f"Backend returned error {response.status_code}: {response.text} for query: {user_query}")
            except Exception as e:
                st.error(f"Failed to reach backend: {e}")
                send_error_email(f"Exception occurred: {e} for query: {user_query}")
