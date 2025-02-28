import streamlit as st
import json
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials from Streamlit Secrets
creds_dict = st.secrets["google"]
creds_json = json.dumps(creds_dict)
creds = service_account.Credentials.from_service_account_info(json.loads(creds_json))

# Initialize Google Drive API
drive_service = build("drive", "v3", credentials=creds)

# Function to get folders from Google Drive
def get_folders(parent_folder_id="root"):
    query = f"'{parent_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

# Function to get files inside a selected folder
def get_files(folder_id):
    query = f"'{folder_id}' in parents"
    results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get("files", [])

# Function to generate a Google Drive direct link
def generate_drive_link(file_id, mime_type):
    if mime_type == "application/vnd.google-apps.spreadsheet":
        return f"https://docs.google.com/spreadsheets/d/{file_id}"
    elif mime_type == "application/vnd.google-apps.document":
        return f"https://docs.google.com/document/d/{file_id}"
    elif mime_type.startswith("application/"):
        return f"https://drive.google.com/file/d/{file_id}/view"
    return f"https://drive.google.com/open?id={file_id}"

# Streamlit UI
st.title("📂 Google Drive Viewer")

# Get root folders
folders = get_folders()

# Sidebar to select a folder
folder_selection = st.sidebar.selectbox("Select a Folder", ["Root"] + [folder["name"] for folder in folders])

# Get the selected folder ID
selected_folder_id = "root"
if folder_selection != "Root":
    for folder in folders:
        if folder["name"] == folder_selection:
            selected_folder_id = folder["id"]
            break

# Display files inside the selected folder
files = get_files(selected_folder_id)

st.subheader(f"📁 {folder_selection}")

if not files:
    st.write("No files found in this folder.")
else:
    for file in files:
        file_link = generate_drive_link(file["id"], file["mimeType"])
        st.markdown(f"📄 **[{file['name']}]({file_link})**")

