import TrashMapServer.settings as s
import TrashMapServer.model_classification as models
from django.http import FileResponse
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, FileResponse, HttpResponseBadRequest
import sqlite3
import os
import json

def dashboard(request):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM Image")
        count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Image WHERE Status=0")
        empty_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Image WHERE Status=1")
        full_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM Image WHERE Status is Null")
        no_labeled_count = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(Avg_R), AVG(Avg_G), AVG(Avg_B) FROM Image")
        Avg_R, Avg_G, Avg_B = cursor.fetchone()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

    return JsonResponse({
        "total_images": count,
        "anotations_balance": {"empty_count": empty_count, "full_count" : full_count, "no_labeled_count": no_labeled_count,
        "Avg_RGB": {"Avg_R": Avg_R, "Avg_G": Avg_G, "Avg_B": Avg_B}
        }
    })

def locations_img(request):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try :
        query = """
        SELECT Location.Id_Location , Location.Latitude, Location.Longitude, Location.city, Location.id_image
        FROM Location
        """
        cursor.execute(query)
        results = cursor.fetchall()
        data = [
            {
                'id_location': row[0],
                'latitude': row[1],
                'longitude': row[2],
                'city': row[3],
                'id_image': row[4]
            }
            for row in results
        ]
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()
    return JsonResponse(data, safe=False)

def upload_img(request):
    if (request.method != 'POST'):
        return HttpResponse("Method not autorized", status=405)

    uploaded_file = request.FILES.get('image') # a verifier
    if not uploaded_file:
        return HttpResponse("No file found", status=400)

    if not uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return HttpResponse("Format de fichier non supporté", status=400)

    #A faire : Extraire Location depuis métadonnées ou corps de requête
    return HttpResponse("Upload en cours (à compléter)")


def predict_img(request):
    return HttpResponse(models.predict())


def modify_img(request, id):
    if request.method not in ['POST', 'PUT']:
        return HttpResponseBadRequest("Seules les requêtes POST ou PUT sont autorisées.")

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Corps de requête JSON invalide"}, status=400)

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Vérifier que l'image existe
        cursor.execute("SELECT Id_Image FROM Image WHERE Id_Image = ?", (id,))
        if cursor.fetchone() is None:
            return JsonResponse({"error": f"Image {id} non trouvée"}, status=404)

        # Préparer les champs modifiables
        image_updates = []
        image_params = []
        if 'Date_taken' in data:
            image_updates.append("Date_taken = ?")
            image_params.append(data['Date_taken'])

        if 'Edges' in data:
            image_updates.append("Edges = ?")
            image_params.append(data['Edges'])

        if 'Status' in data:
            image_updates.append("Status = ?")
            image_params.append(int(data['Status']))  # booléen 0/1

        if image_updates:
            query_img = f"UPDATE Image SET {', '.join(image_updates)} WHERE Id_Image = ?"
            image_params.append(id)
            cursor.execute(query_img, image_params)

        # Préparer mise à jour de la localisation
        location_updates = []
        location_params = []
        if 'Latitude' in data:
            location_updates.append("Latitude = ?")
            location_params.append(data['Latitude'])

        if 'Longitude' in data:
            location_updates.append("Longitude = ?")
            location_params.append(data['Longitude'])

        if 'City' in data:
            location_updates.append("City = ?")
            location_params.append(data['City'])

        if location_updates:
            query_loc = f"UPDATE Location SET {', '.join(location_updates)} WHERE Id_Image = ?"
            location_params.append(id)
            cursor.execute(query_loc, location_params)

        conn.commit()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

    return JsonResponse({"message": f"Image {id} mise à jour avec succès."})


def predict_map(request):
    return HttpResponse("Prédiction de carte à faire")


def img_detail(request, id):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    query = """
    SELECT * FROM Location
    JOIN Image ON Location.Id_Image = Image.Id_Image
    WHERE Location.Id_Image = ?
    """
    try :
        cursor.execute(query, (id,))
        row = cursor.fetchone()
        if not row:
            return HttpResponse("Image not found", status=404)

        # adapter si les colonnes changent
        columns = [desc[0] for desc in cursor.description]
        data = dict(zip(columns, row))
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()
    conn.close()
    return JsonResponse(data)

def get_img(request, id):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT File_path FROM Image WHERE Id_Image = ?", (id,))
        result = cursor.fetchone()
        if not result:
            return HttpResponse("Image not found", status=404)

        relative_path = result[0]
        full_path = os.path.join(s.MEDIA_ROOT, relative_path)

        if not os.path.exists(full_path):
            return HttpResponse("Image file missing", status=404)

        return FileResponse(open(full_path, 'rb'), content_type='image/jpeg')

    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    finally:
        conn.close()
