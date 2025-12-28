# │   - entry point
# │   - loads authenticated google drive services 
# │   - calls recursive builder
# │   - saves final JSON

from auth.auth_manager import get_authenticated_drive_service
from builder.config_builder import write_config
from drive.walker import build_tree
from dotenv import load_dotenv
import os

load_dotenv()
ROOT_FOLDER_ID = os.getenv("GOOGLE_DRIVE_ROOT_FOLDER_ID")


def generate_drive_config(root_folder_id, output_path="output/drive_config.json"):
    '''
    Runs the full pipeline: authenticate → crawl drive → write config.
    This is the entry point you will call from bot.py.
    
    :param root_folder_id: ID of the root folder to start building the tree from
    :param output_file: Path to the output JSON file
    '''
    drive_service = get_authenticated_drive_service()
    drive_tree = build_tree(drive_service, root_folder_id)
    write_config(drive_tree, output_path)

# if __name__ =="__main__":
#     # Example usage
#     OUTPUT_PATH = "output/drive_config.json"
    
#     generate_drive_config(ROOT_FOLDER_ID, OUTPUT_PATH)


