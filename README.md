# YOLO to KITTI Dataset Converter

This repository contains a Python script to convert YOLO-format labels into KITTI-format labels. It is designed for datasets that include image files and YOLO label files. The script maps class IDs to custom class names and ensures compatibility with the KITTI format by utilizing the dimensions of the corresponding images.

---

## Features
- **Convert YOLO labels to KITTI format**: Handles normalized YOLO coordinates and translates them into absolute pixel coordinates using image dimensions.
- **Class mapping support**: Maps YOLO class IDs to meaningful class names as per user-defined mappings.
- **Batch processing**: Processes multiple label folders, output folders, and image folders simultaneously.
- **Command-line interface**: Provides flexibility and ease of use with argparse-based CLI.

---

## Prerequisites

### Python Dependencies
Make sure you have the following Python packages installed:
- `Pillow`
- `tqdm`
- `argparse`
- `json`

To install these dependencies, run:
```bash
pip install Pillow tqdm
```

---

## Usage

### Command
Run the script using the following command:
```bash
python yolo_to_kitti.py \
    -l "path_to_yolo_labels_folder1" "path_to_yolo_labels_folder2" \
    -o "path_to_output_kitti_folder1" "path_to_output_kitti_folder2" \
    -img "path_to_image_folder1" "path_to_image_folder2" \
    -map '{"0": "license_plate", "1": "Pedestrian", "2": "Cyclist"}'
```

### Parameters
- `-l` or `--label-folders`: List of paths to folders containing YOLO label files.
- `-o` or `--output-folders`: List of paths to folders where KITTI label files will be saved.
- `-img` or `--image-folders`: List of paths to folders containing images corresponding to the YOLO labels.
- `-map` or `--class-mapping`: JSON-formatted string to map YOLO class IDs to KITTI class names.

---

## Example

Convert YOLO labels from training and validation folders:
```bash
python yolo_to_kitti.py \
    -l "/path/to/yolo/labels/train" "/path/to/yolo/labels/val" \
    -o "/path/to/output/kitti/train" "/path/to/output/kitti/val" \
    -img "/path/to/images/train" "/path/to/images/val" \
    -map '{"0": "license_plate", "1": "Pedestrian", "2": "Cyclist"}'
```

This will:
1. Read YOLO labels and corresponding images.
2. Convert the YOLO labels into the KITTI format.
3. Save the converted labels to the specified output folders.

---

## Output Format
The converted KITTI label file will follow the standard KITTI annotation format:
```
Class_Name Truncated Occluded Alpha X_Left Y_Top X_Right Y_Bottom 3D_Dimensions Pose
```
For example:
```
license_plate 0.0 0 -1.0 45.00 60.00 100.00 120.00 0 0 0 0 0 0
```

---

## Notes
1. Ensure that image filenames match the corresponding YOLO label filenames (e.g., `image1.jpg` for `image1.txt`).
2. The script currently assumes the use of `.jpg` images. Modify the script if your dataset uses a different format.
3. Class mapping must be provided in JSON format.

---

## License
This project is licensed under the MIT License. Feel free to use and modify it as needed.
