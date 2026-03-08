from dataclasses import dataclass
import json
from telegram import ReplyKeyboardMarkup
from constants import BOOK_CLUB_DEPARTMENT_KEY,DEPARTMENTS

@dataclass
class FileSent:
    telegram_file_id : str
    status: bool

@dataclass
class DriveFile:
    name :str
    drive_id : str

def get_files(
    department: str, 
    year: str,
    semester: str, 
    stream:str,
    subject: str, 
    material_type: str,
    config_map) -> dict[str,DriveFile]:
    
    
    print("fetching file for: department=", department,
          " year=", year,
          " semester=", semester,
          " stream=", stream,
          " subject=", subject,
          " material_type=", material_type)
    
    node = config_map[department][year][semester]

    if stream:
        node = node[stream]

    node = node[subject][material_type]
    files = {}
    for key, value in node.items():
        files[key]= (DriveFile(name=key, drive_id=value))
    return files


def load_config_map(config_path:str = "config/drive_config.json"):
    with open(config_path, "r") as f:
        config_map = json.load(f)
        return config_map
    return {}

    
    
    
    
# ---------------- KEYBOARD ---------------- #

def make_keyboard(options, cols=2, back=True):
    keyboard, row = [], []

    for opt in options:
        row.append(opt)
        if len(row) == cols:
            keyboard.append(row)
            row = []

    if row:
        keyboard.append(row)

    if back:
        keyboard.append(["⬅️ Back"])

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def extract_book_club_files(config_map) -> dict[str, DriveFile]:
    node = config_map.get(DEPARTMENTS[BOOK_CLUB_DEPARTMENT_KEY], {})
    if not isinstance(node, dict) or not node:
        return {}

    files = {}
    for name, drive_id in node.items():
        if not isinstance(name, str) or not isinstance(drive_id, str):
            continue
        files[name] = DriveFile(name=name, drive_id=drive_id)

    return files