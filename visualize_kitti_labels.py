import os
import argparse
import matplotlib.pyplot as plt
from PIL import Image
from tqdm import tqdm


def parse_kitti_label(label_file_path):
    """
    Parse a KITTI label file and return bounding boxes and classes.

    :param label_file_path: Path to the KITTI label file.
    :return: List of dictionaries with bounding box coordinates and class information.
    """
    bboxes = []
    with open(label_file_path, 'r') as file:
        for line in file:
            parts = line.strip().split()
            class_name = parts[0]
            bbox_left = float(parts[4])
            bbox_top = float(parts[5])
            bbox_right = float(parts[6])
            bbox_bottom = float(parts[7])

            bboxes.append({
                "class": class_name,
                "bbox": (bbox_left, bbox_top, bbox_right, bbox_bottom)
            })
    return bboxes


def visualize_kitti_labels(image_folder, kitti_folder, output_folder=None):
    """
    Visualize bounding boxes from KITTI labels on images.

    :param image_folder: Path to the folder containing images.
    :param kitti_folder: Path to the folder containing KITTI label files.
    :param output_folder: Path to save visualized images (optional). If None, display images.
    """
    if output_folder and not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Use tqdm to track progress through the KITTI label files
    for filename in tqdm(os.listdir(kitti_folder), desc="Visualizing labels"):
        if filename.endswith(".txt"):
            # Paths
            label_path = os.path.join(kitti_folder, filename)
            image_path = os.path.join(image_folder, filename.replace(".txt", ".jpg"))  # Change to ".jpg" if needed

            # Check if corresponding image exists
            if not os.path.exists(image_path):
                print(f"Image not found for label: {filename}")
                continue

            # Load image and labels
            image = Image.open(image_path)
            bboxes = parse_kitti_label(label_path)

            # Plot image and bounding boxes
            plt.figure(figsize=(10, 6))
            plt.imshow(image)
            ax = plt.gca()

            for bbox_info in bboxes:
                class_name = bbox_info["class"]
                bbox = bbox_info["bbox"]

                # Draw bounding box
                rect = plt.Rectangle(
                    (bbox[0], bbox[1]),  # Top-left corner
                    bbox[2] - bbox[0],  # Width
                    bbox[3] - bbox[1],  # Height
                    linewidth=2,
                    edgecolor="red",
                    facecolor="none"
                )
                ax.add_patch(rect)
                # Add class name
                ax.text(
                    bbox[0], bbox[1] - 5,
                    class_name,
                    color="red",
                    fontsize=10,
                    backgroundcolor="white"
                )

            # Save or display the image
            if output_folder:
                output_path = os.path.join(output_folder, filename.replace(".txt", ".png"))
                plt.savefig(output_path, bbox_inches="tight")
                plt.close()
            else:
                plt.show()


def main():
    parser = argparse.ArgumentParser(description="Visualize KITTI labels on images.")
    parser.add_argument(
        "-img",
        "--image-folder",
        required=True,
        help="Path to the folder containing images."
    )
    parser.add_argument(
        "-lbl",
        "--kitti-folder",
        required=True,
        help="Path to the folder containing KITTI label files."
    )
    parser.add_argument(
        "-o",
        "--output-folder",
        default=None,
        help="Path to save visualized images. If not specified, images will be displayed interactively."
    )
    args = parser.parse_args()

    # Call the visualization function
    visualize_kitti_labels(args.image_folder, args.kitti_folder, args.output_folder)


if __name__ == "__main__":
    main()

"""

python visualize_kitti_labels.py \
    --image-folder "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/train" \
    --kitti-folder "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/KITTI_train" \
    --output-folder "result_viz"

"""