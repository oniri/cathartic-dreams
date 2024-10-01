import os, json


def read_file(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except IOError as e:
        return f"Error reading file: {e}"


def load_json(file_name):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(dir_path, file_name)

    with open(file_name, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data
