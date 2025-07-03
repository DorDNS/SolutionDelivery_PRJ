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
from PIL import Image as PILImage
import io
import mimetypes
from threading import Thread

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

        cursor.execute("SELECT (Height*Width) AS Size FROM Image")
        sizes = cursor.fetchall()

        cursor.execute("SELECT Contrast_level FROM Image")
        constrasts = cursor.fetchall()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

    return JsonResponse({
        "total_images": count,
        "anotations_balance": {"empty_count": empty_count, "full_count" : full_count, "no_labeled_count": no_labeled_count,
        "Avg_RGB": {"Avg_R": Avg_R, "Avg_G": Avg_G, "Avg_B": Avg_B},
        "Sizes": sizes,
        "Contrasts": constrasts
        }
    })

def locations_img(request):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try :
        query = """
        SELECT Location.Id_Location, Location.latitude, Location.Longitude, Location.city, Location.id_image, Image.Status
        FROM Location
        JOIN Image ON Location.id_image = Image.Id_Image
        """
        cursor.execute(query)
        results = cursor.fetchall()
        data = [
            {
                'id_location': row[0],
                'latitude': row[1],
                'longitude': row[2],
                'city': row[3],
                'id_image': row[4],
                'status': row[5]
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
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    image = request.FILES.get('image')
    if not image:
        return HttpResponse("No file found", status=400)

    file_name = str(uuid.uuid4()) + ".webp"
    os.makedirs(os.path.join(s.MEDIA_ROOT, "Data", "uploads"), exist_ok=True)
    file_path = os.path.join("Data", "uploads", file_name)

    image_bytes = image.read()
    try:
        image_pil = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
        image_pil.save(os.path.join(s.MEDIA_ROOT, file_path), format="WEBP", quality=80)
    except Exception as e:
        return JsonResponse({"error": f"Erreur lors de la conversion WebP : {e}"}, status=500)

    size = request.POST.get('Size')
    date_taken = request.POST.get('Date_taken') or datetime.datetime.now().strftime("%Y-%m-%d")
    status = request.POST.get('Annotation')
    latitude = request.POST.get('latitude')
    longitude = request.POST.get('Longitude')
    city = request.POST.get('City')

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT MAX(Id_Image) FROM Image")
        result = cursor.fetchone()
        id_image = 1 if result[0] is None else result[0] + 1

        cursor.execute("""
            INSERT INTO Image (
                Id_Image, File_name, File_path, Size, Height, Width, Date_taken, Status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (id_image, file_name, file_path, size, 0, 0, date_taken, int(status)))

        if latitude and longitude and city:
            cursor.execute("SELECT MAX(Id_Location) FROM Location")
            loc_id = cursor.fetchone()[0]
            id_location = 1 if loc_id is None else loc_id + 1

            cursor.execute("""
                INSERT INTO Location (Id_Location, Latitude, Longitude, City, Id_Image)
                VALUES (?, ?, ?, ?, ?)
            """, (id_location, float(latitude), float(longitude), city, id_image))

        conn.commit()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

    Thread(target=process_features_async, args=(id_image, os.path.join(s.MEDIA_ROOT, file_path))).start()

    return JsonResponse({"message": "Image uploaded", "Id_Image": id_image})

def process_features_async(id_image, full_path):
    try:
        image_cv2 = cv2.imread(full_path)
        if image_cv2 is None:
            return
        gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)

        def compute_color_histogram(image):
            return {
                col: cv2.calcHist([image], [2 - i], None, [256], [0, 256]).flatten().tolist()
                for i, col in enumerate(['red', 'green', 'blue'])
            }

        def compute_brightness_histogram(gray_image):
            return cv2.calcHist([gray_image], [0], None, [256], [0, 256]).flatten().tolist()

        def mean_color(image):
            mean = cv2.mean(image)
            return {'blue': mean[0], 'green': mean[1], 'red': mean[2]}

        def give_contrast_level(gray_image):
            return float(np.std(gray_image))

        def compute_edges(gray_image):
            edges = cv2.Canny(gray_image, 100, 200)
            return int(np.sum(edges > 0))

        height, width = gray.shape[:2]
        avg_rgb = mean_color(image_cv2)
        contrast_level = give_contrast_level(gray)
        rgb_histogram = compute_color_histogram(image_cv2)
        luminance_histogram = compute_brightness_histogram(gray)
        edges = compute_edges(image_cv2)

        db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE Image SET
                Height = ?, Width = ?, Avg_R = ?, Avg_G = ?, Avg_B = ?,
                Contrast_level = ?, RGB_Histogram = ?, Luminance_Histogram = ?, Edges = ?
            WHERE Id_Image = ?
        """, (
            height, width, avg_rgb['red'], avg_rgb['green'], avg_rgb['blue'],
            contrast_level, json.dumps(rgb_histogram), json.dumps(luminance_histogram), edges, id_image
        ))
        conn.commit()
        conn.close()

    except Exception as e:
        print(f"Erreur traitement async pour image {id_image} : {e}")


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
        print(data)
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


        # Préparer mise à jour de la localisation
        location_updates = []
        location_params = []
        if 'Latitude' in data :
            location_updates.append("Latitude = ?")
            location_params.append(data['Latitude'])

        if 'Longitude' in data:
            location_updates.append("Longitude = ?")
            location_params.append(data['Longitude'])

        if 'City' in data:
            location_updates.append("City = ?")
            location_params.append(data['City'])


        if len(image_updates) > 0:
            query_img = f"UPDATE Image SET {', '.join(image_updates)} WHERE Id_Image = ?"
            image_params.append(id)
            cursor.execute(query_img, image_params)

        if len(location_updates) > 0:
            query_loc = f"UPDATE Location SET {', '.join(location_updates)} WHERE Id_Image = ?"
            location_params.append(id)
            cursor.execute(query_loc, location_params)

        conn.commit()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()
    if len(image_updates) == 0 and len(location_updates) == 0:
        return JsonResponse({"message": f"Aucune mise à jour pour l'image"})

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
    # Si les histogrammes sont des JSON string, les parser
    if 'RGB_Histogram' in data and isinstance(data['RGB_Histogram'], str):
        data['RGB_Histogram'] = json.loads(data['RGB_Histogram'])

    if 'Luminance_Histogram' in data and isinstance(data['Luminance_Histogram'], str):
        data['Luminance_Histogram'] = json.loads(data['Luminance_Histogram'])
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

        # Déterminer le type MIME à partir de l'extension du fichier
        content_type, _ = mimetypes.guess_type(full_path)
        if content_type is None:
            content_type = "application/octet-stream"  # type générique si inconnu

        with open(full_path, 'rb') as f:
            return FileResponse(f, content_type=content_type)

    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)
    finally:
        conn.close()

def img_by_filename(request, filename):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        query = """
        SELECT
            Id_Image, File_name, File_path, Size, Height, Width,
            Date_taken, Avg_R, Avg_G, Avg_B, Contrast_level,
            RGB_Histogram, Luminance_Histogram, Edges, Status
        FROM Image
        WHERE File_name = ?
        """
        cursor.execute(query, (filename,))
        row = cursor.fetchone()

        if not row:
            return JsonResponse({"error": "Image not found"}, status=404)

        keys = [
            "Id_Image","File_name","File_path","Size","Height","Width","Date_taken",
            "Avg_R","Avg_G","Avg_B","Contrast_level","RGB_Histogram","Luminance_Histogram",
            "Edges","Status"
        ]

        data = dict(zip(keys, row))
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

def img_by_filename(request, filename):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        query = """
        SELECT
            Id_Image, File_name, File_path, Size, Height, Width,
            Date_taken, Avg_R, Avg_G, Avg_B, Contrast_level,
            RGB_Histogram, Luminance_Histogram, Edges, Status
        FROM Image
        WHERE File_name = ?
        """
        cursor.execute(query, (filename,))
        row = cursor.fetchone()

        if not row:
            return JsonResponse({"error": "Image not found"}, status=404)

        keys = [
            "Id_Image","File_name","File_path","Size","Height","Width","Date_taken",
            "Avg_R","Avg_G","Avg_B","Contrast_level","RGB_Histogram","Luminance_Histogram",
            "Edges","Status"
        ]

        data = dict(zip(keys, row))
        return JsonResponse(data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()
        
def list_images_paginated(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit
    except ValueError:
        return JsonResponse({'error': 'Invalid pagination params'}, status=400)

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM Image")
        total = cursor.fetchone()[0]

        cursor.execute("""
            SELECT Id_Image, File_name, File_path, Status
            FROM Image
            ORDER BY Id_Image ASC
            LIMIT ? OFFSET ?
        """, (limit, offset))

        rows = cursor.fetchall()
        images = [
            {"Id_Image": r[0], "File_name": r[1], "File_path": r[2], "Status": r[3]}
            for r in rows
        ]
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        conn.close()

    return JsonResponse({
        "page": page,
        "limit": limit,
        "total": total,
        "total_pages": (total + limit - 1) // limit,
        "images": images
    })



def global_histograms(request):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT Width, Height, RGB_Histogram, Luminance_Histogram, Contrast_level, Edges, Status FROM Image")
        rows = cursor.fetchall()

        total_hist_r = [0]*256
        total_hist_g = [0]*256
        total_hist_b = [0]*256
        total_luminance = [0]*256
        contrast_list = []
        count_edges_none = 0
        count_edges_vide = 0
        count_edges_pleine = 0

        # Histogramme des tailles
        size_classes = {'<500px': 0, '500-800px': 0, '800-1200px': 0, '>1200px': 0}

        # Couleurs dominantes globales
        dominant_colors = {'Rouge': 0, 'Vert': 0, 'Bleu': 0}

        # Histogramme contrastes global
        contrast_classes = {'Faible': 0, 'Moyen': 0, 'Élevé': 0}

        # Histogramme des contours
        edges_histogram = {'<5000': 0, '5000-10000': 0, '10000-50000': 0, '>50000': 0}

        #Histogramme des contours moyens
        edges_Average = {'Sans label': 0, 'Pleine': 0, 'Vide': 0}

        for width, height, rgb_json, lum_json, contrast, edges, status in rows:
            max_dim = max(width, height)
            if max_dim < 500:
                size_classes['<500px'] += 1
            elif 500 <= max_dim < 800:
                size_classes['500-800px'] += 1
            elif 800 <= max_dim < 1200:
                size_classes['800-1200px'] += 1
            else:
                size_classes['>1200px'] += 1

            rgb_hist = json.loads(rgb_json)
            lum_hist = json.loads(lum_json)

            # Sum RGB histograms (non utilisé ici mais conservé)
            total_hist_r = [x + y for x, y in zip(total_hist_r, rgb_hist['red'])]
            total_hist_g = [x + y for x, y in zip(total_hist_g, rgb_hist['green'])]
            total_hist_b = [x + y for x, y in zip(total_hist_b, rgb_hist['blue'])]

            # **Déterminer la couleur dominante pour cette image**
            for i in range(256):
                sum_r = rgb_hist['red'][i]*i
                sum_g = rgb_hist['green'][i]*i
                sum_b = rgb_hist['blue'][i]*i
            max_color = max(sum_r, sum_g, sum_b)
            if max_color == sum_r:
                dominant_colors['Rouge'] += 1
            elif max_color == sum_g:
                dominant_colors['Vert'] += 1
            else:
                dominant_colors['Bleu'] += 1

            # Sum luminance
            total_luminance = [x + y for x, y in zip(total_luminance, lum_hist)]

            # **Classer contraste en faible/moyen/élevé**
            if contrast is not None:
                contrast_list.append(contrast)
                if contrast < 30:
                    contrast_classes['Faible'] += 1
                elif 30 <= contrast < 60:
                    contrast_classes['Moyen'] += 1
                else:
                    contrast_classes['Élevé'] += 1

            # **Classer les contours en fonction du nombre d'arêtes détectées**
            if edges < 5000:
                edges_histogram['<5000'] += 1
            elif 5000 <= edges < 10000:
                edges_histogram['5000-10000'] += 1
            elif 10000 <= edges < 50000:
                edges_histogram['10000-50000'] += 1
            else:
                edges_histogram['>50000'] += 1

            # **Calcul le nombre de contours pour les labels**
            if status == 1:
                edges_Average['Pleine'] += edges
                count_edges_pleine += 1
            elif status == 0:
                edges_Average['Vide'] += edges
                count_edges_vide += 1
            else:
                edges_Average['Sans label'] += edges
                count_edges_none += 1

        avg_contrast = sum(contrast_list) / len(contrast_list) if contrast_list else None

        # Calcul des moyennes des contours par label
        if count_edges_pleine > 0:
            edges_Average['Pleine'] /= count_edges_pleine
        if count_edges_vide > 0:
            edges_Average['Vide'] /= count_edges_vide
        if count_edges_none > 0:
            edges_Average['Sans label'] /= count_edges_none

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

    return JsonResponse({
        "Size_Histogram": size_classes,
        "Dominant_Colors": dominant_colors,    
        "Contrast_Histogram": contrast_classes,
        "Average_Contrast": avg_contrast,
        "Edges_Histogram": edges_histogram,
        "Edges_Average": edges_Average
    })

@csrf_exempt
def get_constraints(request):
    """
    GET: Renvoie les contraintes de classification enregistrées dans la table Constraints.
    """
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET allowed")

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Constraints LIMIT 1")
        row = cursor.fetchone()
        if not row:
            return JsonResponse({}, status=204)

        columns = [desc[0] for desc in cursor.description]
        constraints = dict(zip(columns, row))

        # Parser les champs JSON
        if constraints.get('RGB_Histogram'):
            constraints['RGB_Histogram'] = json.loads(constraints['RGB_Histogram'])
        if constraints.get('Luminance_Histogram'):
            constraints['Luminance_Histogram'] = json.loads(constraints['Luminance_Histogram'])

        return JsonResponse(constraints)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

@csrf_exempt
def update_constraints(request):
    """
    POST/PUT: Met à jour ou insère les contraintes de classification.
    """
    if request.method not in ['POST', 'PUT']:
        return HttpResponseBadRequest("Only POST or PUT allowed")

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # Parser JSONs s'ils existent
        rgb_hist = json.dumps(data.get('RGB_Histogram')) if 'RGB_Histogram' in data else None
        lum_hist = json.dumps(data.get('Luminance_Histogram')) if 'Luminance_Histogram' in data else None

        fields = [
            'Size', 'Height', 'Width', 'Date_taken', 'Avg_R', 'Avg_G', 'Avg_B',
            'Contrast_level', 'RGB_Histogram', 'Luminance_Histogram', 'Edges'
        ]
        placeholders = ', '.join(f + ' = ?' for f in fields)
        values = [
            data.get('Size'),
            data.get('Height'),
            data.get('Width'),
            data.get('Date_taken'),
            data.get('Avg_R'),
            data.get('Avg_G'),
            data.get('Avg_B'),
            data.get('Contrast_level'),
            rgb_hist,
            lum_hist,
            data.get('Edges')
        ]

        cursor.execute("SELECT COUNT(*) FROM Constraints")
        exists = cursor.fetchone()[0]

        if exists:
            cursor.execute(f"UPDATE Constraints SET {placeholders}", values)
        else:
            cursor.execute(f"INSERT INTO Constraints ({', '.join(fields)}) VALUES ({', '.join(['?'] * len(fields))})", values)

        conn.commit()

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    finally:
        conn.close()

    return JsonResponse({"message": "Contraintes enregistrées avec succès."})

