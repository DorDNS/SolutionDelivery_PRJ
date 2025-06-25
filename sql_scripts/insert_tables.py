import sqlite3
import csv

def safe_int(value):
    return int(value) if value and value.upper() != 'NULL' else None

def safe_float(value):
    return float(value) if value and value.upper() != 'NULL' else None

def safe_bool(value):
    return bool(int(value)) if value and value.upper() != 'NULL' else None

conn = sqlite3.connect("../backend/src/db.sqlite3")
cur = conn.cursor()

# Charger les images
with open('./image.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute("""
            INSERT INTO Image (
                Id_Image, File_name, File_path, Size, Height, Width,
                Date_taken, Avg_R, Avg_G, Avg_B,
                Contrast_level, RGB_Histogram, Luminance_Histogram, Edges, Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            safe_int(row['Id_Image']),
            row['File_name'],
            row['File_path'],
            safe_float(row['Size']),
            safe_int(row['Height']),
            safe_int(row['Width']),
            row['Date_taken'] if row['Date_taken'] and row['Date_taken'].upper() != 'NULL' else None,
            safe_float(row['Avg_R']),
            safe_float(row['Avg_G']),
            safe_float(row['Avg_B']),
            safe_float(row['Contrast_level']),
            row['RGB_Histogram'] if row['RGB_Histogram'] and row['RGB_Histogram'].upper() != 'NULL' else None,
            row['Luminance_Histogram'] if row['Luminance_Histogram'] and row['Luminance_Histogram'].upper() != 'NULL' else None,
            safe_int(row['Edges']),
            safe_bool(row['Status'])
        ))

# Charger les localisations
with open('./localisation.csv', newline='') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        cur.execute("""
            INSERT INTO Location (
                Id_Location, Latitude, Longitude, City, Id_Image
            ) VALUES (?, ?, ?, ?, ?)
        """, (
            safe_int(row['Id_Location']),
            safe_float(row['Latitude']),
            safe_float(row['Longitude']),
            row['City'],
            safe_int(row['Id_Image'])
        ))

conn.commit()
conn.close()
