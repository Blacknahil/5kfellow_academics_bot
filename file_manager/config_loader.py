import json
import os
from pathlib import Path

from .drive_config_builder import generate_drive_config
from .postgres_store import ensure_table, load_db_config, save_db_config

def read_local_config(config_path:str = "config/drive_config.json"):
    with open(config_path, "r", encoding="utf-8") as f:
        config_map = json.load(f)
        return config_map
    return {}

def write_local_config(data, output_path="config/drive_config.json"):
    """
    Writes the nested config dictionary to a JSON file.
    
    Args:
        data: The dictionary returned by walker.build_tree()
        output_path: Path to the output JSON file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Configuration saved to {output_path.absolute()}")

def load_config(read_drive_status:bool, root_folder_id:str, local_path:str = "config/drive_config.json"):
    path = Path(local_path)
    use_db = os.getenv("DATABASE_URL") is not None

    if use_db:
        try:
            ensure_table()
        except Exception as e:
            print(f"⚠️ Failed to ensure PostgreSQL table: {e}")
    else:
        print("ℹ️ DATABASE_URL is not set. PostgreSQL integration is disabled.")
    
    # 1. explicit rebuild requested 
    if read_drive_status:
        print("📂 Drive reading is ENABLED.")
        config = generate_drive_config(root_folder_id)
        if use_db:
            try:
                save_db_config(config)
            except Exception as e:
                print(f"⚠️ Failed to save configuration to PostgreSQL: {e}")
        write_local_config(config, local_path)
        if use_db:
            print("✅ Configuration generated from Google Drive and saved to both local file and PostgreSQL.")
        else:
            print("✅ Configuration generated from Google Drive and saved to local file.")
        return config
    
    # 2. try Local config first 
    if path.exists():
        print("📂 Attempting to load configuration from local file...")
        try:
            config = read_local_config(local_path)
            if config:
                print("✅ Configuration loaded from local file.")
                return config
        except Exception as e:
            print(f"⚠️ Failed to read local configuration: {e}")
            
    # 3. try loading from PostgreSQL snapshot
    if use_db:
        try:
            print("📂 Attempting to load configuration from PostgreSQL...")
            config = load_db_config()
            if config:
                print("✅ Configuration loaded from PostgreSQL.")
                write_local_config(config, local_path)
                return config

        except Exception as e:
            print(f"⚠️ Failed to load configuration from PostgreSQL: {e}")
    
    # 4. Fallback to google drive if nothing is saved 
    print("⚠️ No config found or PostgreSQL DB unavailable. Reading from Google Drive...")
    config = generate_drive_config(root_folder_id)
    if use_db:
        try:
            save_db_config(config)
        except Exception as e:
            print(f"⚠️ Failed to save configuration to PostgreSQL: {e}")
    write_local_config(config, local_path)
    if use_db:
        print("✅ Configuration generated from Google Drive and saved to both local file and PostgreSQL.")
    else:
        print("✅ Configuration generated from Google Drive and saved to local file.")
    return config

    
         
    