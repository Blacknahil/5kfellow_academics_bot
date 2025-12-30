
from googleapiclient.errors import HttpError
import os
import io
from googleapiclient.http import MediaIoBaseDownload
import asyncio

def list_children(service, folder_id):
    '''
    Lists all files and folders inside a given Google Drive folder.
    
    :param service: Authenticated Drive service object
    :param folder_id: ID of the folder to list children from
    
    Returns: List of dictionaries with keys:
            - id
            - name
            - mimeType
    '''
    query = f"'{folder_id}' in parents and trashed = false"
    items = []
    page_token = None
    try:
        while True:
            response  = service.files().list(
                q = query,
                fields = "nextPageToken, files(id, name, mimeType)",
                pageToken = page_token
            ).execute()
            items.extend(response.get('files', []))
            page_token = response.get('nextPageToken', None)
            if not page_token:
                break
            
        return items
    
    except HttpError as error:
        print(f"An error occurred: {error}")
        print(f"Failed while listing children of folder ID: {folder_id}")
        return []


def get_file_url(file_id):
    '''
    Builds a direct URL to access a Google Drive view url for a file.
    '''
    return f"https://drive.google.com/file/d/{file_id}/view"

def is_folder(item):
    '''
    Checks if a given item is a folder based on its mime type.
    '''
    return item.get("mimeType") == "application/vnd.google-apps.folder"

def _download_file_sync(service, file_id, destination_path = "temp_downloads"):
    '''
    Downloads a file from Google Drive to a local destination.An actual blocking download logic.
    
    :param service: Authenticated Drive service object
    :param file_id: ID of the file to download
    :param destination_path: Local path to save the downloaded file
    '''
    
    try:
        os.makedirs(destination_path, exist_ok = True)
        
        # get file metadata 
        metadata = service.files().get(fileId = file_id, fields= "name").execute()
        file_name = metadata.get("name", f"{file_id}.bin")
        file_path = os.path.join(destination_path, file_name)
        # download the file 
        request = service.files().get_media(fileId = file_id)
        file_handler = io.FileIO(file_path, 'wb')
        downloader = MediaIoBaseDownload(file_handler, request)
        while True:
            status, done = downloader.next_chunk()
            if done:
                break
        print(f"Downloaded file ID: {file_id} to {file_path}")
        return file_path
    except Exception as e:
        print(f"Drive sync download failed for file ID: {file_id} with error: {e}")
        return None
        

async def download_file(service, file_id, destination_path):
    '''
    Async wrapper so downloads don't block the event loop.
    '''
    return await asyncio.to_thread(
        _download_file_sync, service, file_id, destination_path
    )

