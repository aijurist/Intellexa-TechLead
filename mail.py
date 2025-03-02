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


# Define font_path globally
font_path = None  # Default to None
if font_file:
    font_path = "./uploaded_font.ttf"
    with open(font_path, "wb") as f:
        f.write(font_file.read())

# Preview Sample Certificate Before Sending
if template_file and csv_file:
    st.subheader("Preview Certificate")

    if st.button("Preview Sample Certificate"):
        sample_data = df.iloc[0].to_dict() if not df.empty else {col: "Sample " + col for col in positions.keys()}

        if not positions or not font_sizes:
            st.error("Please set text positions and font sizes before previewing!")
        else:
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

        # Generate certificate (now font_path is always available)
        cert_buffer = generate_certificate_pdf(row, font_path, positions, font_sizes, template_file)
        file_name = f"certificate_{row['Name']}.pdf"

        # Send email with attachment
        if send_email(sender_email, sender_password, recipient_email, email_subject, email_body, cert_buffer, file_name):
            success_count += 1
            st.write(f"Certificate sent to {recipient_email}")
        else:
            failed_count += 1

    st.success(f"Process complete! {success_count} emails sent, {failed_count} failed.")
