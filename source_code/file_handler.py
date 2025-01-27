import os
import shutil
import re
from source_code.logger import log_message

def organize_files(source_dir, dest_dir):
    if not os.path.exists(source_dir):
        log_message("Source directory does not exist", level="error")
        return

    file_types = {
        "images": [".jpg", ".jpeg", ".png", ".gif"],
        "documents": [".pdf", ".docx", ".txt"],
        "audio": [".mp3", ".wav"],
        "videos": [".mp4", ".mkv"],
    }

    os.makedirs(dest_dir, exist_ok=True)

    for filename in os.listdir(source_dir):
        file_path = os.path.join(source_dir, filename)
        if os.path.isfile(file_path):
            category = "others"
            for key, extensions in file_types.items():
                if filename.lower().endswith(tuple(extensions)):
                    category = key
                    break

            category_dir = os.path.join(dest_dir, category)
            os.makedirs(category_dir, exist_ok=True)
            shutil.move(file_path, os.path.join(category_dir, filename))
            log_message(f"Moved {filename} to {category_dir}")

    log_message("File organization completed successfully.")
