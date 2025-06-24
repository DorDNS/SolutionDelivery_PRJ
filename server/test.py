import os
import sys
import json
import sqlite3
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.urls import path
from django.core.management import execute_from_command_line

PORT = '8000'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if not settings.configured:
    # PARTIE CHATGPT !!!!
    settings.configure(
        DEBUG=True,
        ROOT_URLCONF=__name__,
        SECRET_KEY='YOUUUUU',
        ALLOWED_HOSTS=['*'],
        MIDDLEWARE=[],
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': os.path.join(BASE_DIR, 'TrashMap.db'),
            }
        },
        INSTALLED_APPS=[],
    )


def home_view(request):
    return HttpResponse("Hello world")


def dashboard(request):
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'TrashMap.db'))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Image")
    total_img = cursor.fetchone()[0]
    conn.close()
    return JsonResponse({'total_img': total_img})


def locations_img(request):
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'TrashMap.db'))
    cursor = conn.cursor()
    query = """
    SELECT Image.Id_Image, Localisation.Latitude, Localisation.Longitude, 
           Localisation.Altitude, Localisation.Ville
    FROM Image
    JOIN Localisation ON Image.Id_Localisation = Localisation.Id_Localisation
    """
    cursor.execute(query)
    results = cursor.fetchall()
    data = [
        {
            'id': row[0],
            'latitude': row[1],
            'longitude': row[2],
            'altitude': row[3],
            'ville': row[4]
        }
        for row in results
    ]
    conn.close()
    return JsonResponse(data, safe=False)


def upload_img(request):
    if request.method != 'POST':
        return HttpResponse("Méthode non autorisée", status=405)

    uploaded_file = request.FILES.get('image')
    if not uploaded_file:
        return HttpResponse("Aucun fichier fourni", status=400)

    if not uploaded_file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
        return HttpResponse("Format de fichier non supporté", status=400)

    # TODO : Extraire localisation depuis métadonnées ou corps de requête
    return HttpResponse("Upload en cours (à compléter)")


def predict_img(request):
    return HttpResponse("Prédiction image à faire")


def modify_img(request, id):
    return HttpResponse(f"Modification de l'image {id} à faire")


def predict_map(request):
    return HttpResponse("Prédiction de carte à faire")


def img_detail(request, id):
    conn = sqlite3.connect(os.path.join(BASE_DIR, 'TrashMap.db'))
    cursor = conn.cursor()
    query = """
    SELECT * FROM Image
    JOIN Localisation ON Image.Id_Localisation = Localisation.Id_Localisation
    WHERE Image.Id_Image = ?
    """
    cursor.execute(query, (id,))
    row = cursor.fetchone()
    if not row:
        return HttpResponse("Image non trouvée", status=404)

    # adapter si les colonnes changent
    columns = [desc[0] for desc in cursor.description]
    data = dict(zip(columns, row))
    conn.close()
    return JsonResponse(data)


urlpatterns = [
    path('', home_view),

    # DASHBOARD-related routes
    path('dashboard/', dashboard),

    # IMG-related routes
    path('img/locations/', locations_img),
    path('img/upload/', upload_img),
    path('img/predict/', predict_img),
    path('img/<int:id>/modify/', modify_img),
    path('img/<int:id>/', img_detail),

    # MAP-related
    path('map/predict/', predict_map),
]

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', __name__)
    execute_from_command_line([sys.argv[0], 'runserver', PORT])
