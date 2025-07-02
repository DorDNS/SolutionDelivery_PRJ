import os
import subprocess
import sqlite3

# 1. Créer la base et les tables
print("Création des tables...")
with open(os.path.join(os.path.dirname(__file__), "create_tables.sql"), "r", encoding="utf-8") as f:
    sql = f.read()

conn = sqlite3.connect("../backend/src/db.sqlite3")
cursor = conn.cursor()
cursor.executescript(sql)
conn.commit()
conn.close()
print("Tables créées.\n")

# 2. Convertir les JSON en CSV
print("🌀 Conversion des JSON en CSV...")
subprocess.run(["python", "convert.py"], check=True)
print("Conversion terminée.\n")

# 3. Insérer les données dans les tables
print("Insertion des données...")
subprocess.run(["python", "insert_tables.py"], check=True)
print("Données insérées.\n")

# 4. Ajouter les contraintes de classification
print("Insertion des contraintes de classification...")
subprocess.run(["python", "insert_classification_constraints.py"], check=True)
print("Contraintes ajoutées.")
