import json
import csv

# Convertir image.json en image.csv 
with open("image.json", "r") as f:
    images = json.load(f)

with open("image.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Écrire les entêtes
    writer.writerow([
        "Id_Image", "Nom_fichier", "Chemin_acces", "Taille", "Hauteur", "Largeur",
        "Date_taken", "Moy_R", "Moy_V", "Moy_B", "Niv_contraste",
        "Histo_RVB", "Histo_Lumi", "Contours", "Etat"
    ])
    # Écrire les lignes
    for img in images:
        etat_val = img.get("Etat")
        if etat_val is None:
            etat_csv = "NULL"   
        elif isinstance(etat_val, str):
            if etat_val.lower() == "oui":
                etat_csv = 1
            elif etat_val.lower() == "non":
                etat_csv = 0
            else:
                etat_csv = "NULL"
        writer.writerow([
            img["Id_Image"],
            img["Nom_fichier"],
            img["Chemin_acces"],
            img["Taille"],
            img["Hauteur"],
            img["Largeur"],
            img["Date_taken"],
            img["Moy_R"],
            img["Moy_V"],
            img["Moy_B"],
            img["Niv_contraste"],
            img["Histo_RVB"],
            img["Histo_Lumi"],
            img["Contours"],
            etat_csv
        ])


# Convertir localisation.json en localisation.csv 
with open("localisation.json", "r") as f:
    localisations = json.load(f)

with open("localisation.csv", "w", newline="") as csvfile:
    writer = csv.writer(csvfile)
    # Écrire les entêtes
    writer.writerow(["Id_Localisation", "Latitude", "Longitude", "Ville", "Id_Image"])
    # Écrire les lignes
    for loc in localisations:
        writer.writerow([
            loc["Id_Localisation"],
            loc["Latitude"],
            loc["Longitude"],
            loc["Ville"],
            loc["Id_Image"]
        ])

