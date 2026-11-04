import os
import re
import time
from contextlib import closing

import psycopg2
import requests
from flask import Flask, jsonify, request
from psycopg2.extras import Json

app = Flask(__name__)

# Configuration lue dans les variables d'environnement
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "tableau")
DB_USER = os.environ.get("DB_USER", "tableau")
DB_PASSWORD = os.environ["DB_PASSWORD"]
SALONS_URL = os.environ.get("SALONS_URL", "http://salons:5000")

FORMAT_CODE = re.compile(r"^[A-Z0-9]{4}$")
FORMAT_COULEUR = re.compile(r"^#[0-9A-Fa-f]{6}$")
MAX_POINTS = 5000
TRAITS_PAR_REPONSE = 500


def connexion():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        connect_timeout=3,
    )


def executer(requete, parametres=()):
    # Ouvre une connexion, exécute la requête, valide et ferme.
    with closing(connexion()) as conn:
        with conn:
            with conn.cursor() as curseur:
                curseur.execute(requete, parametres)
                if curseur.description:
                    return curseur.fetchall()
                return None


def initialiser_base():
    # La base peut mettre quelques secondes à démarrer : on réessaie.
    for _ in range(30):
        try:
            executer(
                "CREATE TABLE IF NOT EXISTS traits ("
                "id SERIAL PRIMARY KEY, "
                "salon_code VARCHAR(8) NOT NULL, "
                "couleur VARCHAR(7) NOT NULL, "
                "taille INTEGER NOT NULL, "
                "points JSONB NOT NULL, "
                "cree_le TIMESTAMP DEFAULT NOW())"
            )
            executer(
                "CREATE INDEX IF NOT EXISTS idx_traits_salon "
                "ON traits (salon_code, id)"
            )
            return
        except psycopg2.Error:
            time.sleep(2)
    raise RuntimeError("Base de données inaccessible")


initialiser_base()


def points_valides(points):
    if not isinstance(points, list) or not 1 <= len(points) <= MAX_POINTS:
        return False
    for point in points:
        if not isinstance(point, list) or len(point) != 2:
            return False
        if not all(isinstance(v, (int, float)) for v in point):
            return False
    return True


def salon_existe(code):
    # Appel vers le service salons pour vérifier que le salon existe.
    try:
        reponse = requests.get(f"{SALONS_URL}/salons/{code}", timeout=3)
    except requests.RequestException:
        return None
    if reponse.status_code == 200:
        return True
    if reponse.status_code == 404:
        return False
    return None


@app.route("/health")
def health():
    # Utilisé par Docker et Kubernetes pour savoir si le service fonctionne.
    try:
        executer("SELECT 1")
    except psycopg2.Error:
        return jsonify(status="base indisponible"), 503
    return jsonify(status="ok")


@app.route("/traits/<code>", methods=["POST"])
def ajouter_trait(code):
    code = code.upper()
    if not FORMAT_CODE.match(code):
        return jsonify(erreur="Salon introuvable"), 404

    donnees = request.get_json(silent=True) or {}
    couleur = donnees.get("couleur")
    taille = donnees.get("taille")
    points = donnees.get("points")

    if not isinstance(couleur, str) or not FORMAT_COULEUR.match(couleur):
        return jsonify(erreur="Couleur invalide"), 400
    if not isinstance(taille, int) or isinstance(taille, bool) or not 1 <= taille <= 60:
        return jsonify(erreur="Taille invalide"), 400
    if not points_valides(points):
        return jsonify(erreur="Points invalides"), 400

    existe = salon_existe(code)
    if existe is None:
        return jsonify(erreur="Service salons indisponible"), 503
    if not existe:
        return jsonify(erreur="Salon introuvable"), 404

    lignes = executer(
        "INSERT INTO traits (salon_code, couleur, taille, points) "
        "VALUES (%s, %s, %s, %s) RETURNING id",
        (code, couleur, taille, Json(points)),
    )
    return jsonify(id=lignes[0][0]), 201


@app.route("/traits/<code>")
def lire_traits(code):
    code = code.upper()
    apres = request.args.get("apres", default=0, type=int)
    lignes = executer(
        "SELECT id, couleur, taille, points FROM traits "
        "WHERE salon_code = %s AND id > %s ORDER BY id LIMIT %s",
        (code, apres, TRAITS_PAR_REPONSE),
    )
    traits = [
        {"id": ligne[0], "couleur": ligne[1], "taille": ligne[2], "points": ligne[3]}
        for ligne in lignes
    ]
    return jsonify(traits)
