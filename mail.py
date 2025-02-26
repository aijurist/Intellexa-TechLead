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

def add_text_to_certificate(image, data, font, positions, font_sizes):
    draw = ImageDraw.Draw(image)
    for key, value in data.items():
        font_size = font_sizes.get(key, 40)  # Default font size
        font_used = ImageFont.truetype(font, font_size) if font else ImageFont.load_default()
        draw.text(positions[key], value, fill="black", font=font_used)
    return image

def generate_certificate(template, data, font, positions, font_sizes, file_type):
    image = template.copy()
    cert = add_text_to_certificate(image, data, font, positions, font_sizes)
    img_buffer = io.BytesIO()
    cert.save(img_buffer, format=file_type.upper())
    img_buffer.seek(0)
    return img_buffer, cert

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

    st.subheader("Adjust Text Positions and Font Sizes")
    positions = {}
    font_sizes = {}
    if csv_file:
        df = pd.read_csv(csv_file)
        for column in df.columns:
            x_pos = st.number_input(f"{column} X Position", min_value=0, value=200)
            y_pos = st.number_input(f"{column} Y Position", min_value=0, value=150)
            font_size = st.number_input(f"{column} Font Size", min_value=10, max_value=100, value=40)
            positions[column] = (x_pos, y_pos)
            font_sizes[column] = font_size

    if template_file and csv_file:
        template = Image.open(template_file).convert("RGB")
        df = pd.read_csv(csv_file)
        if st.button("Preview Sample Certificate"):
            sample_data = df.iloc[0].to_dict() if not df.empty else {"Name": "Sample Name", "College": "Sample College", "Events": "Sample Event"}
            _, sample_cert = generate_certificate(template, sample_data, None, positions, font_sizes, file_type)
            st.image(sample_cert, caption="Sample Certificate Preview", use_column_width=True)

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
                                cert_buffer, _ = generate_certificate(template, row, None, positions, font_sizes, file_type)
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
