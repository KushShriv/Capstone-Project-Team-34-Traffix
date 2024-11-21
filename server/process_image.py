import cv2
import numpy as np
import csv
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(filename='logs/process_image.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Define a function to process images for each client
def process_client_image(client_image_path, output_csv_path):
    # Load the uploaded image
    img = cv2.imread(client_image_path)
    if img is None:
        logging.error(f'Failed to load image at {client_image_path}.')
        return

    logging.info(f'Image loaded successfully from {client_image_path}.')

    # Convert image to HSV (Hue, Saturation, Value)
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Define the center of the junction (adjust these coordinates if needed)
    center_x, center_y = 964, 472

    # Define radii for the concentric circles
    radii = [150, 300, 450]

    # Draw the concentric circles (not displayed)
    output_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    for radius in radii:
        cv2.circle(output_image, (center_x, center_y), radius, (255, 0, 0), 2)

    # Define color ranges for detection
    color_ranges = {
        4: ([0, 70, 50], [10, 255, 255]),  # Deep red
        3: ([170, 70, 50], [180, 255, 255]),  # Red
        2: ([20, 100, 100], [30, 255, 255]),  # Yellow
        1: ([35, 100, 100], [85, 255, 255])  # Green
    }

    # Function to detect color within a range and return a binary mask
    def detect_color(hsv_img, color_range):
        lower, upper = map(np.array, color_range)
        return cv2.inRange(hsv_img, lower, upper)

    # Extract regions based on direction and distance zone (near, little far, far)
    def extract_roi(hsv_img, center, direction, zone):
        h, w = hsv_img.shape[:2]
        cx, cy = center
        d = int(min(h, w) / 6)  # Distance step for 'near', 'little far', 'far'
        if direction == 'top':
            if zone == 'near':
                return hsv_img[cy - d:cy, cx - w // 4:cx + w // 4]
            elif zone == 'little far':
                return hsv_img[cy - 2*d:cy - d, cx - w // 4:cx + w // 4]
            elif zone == 'far':
                return hsv_img[cy - 3*d:cy - 2*d, cx - w // 4:cx + w // 4]
        elif direction == 'right':
            if zone == 'near':
                return hsv_img[cy - h // 4:cy + h // 4, cx + 20:cx + d - 20]
            elif zone == 'little far':
                return hsv_img[cy - h // 4:cy + h // 4, cx + d + 20:cx + 2*d - 20]
            elif zone == 'far':
                return hsv_img[cy - h // 4:cy + h // 4, cx + 2*d + 20:cx + 3*d - 20]
        elif direction == 'bottom':
            if zone == 'near':
                return hsv_img[cy:cy + d, cx - w // 4:cx + w // 4]
            elif zone == 'little far':
                return hsv_img[cy + d:cy + 2*d, cx - w // 4:cx + w // 4]
            elif zone == 'far':
                return hsv_img[cy + 2*d:cy + 3*d, cx - w // 4:cx + w // 4]
        elif direction == 'left':
            if zone == 'near':
                return hsv_img[cy - h // 4:cy + h // 4, cx - d + 20:cx - 20]
            elif zone == 'little far':
                return hsv_img[cy - h // 4:cy + h // 4, cx - 2*d + 20:cx - d - 20]
            elif zone == 'far':
                return hsv_img[cy - h // 4:cy + h // 4, cx - 3*d + 20:cx - 2*d - 20]

        return hsv_img  # Default case

    # Function to label traffic
    def label_traffic(hsv_img, center):
        labels = np.zeros((3, 4), dtype=int)
        directions = ['top', 'right', 'bottom', 'left']
        zones = ['near', 'little far', 'far']

        for i, direction in enumerate(directions):
            for j, zone in enumerate(zones):
                roi = extract_roi(hsv_img, center, direction, zone)
                for label, (lower, upper) in color_ranges.items():
                    if detect_color(roi, (lower, upper)).any():
                        labels[j, i] = label
                        logging.info(f'Detected {label} in {direction} zone {zone}.')
                        break
        return labels

    # Center of the image (the intersection)
    center = (img.shape[1] // 2, img.shape[0] // 2)

    # Label the traffic and log the result
    result = label_traffic(hsv, center)

    # Flatten the result matrix to a single line
    result_flat = result.flatten()

    # Write the zeros line and then the flattened result to the CSV file
    num_zeros = result_flat.size
    zeros_line = [0] * num_zeros

    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(zeros_line)   # Write the line of zeros
        writer.writerow(result_flat)  # Write the actual result

    logging.info(f'Output saved to {output_csv_path}')

# Path to the directory containing images
image_folder = os.getenv('IMAGE_FOLDER') 

# Get all image files in the directory
client_images = [
    os.path.join(image_folder, f) 
    for f in os.listdir(image_folder) 
    if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))
]

# Process each client image
for i, client_image in enumerate(client_images):
    output_csv_path = f'temp/density/density_client{i + 1}.csv'
    process_client_image(client_image, output_csv_path)
