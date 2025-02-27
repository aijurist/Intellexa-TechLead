# import streamlit as st
# import pandas as pd
# from PIL import Image, ImageDraw, ImageFont
# import io
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders

# def add_text_to_certificate(image, data, font_path, positions, font_sizes):
#     draw = ImageDraw.Draw(image)
#     fonts = {}
    
#     for key in data.keys():
#         if key in positions:
#             font_size = font_sizes.get(key, 40)  # Default to 40 if not set
            
#             if font_size not in fonts:
#                 try:
#                     fonts[font_size] = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.truetype("DejaVuSans.ttf", font_size)
#                 except IOError:
#                     fonts[font_size] = ImageFont.load_default()
            
#             draw.text(positions[key], str(data[key]), fill="black", font=fonts[font_size])
    
#     return image

# def generate_certificate(template, data, font_path, positions, font_sizes, file_type):
#     image = template.copy()
    
#     # Remove email from data dictionary
#     data_without_email = {key: value for key, value in data.items() if key.lower() != "email"}

#     # Apply text to certificate
#     cert = add_text_to_certificate(image, data_without_email, font_path, positions, font_sizes)

#     img_buffer = io.BytesIO()
    
#     # Convert to PDF for better font preservation
#     if file_type.lower() == "pdf":
#         pdf_buffer = io.BytesIO()
#         cert.save(pdf_buffer, format="PDF")
#         pdf_buffer.seek(0)
#         return pdf_buffer, cert

#     cert.save(img_buffer, format=file_type.upper())
#     img_buffer.seek(0)
#     return img_buffer, cert


# import base64
# import smtplib
# import pandas as pd
# import streamlit as st
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.application import MIMEApplication
# from email.mime.base import MIMEBase
# from email import encoders
# from PIL import Image
# from io import BytesIO

# import smtplib
# import base64
# import pandas as pd
# import streamlit as st
# from io import BytesIO
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText
# from email.mime.application import MIMEApplication
# from email.mime.base import MIMEBase
# from email import encoders
# from PIL import Image

# def send_emails():
#     st.title("Certificate Generator & Email Sender")

#     sender_email = st.text_input("Enter your email")
#     sender_password = st.text_input("Enter your 16-digit app password", type="password")
#     recipient_email = st.text_input("Enter recipient email (leave blank if uploading CSV)")
#     csv_file = st.file_uploader("Upload CSV file", type=["csv"])
#     email_subject = st.text_input("Email Subject")
#     email_body = st.text_area("Email Body")
#     uploaded_file = st.file_uploader("Attach a file (Optional)", type=["jpg", "jpeg", "png", "pdf", "zip", "docx"])
#     template_file = st.file_uploader("Upload Certificate Template", type=["png", "jpg", "jpeg"])
#     font_file = st.file_uploader("Upload Font File (Optional, e.g., Arial.ttf)", type=["ttf"])
#     file_type = st.selectbox("Select certificate format", ["pdf", "png", "jpg", "jpeg"], index=0)

#     st.subheader("Set Text Positions and Font Sizes")
#     positions = {}
#     font_sizes = {}

#     if csv_file:
#         csv_file.seek(0)
#         try:
#             df = pd.read_csv(csv_file, encoding="utf-8")
#         except pd.errors.EmptyDataError:
#             st.error("CSV file is empty or invalid.")
#             st.stop()

#         for column in df.columns:
#             if column.lower() != "email":
#                 x_pos = st.number_input(f"{column} X Position", min_value=0, value=200)
#                 y_pos = st.number_input(f"{column} Y Position", min_value=0, value=150)
#                 font_size = st.number_input(f"{column} Font Size", min_value=10, max_value=100, value=40)
#                 positions[column] = (x_pos, y_pos)
#                 font_sizes[column] = font_size

#     if template_file and csv_file:
#         template = Image.open(template_file).convert("RGB")

#         if st.button("Preview Sample Certificate"):
#             sample_data = df.iloc[0].to_dict() if not df.empty else {col: "Sample " + col for col in positions.keys()}
#             _, sample_cert = generate_certificate(template, sample_data, font_file, positions, font_sizes, file_type)
#             st.image(sample_cert, caption="Sample Certificate Preview", use_column_width=True)

#     if st.button("Send Emails"):
#         if not all([sender_email, sender_password, email_subject, email_body]) or (not recipient_email and not csv_file):
#             st.error("Fill all required fields before sending emails.")
#             return

#         recipients = []
#         data = []

#         if recipient_email:
#             recipients.append(recipient_email.strip())
#         if csv_file:
#             recipients.extend(df["email"].dropna().astype(str).str.strip().tolist())
#             data = df.to_dict(orient="records")

#         try:
#             SMTP_SERVER = "smtp.gmail.com"
#             SMTP_PORT = 587

#             with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#                 server.starttls()
#                 server.login(sender_email, sender_password)

#                 for recipient in recipients:
#                     msg = MIMEMultipart()
#                     msg["From"] = sender_email
#                     msg["To"] = recipient
#                     msg["Subject"] = email_subject

#                     # Certificate Processing
#                     if template_file and data:
#                         row = next((r for r in data if r["email"].strip() == recipient), None)

#                         if row:
#                             template_copy = template.copy()
#                             cert_buffer, _ = generate_certificate(template_copy, row, font_file, positions, font_sizes, file_type)

#                             # Convert certificate to Base64 for embedding
#                             cert_buffer.seek(0)
#                             base64_image = base64.b64encode(cert_buffer.read()).decode('utf-8')

#                             # Email body with embedded image
#                             html_content = f"""
#                             <html>
#                                 <body>
#                                     <p>{email_body}</p>
#                                     <img src="data:image/{file_type};base64,{base64_image}" alt="Certificate">
#                                     <p>You can also <a href="cid:certificate_attachment">download the certificate</a>.</p>
#                                 </body>
#                             </html>
#                             """
#                             msg.attach(MIMEText(html_content, "html"))

#                             # Attach certificate for download
#                             cert_buffer.seek(0)
#                             attachment = MIMEApplication(cert_buffer.read(), Name=f"certificate_{row['Name']}.{file_type}")
#                             attachment.add_header('Content-Disposition', f'attachment; filename="certificate_{row["Name"]}.{file_type}"')
#                             msg.attach(attachment)

#                     # Attach other uploaded files
#                     if uploaded_file:
#                         uploaded_file.seek(0)
#                         file_data = uploaded_file.read()
#                         part = MIMEBase("application", "octet-stream")
#                         part.set_payload(file_data)
#                         encoders.encode_base64(part)
#                         part.add_header("Content-Disposition", f"attachment; filename={uploaded_file.name}")
#                         msg.attach(part)

#                     try:
#                         server.sendmail(sender_email, recipient, msg.as_string())
#                         st.write(f"✅ Email sent to {recipient}")
#                     except Exception as email_error:
#                         st.error(f"❌ Failed to send email to {recipient}: {email_error}")

#             st.success("🎉 All emails sent successfully!")
#         except Exception as e:
#             st.error(f"❌ Error: {e}")

# if __name__ == "__main__":
#     send_emails()


import streamlit as st
import pandas as pd
import smtplib
import io
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.pagesizes import A4
from PIL import Image

# Function to generate a certificate as a PDF with embedded font
def generate_certificate_pdf(data, font_path, positions, font_sizes, template_file):
    buffer = io.BytesIO()

    # Convert the uploaded template file into a temporary image file
    template = Image.open(template_file)
    width, height = template.size  # Get the actual template dimensions

    # Save the image as a temporary file so ReportLab can access it
    temp_template_path = "./temp_certificate.png"
    template.save(temp_template_path)

    # Create PDF canvas with the same dimensions as the template
    c = canvas.Canvas(buffer, pagesize=(width, height))

    # Register the font safely
    if font_path:
        try:
            pdfmetrics.registerFont(TTFont("CustomFont", font_path))
            font_name = "CustomFont"
        except Exception as e:
            st.error(f"Font Error: {e}")
            font_name = "Helvetica"
    else:
        font_name = "Helvetica"  # Default font

    # Draw the template image as the background
    c.drawImage(temp_template_path, 0, 0, width, height)

    # Apply text positions and font sizes
    text_drawn = False
    for key, value in data.items():
        if key in positions and value:
            x, y = positions[key]
            font_size = font_sizes.get(key, 40)
            c.setFont(font_name, font_size)
            c.drawString(x, y, str(value))
            text_drawn = True

    if not text_drawn:
        print("⚠ Warning: No text drawn on the certificate!")

    c.save()
    buffer.seek(0)
    return buffer


# Function to send email with certificate attached
def send_email(sender_email, sender_password, recipient_email, email_subject, email_body, cert_buffer, file_name):
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = email_subject

    # Attach the email body
    msg.attach(MIMEText(email_body, "plain"))

    # Attach the certificate
    attachment = MIMEApplication(cert_buffer.read(), Name=file_name)
    attachment.add_header('Content-Disposition', f'attachment; filename="{file_name}"')
    msg.attach(attachment)

    # Send the email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipient_email, msg.as_string())
        return True
    except Exception as e:
        st.error(f"Failed to send email to {recipient_email}: {e}")
        return False

# Streamlit UI
st.title("Automated Certificate Generator & Email Sender")

sender_email = st.text_input("Enter your email")
sender_password = st.text_input("Enter your 16-digit app password", type="password")
csv_file = st.file_uploader("Upload CSV file", type=["csv"])
email_subject = st.text_input("Email Subject")
email_body = st.text_area("Email Body")
template_file = st.file_uploader("Upload Certificate Template", type=["png", "jpg", "jpeg"])
font_file = st.file_uploader("Upload Font File (Optional, e.g., Arial.ttf)", type=["ttf"])
file_type = "pdf"  # Always generate PDFs for proper font embedding

st.subheader("Set Text Positions and Font Sizes")
positions = {}
font_sizes = {}

# Load CSV file and let the user set text positions
if csv_file:
    csv_file.seek(0)
    df = pd.read_csv(csv_file, encoding="utf-8")

    for column in df.columns:
        if column.lower() != "email":
            x_pos = st.number_input(f"{column} X Position", min_value=0, value=200)
            y_pos = st.number_input(f"{column} Y Position", min_value=0, value=150)
            font_size = st.number_input(f"{column} Font Size", min_value=10, max_value=100, value=40)
            positions[column] = (x_pos, y_pos)
            font_sizes[column] = font_size


import fitz  # PyMuPDF for PDF to image conversion
import streamlit as st
import io
from PIL import Image


# Function to display the certificate preview in Streamlit
def show_certificate_preview(cert_buffer):
    try:
        pdf_document = fitz.open("pdf", cert_buffer.getvalue())  # Load PDF from bytes
        first_page = pdf_document[0]  # Get first page
        pix = first_page.get_pixmap()  # Render page to image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Convert to PIL image
        
        st.image(img, caption="Sample Certificate Preview", use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying preview: {e}")


# Preview Certificate Before Sending
def show_certificate_preview(cert_buffer):
    try:
        pdf_document = fitz.open("pdf", cert_buffer.getvalue())  # Load PDF from bytes
        first_page = pdf_document[0]  # Get first page
        pix = first_page.get_pixmap()  # Render page to image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)  # Convert to PIL image
        
        st.image(img, caption="Sample Certificate Preview", use_column_width=True)
    except Exception as e:
        st.error(f"Error displaying preview: {e}")

# Preview Sample Certificate Before Sending
if template_file and csv_file:
    st.subheader("Preview Certificate")

    if st.button("Preview Sample Certificate"):
        # Load sample data from the CSV
        sample_data = df.iloc[0].to_dict() if not df.empty else {col: "Sample " + col for col in positions.keys()}

        # Ensure font path is set
        font_path = None  # Default to None
        if font_file:
            font_path = "./uploaded_font.ttf"
            with open(font_path, "wb") as f:
                f.write(font_file.read())

        # Ensure positions & font_sizes are set
        if not positions or not font_sizes:
            st.error("Please set text positions and font sizes before previewing!")
        else:
            # Generate the sample certificate
            cert_buffer = generate_certificate_pdf(sample_data, font_path, positions, font_sizes, template_file)
            show_certificate_preview(cert_buffer)  # Show preview in Streamlit




# Ensure the template file is uploaded
if template_file:
    template = Image.open(template_file).convert("RGB")
else:
    st.error("Please upload a certificate template.")
    st.stop()

# Generate and Send Emails Sequentially
if st.button("Generate & Send Certificates"):
    success_count = 0
    failed_count = 0

    for _, row in df.iterrows():
        recipient_email = row.get("email", "").strip()
        if not recipient_email:
            st.warning("Skipping row with missing email.")
            continue

        # Generate certificate
        cert_buffer = generate_certificate_pdf(row, font_path, positions, font_sizes, template_file)
        file_name = f"certificate_{row['Name']}.pdf"

        # Send email with attachment
        if send_email(sender_email, sender_password, recipient_email, email_subject, email_body, cert_buffer, file_name):
            success_count += 1
            st.write(f"Certificate sent to {recipient_email}")
        else:
            failed_count += 1

    st.success(f"Process complete! {success_count} emails sent, {failed_count} failed.")
