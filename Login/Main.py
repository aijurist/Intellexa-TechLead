import streamlit as st
import google.auth
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load Google Drive credentials from Streamlit Secrets
SCOPES = ["https://www.googleapis.com/auth/drive"]
creds = service_account.Credentials.from_service_account_info(dict(st.secrets["google"]), scopes=SCOPES)

# Initialize Drive API client
drive_service = build("drive", "v3", credentials=creds)

# Function to retrieve all files with pagination
@st.cache_data(ttl=600)  # Cache results for 10 minutes to optimize performance
def get_all_files():
    files = []
    page_token = None
    while True:
        results = drive_service.files().list(
            fields="nextPageToken, files(id, name)",
            pageSize=100,  # Fetch 100 files at a time for efficiency
            pageToken=page_token
        ).execute()
        files.extend(results.get("files", []))
        page_token = results.get("nextPageToken")
        if not page_token:
            break
    return files

# Function to retrieve only folders from Google Drive
@st.cache_data(ttl=600)
def get_folders():
    query = "mimeType='application/vnd.google-apps.folder' and trashed=false"
    results = drive_service.files().list(
        q=query, fields="files(id, name)"
    ).execute()
    return results.get("files", [])

# Streamlit UI
st.title("Google Drive File Viewer")

# Display files
files = get_all_files()
if files:
    st.write(f"### Found {len(files)} files:")
    for file in files:
        st.write(f"- 📄 **{file['name']}** (ID: `{file['id']}`)")
else:
    st.write("No files found.")

# Display folders
folders = get_folders()
if folders:
    st.write(f"### Found {len(folders)} folders:")
    for folder in folders:
        st.write(f"- 📁 **{folder['name']}** (ID: `{folder['id']}`)")
else:
    st.write("No folders found.")




# import streamlit as st
# from googleapiclient.discovery import build
# from google.oauth2 import service_account

# # Set up authentication
# SERVICE_ACCOUNT_FILE = "your-service-account.json"
# SCOPES = ["https://www.googleapis.com/auth/drive"]


# credentials = service_account.Credentials.from_service_account_info(st.secrets["google"])

# drive_service = build("drive", "v3", credentials=credentials)

# # Function to fetch files in a given folder
# def get_files_in_folder(folder_id):
#     query = f"'{folder_id}' in parents and trashed=false"
#     results = drive_service.files().list(q=query, fields="files(id, name, mimeType)").execute()
#     return results.get("files", [])

# # Function to get the root folder contents
# def get_files_in_root():
#     return get_files_in_folder("root")

# # Recursive function to display folders with toggle
# def display_folder_contents(folder_id, level=0):
#     files = get_files_in_folder(folder_id)

#     if not files:
#         st.write(" " * (level * 4) + "📂 No files found")

#     for file in files:
#         indent = " " * (level * 4)
#         if file["mimeType"] == "application/vnd.google-apps.folder":
#             with st.expander(f"{indent}📂 {file['name']}"):
#                 display_folder_contents(file["id"], level + 1)
#         else:
#             file_url = f"https://drive.google.com/file/d/{file['id']}/view"
#             st.markdown(f"{indent}📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)

# # UI Section
# st.title("📂 Google Drive File Explorer")

# # Display files in root folder
# st.subheader("📄 Files in Root Directory")
# root_files = get_files_in_root()

# if root_files:
#     for file in root_files:
#         if file["mimeType"] == "application/vnd.google-apps.folder":
#             with st.expander(f"📂 {file['name']}"):
#                 display_folder_contents(file["id"])
#         else:
#             file_url = f"https://drive.google.com/file/d/{file['id']}/view"
#             st.markdown(f"📄 **[{file['name']}]({file_url})**", unsafe_allow_html=True)
# else:
#     st.write("⚠️ No files found in the root directory.")
