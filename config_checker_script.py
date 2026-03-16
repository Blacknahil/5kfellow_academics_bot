import json

CONFIG_PATH = "config/drive_config.json"
THRESHOLD = 130


def count_long_filenames(node, path=None):
    if path is None:
        path = []

    count = 0

    if isinstance(node, dict):
        # Detect leaf nodes (filename → drive_id)
        if node and all(isinstance(v, str) for v in node.values()):
            for filename in node.keys():
                if len(filename) > THRESHOLD:
                    print(
                        f"{len(filename)} chars | {'/'.join(path)} | {filename}"
                    )
                    count += 1
        else:
            for key, value in node.items():
                count += count_long_filenames(value, path + [key])

    return count


def main():
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)

    total = count_long_filenames(config)

    print("\nSummary")
    print("-------")
    print(f"Files with name length > {THRESHOLD}: {total}")


if __name__ == "__main__":
    main()