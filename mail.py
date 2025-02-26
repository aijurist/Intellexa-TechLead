import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import zipfile
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def add_text_to_certificate(image, name, college, events, font, positions):
    draw = ImageDraw.Draw(image)
    font_name = font if font else ImageFont.load_default()
    font_college = font if font else ImageFont.load_default()
    font_events = font if font else ImageFont.load_default()

    draw.text(positions["name"], name, fill="black", font=font_name)
    draw.text(positions["college"], college, fill="black", font=font_college)
    draw.text(positions["events"], events, fill="black", font=font_events)

    return image

def generate_certificate(template, name, college, events, font, positions, file_type):
    image = template.copy()
    cert = add_text_to_certificate(image, name, college, events, font, positions)
    img_buffer = io.BytesIO()
    cert.save(img_buffer, format=file_type.upper())
    img_buffer.seek(0)
    return img_buffer

def send_emails():
    st.title("Email Sending & Certificate Generator App")
    sender_email = st.text_input("Enter your email address")
    sender_password = st.text_input("Enter your 16-digit app password", type="password")
    recipient_email = st.text_input("Enter recipient email (leave blank if uploading CSV)")
    csv_file = st.file_uploader("Upload recipients CSV file", type=["csv"])
    email_subject = st.text_input("Enter email subject")
    email_body = st.text_area("Enter email body")
    uploaded_file = st.file_uploader("Attach a file (Optional)", type=["jpg", "jpeg", "png", "pdf", "zip", "docx"])
    template_file = st.file_uploader("Upload certificate template (Optional)", type=["png", "jpg", "jpeg"])
    file_type = st.selectbox("Select certificate format", ["png", "jpg", "jpeg"], index=0)

    if st.button("Send Emails"):
        if not all([sender_email, sender_password, email_subject, email_body]) or (not recipient_email and not csv_file):
            st.error("Please provide all required inputs before sending emails.")
            return
        
        recipients = []
        data = {}
        if recipient_email:
            recipients.append(recipient_email.strip())
        if csv_file:
            df = pd.read_csv(csv_file)
            recipients.extend(df["email"].dropna().astype(str).str.strip().tolist())
            data = df.to_dict(orient="records")
        
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
                    
                    if template_file and data:
                        template = Image.open(template_file)
                        for row in data:
                            if row["email"].strip() == recipient:
                                cert_buffer = generate_certificate(template, row['Name'], row['College'], row['Events'], None, {"name": (200, 150), "college": (200, 200), "events": (200, 250)}, file_type)
                                part = MIMEBase("application", "octet-stream")
                                part.set_payload(cert_buffer.getvalue())
                                encoders.encode_base64(part)
                                part.add_header("Content-Disposition", f"attachment; filename=certificate_{row['Name']}.{file_type}")
                                msg.attach(part)
                    
                    if uploaded_file:
                        file_data = uploaded_file.read()
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(file_data)
                        encoders.encode_base64(part)
                        part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
                        msg.attach(part)
                    
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
