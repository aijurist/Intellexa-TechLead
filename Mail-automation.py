# import smtplib
# import pandas as pd
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import streamlit as st
# import io

# def send_emails():
#     st.title("Email Sending App")
    
#     sender_email = st.text_input("Enter your email address")
#     sender_password = st.text_input("Enter your 16-digit app password", type="password")
    
#     recipient_email = st.text_input("Enter recipient email (leave blank if uploading CSV)")
#     csv_file = st.file_uploader("Upload recipients CSV file", type="csv")
    
#     email_subject = st.text_input("Enter email subject")
#     email_body = st.text_area("Enter email body (use {name} to personalize recipient name)")
    
#     attachment = st.file_uploader("Attach a file", type=None)
    
#     if st.button("Send Emails"):
#         if not all([sender_email, sender_password, email_subject, email_body]) or (not recipient_email and not csv_file):
#             st.error("Please provide all required inputs before sending emails.")
#             return
        
#         recipients = []
#         if recipient_email:
#             recipients.append({"email": recipient_email.strip(), "name": "there"})
#         if csv_file:
#             df = pd.read_csv(csv_file)
#             for _, row in df.iterrows():
#                 recipients.append({"email": row["email"].strip(), "name": row.get("name", "there").strip()})
        
#         try:
#             SMTP_SERVER = "smtp.gmail.com"
#             SMTP_PORT = 587
            
#             with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#                 server.starttls()
#                 server.login(sender_email, sender_password)
                
#                 for recipient in recipients:
#                     msg = MIMEMultipart()
#                     msg["From"] = sender_email
#                     msg["To"] = recipient["email"]
#                     msg["Subject"] = email_subject
                    
#                     personalized_body = email_body.replace("{name}", recipient["name"])
#                     msg.attach(MIMEText(personalized_body, "plain"))
                    
#                     if attachment is not None:
#                         part = MIMEBase("application", "octet-stream")
#                         part.set_payload(attachment.read())
#                         encoders.encode_base64(part)
#                         part.add_header("Content-Disposition", f"attachment; filename={attachment.name}")
#                         msg.attach(part)
                    
#                     try:
#                         server.sendmail(sender_email, recipient["email"], msg.as_string())
#                         st.write(f"Email sent to {recipient["email"]}")
#                     except Exception as email_error:
#                         st.error(f"Failed to send email to {recipient["email"]}: {email_error}")
            
#             st.success("All emails sent successfully!")
#         except Exception as e:
#             st.error(f"Error: {e}")

# if __name__ == "__main__":
#     send_emails()



import smtplib
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st
import io

def send_emails():
    st.title("Email Sending App")
    
    sender_email = st.text_input("Enter your email address")
    sender_password = st.text_input("Enter your 16-digit app password", type="password")
    
    recipient_email = st.text_input("Enter recipient email (leave blank if uploading CSV)")
    csv_file = st.file_uploader("Upload recipients CSV file", type="csv")
    
    email_subject = st.text_input("Enter email subject")
    email_body = st.text_area("Enter email body (supports HTML: <b>bold</b>, <i>italic</i>, etc.)")
    
    attachment = st.file_uploader("Attach a file", type=None)
    
    if st.button("Send Emails"):
        if not all([sender_email, sender_password, email_subject, email_body]) or (not recipient_email and not csv_file):
            st.error("Please provide all required inputs before sending emails.")
            return
        
        recipients = []
        if recipient_email:
            recipients.append({"email": recipient_email.strip(), "name": "there"})
        if csv_file:
            df = pd.read_csv(csv_file)
            for _, row in df.iterrows():
                recipients.append({"email": row["email"].strip(), "name": row.get("name", "there").strip()})
        
        try:
            SMTP_SERVER = "smtp.gmail.com"
            SMTP_PORT = 587
            
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                
                for recipient in recipients:
                    msg = MIMEMultipart()
                    msg["From"] = sender_email
                    msg["To"] = recipient["email"]
                    msg["Subject"] = email_subject
                    
                    # Support HTML for formatting
                    personalized_body = email_body.replace("{name}", recipient["name"])
                    msg.attach(MIMEText(personalized_body, "html"))  # Change to "html"
                    
                    if attachment is not None:
                        file_data = attachment.read()
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(file_data)
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={attachment.name}")
                        msg.attach(part)
                    
                    try:
                        server.sendmail(sender_email, recipient["email"], msg.as_string())
                        st.write(f"✅ Email sent to {recipient['email']}")
                    except Exception as email_error:
                        st.error(f"❌ Failed to send email to {recipient['email']}: {email_error}")
            
            st.success("🎉 All emails sent successfully!")
        except Exception as e:
            st.error(f"🚨 Error: {e}")

if __name__ == "__main__":
    send_emails()

