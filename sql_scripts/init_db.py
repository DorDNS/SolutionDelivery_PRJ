import os
import sqlite3
import subprocess

# Chemin vers la base de données (avec création du dossier si nécessaire)
db_relative_path = "../backend/src/db.sqlite3"
base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.abspath(os.path.join(base_dir, db_relative_path))
db_folder = os.path.dirname(db_path)

if not os.path.exists(db_folder):
    os.makedirs(db_folder, exist_ok=True)

# 1. Créer la base et les tables
print("Création des tables...")
with open(os.path.join(base_dir, "create_tables.sql"), "r", encoding="utf-8") as f:
    sql = f.read()

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.executescript(sql)
conn.commit()
conn.close()
print("Tables créées.\n")

# 2. Insérer les données dans les tables (à partir des CSV)
print("Insertion des données...")
subprocess.run(["python", "insert_tables.py"], cwd=base_dir, check=True)
print("Données insérées.\n")

# 3. Ajouter les contraintes de classification
print("Insertion des contraintes de classification...")
subprocess.run(["python", "insert_classification_constraints.py"], cwd=base_dir, check=True)
print("Contraintes ajoutées.")


