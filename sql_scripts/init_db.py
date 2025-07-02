import sqlite3

with open("create_tables.sql", "r", encoding="utf-8") as f:
    sql = f.read()

# Crée ou ouvre le fichier SQLite à l'emplacement cible
conn = sqlite3.connect("../backend/src/db.sqlite3")
cursor = conn.cursor()

# Exécute toutes les requêtes du script SQL
cursor.executescript(sql)

conn.commit()
conn.close()

print("Base de données initialisée avec succès.")
