import pandas as pd
import os
import ast
import shutil

# At the top of convert_to_yolo.py
base_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), 'data', 'signverod')
output_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), 'data', 'signverod_yolo')
images_dir = os.path.join(base_dir, 'images')
image_ids_csv = os.path.join(base_dir, 'image_ids.csv')
train_csv = os.path.join(base_dir, 'train.csv')
test_csv = os.path.join(base_dir, 'test.csv')

# Create output folders
for split in ['train', 'val']:
    os.makedirs(os.path.join(output_dir, split, 'images'), exist_ok=True)
    os.makedirs(os.path.join(output_dir, split, 'labels'), exist_ok=True)

# Load image metadata (id to filename map)
image_df = pd.read_csv(image_ids_csv)
id_to_file = dict(zip(image_df['id'], image_df['file_name']))

# Function to convert one split (train or val)
def convert_split(annotations_csv, split_name):
    df = pd.read_csv(annotations_csv)
    # Group annotations by image_id
    grouped = df.groupby('image_id')
    
    for image_id, group in grouped:
        file_name = id_to_file.get(image_id)
        if not file_name:
            print(f"Warning: Image ID {image_id} not found in image_ids.csv")
            continue
        
        # Copy image to output
        src_img = os.path.join(images_dir, file_name)
        dst_img = os.path.join(output_dir, split_name, 'images', file_name)
        if os.path.exists(src_img):
            shutil.copy(src_img, dst_img)
        else:
            print(f"Warning: Image {file_name} not found")
            continue
        
        # Create label file
        label_path = os.path.join(output_dir, split_name, 'labels', file_name.replace('.png', '.txt'))
        with open(label_path, 'w') as f:
            for _, row in group.iterrows():
                bbox_str = row['bbox']
                bbox = ast.literal_eval(bbox_str)  # Parse string to list [x_min, y_min, w, h]
                class_id = int(row['category_id']) - 1  # YOLO classes start at 0
                center_x = bbox[0] + (bbox[2] / 2)
                center_y = bbox[1] + (bbox[3] / 2)
                width = bbox[2]
                height = bbox[3]
                f.write(f"{class_id} {center_x} {center_y} {width} {height}\n")

# Convert train and val (using test.csv as val)
convert_split(train_csv, 'train')
convert_split(test_csv, 'val')

print("Conversion complete! Check ./signverod_yolo for folders.")