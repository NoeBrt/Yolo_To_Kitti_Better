import os
import shutil
from PIL import Image
import argparse
from tqdm import tqdm
import json
from collections import defaultdict
from pathlib import Path


def verify_conversion(original_folders, converted_folders, folder_type="labels") -> dict:
    """
    Verifies that files were converted/copied correctly by comparing source and destination folders.

    This function performs several checks:
    1. Counts files in both source and destination folders
    2. Ensures all expected files are present
    3. For labels, verifies content integrity
    4. For images, checks if they can be opened (basic corruption check)

    Args:
        original_folders: List of source folder paths
        converted_folders: List of destination folder paths
        folder_type: Type of content being verified ("labels" or "images")

    Returns:
        Dictionary containing verification results and statistics
    """
    verification_results = defaultdict(dict)

    for idx, (src_folder, dst_folder) in enumerate(zip(original_folders, converted_folders)):
        print(f"\nVerifying {folder_type} for set {idx + 1}:")
        print(f"Source: {src_folder}")
        print(f"Destination: {dst_folder}")

        # Get file lists
        src_files = set(f for f in os.listdir(src_folder)
                        if f.endswith('.txt' if folder_type == "labels" else ('.png', '.jpg')))
        dst_files = set(f for f in os.listdir(dst_folder)
                        if f.endswith('.txt' if folder_type == "labels" else ('.png', '.jpg')))

        # Store counts
        verification_results[idx] = {
            "source_count": len(src_files),
            "destination_count": len(dst_files),
            "missing_files": src_files - dst_files,
            "unexpected_files": dst_files - src_files,
            "verification_errors": []
        }

        # Verify file integrity
        print(f"Verifying file integrity...")
        for filename in tqdm(dst_files):
            try:
                if folder_type == "images":
                    # Try to open the image to verify it's not corrupted
                    image_path = os.path.join(dst_folder, filename)
                    with Image.open(image_path) as img:
                        img.verify()
                else:
                    # For labels, verify the file has content and is properly formatted
                    label_path = os.path.join(dst_folder, filename)
                    with open(label_path, 'r') as f:
                        lines = f.readlines()
                        if not lines:
                            verification_results[idx]["verification_errors"].append(
                                f"{filename}: Empty label file")
                            continue

                        # Verify KITTI format (15 space-separated values per line)
                        for line_num, line in enumerate(lines, 1):
                            parts = line.strip().split()
                            if len(parts) != 15:
                                verification_results[idx]["verification_errors"].append(
                                    f"{filename}:{line_num}: Invalid KITTI format")

            except Exception as e:
                verification_results[idx]["verification_errors"].append(
                    f"{filename}: {str(e)}")

    return verification_results


def print_verification_report(verification_results: dict, folder_type: str) -> None:
    """
    Prints a detailed report of the verification results.

    This function provides a comprehensive summary of the verification process,
    highlighting any discrepancies or issues that were found.
    """
    print(f"\n=== {folder_type.title()} Verification Report ===")

    all_passed = True
    for idx, results in verification_results.items():
        print(f"\nSet {idx + 1}:")
        print(f"Source files: {results['source_count']}")
        print(f"Destination files: {results['destination_count']}")

        if results['source_count'] != results['destination_count']:
            all_passed = False
            print(
                f"❌ Count mismatch! Different number of files in source and destination.")

        if results['missing_files']:
            all_passed = False
            print(f"❌ Missing files: {len(results['missing_files'])}")
            for filename in sorted(results['missing_files'])[:5]:
                print(f"  - {filename}")
            if len(results['missing_files']) > 5:
                print(f"  ... and {len(results['missing_files']) - 5} more")

        if results['unexpected_files']:
            all_passed = False
            print(
                f"❌ Unexpected files found: {len(results['unexpected_files'])}")
            for filename in sorted(results['unexpected_files'])[:5]:
                print(f"  - {filename}")
            if len(results['unexpected_files']) > 5:
                print(f"  ... and {len(results['unexpected_files']) - 5} more")

        if results['verification_errors']:
            all_passed = False
            print(
                f"❌ Integrity check failures: {len(results['verification_errors'])}")
            for error in results['verification_errors'][:5]:
                print(f"  - {error}")
            if len(results['verification_errors']) > 5:
                print(
                    f"  ... and {len(results['verification_errors']) - 5} more")

        if (results['source_count'] == results['destination_count'] and
            not results['missing_files'] and
            not results['unexpected_files'] and
                not results['verification_errors']):
            print("✅ All files verified successfully!")

    print(
        f"\nOverall Verification Status: {'✅ PASSED' if all_passed else '❌ FAILED'}")


def copy_image_file(src_path: str, dst_path: str) -> bool:
    """
    Copies an image file from source to destination path.

    Args:
        src_path: Source path of the image file
        dst_path: Destination path where the image should be copied

    Returns:
        bool: True if copy was successful, False otherwise
    """
    try:
        # Create the destination directory if it doesn't exist
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)  # copy2 preserves metadata
        return True
    except Exception as e:
        print(f"Error copying image {src_path}: {str(e)}")
        return False


def yolo_to_kitti_with_image_dimensions(yolo_folder, kitti_folder, image_folder, img_output_folder, class_mapping):
    """
    Converts YOLO format labels to KITTI format and optionally copies images.

    Args:
        yolo_folder: Directory containing YOLO labels
        kitti_folder: Directory to save KITTI labels
        image_folder: Directory containing source images
        img_output_folder: Optional directory to copy images to (None if no copying needed)
        class_mapping: Dictionary mapping class IDs to class names
    """
    if not os.path.exists(kitti_folder):
        os.makedirs(kitti_folder)

    # Create image output directory if specified
    if img_output_folder:
        os.makedirs(img_output_folder, exist_ok=True)

    # Track statistics for reporting
    processed_labels = 0
    copied_images = 0
    failed_copies = 0

    # Use tqdm to track progress over the files in the YOLO folder
    for filename in tqdm(os.listdir(yolo_folder), desc=f"Processing {yolo_folder}"):
        if filename.endswith(".txt"):
            yolo_label_path = os.path.join(yolo_folder, filename)
            kitti_label_path = os.path.join(kitti_folder, filename)
            image_path = os.path.join(
                image_folder, filename.replace(".txt", ".png"))

            if not os.path.exists(image_path):
                print(f"Image not found for label: {filename}")
                continue

            # Get image dimensions
            image = Image.open(image_path)
            image_width, image_height = image.size

            # Convert and write KITTI label
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
                    kitti_file.write(
                        f"{class_name} {truncated} {occluded} {alpha} {x_left:.2f} {y_top:.2f} {x_right:.2f} {y_bottom:.2f} 0 0 0 0 0 0 0\n")

            processed_labels += 1

            # Copy image if output directory is specified
            if img_output_folder:
                dst_image_path = os.path.join(
                    img_output_folder, os.path.basename(image_path))
                if copy_image_file(image_path, dst_image_path):
                    copied_images += 1
                else:
                    failed_copies += 1

    # Print detailed summary
    print(f"\nProcessing Summary for {yolo_folder}:")
    print(f"Labels processed: {processed_labels}")
    if img_output_folder:
        print(f"Images copied: {copied_images}")
        if failed_copies > 0:
            print(f"Failed image copies: {failed_copies}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert YOLO labels to KITTI format and optionally copy images.")
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
    # Add new argument for image output directories
    parser.add_argument(
        "-img-output",
        "--image-output-folders",
        nargs="+",
        help="Optional list of folders to copy images to.",
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

    # Check if image output folders were provided and match input folders
    if args.image_output_folders and len(args.image_output_folders) != len(args.label_folders):
        print("Error: The number of image output folders must match the number of input folders.")
        return

    # Check folder lists lengths match
    if not (len(args.label_folders) == len(args.output_folders) == len(args.image_folders)):
        print("Error: The number of input, output, and image folders must match.")
        return

    # Process each set of folders
    for idx, (yolo_folder, kitti_folder, image_folder) in enumerate(
        zip(args.label_folders, args.output_folders, args.image_folders)
    ):
        img_output_folder = args.image_output_folders[idx] if args.image_output_folders else None
        print(f"\nProcessing set {idx + 1}:")
        print(f"YOLO labels: {yolo_folder}")
        print(f"KITTI output: {kitti_folder}")
        print(f"Source images: {image_folder}")
        if img_output_folder:
            print(f"Image output: {img_output_folder}")

        yolo_to_kitti_with_image_dimensions(
            yolo_folder, kitti_folder, image_folder, img_output_folder, class_mapping
        )

    # Verify the conversion results
    print("\nVerifying conversion results...")

    # Verify labels
    label_verification = verify_conversion(
        args.label_folders,
        args.output_folders,
        folder_type="labels"
    )
    print_verification_report(label_verification, "Labels")

    # Verify images if they were copied
    if args.image_output_folders:
        image_verification = verify_conversion(
            args.image_folders,
            args.image_output_folders,
            folder_type="images"
        )
        print_verification_report(image_verification, "Images")


if __name__ == "__main__":
    main()


"""
python yolo_to_kitti.py \
    -l "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/val" \
    -o "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/KITTI_train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/KITTI_val" \
    -img "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/val" \
    -img-output "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/KITTI_train" "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/KITTI_val" \
    -map '{"0": "license_plate", "1": "Pedestrian", "2": "Cyclist"}'
"""
