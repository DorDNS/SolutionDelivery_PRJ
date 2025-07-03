import sqlite3
import settings as s
import os

def get_constraints_from_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ClassificationConstraints LIMIT 1")
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise ValueError("Aucune contrainte trouvée dans la table.")

    columns = [
        "id", "min_size", "max_size", "min_height", "max_height", "min_width", "max_width",
        "min_avg_r", "max_avg_r", "min_avg_g", "max_avg_g", "min_avg_b", "max_avg_b",
        "min_contrast", "max_contrast", "min_edges", "max_edges"
    ]
    return dict(zip(columns, row))

def get_image_from_db(db_path, with_label=False):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = "SELECT * FROM Image"

    if (with_label):
        query="SELECT * FROM Image WHERE File_Path LIKE '/train/with_label/%' "
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()

    return rows

def classify_bin(image_data, constraints):
    # Vérifie si chaque caractéristique est dans la plage définie par les contraintes
    in_range = (
        constraints["min_size"]     <= image_data["Size"]            <= constraints["max_size"]     and
        constraints["min_height"]   <= image_data["Height"]          <= constraints["max_height"]   and
        constraints["min_width"]    <= image_data["Width"]           <= constraints["max_width"]    and
        constraints["min_avg_r"]    <= image_data["Avg_R"]           <= constraints["max_avg_r"]    and
        constraints["min_avg_g"]    <= image_data["Avg_G"]           <= constraints["max_avg_g"]    and
        constraints["min_avg_b"]    <= image_data["Avg_B"]           <= constraints["max_avg_b"]    and
        constraints["min_contrast"] <= image_data["Contrast_level"]  <= constraints["max_contrast"] and
        constraints["min_edges"]    <= image_data["Edges"]           <= constraints["max_edges"]
    )
    # recuperer uniquement les images dont le path est Data/train/with_label/clean ou Data/train/with_label/dirty


    # classifier
    edges...

    # tester l'accuracy.

    return 1 if in_range else 0

# Exemple d'utilisation
db_path = os.join(s.BASE_DIR, "db.sqlite3")

image_data = get_image_from_db(db_path, True)

constraints = get_constraints_from_db(db_path)

status = classify_bin(image_data, constraints)
print("Status =", status)
