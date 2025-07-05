import TrashMapServer.settings as s
import TrashMapServer.model_classification as models
from django.http import FileResponse, HttpResponse, JsonResponse, HttpResponseNotFound, HttpResponseBadRequest
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
import requests
from TrashMapServer import deep_model

def dashboard(request):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    COUNT(*) AS total,
                    COUNT(CASE WHEN Status = 0 THEN 1 END),
                    COUNT(CASE WHEN Status = 1 THEN 1 END),
                    COUNT(CASE WHEN Status IS NULL THEN 1 END),
                    AVG(Avg_R), AVG(Avg_G), AVG(Avg_B)
                FROM Image
            """)
            count, empty_count, full_count, no_labeled_count, Avg_R, Avg_G, Avg_B = cursor.fetchone()

            cursor.execute("SELECT (Height * Width) AS Size, Contrast_level FROM Image")
            rows = cursor.fetchall()
            sizes = [r[0] for r in rows]
            contrasts = [r[1] for r in rows]

            return JsonResponse({
                "total_images": count,
                "anotations_balance": {
                    "empty_count": empty_count,
                    "full_count": full_count,
                    "no_labeled_count": no_labeled_count,
                    "Avg_RGB": {"Avg_R": Avg_R, "Avg_G": Avg_G, "Avg_B": Avg_B},
                    "Sizes": sizes,
                    "Contrasts": contrasts
                }
            })
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def locations_img(request):
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT Location.Id_Location, Location.latitude, Location.Longitude, Location.city, Location.id_image, Image.Status
                FROM Location
                JOIN Image ON Location.id_image = Image.Id_Image
            """)
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
            return JsonResponse(data, safe=False)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        

def call_roboflow_api(image_path):
    url = "https://detect.roboflow.com/trash-detection-oeuhp/5"
    api_key = "NZsgeWVOO3DkaAwzxF4Q"

    with open(image_path, "rb") as img_file:
        response = requests.post(
            url,
            params={"api_key": api_key},
            files={"file": img_file}
        )

    if response.status_code != 200:
        print("Erreur Roboflow (fichier) :", response.status_code, response.text)
        response.raise_for_status()

    return response.json()


def crop_trash_region(image_path, detections, classes_to_keep=['Trash', 'Trash-can']):
    img = PILImage.open(image_path)
    lefts, tops, rights, bottoms = [], [], [], []

    for obj in detections.get('predictions', []):
        if obj['class'] in classes_to_keep:
            x, y, w, h = obj['x'], obj['y'], obj['width'], obj['height']
            left = int(x - w/2)
            top = int(y - h/2)
            right = int(x + w/2)
            bottom = int(y + h/2)
            lefts.append(left)
            tops.append(top)
            rights.append(right)
            bottoms.append(bottom)

    if not lefts:
        return None

    left = max(min(lefts), 0)
    top = max(min(tops), 0)
    right = min(max(rights), img.width)
    bottom = min(max(bottoms), img.height)

    cropped_img = img.crop((left, top, right, bottom))
    return cropped_img


@csrf_exempt
def upload_img(request):
    if request.method != 'POST':
        return HttpResponse("Method not allowed", status=405)

    image = request.FILES.get('image')
    if not image:
        return HttpResponse("No file found", status=400)

    # Sauvegarde image complète en WebP
    file_name = str(uuid.uuid4()) + ".webp"
    upload_dir = os.path.join(s.MEDIA_ROOT, "Data", "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join("Data", "uploads", file_name)
    full_path = os.path.join(s.MEDIA_ROOT, file_path)

    image_bytes = image.read()
    try:
        image_pil = PILImage.open(io.BytesIO(image_bytes)).convert("RGB")
        image_pil.save(full_path, format="WEBP", quality=80)
    except Exception as e:
        return JsonResponse({"error": f"Erreur lors de la conversion WebP : {e}"}, status=500)

    size = request.POST.get('Size')
    date_taken = request.POST.get('Date_taken') or datetime.datetime.now().strftime("%Y-%m-%d")
    status = request.POST.get('Annotation')
    latitude = request.POST.get('Latitude')
    longitude = request.POST.get('Longitude')
    city = request.POST.get('City')

    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Image (
                    File_name, File_path, Size, Height, Width, Date_taken, Status
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (file_name, file_path, size, 0, 0, date_taken, int(status) if status else 0))
            id_image = cursor.lastrowid

            if latitude and longitude and city:
                cursor.execute("""
                    INSERT INTO Location (Id_Location, Latitude, Longitude, City, Id_Image)
                    VALUES (?, ?, ?, ?, ?)
                """, (id_image, float(latitude), float(longitude), city, id_image))

            conn.commit()
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    # Lance le traitement asynchrone avec crop et features
    Thread(target=process_features_async, args=(id_image, full_path)).start()

    return JsonResponse({"message": "Image uploaded", "Id_Image": id_image})


def process_features_async(id_image, full_path):
    try:
        detections = call_roboflow_api(full_path)

        # --- Crop englobant Trash + Trash-can ---
        cropped_img = crop_trash_region(full_path, detections)
        if cropped_img is None:
            print(f"Aucune détection Trash/Trash-can pour image {id_image}, extraction features sur image complète.")
            cropped_img = PILImage.open(full_path)
            
        # Sauvegarder le crop
        crop_dir = os.path.join(s.MEDIA_ROOT, "Data", "crops")
        crop_file_name = f"crop_{id_image}.webp"
        crop_path = os.path.join(crop_dir, crop_file_name)
        cropped_img.save(crop_path, format="WEBP", quality=80)

        # --- Extraction des features sur le crop ---
        image_cv2 = cv2.cvtColor(np.array(cropped_img), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(image_cv2, cv2.COLOR_BGR2GRAY)

        def mean_color(img):
            mean = cv2.mean(img)
            return {'blue': mean[0], 'green': mean[1], 'red': mean[2]}

        def compute_histograms():
            return {
                'rgb': {
                    col: cv2.calcHist([image_cv2], [2 - i], None, [256], [0, 256]).flatten().tolist()
                    for i, col in enumerate(['red', 'green', 'blue'])
                },
                'luminance': cv2.calcHist([gray], [0], None, [256], [0, 256]).flatten().tolist()
            }

        height, width = gray.shape[:2]
        avg_rgb = mean_color(image_cv2)
        contrast_level = float(np.std(gray))
        edges = int(np.sum(cv2.Canny(gray, 100, 200) > 0))
        hists = compute_histograms()

        # --- Mise à jour base ---
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE Image SET
                    Height = ?, Width = ?, Avg_R = ?, Avg_G = ?, Avg_B = ?,
                    Contrast_level = ?, RGB_Histogram = ?, Luminance_Histogram = ?, Edges = ?
                WHERE Id_Image = ?
            """, (
                height, width, avg_rgb['red'], avg_rgb['green'], avg_rgb['blue'],
                contrast_level, json.dumps(hists['rgb']), json.dumps(hists['luminance']), edges, id_image
            ))
            conn.commit()

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
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT Id_Image FROM Image WHERE Id_Image = ?", (id,))
        if cursor.fetchone() is None:
            return JsonResponse({"error": f"Image {id} non trouvée"}, status=404)

        image_updates, image_params = [], []
        for field in ['Date_taken', 'Edges', 'Status']:
            if field in data:
                image_updates.append(f"{field} = ?")
                val = int(data[field]) if field == 'Status' else data[field]
                image_params.append(val)

        location_updates, location_params = [], []
        for field in ['Latitude', 'Longitude', 'City']:
            if field in data:
                location_updates.append(f"{field} = ?")
                location_params.append(data[field])

        if image_updates:
            cursor.execute(f"UPDATE Image SET {', '.join(image_updates)} WHERE Id_Image = ?", (*image_params, id))
        if location_updates:
            cursor.execute(f"UPDATE Location SET {', '.join(location_updates)} WHERE Id_Image = ?", (*location_params, id))

        conn.commit()

    if not image_updates and not location_updates:
        return JsonResponse({"message": "Aucune mise à jour pour l'image"})

    return JsonResponse({"message": f"Image {id} mise à jour avec succès."})


def predict_map(request):
    return HttpResponse("Prédiction de carte à faire")


def img_detail(request, id):
    query = """
    SELECT * FROM Location
    JOIN Image ON Location.Id_Image = Image.Id_Image
    WHERE Location.Id_Image = ?
    """
    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            if not row:
                return HttpResponse("Image not found", status=404)

            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))

            # Parsing JSON fields if necessary
            for field in ('RGB_Histogram', 'Luminance_Histogram'):
                if field in data and isinstance(data[field], str):
                    data[field] = json.loads(data[field])

            return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def get_img(request, id):
    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT File_path FROM Image WHERE Id_Image = ?", (id,))
            result = cursor.fetchone()
            if not result:
                return HttpResponse("Image not found", status=404)

        relative_path = result[0]
        full_path = os.path.join(s.MEDIA_ROOT, relative_path)

        if not os.path.exists(full_path):
            return HttpResponse("Image file missing", status=404)

        content_type, _ = mimetypes.guess_type(full_path)
        content_type = content_type or "application/octet-stream"

        with open(full_path, 'rb') as f:
            return FileResponse(f, content_type=content_type)
    except Exception as e:
        return HttpResponse(f"Error: {e}", status=500)


def img_by_filename(request, filename):
    query = """
    SELECT
        Id_Image, File_name, File_path, Size, Height, Width,
        Date_taken, Avg_R, Avg_G, Avg_B, Contrast_level,
        RGB_Histogram, Luminance_Histogram, Edges, Status
    FROM Image
    WHERE File_name = ?
    """
    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (filename,))
            row = cursor.fetchone()
            if not row:
                return JsonResponse({"error": "Image not found"}, status=404)

            keys = [
                "Id_Image", "File_name", "File_path", "Size", "Height", "Width", "Date_taken",
                "Avg_R", "Avg_G", "Avg_B", "Contrast_level", "RGB_Histogram", "Luminance_Histogram",
                "Edges", "Status"
            ]
            data = dict(zip(keys, row))
            return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def list_images_paginated(request):
    try:
        page = int(request.GET.get('page', 1))
        limit = int(request.GET.get('limit', 10))
        offset = (page - 1) * limit
    except ValueError:
        return JsonResponse({'error': 'Invalid pagination params'}, status=400)

    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
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
        return JsonResponse({
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit,
            "images": images
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)




def global_histograms(request):
    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT Width, Height, RGB_Histogram, Luminance_Histogram, Contrast_level, Edges, Status
                FROM Image
            """)
            rows = cursor.fetchall()

        # Init structures
        size_classes = {'<500px': 0, '500-800px': 0, '800-1200px': 0, '>1200px': 0}
        dominant_colors = {'Rouge': 0, 'Vert': 0, 'Bleu': 0}
        dominant_colors_label = {'Pleine': {'Rouge': 0, "Vert": 0, "Bleu": 0}, 'Vide': {'Rouge': 0, "Vert": 0, "Bleu": 0}}
        contrast_classes = {'Faible': 0, 'Moyen': 0, 'Élevé': 0}
        contrast_avg_label = {'Pleine': {'Faible': 0, "Moyen": 0, "Élevé": 0}, 'Vide': {'Faible': 0, "Moyen": 0, "Élevé": 0}}
        edges_histogram = {'<5000': 0, '5000-10000': 0, '10000-50000': 0, '>50000': 0}
        edges_Average = {'Sans label': 0, 'Pleine': 0, 'Vide': 0}
        contrast_list = []
        count_edges = {'Pleine': 0, 'Vide': 0, 'Sans label': 0}

        for width, height, rgb_json, lum_json, contrast, edges, status in rows:
            # Taille
            max_dim = max(width, height)
            if max_dim < 500:
                size_classes['<500px'] += 1
            elif max_dim < 800:
                size_classes['500-800px'] += 1
            elif max_dim < 1200:
                size_classes['800-1200px'] += 1
            else:
                size_classes['>1200px'] += 1

            # Histogrammes
            rgb_hist = json.loads(rgb_json)
            lum_hist = json.loads(lum_json)

            # Couleur dominante
            sum_r = sum(i * rgb_hist['red'][i] for i in range(256))
            sum_g = sum(i * rgb_hist['green'][i] for i in range(256))
            sum_b = sum(i * rgb_hist['blue'][i] for i in range(256))
            max_color = max(sum_r, sum_g, sum_b)
            if max_color == sum_r:
                dominant_colors['Rouge'] += 1
                if status == 1:
                    dominant_colors_label['Pleine']['Rouge'] += 1
                elif status == 0:
                    dominant_colors_label['Vide']['Rouge'] += 1
            elif max_color == sum_g:
                dominant_colors['Vert'] += 1
                if status == 1:
                    dominant_colors_label['Pleine']['Vert'] += 1
                elif status == 0:
                    dominant_colors_label['Vide']['Vert'] += 1
            else:
                dominant_colors['Bleu'] += 1
                if status == 1:
                    dominant_colors_label['Pleine']['Bleu'] += 1
                elif status == 0:
                    dominant_colors_label['Vide']['Bleu'] += 1

            # Contraste
            if contrast is not None:
                contrast_list.append(contrast)
                if contrast < 30:
                    contrast_classes['Faible'] += 1
                    if status == 1:
                        contrast_avg_label['Pleine']['Faible'] += 1
                    elif status == 0:
                        contrast_avg_label['Vide']['Faible'] += 1
                elif contrast < 60:
                    contrast_classes['Moyen'] += 1
                    if status == 1:
                        contrast_avg_label['Pleine']['Moyen'] += 1
                    elif status == 0:
                        contrast_avg_label['Vide']['Moyen'] += 1
                else:
                    contrast_classes['Élevé'] += 1
                    if status == 1:
                        contrast_avg_label['Pleine']['Élevé'] += 1
                    elif status == 0:
                        contrast_avg_label['Vide']['Élevé'] += 1

            # Arêtes
            if edges < 5000:
                edges_histogram['<5000'] += 1
            elif edges < 10000:
                edges_histogram['5000-10000'] += 1
            elif edges < 50000:
                edges_histogram['10000-50000'] += 1
            else:
                edges_histogram['>50000'] += 1

            # Moyenne par statut
            if status == 1:
                edges_Average['Pleine'] += edges
                count_edges['Pleine'] += 1
            elif status == 0:
                edges_Average['Vide'] += edges
                count_edges['Vide'] += 1
            else:
                edges_Average['Sans label'] += edges
                count_edges['Sans label'] += 1

        # Moyennes
        for key in edges_Average:
            if count_edges[key]:
                edges_Average[key] /= count_edges[key]

        avg_contrast = sum(contrast_list) / len(contrast_list) if contrast_list else None

        return JsonResponse({
            "Size_Histogram": size_classes,
            "Dominant_Colors": dominant_colors,
            "Dominant_Colors_Label": dominant_colors_label,
            "Contrast_Histogram": contrast_classes,
            "Contrast_Level_Label": contrast_avg_label,
            "Average_Contrast": avg_contrast,
            "Edges_Histogram": edges_histogram,
            "Edges_Average": edges_Average
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def get_constraints(request):
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET allowed")

    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM Constraints LIMIT 1")
            row = cursor.fetchone()

            if not row:
                return JsonResponse({}, status=204)

            columns = [desc[0] for desc in cursor.description]
            constraints = dict(zip(columns, row))

        for key in ['RGB_Histogram', 'Luminance_Histogram']:
            if constraints.get(key) and isinstance(constraints[key], str):
                constraints[key] = json.loads(constraints[key])

        return JsonResponse(constraints)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def update_constraints(request):
    if request.method not in ['POST', 'PUT']:
        return HttpResponseBadRequest("Only POST or PUT allowed")

    try:
        data = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    fields = [
        'Size', 'Height', 'Width', 'Date_taken', 'Avg_R', 'Avg_G', 'Avg_B',
        'Contrast_level', 'RGB_Histogram', 'Luminance_Histogram', 'Edges'
    ]
    values = [
        data.get('Size'),
        data.get('Height'),
        data.get('Width'),
        data.get('Date_taken'),
        data.get('Avg_R'),
        data.get('Avg_G'),
        data.get('Avg_B'),
        data.get('Contrast_level'),
        json.dumps(data.get('RGB_Histogram')) if data.get('RGB_Histogram') else None,
        json.dumps(data.get('Luminance_Histogram')) if data.get('Luminance_Histogram') else None,
        data.get('Edges')
    ]

    try:
        with sqlite3.connect(os.path.join(s.BASE_DIR, 'db.sqlite3')) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM Constraints")
            exists = cursor.fetchone()[0]

            if exists:
                placeholders = ', '.join(f + ' = ?' for f in fields)
                cursor.execute(f"UPDATE Constraints SET {placeholders}", values)
            else:
                placeholders = ', '.join(['?'] * len(fields))
                cursor.execute(
                    f"INSERT INTO Constraints ({', '.join(fields)}) VALUES ({placeholders})",
                    values
                )
            conn.commit()

        return JsonResponse({"message": "Contraintes enregistrées avec succès."})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def get_app_config(request):
    if request.method != 'GET':
        return HttpResponseBadRequest("Only GET allowed")
    db = os.path.join(s.BASE_DIR, 'db.sqlite3')
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute("SELECT value FROM AppConfig WHERE key='intelligent_mode'")
        row = cur.fetchone()
    mode = bool(int(row[0])) if row else False
    return JsonResponse({ "intelligent_mode": mode })

@csrf_exempt
def update_app_config(request):
    if request.method not in ('POST','PUT'):
        return HttpResponseBadRequest("Only POST/PUT allowed")
    try:
        data = json.loads(request.body)
        val = '1' if data.get('intelligent_mode') else '0'
    except:
        return HttpResponseBadRequest("Invalid JSON")
    db = os.path.join(s.BASE_DIR, 'db.sqlite3')
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        # 🔥 UPSERT : insert si absent, update si présent
        cur.execute("""
            INSERT INTO AppConfig (key, value)
            VALUES ('intelligent_mode', ?)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value
        """, (val,))
        conn.commit()
    return JsonResponse({ "intelligent_mode": bool(int(val)) })

@csrf_exempt
def predict_crops_all(request):
    """
    Parcourt tous les crops sauvegardés, prédit avec le modèle CNN importé
    et retourne un dictionnaire { id_image : prediction }
    """
    crops_dir = os.path.join(s.MEDIA_ROOT, "Data", "crops")
    results = {}

    for filename in os.listdir(crops_dir):
        if not filename.endswith(".webp"):
            continue

        id_image = filename.replace("crop_", "").replace(".webp", "")
        img_path = os.path.join(crops_dir, filename)

        # 🔥 Cast la prédiction en float ou int natif
        preds = deep_model.predict_image(img_path)
        pred_value = float(preds) if hasattr(preds, '__float__') else bool(preds)

        results[id_image] = pred_value

    return JsonResponse({"predictions": results})

@csrf_exempt
def predict_missing_crops(request):
    """
    Prédit uniquement les images dont Status_DeepIA est NULL
    en utilisant les crops dans Data/crops/crop_{id}.webp
    """
    db_path = os.path.join(s.BASE_DIR, 'db.sqlite3')
    crops_dir = os.path.join(s.MEDIA_ROOT, "Data", "crops")

    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT Id_Image FROM Image WHERE Status_DeepIA IS NULL")
            images = cursor.fetchall()

            results = []
            for (id_image,) in images:
                crop_filename = f"crop_{id_image}.webp"
                crop_path = os.path.join(crops_dir, crop_filename)

                if not os.path.exists(crop_path):
                    print(f"[WARN] Crop non trouvé : {crop_path}")
                    continue  # 🔥 Ignore si crop absent

                # Prédiction sur l'image cropée
                status_ia = int(deep_model.predict_image(crop_path))  # True -> 1, False -> 0

                # Mise à jour en BDD
                cursor.execute(
                    "UPDATE Image SET Status_DeepIA = ? WHERE Id_Image = ?",
                    (status_ia, id_image)
                )
                results.append({"Id_Image": id_image, "prediction": status_ia})

            conn.commit()

        return JsonResponse({"predictions": results})

    except Exception as e:
        print(f"[ERROR] predict_missing_crops : {e}")
        return HttpResponseBadRequest(f"Erreur : {e}")