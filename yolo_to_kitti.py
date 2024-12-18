import os
from PIL import Image
import argparse
from tqdm import tqdm
import json

def yolo_to_kitti_with_image_dimensions(yolo_folder, kitti_folder, image_folder, class_mapping):
    if not os.path.exists(kitti_folder):
        os.makedirs(kitti_folder)

    # Use tqdm to track progress over the files in the YOLO folder
    for filename in tqdm(os.listdir(yolo_folder), desc=f"Converting {yolo_folder}"):
        if filename.endswith(".txt"):
            yolo_label_path = os.path.join(yolo_folder, filename)
            kitti_label_path = os.path.join(kitti_folder, filename)
            image_path = os.path.join(image_folder, filename.replace(".txt", ".jpg"))  # Change to ".jpg" if needed

            if not os.path.exists(image_path):
                print(f"Image not found for label: {filename}")
                continue

            # Get image dimensions
            image = Image.open(image_path)
            image_width, image_height = image.size

            with open(yolo_label_path, 'r') as yolo_file, open(kitti_label_path, 'w') as kitti_file:
                for line in yolo_file:
                    parts = line.strip().split()
                    class_id = int(parts[0])
                    x_center, y_center, width, height = map(float, parts[1:])

                    # Convert normalized YOLO coordinates to absolute pixel coordinates
                    x_left = (x_center - width / 2) * image_width
                    y_top = (y_center - height / 2) * image_height
                    x_right = (x_center + width / 2) * image_width
                    y_bottom = (y_center + height / 2) * image_height
                    # Map class_id to KITTI class name
                    class_name = class_mapping.get(str(class_id), "DontCare")

                    # Default KITTI fields
                    truncated = 0.0
                    occluded = 0
                    alpha = -1.0

                    # Write KITTI label
                    kitti_file.write(f"{class_name} {truncated} {occluded} {alpha} {x_left:.2f} {y_top:.2f} {x_right:.2f} {y_bottom:.2f} 0 0 0 0 0 0\n")

    print(f"Conversion completed. KITTI labels saved in '{kitti_folder}'.")

def main():
    parser = argparse.ArgumentParser(description="Convert YOLO labels to KITTI format.")
    parser.add_argument(
        "-l",
        "--label-folders",
        nargs="+",
        required=True,
        help="List of YOLO label folders to process.",
    )
    parser.add_argument(
        "-o",
        "--output-folders",
        nargs="+",
        required=True,
        help="List of KITTI label folders to save outputs.",
    )
    parser.add_argument(
        "-img",
        "--image-folders",
        nargs="+",
        required=True,
        help="List of image folders corresponding to YOLO labels.",
    )
    parser.add_argument(
        "-map",
        "--class-mapping",
        required=True,
        type=str,
        help="Class mapping in JSON format (e.g., '{\"0\": \"licence_plate\"}')",
    )
    args = parser.parse_args()

    # Parse class mapping
    try:
        class_mapping = json.loads(args.class_mapping)
    except json.JSONDecodeError as e:
        print(f"Invalid class mapping JSON: {e}")
        return

    # Check folder lists lengths match
    if not (
        len(args.label_folders) == len(args.output_folders) == len(args.image_folders)
    ):
        print("Error: The number of input, output, and image folders must match.")
        return

    # Process each set of folders
    for yolo_folder, kitti_folder, image_folder in zip(
        args.label_folders, args.output_folders, args.image_folders
    ):
        print(f"Processing: {yolo_folder} -> {kitti_folder}")
        yolo_to_kitti_with_image_dimensions(
            yolo_folder, kitti_folder, image_folder, class_mapping
        )

if __name__ == "__main__":
    main()


"""
python yolo_to_kitti.py \
    -l "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/val" \
    -o "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/KITTI_train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/KITTI_val " \
    -img "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/val" \
    -map '{"0": "license_plate", "1": "Pedestrian", "2": "Cyclist"}'
"""