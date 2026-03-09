from .auth.auth_manager import get_authenticated_drive_service
from .drive.walker import build_tree
import os

def generate_drive_config(root_folder_id, output_path="output/drive_config.json"):
    '''
    Runs the full pipeline: authenticate → crawl drive → write config.
    This is the entry point you will call from bot.py.
    
    :param root_folder_id: ID of the root folder to start building the tree from
    :param output_path: Path to the output JSON file
    '''
    if root_folder_id is None or not str(root_folder_id).strip():
        raise ValueError("Root folder ID must be provided and cannot be empty.")
    drive_service = get_authenticated_drive_service()
    drive_tree = build_tree(drive_service, root_folder_id)
    return drive_tree


