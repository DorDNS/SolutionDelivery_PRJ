import os
import sqlite3
from PIL import Image


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
MEDIA_DIR = os.path.join(BASE_DIR, "media", "Data")
DB_PATH = os.path.join(BASE_DIR, "db.sqlite3")
print("MEDIA_DIR =", MEDIA_DIR)


VALID_EXTENSIONS = ('.jpg', '.jpeg', '.png')

def find_images_recursive(folder):
    images = []
    for root, dirs, files in os.walk(folder):
        for file in files:
            if file.lower().endswith(VALID_EXTENSIONS):
                images.append(os.path.join(root, file))
    return images

def convert_and_update(image_path):
    try:
        base_dir = os.path.dirname(image_path)
        file_name = os.path.basename(image_path)
        base_name, _ = os.path.splitext(file_name)
        new_file_name = base_name + ".webp"
        new_path = os.path.join(base_dir, new_file_name)

        # Convertir en .webp
        img = Image.open(image_path).convert("RGB")
        img.save(new_path, "webp", quality=80)

        # Supprimer l'ancienne image
        os.remove(image_path)

        # Chemins relatifs pour la BDD
        rel_old = os.path.relpath(image_path, MEDIA_DIR)
        rel_new = os.path.relpath(new_path, MEDIA_DIR)

        # Mise à jour BDD
        update_database(file_name, new_file_name, rel_new)
        print(f"{file_name} → {new_file_name}")
        return 1
    except Exception as e:
        print(f"Erreur sur {image_path} : {e}")
        return 0

def update_database(old_file_name, new_file_name, new_file_path):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Image
            SET File_name = ?, File_path = ?
            WHERE File_name = ?
        """, (new_file_name, new_file_path, old_file_name))
        conn.commit()
    except Exception as e:
        print(f"Erreur BDD pour {old_file_name} : {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("Conversion des images dans train/ et test/ vers .webp")

    total_converted = 0
    for subdir in ["train", "test"]:
        folder_path = os.path.join(MEDIA_DIR, subdir)
        images = find_images_recursive(folder_path)
        print(f"Found {len(images)} images in {subdir}/ and its subfolders.")
        for image_path in images:
            total_converted += convert_and_update(image_path)

    print(f"\nTerminé : {total_converted} images converties dans la bdd")
