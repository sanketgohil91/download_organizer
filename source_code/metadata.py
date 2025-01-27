import os
import csv
from datetime import datetime
from source_code.logger import log_message

def extract_metadata(directory, output_file):
    if not os.path.exists(directory):
        log_message("Directory does not exist", level="error")
        return

    metadata = []
    for root, _, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            file_info = os.stat(file_path)

            metadata.append({
                "File Name": file,
                "Category": os.path.basename(root),
                "File Size (KB)": round(file_info.st_size / 1024, 2),
                "Creation Date": datetime.fromtimestamp(file_info.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                "Modification Date": datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            })

    with open(output_file, "w", newline="") as csvfile:
        fieldnames = ["File Name", "Category", "File Size (KB)", "Creation Date", "Modification Date"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(metadata)

    log_message(f"Metadata extracted to {output_file}")
