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
    csv_file = st.file_uploader("Upload the recipients CSV file", type="csv")
    email_content_file = st.file_uploader("Upload the email content text file", type="txt")
    
    if st.button("Send Emails"):
        if not all([sender_email, sender_password, csv_file, email_content_file]):
            st.error("Please provide all inputs before sending emails.")
            return
        
        try:
            df = pd.read_csv(csv_file)
            email_body = io.StringIO(email_content_file.getvalue().decode("utf-8")).read()
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.set_debuglevel(1)  # Enable debug mode to see SMTP responses
                server.starttls()
                server.login(sender_email, sender_password)
                
                for _, row in df.iterrows():
                    recipient_email = row.get("email", "").strip()
                    recipient_name = row.get("name", "").strip()
                    if not recipient_email:
                        continue
                    
                    subject = f"Personalized Message for {recipient_name}" if recipient_name else "Your Message"
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = recipient_email
                    msg["Subject"] = subject
                    msg.attach(MIMEText(email_body, "plain"))
                    
                    try:
                        server.sendmail(sender_email, recipient_email, msg.as_string())
                        st.write(f"✅ Email sent to {recipient_email}")
                    except Exception as email_error:
                        st.error(f"❌ Failed to send to {recipient_email}: {email_error}")

            st.success("✅ All emails sent successfully (Check logs for failures)")
        except smtplib.SMTPAuthenticationError:
            st.error("❌ Authentication failed! Check your email & app password.")
        except smtplib.SMTPConnectError:
            st.error("❌ Could not connect to SMTP server. Check your internet connection.")
        except Exception as e:
            st.error(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    send_emails()
