import os
import shutil
from sklearn.model_selection import train_test_split

def clear_directory(directory):
    """Remove all files and subdirectories in the given directory."""
    if os.path.exists(directory):
        for item in os.listdir(directory):
            item_path = os.path.join(directory, item)
            if os.path.isfile(item_path):
                os.unlink(item_path)
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)

def split_and_merge_synthetics(images_dir, labels_dir, train_dir, val_dir, train_ratio=0.8):
    """Split synthetics and merge into existing train/val dirs."""
    # Get all images (exclude PDFs)
    images = [f for f in os.listdir(images_dir) if f.endswith('.png')]
    
    # Split images
    train_imgs, val_imgs = train_test_split(images, train_size=train_ratio, random_state=42)
    
    # Copy train files
    for img in train_imgs:
        shutil.copy(os.path.join(images_dir, img), os.path.join(train_dir, 'images', img))
        label = img.replace('.png', '.txt')
        if os.path.exists(os.path.join(labels_dir, label)):
            shutil.copy(os.path.join(labels_dir, label), os.path.join(train_dir, 'labels', label))
    
    # Copy val files
    for img in val_imgs:
        shutil.copy(os.path.join(images_dir, img), os.path.join(val_dir, 'images', img))
        label = img.replace('.png', '.txt')
        if os.path.exists(os.path.join(labels_dir, label)):
            shutil.copy(os.path.join(labels_dir, label), os.path.join(val_dir, 'labels', label))

if __name__ == "__main__":
    # Paths
    synth_images = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\test_samples\images"
    synth_labels = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\test_samples\labels"
    signverod_train_images = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\signverod_yolo\train\images"
    signverod_train_labels = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\signverod_yolo\train\labels"
    signverod_val_images = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\signverod_yolo\val\images"
    signverod_val_labels = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\signverod_yolo\val\labels"
    output_dir = r"C:\Users\user\OneDrive\Desktop\MirrorMask\data\dataset"

    print(f"Output directory: {output_dir}")
    print(f"Copying train images to: {os.path.join(output_dir, 'train', 'images')}")
    print(f"Copying val images to: {os.path.join(output_dir, 'val', 'images')}")

    # Create and clear output directories
    for split in ['train', 'val']:
        clear_directory(os.path.join(output_dir, split, 'images'))
        clear_directory(os.path.join(output_dir, split, 'labels'))
        os.makedirs(os.path.join(output_dir, split, 'images'), exist_ok=True)
        os.makedirs(os.path.join(output_dir, split, 'labels'), exist_ok=True)

        print(f"Train images dir exists: {os.path.exists(os.path.join(output_dir, 'train', 'images'))}")
        print(f"Val images dir exists: {os.path.exists(os.path.join(output_dir, 'val', 'images'))}")

    # Copy SignVerOD train to dataset train (if exists)
    if os.path.exists(signverod_train_images):
        for file in os.listdir(signverod_train_images):
            if file.endswith('.png'):
                shutil.copy(os.path.join(signverod_train_images, file), os.path.join(output_dir, 'train', 'images', file))
        for file in os.listdir(signverod_train_labels):
            if file.endswith('.txt'):
                shutil.copy(os.path.join(signverod_train_labels, file), os.path.join(output_dir, 'train', 'labels', file))
        print(f"Copied SignVerOD train: {len(os.listdir(signverod_train_images))} images")
    else:
        print("Warning: SignVerOD train/images not found")

    # Copy SignVerOD val to dataset val (if exists)
    if os.path.exists(signverod_val_images):
        for file in os.listdir(signverod_val_images):
            if file.endswith('.png'):
                shutil.copy(os.path.join(signverod_val_images, file), os.path.join(output_dir, 'val', 'images', file))
        for file in os.listdir(signverod_val_labels):
            if file.endswith('.txt'):
                shutil.copy(os.path.join(signverod_val_labels, file), os.path.join(output_dir, 'val', 'labels', file))
        print(f"Copied SignVerOD val: {len(os.listdir(signverod_val_images))} images")
    else:
        print("Warning: SignVerOD val/images not found")

    # Split and merge synthetics
    if os.path.exists(synth_images):
        split_and_merge_synthetics(synth_images, synth_labels, os.path.join(output_dir, 'train'), os.path.join(output_dir, 'val'))
        print(f"Added synthetics: ~{int(len(os.listdir(synth_images)) * 0.8)} to train, ~{int(len(os.listdir(synth_images)) * 0.2)} to val")
    else:
        print("Warning: Synthetics images not found")

    # Final count
    train_count = len(os.listdir(os.path.join(output_dir, 'train', 'images')))
    val_count = len(os.listdir(os.path.join(output_dir, 'val', 'images')))
    print(f"Final dataset: Train images = {train_count}, Val images = {val_count}")