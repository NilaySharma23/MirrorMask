from faker import Faker
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import random
import os
import img2pdf

fake = Faker()

def generate_document(filename, make_pdf=False):
    # Image size (simulate A4: wider for docs)
    width, height = 800, 1200
    img = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    # In generate_document function
    assets_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), 'data', 'assets')
    signature_files = [
        os.path.join(assets_dir, 'signature1.png'),
        os.path.join(assets_dir, 'signature2.png'),
        os.path.join(assets_dir, 'signature3.png')
    ]
    photo_files = [
        os.path.join(assets_dir, 'photo1.png'),
        os.path.join(assets_dir, 'photo2.png'),
        os.path.join(assets_dir, 'photo3.png')
    ]
    font_path = os.path.join(assets_dir, 'IndieFlower-Regular.ttf')
    try:
        font = ImageFont.truetype(font_path, 20)  # Handwritten font, size 20
    except Exception as e:
        print(f"Font error: {e}, using default font")
        font = ImageFont.load_default()

    # List to collect ground truth bboxes (for YOLO .txt)
    labels = []

    # Add fake name
    name = fake.name()
    name_x = random.randint(50, 150)
    name_y = random.randint(50, 150)
    name_text = f"Name: {name}"
    draw.text((name_x, name_y), name_text, fill=(0, 0, 0), font=ImageFont.load_default())

    # Add handwritten initials
    initials = ''.join([n[0] for n in name.split() if n])
    initials_x = random.randint(50, 150)
    initials_y = name_y + random.randint(40, 60)
    draw.text((initials_x, initials_y), f"Initials: {initials}", fill=(0, 0, 0), font=font)
    text_bbox = draw.textbbox((initials_x, initials_y), f"Initials: {initials}", font=font)
    bbox = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
    center_x = (bbox[0] + bbox[2]) / 2 / width
    center_y = (bbox[1] + bbox[3]) / 2 / height
    w_norm = (bbox[2] - bbox[0]) / width
    h_norm = (bbox[3] - bbox[1]) / height
    labels.append(f"1 {center_x} {center_y} {w_norm} {h_norm}")  # Class 1: initials

    # Add fake address
    address = fake.address().replace('\n', ', ')
    address_x = random.randint(50, 150)
    address_y = initials_y + random.randint(40, 60)
    draw.text((address_x, address_y), f"Address: {address}", fill=(0, 0, 0), font=ImageFont.load_default())

    # Add fake Aadhaar
    aadhaar = fake.numerify('#### #### ####')
    aadhaar_x = random.randint(50, 150)
    aadhaar_y = address_y + random.randint(40, 60)
    draw.text((aadhaar_x, aadhaar_y), f"Aadhaar: {aadhaar}", fill=(0, 0, 0), font=ImageFont.load_default())
    # Label Aadhaar (class 4)
    text_bbox = draw.textbbox((aadhaar_x, aadhaar_y), f"Aadhaar: {aadhaar}", font=ImageFont.load_default())
    bbox = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
    center_x = (bbox[0] + bbox[2]) / 2 / width
    center_y = (bbox[1] + bbox[3]) / 2 / height
    w_norm = (bbox[2] - bbox[0]) / width
    h_norm = (bbox[3] - bbox[1]) / height
    labels.append(f"4 {center_x} {center_y} {w_norm} {h_norm}")  # Class 4: aadhar

    # Add fake phone
    phone = fake.numerify('##########')  # 10-digit phone
    phone_x = random.randint(50, 150)
    phone_y = aadhaar_y + random.randint(40, 60)
    draw.text((phone_x, phone_y), f"Phone: {phone}", fill=(0, 0, 0), font=ImageFont.load_default())
    # Label phone (class 2)
    text_bbox = draw.textbbox((phone_x, phone_y), f"Phone: {phone}", font=ImageFont.load_default())
    bbox = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
    center_x = (bbox[0] + bbox[2]) / 2 / width
    center_y = (bbox[1] + bbox[3]) / 2 / height
    w_norm = (bbox[2] - bbox[0]) / width
    h_norm = (bbox[3] - bbox[1]) / height
    labels.append(f"2 {center_x} {center_y} {w_norm} {h_norm}")  # Class 2: phone

    # Add handwritten date
    date = fake.date(pattern='%d-%m-%Y')
    date_x = random.randint(50, 150)
    date_y = phone_y + random.randint(40, 60)
    draw.text((date_x, date_y), f"Date: {date}", fill=(0, 0, 0), font=font)
    text_bbox = draw.textbbox((date_x, date_y), f"Date: {date}", font=font)
    bbox = [text_bbox[0], text_bbox[1], text_bbox[2], text_bbox[3]]
    center_x = (bbox[0] + bbox[2]) / 2 / width
    center_y = (bbox[1] + bbox[3]) / 2 / height
    w_norm = (bbox[2] - bbox[0]) / width
    h_norm = (bbox[3] - bbox[1]) / height
    labels.append(f"3 {center_x} {center_y} {w_norm} {h_norm}")  # Class 3: date

    # Add 1-2 signatures with random positions and overlap chance
    num_sigs = random.randint(1, 2)
    overlap_chance = random.random() < 0.6
    for i in range(num_sigs):
        sig_file = random.choice(signature_files)
        try:
            sig_img = Image.open(sig_file).convert('RGBA')
            scale = random.uniform(0.8, 1.2)
            sig_size = (int(200 * scale), int(50 * scale))
            sig_img = sig_img.resize(sig_size, Image.Resampling.LANCZOS)
            sig_x = random.randint(100, 300)
            if i == 0 and overlap_chance:
                sig_y = random.randint(90, 110)
            else:
                sig_y = random.randint(250, 350)
            img.paste(sig_img, (sig_x, sig_y), sig_img)
            bbox = [sig_x, sig_y, sig_x + sig_size[0], sig_y + sig_size[1]]
            center_x = (bbox[0] + bbox[2]) / 2 / width
            center_y = (bbox[1] + bbox[3]) / 2 / height
            w_norm = (bbox[2] - bbox[0]) / width
            h_norm = (bbox[3] - bbox[1]) / height
            labels.append(f"0 {center_x} {center_y} {w_norm} {h_norm}")  # Class 0: signature
        except Exception as e:
            print(f"Signature error: {sig_file} - {e}")
            continue

    # Add isolated bottom-right signature (75% chance)
    if random.random() < 0.75:
        iso_sig_file = random.choice(signature_files)
        try:
            iso_sig = Image.open(iso_sig_file).convert('RGBA')
            angle = random.uniform(-15, 15)
            scale = random.uniform(0.8, 1.2)
            iso_size = (int(150 * scale), int(40 * scale))
            iso_sig = iso_sig.resize(iso_size, Image.Resampling.LANCZOS).rotate(angle, expand=True)
            iso_x, iso_y = 600, 1000
            img.paste(iso_sig, (iso_x, iso_y), iso_sig)
            bbox = [iso_x, iso_y, iso_x + iso_size[0], iso_y + iso_size[1]]
            center_x = (bbox[0] + bbox[2]) / 2 / width
            center_y = (bbox[1] + bbox[3]) / 2 / height
            w_norm = (bbox[2] - bbox[0]) / width
            h_norm = (bbox[3] - bbox[1]) / height
            labels.append(f"0 {center_x} {center_y} {w_norm} {h_norm}")
        except Exception as e:
            print(f"Isolated signature error: {iso_sig_file} - {e}")

    # Add photo (for later face detection)
    photo_file = random.choice(photo_files)
    photo_x = random.randint(100, 200)
    photo_y = random.randint(400, 450)
    try:
        photo_img = Image.open(photo_file).convert('RGB').resize((100, 100))
        img.paste(photo_img, (photo_x, photo_y))
        draw.text((photo_x, photo_y + 110), "Photo", fill=(0, 0, 0), font=ImageFont.load_default())
    except Exception as e:
        print(f"Photo error: {photo_file} - {e}")
        draw.rectangle([(photo_x, photo_y), (photo_x + 100, photo_y + 100)], outline=(255, 0, 0), width=2)
        draw.text((photo_x, photo_y + 110), "Photo", fill=(0, 0, 0), font=ImageFont.load_default())
    # Label photo (class 5)
    photo_bbox = [photo_x, photo_y, photo_x + 100, photo_y + 100]
    center_x = (photo_bbox[0] + photo_bbox[2]) / 2 / width
    center_y = (photo_bbox[1] + photo_bbox[3]) / 2 / height
    w_norm = (photo_bbox[2] - photo_bbox[0]) / width
    h_norm = (photo_bbox[3] - photo_bbox[1]) / height
    labels.append(f"5 {center_x} {center_y} {w_norm} {h_norm}")  # Class 5: photo

    # Save PNG
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img.save(filename)
    print(f"Generated PNG: {filename}")

    return labels, img

if __name__ == "__main__":
    root_dir = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')), 'data')
    images_dir = os.path.join(root_dir, 'test_samples', 'images')
    labels_dir = os.path.join(root_dir, 'test_samples', 'labels')
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(labels_dir, exist_ok=True)
    for i in range(50):  # Generate 50 samples
        filename = os.path.join(images_dir, f'sample_{i+1}.png')
        make_pdf = (i % 4 == 0)  # PDF every 4th sample
        labels, generated_img = generate_document(filename, make_pdf)
        label_filename = os.path.join(labels_dir, f'sample_{i+1}.txt')
        with open(label_filename, 'w') as f:
            f.write('\n'.join(labels))
        print(f"Generated labels: {label_filename}")
        if make_pdf:
            pdf_filename = filename.replace('.png', '.pdf')
            # FIXED AGAIN: Save temp PNG and use path for img2pdf
            temp_png = filename  # Already saved by generate_document
            with open(pdf_filename, 'wb') as f:
                f.write(img2pdf.convert(temp_png))  # Use file path
            print(f"Generated PDF: {pdf_filename}")