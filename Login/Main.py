# import streamlit as st
# import google.auth
# from google.oauth2 import service_account
# from googleapiclient.discovery import build

# # Load Google Drive credentials from Streamlit Secrets
# SCOPES = ["https://www.googleapis.com/auth/drive"]
# creds = service_account.Credentials.from_service_account_info(dict(st.secrets["google"]), scopes=SCOPES)

# # Initialize Drive API client
# drive_service = build("drive", "v3", credentials=creds)

# # Function to retrieve all files with pagination
# @st.cache_data(ttl=600)  # Cache results for 10 minutes to optimize performance
# def get_all_files():
#     files = []
#     page_token = None
#     while True:
#         results = drive_service.files().list(
#             fields="nextPageToken, files(id, name)",
#             pageSize=100,  # Fetch 100 files at a time for efficiency
#             pageToken=page_token
#         ).execute()
#         files.extend(results.get("files", []))
#         page_token = results.get("nextPageToken")
#         if not page_token:
#             break
#     return files

# # Function to retrieve only folders from Google Drive
# @st.cache_data(ttl=600)
# def get_folders():
#     query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
#     results = drive_service.files().list(
#         q=query, fields="files(id, name)"
#     ).execute()
#     return results.get("files", [])

# # Streamlit UI
# st.title("Google Drive File Viewer")

# # Display files
# files = get_all_files()
# if files:
#     st.write(f"### Found {len(files)} files:")
#     for file in files:
#         st.write(f"- 📄 **{file['name']}** (ID: `{file['id']}`)")
# else:
#     st.write("No files found.")

# # Display folders
# folders = get_folders()
# if folders:
#     st.write(f"### Found {len(folders)} folders:")
#     for folder in folders:
#         st.write(f"- 📁 **{folder['name']}** (ID: `{folder['id']}`)")
# else:
#     st.write("No folders found.")




import streamlit as st
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load Google Drive credentials from Streamlit Secrets
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds_dict = dict(st.secrets["google"])
creds = service_account.Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
drive_service = build("drive", "v3", credentials=creds)

# Function to get all files
def get_all_files():
    results = drive_service.files().list(fields="files(id, name)").execute()
    return results.get("files", [])

# Function to get folders from Google Drive
def get_folders():
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get("files", [])

# Streamlit UI
st.title("📂 Google Drive File Manager")

# Display folders
st.subheader("📁 Folders")
folders = get_folders()
if folders:
    for folder in folders:
        st.markdown(f"📂 **{folder['name']}**", unsafe_allow_html=True)
else:
    st.write("No folders found.")

st.subheader("📄 Files")
files = get_all_files()
if files:
    for file in files:
        file_url = f"https://drive.google.com/file/d/{file['id']}/view"
        st.markdown(f"📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)
else:
    st.write("No files found.")

