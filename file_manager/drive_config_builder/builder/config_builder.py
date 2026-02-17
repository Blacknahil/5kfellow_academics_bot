import json
from pathlib import Path

def write_config(data, output_path="config/drive_config.json"):
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