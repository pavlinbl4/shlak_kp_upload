import os


def check_file(file_name: str) -> object:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, file_name)
    return os.path.isfile(file_path)


def create_dir(folder_name: str):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    folder_path = os.path.join(script_dir, folder_name)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    return folder_path


if __name__ == '__main__':
    print(create_dir("Uploaded_images"))
