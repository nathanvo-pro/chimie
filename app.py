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
# Formule : concentration = (intensité - B) / A
# ──────────────────────────────────────────────────────────────
CALIB = {
    "or":     {"A": 8.12,  "B": 152.33},   # nanoparticules d'or  (canal vert)
    "argent": {"A": 8.81,  "B": 149.42},   # nanotriangles d'argent (canal jaune)
}

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
def process_image(image_file, mode: str = "or") -> float:
    """
    Analyse l'image (déjà rognée côté navigateur via Cropper.js)
    et renvoie l'intensité moyenne selon le mode choisi.

    Modes
    -----
    - "or"     : canal VERT seul  →  arr[:,:,1]
    - "argent" : canal JAUNE       →  (R + G) / 2
    """
    img = Image.open(image_file).convert("RGB")
    arr = np.array(img)

    if mode == "argent":
        # Intensité jaune = (Rouge + Vert) / 2
        R = arr[:, :, 0].astype(np.float32)
        G = arr[:, :, 1].astype(np.float32)
        mean_intensity = float(np.mean((R + G) / 2))
    else:
        # Intensité verte
        green = arr[:, :, 1].astype(np.float32)
        mean_intensity = float(np.mean(green))

    return mean_intensity


# ──────────────────────────────────────────────────────────────
# CALIBRATION
# ──────────────────────────────────────────────────────────────
def calibrate(intensity: float, mode: str = "or") -> float:
    """
    Convertit l'intensité en concentration d'anticorps
    via la formule :  concentration = (intensité - B) / A
    avec les constantes correspondant au mode choisi.
    """
    c = CALIB[mode]
    concentration = (intensity - c["B"]) / c["A"]
    if concentration < 0:
        concentration = 0
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

    # Lire le mode (or / argent)
    mode = request.form.get("mode", "or")
    if mode not in CALIB:
        return jsonify({"error": "Mode invalide. Choisis 'or' ou 'argent'."}), 400

    # Traitement direct en mémoire (sans sauvegarde disque pour Vercel)
    try:
        # Étape 1 : extraction de l'intensité selon le mode
        intensity = process_image(file.stream, mode)

        # Étape 2 : calibration → concentration
        concentration = calibrate(intensity, mode)

        canal = "jaune (R+G)/2" if mode == "argent" else "verte"
        return jsonify({
            "concentration": float(f"{concentration:.4g}"),
            "unit": "µg/mL",
            "intensity": round(intensity, 2),
            "canal": canal,
            "mode": mode,
        })

    except Exception as e:
        return jsonify({"error": f"Erreur lors de l'analyse : {str(e)}"}), 500


# ──────────────────────────────────────────────────────────────
# POINT D'ENTRÉE
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
