import os
import tensorflow as tf
from tensorflow.keras.models import load_model

# Chemin absolu vers le modèle .keras
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'trashmap_cn_crop.keras')

# Charger le modèle une seule fois
model = load_model(MODEL_PATH)

def predict_image(image_path, target_size=(128,128)):
    """
    Prend un chemin vers une image, retourne la prédiction binaire du modèle CNN
    """
    img = tf.keras.utils.load_img(image_path, target_size=target_size)
    x = tf.keras.utils.img_to_array(img) / 255.0
    x = tf.expand_dims(x, axis=0)  # shape (1,128,128,3)

    preds = model.predict(x)
    return (preds[0][0] > 0.5)  # retourne un booléen : True (pleine) ou False (vide)