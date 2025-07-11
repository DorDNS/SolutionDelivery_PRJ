"""
URL configuration for TrashMapServer project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import TrashMapServer.views as v
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # DASHBOARD-related routes
    path('dashboard/<str:date>/', v.dashboard),
    
    # IMG-related routes
    path("img/list/", v.list_images_paginated),
    path('img/locations/<str:date>/', v.locations_img),     # GET: Return ids and locations of images for map
    path('img/upload/', v.upload_img),           # POST: Upload an image
    path('img/<int:id>/modify/', v.modify_img),  # POST/PUT: Annotate/modify image
    path('img/metadatas/<int:id>/', v.img_detail),          # GET: Get all info of this image
    path('img/img/<int:id>', v.get_img),                ## GET: Get the image
    path('img/global_histograms/<str:date>/', v.global_histograms),
    path('api/image/<str:filename>/', v.img_by_filename),  # GET : infos via nom de fichier
    

    #Constraints
    path('api/constraints/', v.get_constraints, name='get_constraints'),
    path('api/constraints/update/', v.update_constraints, name='update_constraints'),
    path('api/constraints/reset/', v.reset_constraints, name='update_constraints'),

    path('api/config/', v.get_app_config),
    path('api/config/update/',   v.update_app_config),

    path('img/predict_crops_all/', v.predict_crops_all),
    path('img/predict_cond_all/', v.predict_cond_all),
    
    path('img/predict_missing_crops/', v.predict_missing_crops),
    path('api/geocode_proxy/', v.geocode_proxy),
    path('api/reverse_geocode_proxy/', v.reverse_geocode_proxy),
    path('img/predict_only/deep/', v.predict_only_deep),
    path('img/predict_only/cond/', v.predict_only_cond),

    path('img/count_missing_predictions/', v.count_images_without_prediction),
    
    path("subscribe/", v.subscribe_email, name="subscribe_email"),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)