"""
Application Flask — Détection d'Anticorps Bovins dans le Lait de Brebis
=========================================================================
Ce fichier contient le backend de l'application :
  • Route « / »        → sert l'interface utilisateur (index.html)
  • Route « /predict » → reçoit une image, l'analyse, renvoie un JSON

Déploiement : compatible Render / PythonAnywhere (gunicorn app:app)
"""

import io
from flask import Flask, render_template, request, jsonify
from PIL import Image
import numpy as np

# ──────────────────────────────────────────────────────────────
# CONSTANTES DE CALIBRATION
# Formule : concentration = (intensité_verte - B) / A
# A = pente de la droite de calibration
# B = ordonnée à l'origine
# ──────────────────────────────────────────────────────────────
A: float = 8.12    # pente (à ajuster selon ta courbe)
B: float = 152.33  # ordonnée à l'origine

# ──────────────────────────────────────────────────────────────
# CONFIGURATION FLASK
# ──────────────────────────────────────────────────────────────
app = Flask(__name__)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff"}


def allowed_file(filename: str) -> bool:
    """Vérifie que l'extension du fichier est autorisée."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# ──────────────────────────────────────────────────────────────
# TRAITEMENT D'IMAGE
# ──────────────────────────────────────────────────────────────
def process_image(image_file) -> float:
    """
    Analyse l'image (déjà rognée côté navigateur via Cropper.js)
    et renvoie l'intensité moyenne du canal VERT.

    Paramètres
    ----------
    image_file : file-like object
        Fichier image (bytes) ou chemin.

    Retourne
    --------
    float
        Intensité moyenne du canal vert (0–255).
    """

    # 1. Charger l'image en RGB depuis la mémoire
    img = Image.open(image_file).convert("RGB")
    arr = np.array(img)

    # 2. Calcul de l'intensité moyenne du canal VERT
    green_channel = arr[:, :, 1].astype(np.float32)
    mean_intensity = float(np.mean(green_channel))

    return mean_intensity


# ──────────────────────────────────────────────────────────────
# CALIBRATION
# ──────────────────────────────────────────────────────────────
def calibrate(intensity: float) -> float:
    """
    Convertit l'intensité verte en concentration d'anticorps
    via la formule :  concentration = (intensité - B) / A

    Paramètres
    ----------
    intensity : float
        Intensité verte moyenne renvoyée par process_image().

    Retourne
    --------
    float
        Concentration estimée en anticorps (µg/mL).
        La valeur est bornée à 0 minimum (pas de concentration négative).
    """
    concentration = (intensity - B) / A
    return concentration


# ──────────────────────────────────────────────────────────────
# ROUTES
# ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    """Affiche la page principale."""
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    """
    Reçoit une image via multipart/form-data, l'analyse,
    et renvoie la concentration en JSON.
    """
    # Vérifier qu'un fichier est présent dans la requête
    if "image" not in request.files:
        return jsonify({"error": "Aucune image reçue."}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "Nom de fichier vide."}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Format de fichier non supporté."}), 400

    # Traitement direct en mémoire (sans sauvegarde disque pour Vercel)
    try:
        # Étape 1 : extraction de l'intensité
        # On passe directement le flux de fichier (file.stream) à Pillow
        intensity = process_image(file.stream)

        # Étape 2 : calibration → concentration
        concentration = calibrate(intensity)

        return jsonify({
            "concentration": float(f"{concentration:.4g}"),
            "unit": "µg/mL",
            "intensity": round(intensity, 2),
        })

    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'analyse : {str(e)}"}), 500


# ──────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
