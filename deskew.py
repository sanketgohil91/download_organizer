import os
import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
import io

def get_skew_angle(image):
    """Detect the skew angle using Hough Line Transform."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150, apertureSize=3)

    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=50, maxLineGap=5)
    angles = []

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            angles.append(angle)

    return np.median(angles) if angles else 0  # Return median angle or 0 if no skew detected

def rotate_image(image, angle):
    """Rotate image by a given angle without cropping or quality loss."""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REPLICATE)

    return rotated

def deskew_pdf(input_pdf, output_pdf):
    """Extract images, deskew them without quality loss, and save to a new PDF."""
    doc = fitz.open(input_pdf)
    new_doc = fitz.open()

    for page in doc:
        new_page = new_doc.new_page(width=page.rect.width, height=page.rect.height)
        img_list = page.get_images(full=True)

        if not img_list:
            new_page.show_pdf_page(new_page.rect, doc, page.number)
            continue  # Copy original page if no images found

        for img in img_list:
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            img_ext = base_image["ext"]  # Preserve original format (JPEG, PNG, etc.)

            image = Image.open(io.BytesIO(image_bytes))
            open_cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

            angle = get_skew_angle(open_cv_image)

            if abs(angle) > 1:
                corrected_image = rotate_image(open_cv_image, angle)
                pil_corrected = Image.fromarray(cv2.cvtColor(corrected_image, cv2.COLOR_BGR2RGB))
            else:
                pil_corrected = image  # Keep original if no skew detected

            img_bytes = io.BytesIO()
            pil_corrected.save(img_bytes, format=img_ext.upper())  # Save in original format

            new_page.insert_image(new_page.rect, stream=img_bytes.getvalue())

    new_doc.save(output_pdf, deflate=False)  # Disable compression
    new_doc.close()
    doc.close()

def process_folders(base_folder):
    """Find all subfolders and process PDFs inside them."""
    for folder_name in os.listdir(base_folder):
        folder_path = os.path.join(base_folder, folder_name)
        
        if not os.path.isdir(folder_path):
            continue  # Skip if it's not a folder
        
        # Create deskewed output folder inside each subfolder
        output_folder = os.path.join(folder_path, "deskewed_pdfs")
        os.makedirs(output_folder, exist_ok=True)

        pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

        for pdf_file in pdf_files:
            input_pdf = os.path.join(folder_path, pdf_file)
            output_pdf = os.path.join(output_folder, pdf_file)

            print(f"Processing: {pdf_file} in {folder_name}")
            deskew_pdf(input_pdf, output_pdf)
            print(f"Saved corrected PDF: {output_pdf}")

# Define base directory containing all folders
base_directory = os.path.dirname(__file__)  # Change this if needed

# Run the deskewing process
process_folders(base_directory)
