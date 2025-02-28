# import streamlit as st
# import google.auth
# from google.oauth2 import service_account
# from googleapiclient.discovery import build

# # Load Google Drive credentials from Streamlit Secrets
# SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
# creds_dict = dict(st.secrets["google"])
# creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
# drive_service = build("drive", "v3", credentials=creds)

# # Function to get all files (including parent folder IDs)
# def get_all_files():
#     results = drive_service.files().list(fields="files(id, name, parents, mimeType)").execute()
#     return results.get("files", [])

# # Function to get folders
# def get_folders():
#     query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
#     results = drive_service.files().list(q=query, fields="files(id, name)").execute()
#     return results.get("files", [])

# # Streamlit UI
# st.title("📂 Google Drive File Manager")

# # Get folders and files
# folders = get_folders()
# files = get_all_files()

# # Create a dictionary to map folder IDs to their contents
# folder_contents = {folder["id"]: [] for folder in folders}
# standalone_files = []

# # Categorize files into folders or standalone (excluding folders from standalone)
# for file in files:
#     if file["mimeType"] == "application/vnd.google-apps.folder":
#         continue  # Skip folders in standalone files
#     if "parents" in file:
#         parent_id = file["parents"][0]  # Assuming single parent
#         if parent_id in folder_contents:
#             folder_contents[parent_id].append(file)
#         else:
#             standalone_files.append(file)
#     else:
#         standalone_files.append(file)

# # Display folders and their files
# st.subheader("📁 Folders")
# if folders:
#     for folder in folders:
#         with st.expander(f"📂 {folder['name']}"):
#             if folder_contents[folder["id"]]:
#                 for file in folder_contents[folder["id"]]:
#                     file_url = f"https://drive.google.com/file/d/{file['id']}/preview"
#                     st.markdown(f"📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)
#             else:
#                 st.write("No files in this folder.")
# else:
#     st.write("No folders found.")

# # Display standalone files (excluding folders)
# st.subheader("📄 Standalone Files")
# if standalone_files:
#     for file in standalone_files:
#         file_url = f"https://drive.google.com/file/d/{file['id']}/view"
#         st.markdown(f"📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)
# else:
#     st.write("No standalone files found.")


import time
import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials securely from Streamlit Secrets
SCOPES = ["https://www.googleapis.com/auth/drive.metadata.readonly"]
creds_dict = dict(st.secrets["google"])
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)

# Initialize Google Drive API
drive_service = build("drive", "v3", credentials=creds)

# Rate-limiting function to prevent excessive API calls
def api_request(func, *args, **kwargs):
    time.sleep(0.5)  # Prevents API abuse
    return func(*args, **kwargs)

# Function to fetch all files with secure webViewLink
def get_all_files():
    query = "trashed=false"
    results = api_request(
        drive_service.files().list,
        q=query,
        fields="files(id, name, parents, mimeType, webViewLink)"
    ).execute()
    return results.get("files", [])

# Function to fetch only folders
def get_folders():
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = api_request(
        drive_service.files().list,
        q=query,
        fields="files(id, name)"
    ).execute()
    return results.get("files", [])

# Streamlit UI
st.title("🔐 Secure Google Drive File Manager")

# Get folders and files
folders = get_folders()
files = get_all_files()

# Categorize files into folders and standalone files
folder_contents = {folder["id"]: [] for folder in folders}
standalone_files = []

for file in files:
    if file["mimeType"] == "application/vnd.google-apps.folder":
        continue  # Skip folders in standalone files
    if "parents" in file:
        parent_id = file["parents"][0]  # Assuming a single parent folder
        if parent_id in folder_contents:
            folder_contents[parent_id].append(file)
        else:
            standalone_files.append(file)
    else:
        standalone_files.append(file)

# Display folders and their files securely
st.subheader("📁 Secure Folders")
if folders:
    for folder in folders:
        with st.expander(f"📂 {folder['name']}"):
            if folder_contents[folder["id"]]:
                for file in folder_contents[folder["id"]]:
                    file_url = file.get("webViewLink", "#")  # Secure Drive link
                    st.markdown(f"📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)
            else:
                st.write("No files in this folder.")
else:
    st.write("No folders found.")

# Display standalone files securely
st.subheader("📄 Secure Standalone Files")
if standalone_files:
    for file in standalone_files:
        file_url = file.get("webViewLink", "#")
        st.markdown(f"📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)
else:
    st.write("No standalone files found.")
