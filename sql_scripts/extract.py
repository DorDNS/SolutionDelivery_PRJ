import os
import cv2
import numpy as np
import json
import random
from datetime import datetime, timedelta
from PIL import Image, ExifTags
from fractions import Fraction

def random_date():
    end = datetime.now()
    start = end - timedelta(days=30)
    random_days = random.randint(0, 30)
    return (start + timedelta(days=random_days)).strftime('%Y-%m-%d')

def random_location_paris():
    lat_offset = random.uniform(-0.025, 0.025)
    lon_offset = random.uniform(-0.035, 0.035)
    return {
        'latitude': round(48.8566 + lat_offset, 6),
        'longitude': round(2.3522 + lon_offset, 6),
        'ville': "Paris"
    }

def get_file_size_kb(image_path):
    size_bytes = os.path.getsize(image_path)
    return round(size_bytes / 1024, 2)

def extract_exif_data(image_path):
    exif_data = {}
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if exif:
            for tag, value in exif.items():
                decoded = ExifTags.TAGS.get(tag, tag)
                exif_data[decoded] = value
    except Exception as e:
        print(f"Erreur EXIF {image_path}: {e}")
    return exif_data

def get_image_date(exif_data):
    date = exif_data.get("DateTimeOriginal") or exif_data.get("DateTime")
    if date:
        return date.split(" ")[0].replace(":", "-")
    else:
        return random_date()

def _convert_to_degrees(value):
    d = float(Fraction(value[0][0], value[0][1]))
    m = float(Fraction(value[1][0], value[1][1]))
    s = float(Fraction(value[2][0], value[2][1]))
    return d + (m / 60.0) + (s / 3600.0)

def get_image_location(exif_data):
    gps_info = exif_data.get("GPSInfo")
    if gps_info:
        try:
            gps_lat = gps_info[2]
            gps_lat_ref = gps_info[1]
            gps_lon = gps_info[4]
            gps_lon_ref = gps_info[3]

            lat = _convert_to_degrees(gps_lat)
            if gps_lat_ref == 'S': lat = -lat

            lon = _convert_to_degrees(gps_lon)
            if gps_lon_ref == 'W': lon = -lon

            return {'latitude': round(lat, 6), 'longitude': round(lon, 6), 'ville': "EXIF"}
        except Exception as e:
            print(f"Erreur GPS : {e}")
            return random_location_paris()
    else:
        return random_location_paris()

def compute_color_histogram(image):
    hist_data = {}
    for i, col in enumerate(['red', 'green', 'blue']):
        hist = cv2.calcHist([image], [2 - i], None, [256], [0, 256])
        hist_data[col] = hist.flatten().tolist()
    return hist_data

def compute_brightness_histogram(gray_image):
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    return hist.flatten().tolist()

def mean_color(image):
    mean = cv2.mean(image)
    return {'blue': mean[0], 'green': mean[1], 'red': mean[2]}

def contrast_level(gray_image):
    return float(np.std(gray_image))

def process_image(image_path, image_id):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Erreur lecture image : {image_path}")
        return None

    height, width = image.shape[:2]
    exif_data = extract_exif_data(image_path)
    date = get_image_date(exif_data)
    location = get_image_location(exif_data)

    color_hist = compute_color_histogram(image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness_hist = compute_brightness_histogram(gray)
    avg_color = mean_color(image)
    contrast = contrast_level(gray)
    edges = cv2.Canny(gray, 100, 200)
    contour_count = int(np.sum(edges > 0))

    file_size_kb = get_file_size_kb(image_path)
    rel_path = os.path.relpath(image_path, start=os.getcwd())
    filename = os.path.basename(image_path)

    # Etat : "oui" si poubelle pleine, "non" si vide, sinon None
    lower_path = image_path.lower()
    if "with_label/dirty" in lower_path:
        etat = "oui"
    elif "with_label/clean" in lower_path:
        etat = "non"
    else:
        etat = None


    image_row = {
        "Id_Image": image_id,
        "Nom_fichier": filename,
        "Chemin_acces": rel_path,
        "Taille": file_size_kb,
        "Hauteur": height,
        "Largeur": width,
        "Date_taken": date,
        "Moy_R": avg_color["red"],
        "Moy_V": avg_color["green"],
        "Moy_B": avg_color["blue"],
        "Niv_contraste": contrast,
        "Histo_RVB": json.dumps(color_hist),
        "Histo_Lumi": json.dumps(brightness_hist),
        "Contours": contour_count,
        "Etat": etat
    }

    localisation_row = {
        "Id_Localisation": image_id,
        "Latitude": location["latitude"],
        "Longitude": location["longitude"],
        "Ville": location["ville"],
        "Id_Image": image_id
    }

    return image_row, localisation_row

def process_folder(root_dir):
    image = []
    localisation = []
    image_id = 1
    for subdir, dirs, files in os.walk(root_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
                image_path = os.path.join(subdir, file)
                res = process_image(image_path, image_id)
                if res:
                    image_row, localisation_row = res
                    image.append(image_row)
                    localisation.append(localisation_row)
                    image_id += 1
    return image, localisation

if __name__ == "__main__":
    data_dir = "Data"
    image, localisation= process_folder(data_dir)

    with open("image.json", "w") as f:
        json.dump(image, f, indent=4)

    with open("localisation.json", "w") as f:
        json.dump(localisation, f, indent=4)

    print("Extraction terminée")
