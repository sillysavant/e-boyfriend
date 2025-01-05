import json

def read_json_file(file_path: str):
    """Reads JSON content from a file."""
    with open(file_path, "r") as file:
        return json.load(file)