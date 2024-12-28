import argparse
import os
import shutil
import logging
import cv2
import numpy as np

# Python script to extract multiple icons/images from a single composite image
def extract_multiple_images_from_composite(input_path, output_path):
    # Load the image
    img = cv2.imread(input_path)

    if img is None:
        print(f"Error: Could not load image from {input_path}")
        return

    # Convert to grayscale and apply adaptive thresholding to get a binary image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    adaptive_thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        11,
        2
    )

    # Detect contours
    contours, _ = cv2.findContours(adaptive_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Create output directory if it does not exist
    os.makedirs(output_path, exist_ok=True)

    # Extract the regions of interest based on the contours
    extracted_files = []

    # Iterate over the contours
    for i, contour in enumerate(contours):
        # Get the bounding box of the contour
        x, y, w, h = cv2.boundingRect(contour)

        if w > 20 and h > 20:  # Ignore small contours (noise)
            roi = img[y:y + h, x:x + w]

            # Create mask for transparency
            mask = np.zeros((h, w), dtype=np.uint8)
            cv2.drawContours(mask, [contour - [x, y]], -1, (255), thickness=cv2.FILLED)
            roi_transparent = cv2.bitwise_and(roi, roi, mask=mask)

            # Save the extracted icon
            img_path = os.path.join(output_path, f"icon_{i + 1}.png")
            cv2.imwrite(img_path, roi_transparent)
            extracted_files.append(img_path)

    # Optionally zip the output folder
    zip_file_path = f"{output_path}.zip"
    shutil.make_archive(output_path, 'zip', output_path)

    print(f"Extraction complete. Saved {len(extracted_files)} icons.")
    print(f"Icons saved in: {output_path}")
    print(f"Download ZIP: {zip_file_path}")

if __name__ == "__main__":
    # Set up argument parser
    parser = argparse.ArgumentParser(prog="extract_icons",usage='python %(prog)s <image path> <output directory>',description="Extract icons from an image.")
    parser.print_help()
    parser.add_argument("image_path", type=str, help="Path to the input image.")
    parser.add_argument("output_dir", type=str, help="Directory to save extracted icons.")

    # Parse arguments
    args = parser.parse_args()

    # Check if arguments are provided
    if not args.image_path or not args.output_dir:
        parser.error("Both <image path> and <output directory> arguments are required.")

    parser.print_help()
    # Run the extraction function
    extract_multiple_images_from_composite(args.image_path, args.output_dir)