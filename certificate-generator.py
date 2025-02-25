import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from matplotlib import font_manager
import zipfile
import io


def add_text_to_certificate(image, name, college, events, positions, font_path):
    draw = ImageDraw.Draw(image)
    font_name = ImageFont.truetype(font_path, 50)
    font_college = ImageFont.truetype(font_path, 40)
    font_events = ImageFont.truetype(font_path, 35)

    draw.text(positions["name"], name, fill="black", font=font_name)
    draw.text(positions["college"], college, fill="black", font=font_college)
    draw.text(positions["events"], events, fill="black", font=font_events)

    return image


def generate_certificates(template, csv_data, positions, font_path, file_type):
    df = pd.read_csv(csv_data)
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for index, row in df.iterrows():
            image = template.copy()
            cert = add_text_to_certificate(image, row['Name'], row['College'], row['Events'], positions, font_path)
            img_buffer = io.BytesIO()
            cert.save(img_buffer, format=file_type.upper())
            zipf.writestr(f"certificate_{index+1}.{file_type}", img_buffer.getvalue())
    
    zip_buffer.seek(0)
    return zip_buffer

# Streamlit UI
st.title("Certificate Generator")

uploaded_template = st.file_uploader("Upload Certificate Template (JPG/PNG)", type=["jpg", "jpeg", "png"])
uploaded_csv = st.file_uploader("Upload CSV File", type=["csv"])

file_type = st.selectbox("Select Output Format", ["jpg", "png"], index=0)

uploaded_font = st.file_uploader("Upload Custom Font (TTF)", type=["ttf"])

st.subheader("Adjust Text Positions")
name_x = st.number_input("Name X Position", min_value=0, value=500)
name_y = st.number_input("Name Y Position", min_value=0, value=300)
college_x = st.number_input("College X Position", min_value=0, value=500)
college_y = st.number_input("College Y Position", min_value=0, value=400)
events_x = st.number_input("Events X Position", min_value=0, value=500)
events_y = st.number_input("Events Y Position", min_value=0, value=500)

positions = {
    "name": (name_x, name_y),
    "college": (college_x, college_y),
    "events": (events_x, events_y)
}

if uploaded_template and uploaded_csv:
    template = Image.open(uploaded_template).convert("RGB")
    
    if uploaded_font:
        font_path = io.BytesIO(uploaded_font.read())
    else:
        font_path = font_manager.findSystemFonts(fontpaths=None, fontext='ttf')[0]
    
    if st.button("Preview Sample Certificate"):
        sample_image = template.copy()
        sample_cert = add_text_to_certificate(sample_image, "Sample Name", "Sample College", "Sample Event", positions, font_path)
        st.image(sample_cert, caption="Sample Certificate", use_container_width=True)
    
    if st.button("Generate Certificates"):
        zip_buffer = generate_certificates(template, uploaded_csv, positions, font_path, file_type)
        st.download_button("Download Certificates", zip_buffer, file_name="certificates.zip", mime="application/zip")
