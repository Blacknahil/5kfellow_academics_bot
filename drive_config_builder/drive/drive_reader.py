
from googleapiclient.errors import HttpError

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
    try:
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q = query,
            fields = "files(id, name, mimeType)"
        ).execute()
        items = results.get('files', [])
        return items
    
    except HttpError as error:
        print(f"An error occurred: {error}")
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