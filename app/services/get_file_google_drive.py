import re
import requests
import os

def extract_drive_file_id(drive_url):
    """Extracts the file ID from a Google Drive URL."""
    match = re.search(r'/d/([\w-]+)', drive_url)
    if match:
        return match.group(1)
    match = re.search(r'id=([\w-]+)', drive_url)
    if match:
        return match.group(1)
    raise ValueError("Invalid Google Drive URL")

def download_pdf_from_google_drive(file_id):
    """
    Downloads a PDF file from Google Drive given its file ID.
    Returns (file_bytes, filename)
    """
    URL = os.getenv("GOOGLE_DRIVE_URL")
    session = requests.Session()
    response = session.get(URL, params={'id': file_id}, stream=True)
    if 'Content-Disposition' in response.headers:
        filename = response.headers['Content-Disposition'].split('filename=')[-1].strip('"')
    else:
        filename = f"{file_id}.pdf"
    file_bytes = response.content
    if not filename.endswith('.pdf'):
        filename += '.pdf'
    return file_bytes, filename