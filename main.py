from source_code.file_handler import organize_files
from source_code.metadata import extract_metadata
from source_code.downloader import download_files
from source_code.logger import setup_logger
import os

def main():
    setup_logger()
    base_directory = "downloads"  # Example base directory

    # Step 1: Download files
    urls = ["https://example.com/sample1.jpg", "https://example.com/sample2.pdf"]
    temp_dir = os.path.join(base_directory, "temp")
    download_files(urls, temp_dir)

    # Step 2: Organize files
    organized_dir = os.path.join(base_directory, "organized")
    organize_files(temp_dir, organized_dir)

    # Step 3: Extract metadata
    metadata_file = os.path.join(organized_dir, "metadata.csv")
    extract_metadata(organized_dir, metadata_file)

if __name__ == "__main__":
    main()
