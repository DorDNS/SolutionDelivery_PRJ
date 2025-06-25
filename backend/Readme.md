1. Création du .env :
    - Executer `python3 -m venv .env` dans le dossier './backend/'
    - source .env/bin/activate
2. Executer `pip install -r setup.txt` dans le dossier './backend/'
3. Executer `python3 manage.py runserver` dans le dossier './backend/src' pour demarrer le serveur

En plus : normalement la base de données est remplie, (pour tester la db : sqlite3 db.sqlite3 puis '.tables') si c'est pas le cas :
-> utiliser insert_tables.py
