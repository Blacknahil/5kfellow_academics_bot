from dataclasses import dataclass
import json
from telegram import ReplyKeyboardMarkup

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
    config_map) -> list[DriveFile]:
    
    normalized_department = department.lower().replace(" ", "_").strip()
    normalized_year = year.lower().replace(" ", "_").strip()
    normalized_semester = semester.lower().replace(" ", "_").strip()
    normalized_stream = stream.lower().replace(" ", "_").strip() if stream else None
    normalized_subject = subject.lower().replace(" ", "_").strip()
    normalized_material_type = material_type.lower().replace(" ", "_").strip()
    
    print("fetching file for: department=", normalized_department,
          " year=", normalized_year,
          " semester=", normalized_semester,
          " stream=", normalized_stream,
          " subject=", normalized_subject,
          " material_type=", normalized_material_type)
    
    node = config_map[normalized_department][normalized_year][normalized_semester]

    if normalized_stream:
        node = node[normalized_stream]

    node = node[normalized_subject][normalized_material_type]
    files = []
    for key, value in node.items():
        files.append(DriveFile(name=key, drive_id=value))
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