import os
import cv2
import numpy as np
import json
import random
from datetime import datetime, timedelta
from PIL import Image, ExifTags
from fractions import Fraction
import pandas as pd
import math
import sqlite3
from django.conf import settings 

def extract_features_from_path(file_path):

    def get_file_size_kb(image_path):
        size_bytes = os.path.getsize(image_path)
        return round(size_bytes / 1024, 2)

    def compute_color_histogram(image):
        hist_data = {}
        for i, col in enumerate(['red', 'green', 'blue']):
            hist = cv2.calcHist([image], [2 - i], None, [256], [0, 256])
            hist_data[col] = hist.flatten().tolist()
        return hist_data

    def mean_color(image):
        mean = cv2.mean(image)
        return {'blue': mean[0], 'green': mean[1], 'red': mean[2]}

    def contrast_level(gray_image):
        return float(np.std(gray_image))

    def extract_max_indices(hist):
        if pd.isna(hist):
            return pd.Series([None, None, None], index=["Max_Red_Index", "Max_Green_Index", "Max_Blue_Index"])
        
        #hist = json.loads(hist_str)
        r = max(enumerate(hist["red"]), key=lambda x: x[1])[0]
        g = max(enumerate(hist["green"]), key=lambda x: x[1])[0]
        b = max(enumerate(hist["blue"]), key=lambda x: x[1])[0]
        return pd.Series([r, g, b], index=["Max_Red_Index", "Max_Green_Index", "Max_Blue_Index"])

    def process_image(image_path):
        image = cv2.imread(image_path)
        if image is None:
            print(f"Erreur lecture image : {image_path}")
            return None


        color_hist = compute_color_histogram(image)
        print(color_hist)
        max_indices = extract_max_indices(color_hist)
        max_blue_index = max_indices["Max_Blue_Index"]
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        avg_color = mean_color(image)
        contrast = contrast_level(gray)
        edges = cv2.Canny(gray, 100, 200)
        contour_count = int(np.sum(edges > 0))

        file_size_kb = get_file_size_kb(image_path)

        image_row = {
            "Size": file_size_kb,
            "Avg_B": avg_color["blue"],
            "Contrast_level": contrast,
            "Edges": contour_count,
            "Max_Blue_Index": max_blue_index
        }
        print("--image_row--")
        print(image_row)
        return image_row
    return process_image(file_path)


def distance_m(lat1, lon1, lat2, lon2):
    R = 6371e3  # m
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = math.sin(d_phi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(d_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

DB_PATH = os.path.join(settings.BASE_DIR, "db.sqlite3")

def is_zone_red_from_db(lat_new, lon_new, id_image_new, radius=150):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = """
            SELECT L.Latitude, L.Longitude
            FROM Location L
            JOIN Image I ON L.Id_Image = I.Id_Image
            WHERE I.Status = 1 AND L.Id_Image != ?
        """
        cursor.execute(query, (id_image_new,))
        yellow_zones = cursor.fetchall()
        conn.close()

        for lat_old, lon_old in yellow_zones:
            dist = distance_m(lat_new, lon_new, lat_old, lon_old)
            if dist < 2 * radius:
                return True  # chevauchement → rouge

        return False

    except Exception as e:
        print(f"[ERREUR] dans is_zone_red_from_db : {e}")
        return False
def generate_zone_report_from_row(lat, lon, city, id_image):
    return (
        f"Zone critique détectée !\n\n"
        f"Coordonnées : ({lat}, {lon})\n"
        f"Ville : {city}\n"
        f"Image associée : {id_image}\n\n"
        f"Plusieurs dépôts pleins se chevauchent dans cette zone."
    )