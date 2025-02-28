import streamlit as st
import json
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load Google Drive credentials from Streamlit Secrets
creds_dict = dict(st.secrets["google"])  # Convert AttrDict to a normal dict
creds = service_account.Credentials.from_service_account_info(creds_dict)

# Initialize Google Drive API
drive_service = build("drive", "v3", credentials=creds)

# Function to get folders from Google Drive
def get_folders(parent_folder_id="root"):
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

# Function to get files inside a selected folder
def get_files(folder_id):
    query = f"'{folder_id}' in parents and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get("files", [])

# Function to generate a Google Drive direct link
def generate_drive_link(file_id, mime_type):
    base_url = "https://drive.google.com"
    google_docs_types = {
        "application/vnd.google-apps.spreadsheet": "spreadsheets",
        "application/vnd.google-apps.document": "document",
        "application/vnd.google-apps.presentation": "presentation",
        "application/vnd.google-apps.drawing": "drawings",
        "application/vnd.google-apps.form": "forms",
    }
    if mime_type in google_docs_types:
        return f"https://docs.google.com/{google_docs_types[mime_type]}/d/{file_id}"
    elif mime_type.startswith("application/"):
        return f"{base_url}/file/d/{file_id}/view"
    return f"{base_url}/open?id={file_id}"

# Function to check permissions of a file
def check_permissions(file_id):
    permissions = drive_service.permissions().list(fileId=file_id).execute()
    return permissions.get("permissions", [])

# Streamlit UI
st.title("📂 Google Drive Viewer")

# Get root folders
folders = get_folders()

# Handle empty folder case
folder_options = ["Root"]
folder_dict = {"Root": "root"}

if folders:
    for folder in folders:
        folder_options.append(folder["name"])
        folder_dict[folder["name"]] = folder["id"]

folder_selection = st.sidebar.selectbox("Select a Folder", folder_options)

# Get the selected folder ID
selected_folder_id = folder_dict[folder_selection]

# Display files inside the selected folder
files = get_files(selected_folder_id)

st.subheader(f"📁 {folder_selection}")

if not files:
    st.write("📭 No files found in this folder.")
else:
    for file in files:
        file_link = generate_drive_link(file["id"], file["mimeType"])
        st.markdown(f"📄 **[{file['name']}]({file_link})**")
        
        # Fetch and display permission details
        permissions = check_permissions(file["id"])
        if permissions:
            st.write("🔑 **Permissions:**")
            for perm in permissions:
                st.write(f"- Role: {perm.get('role', 'Unknown')}, Type: {perm.get('type', 'Unknown')}")
        else:
            st.write("🔒 No permissions found.")
