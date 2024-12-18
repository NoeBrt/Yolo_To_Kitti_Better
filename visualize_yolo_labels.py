import cv2
import os
import random
import argparse


# Function to plot bounding box on the image
def plot_one_box(x, image, color=None, label=None, line_thickness=None):
    tl = line_thickness or round(
        0.002 * (image.shape[0] + image.shape[1]) / 2) + 1  # line/font thickness
    color = color or [random.randint(0, 255) for _ in range(3)]
    c1, c2 = (int(x[0]), int(x[1])), (int(x[2]), int(x[3]))
    cv2.rectangle(image, c1, c2, color, thickness=tl, lineType=cv2.LINE_AA)
    if label:
        tf = max(tl - 1, 1)  # font thickness
        t_size = cv2.getTextSize(label, 0, fontScale=tl / 3, thickness=tf)[0]
        c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
        cv2.rectangle(image, c1, c2, color, -1, cv2.LINE_AA)  # filled
        cv2.putText(image, label, (c1[0], c1[1] - 2), 0, tl / 3,
                    [225, 255, 255], thickness=tf, lineType=cv2.LINE_AA)

# Function to draw boxes on the image
def draw_box_on_image(image_name, classes, colors, LABEL_FOLDER, RAW_IMAGE_FOLDER, OUTPUT_IMAGE_FOLDER):
    txt_path = os.path.join(LABEL_FOLDER, '%s.txt' % (image_name))
    if image_name == '.DS_Store':
        return 0
    image_path = os.path.join(RAW_IMAGE_FOLDER, '%s.jpg' % (image_name))
    save_file_path = os.path.join(OUTPUT_IMAGE_FOLDER, '%s.jpg' % (image_name))

    source_file = open(txt_path) if os.path.exists(txt_path) else []
    image = cv2.imread(image_path)
    try:
        height, width, channels = image.shape
    except:
        print('no shape info.')
        return 0

    box_number = 0
    for line in source_file:
        staff = line.split()
        class_idx = int(staff[0])

        x_center, y_center, w, h = float(staff[1])*width, float(staff[2])*height, float(staff[3])*width, float(staff[4])*height
        x1 = round(x_center - w / 2)
        y1 = round(y_center - h / 2)
        x2 = round(x_center + w / 2)
        y2 = round(y_center + h / 2)

        plot_one_box([x1, y1, x2, y2], image, color=colors[class_idx],
                     label=classes[class_idx], line_thickness=None)

        box_number += 1

    cv2.imwrite(save_file_path, image)
    return box_number  # Return the count of boxes


# Function to collect image names and save them into a text file
def make_name_list(RAW_IMAGE_FOLDER):
    image_file_list = os.listdir(RAW_IMAGE_FOLDER)
    image_names = [os.path.splitext(image_file_name)[0] for image_file_name in image_file_list]
    return image_names

def main():
    parser = argparse.ArgumentParser(description="Add bounding boxes to images based on label files.")
    parser.add_argument(
        "--image-folder", required=True, help="Path to the folder containing raw images."
    )
    parser.add_argument(
        "--label-folder", required=True, help="Path to the folder containing yolo label files."
    )
    parser.add_argument(
        "--output-folder", required=True, help="Path to the folder where output images will be saved."
    )
    parser.add_argument(
        "--class-names", required=True, nargs='+', help="List of class names."
    )

    args = parser.parse_args()

    # Get the image names
    image_names = make_name_list(args.image_folder)

    # Randomly generate colors for each class
    random.seed(42)
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in range(len(args.class_names))]

    box_total = 0
    image_total = 0
    for image_name in image_names:
        box_num = draw_box_on_image(image_name, args.class_names, colors,
                                    args.label_folder, args.image_folder, args.output_folder)
        box_total += box_num
        image_total += 1
        print(f'Box number: {box_total}, Image number: {image_total}')


if __name__ == '__main__':
    main()


"""
python visualize_yolo_labels.py \
    --image-folder "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/images/train" \
    --label-folder "/home/noe/Desktop/Flwr-Repos/licence-plate/dataset/UC3M-LP-yolo/LP/labels/train" \
    --output-folder "./result_viz_yolo" \
  --class-names "license_plate"
"""