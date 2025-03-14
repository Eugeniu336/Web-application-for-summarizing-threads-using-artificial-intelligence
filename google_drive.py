import os
import io
import streamlit as st
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# Setăm permisiunile necesare
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


def get_google_drive_service():
    """Obține un serviciu Google Drive autorizat."""
    creds = None

    # Verifică dacă există deja token-uri salvate
    if 'token.json' in os.listdir('.'):
        try:
            creds = Credentials.from_authorized_user_info(st.session_state.get('google_creds'))
        except:
            pass

    # Dacă nu există credențiale valide, utilizatorul trebuie să se autentifice
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Verificăm dacă există fișierul client_secrets.json
            if not os.path.exists('client_secrets.json'):
                st.error("Fișierul client_secrets.json nu a fost găsit. Descărcați-l din Google Cloud Console.")
                return None

            # Specificăm redirect_uri explicit pentru a se potrivi cu cel din consola Google
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                SCOPES,
                redirect_uri='localhost:8509'
            )

            # Folosim run_local_server cu port explicit
            creds = flow.run_local_server(port=8509)

        # Salvăm credențialele pentru utilizare viitoare
        st.session_state['google_creds'] = creds.to_json()

    # Construim serviciul
    return build('drive', 'v3', credentials=creds)


def list_files(service, query=None, max_results=10):
    """Listează fișierele din Google Drive care corespund căutării."""

    if query is None:
        # Căutăm doar tipurile de fișiere compatibile
        query = "mimeType='application/pdf' or mimeType='text/plain' or mimeType='application/vnd.openxmlformats-officedocument.wordprocessingml.document' or mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or mimeType='text/csv'"

    results = service.files().list(
        q=query,
        pageSize=max_results,
        fields="nextPageToken, files(id, name, mimeType)"
    ).execute()

    return results.get('files', [])


def download_file(service, file_id):
    """Descarcă un fișier din Google Drive și îl salvează temporar."""
    request = service.files().get_media(fileId=file_id)

    file_bytes = io.BytesIO()
    downloader = MediaIoBaseDownload(file_bytes, request)

    done = False
    while not done:
        status, done = downloader.next_chunk()

    file_bytes.seek(0)
    return file_bytes