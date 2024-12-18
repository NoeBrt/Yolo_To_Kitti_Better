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
## Process

### You Have a Dataset with YOLO Labels
In YOLO format, each label file (e.g., `0000.txt`) contains lines of annotation in the following structure:
```
<class_id> <x_center> <y_center> <width> <height>
```
- **`class_id`**: The class index (e.g., `0` for `license_plate`).
- **`x_center`**, **`y_center`**: Normalized coordinates (values between 0 and 1) representing the center of the bounding box.
- **`width`**, **`height`**: Normalized width and height of the bounding box.

### Example
Imagine the YOLO label file `0000.txt` containing:
```
0 0.4994212962962963 0.4216820987654321 0.19328703703703703 0.12011316872427984
```
- `class_id = 0` → Corresponds to the `license_plate` class.
- `x_center = 0.499421`
- `y_center = 0.421682`
- `width = 0.193287`
- `height = 0.120113`

Assume the corresponding image `0000.jpg` has dimensions **image_width = 512**, **image_height = 384**.

### Conversion Process
To convert YOLO to KITTI, the following formulas are used:
1. **Calculate Absolute Coordinates**:
   - \( x_{\text{left}} = (x_{\text{center}} - \frac{\text{width}}{2}) \times \text{image\_width} \)
   - \( y_{\text{top}} = (y_{\text{center}} - \frac{\text{height}}{2}) \times \text{image\_height} \)
   - \( x_{\text{right}} = (x_{\text{center}} + \frac{\text{width}}{2}) \times \text{image\_width} \)
   - \( y_{\text{bottom}} = (y_{\text{center}} + \frac{\text{height}}{2}) \times \text{image\_height} \)

2. **Map Class ID to Name**:
   - Use the provided `class_mapping` JSON to map `0` → `license_plate`.

### Calculation for `0000.txt`:
Using the formulas above:
- \( x_{\text{left}} = (0.499421 - \frac{0.193287}{2}) \times 512 = 257.78 \)
- \( y_{\text{top}} = (0.421682 - \frac{0.120113}{2}) \times 384 = 173.58 \)
- \( x_{\text{right}} = (0.499421 + \frac{0.193287}{2}) \times 512 = 381.48 \)
- \( y_{\text{bottom}} = (0.421682 + \frac{0.120113}{2}) \times 384 = 231.23 \)

The KITTI format line becomes:
```
license_plate 0.0 0 -1.0 257.78 173.58 381.48 231.23 0 0 0 0 0 0
```

---

## Verification

### Visualizing YOLO vs KITTI
To ensure correctness, you can visualize the bounding boxes in both formats on the image using visualize_kitti_labels.py

#### command to visualise KITTI dataset
```
python visualize_kitti_labels.py \
    --image-folder "path/to/images" \
    --kitti-folder "path/to/kitty/labels" \
    --output-folder "result_viz"
```

#### command to visualise YOLO dataset
```
python visualize_yolo_labels.py \
    --image-folder "/path/to/image" \
    --label-folder "/path/to/yolo/labels" \
    --output-folder "./result_viz_yolo" \
    --class-names "licence plate"
```
<div style="text-align: center;">
<table>
  <tr>
    <td style="text-align: center;">
      <img src="https://github.com/user-attachments/assets/055e2fc3-02e0-4f98-b5e1-a4db4d8db593" alt="KITTI Dataset Sample" width="400">
      <p>KITTI Dataset Sample</p>
    </td>
    <td style="text-align: center;">
      <img src="https://github.com/user-attachments/assets/baee6e32-c4c9-4a2e-821e-ecb2dbda9032" alt="YOLO Dataset Sample" width="400">
      <p>YOLO Dataset Sample</p>
    </td>
  </tr>
</table>
</div>

---

## Notes
1. Ensure that image filenames match the corresponding YOLO label filenames (e.g., `image1.jpg` for `image1.txt`).
2. The script currently assumes the use of `.jpg` images. Modify the script if your dataset uses a different format.
3. Class mapping must be provided in JSON format.

---

## License
This project is licensed under the MIT License. Feel free to use and modify it as needed.


