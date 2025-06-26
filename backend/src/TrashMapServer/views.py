import TrashMapServer.settings as s
import TrashMapServer.model_classification as models
from django.http import FileResponse
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound, FileResponse, HttpResponseBadRequest
import sqlite3
import datetime
import os
import json
import cv2
import numpy as np
from django.views.decorators.csrf import csrf_exempt
import uuid


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

@csrf_exempt
def upload_img(request):
    def compute_color_histogram(image):
        hist_data = {}
        for i, col in enumerate(['red', 'green', 'blue']):
            hist = cv2.calcHist([image], [2 - i], None, [256], [0, 256])
            hist_data[col] = hist.flatten().tolist()
        return hist_data

    def compute_brightness_histogram(gray_image):
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
        return hist.flatten().tolist()

    def mean_color(image):
        mean = cv2.mean(image)
        return {'blue': mean[0], 'green': mean[1], 'red': mean[2]}

    def give_contrast_level(gray_image):
        return float(np.std(gray_image))
    
    def compute_edges(gray_image):
        # A FAIRE !!!
        return (0)


    if (request.method != 'POST'):
        return HttpResponse("Method not autorized", status=405)

    image = request.FILES.get('image')
    __, file_ext = os.path.splitext(request.POST.get('File_name'))

    file_name = str(uuid.uuid4())+file_ext

    file_path = os.path.join("Data", "uploads", file_name)  # Pour l'enregistrement logique

    image_bytes = image.read()
    image_np = np.frombuffer(image_bytes, np.uint8)
    image_cv2 = cv2.imdecode(image_np, cv2.IMREAD_COLOR)
    gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)

    size = request.POST.get('Size')
    height = request.POST.get('Height')
    width = request.POST.get('Width')
    date_taken = request.POST.get('Date_taken') or datetime.now().strftime("%Y-%m-%d")
    avg_rgb = mean_color(image_cv2)
    contrast_level = give_contrast_level(gray)
    rgb_histogram = compute_color_histogram(image_cv2)
    luminance_histogram = compute_brightness_histogram(gray)
    edges = compute_edges(image_cv2)
    status = request.POST.get('Annotation')
    latitude = request.POST.get('Latitude')
    longitude = request.POST.get('Longitude')
    city = request.POST.get('City')

    if not image:
        return HttpResponse("No file found", status=400)

    if not image.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.pdf', '.gif')):
        return HttpResponse("Format de fichier non supporté", status=400)
    if (file_name is None or size is None or height is None or width is None):
        return HttpResponse("Missing argument(s)", status=402)

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try :
        # Générer id_image automatiquement
        cursor.execute("SELECT MAX(Id_Image) FROM Image")
        result = cursor.fetchone()
        id_image = 1 if result[0] is None else result[0] + 1
        
        query = """
            INSERT INTO Image (
                Id_Image, File_name, File_path, Size, Height, Width, Date_taken,
                Avg_R, Avg_G, Avg_B, Contrast_level, RGB_Histogram,
                Luminance_Histogram, Edges, Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        cursor.execute(query, (
            id_image, file_name, file_path, size, height, width, date_taken,
            avg_rgb["red"], avg_rgb["green"], avg_rgb["blue"], contrast_level,
            json.dumps(rgb_histogram), json.dumps(luminance_histogram),
            edges, int(status)  # SQLite n'a pas de type bool, 0 ou 1
        ))

        if latitude and longitude and city:
            cursor.execute("SELECT MAX(Id_Location) FROM Location")
            loc_id = cursor.fetchone()[0]
            id_location = 1 if loc_id is None else loc_id + 1

            query_loc = """
            INSERT INTO Location (Id_Location, Latitude, Longitude, City, Id_Image)
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(query_loc, (
                id_location, float(latitude), float(longitude), city, id_image
            ))
        cv2.imwrite(os.path.join(s.MEDIA_ROOT, file_path), image_cv2)

        conn.commit()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

    finally:
        conn.close()

    #A faire : Extraire Location depuis métadonnées ou corps de requête
    return JsonResponse({
        "file_name": file_name,
        "file_path": file_path,
        "size": size,
        "height": height,
        "width": width,
        "date_taken": date_taken,
        "avg_rgb": avg_rgb,
        "contrast_level": contrast_level,
        "rgb_histogram": rgb_histogram,
        "luminance_histogram": luminance_histogram,
        "edges": edges,
        "status": status,
        "latitude": latitude,
        "longitude": longitude,
        "city": city
    })


def predict_img(request):
    return HttpResponse(models.predict())

@csrf_exempt
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
