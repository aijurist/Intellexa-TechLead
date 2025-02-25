import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import streamlit as st
import io

def send_emails():
    st.title("Email Sending App")
    
    sender_email = st.text_input("Enter your email address")
    sender_password = st.text_input("Enter your 16-digit app password", type="password")
    
    recipient_email = st.text_input("Enter recipient email (leave blank if uploading CSV)")
    csv_file = st.file_uploader("Upload recipients CSV file", type="csv")
    
    email_subject = st.text_input("Enter email subject")
    email_body = st.text_area("Enter email body")
    
    if st.button("Send Emails"):
        if not all([sender_email, sender_password, email_subject, email_body]) or (not recipient_email and not csv_file):
            st.error("Please provide all required inputs before sending emails.")
            return
        
        recipients = []
        if recipient_email:
            recipients.append(recipient_email.strip())
        if csv_file:
            df = pd.read_csv(csv_file)
            recipients.extend(df["email"].dropna().astype(str).str.strip().tolist())
        
        try:
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                
                for recipient in recipients:
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = recipient
                    msg["Subject"] = email_subject
                    msg.attach(MIMEText(email_body, "plain"))
                    
                    try:
                        server.sendmail(sender_email, recipient, msg.as_string())
                        st.write(f"Email sent to {recipient}")
                    except Exception as email_error:
                        st.error(f"Failed to send email to {recipient}: {email_error}")
                
            st.success("All emails sent successfully!")
        except Exception as e:
            st.error(f"Error: {e}")

if __name__ == "__main__":
    send_emails()
