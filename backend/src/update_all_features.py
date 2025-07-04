import os
import sqlite3
from TrashMapServer.views import process_features_async
from TrashMapServer.views import call_roboflow_api
from django.conf import settings as s
import django
import time

# Initialise Django si le script est lancé en dehors du serveur
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TrashMapServer.settings')
django.setup()

# Connexion à la BDD
db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Récupérer toutes les images de la BDD
cursor.execute("SELECT Id_Image, File_path FROM Image")
rows = cursor.fetchall()
conn.close()

print(f"{len(rows)} images trouvées dans la base.")

for id_image, file_path in rows:
    full_path = os.path.join(s.MEDIA_ROOT, "Data", file_path)
    if not os.path.exists(full_path):
        print(f"Fichier non trouvé : {full_path}")
        continue
    print(f"Traitement image {id_image} ({file_path})...")
    process_features_async(id_image, full_path)
    time.sleep(0.5)  # pour ne pas surcharger l'API Roboflow (ajuste selon ta limite)

print("Mise à jour terminée pour toutes les images.")

if __name__ == "__main__":
    test_img = "/media/Data/test/02587_03.webp"
    print(call_roboflow_api(test_img))