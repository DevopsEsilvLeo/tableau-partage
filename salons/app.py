import os
import re
import secrets
import time
from contextlib import closing

import psycopg2
from flask import Flask, jsonify

app = Flask(__name__)

# Configuration lue dans les variables d'environnement
DB_HOST = os.environ.get("DB_HOST", "db")
DB_PORT = os.environ.get("DB_PORT", "5432")
DB_NAME = os.environ.get("DB_NAME", "tableau")
DB_USER = os.environ.get("DB_USER", "tableau")
DB_PASSWORD = os.environ["DB_PASSWORD"]

# Caractères faciles à lire (sans 0, O, 1 et I)
CARACTERES = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
FORMAT_CODE = re.compile(r"^[A-Z0-9]{4}$")


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
                "CREATE TABLE IF NOT EXISTS salons ("
                "code VARCHAR(8) PRIMARY KEY, "
                "cree_le TIMESTAMP DEFAULT NOW())"
            )
            return
        except psycopg2.Error:
            time.sleep(2)
    raise RuntimeError("Base de données inaccessible")


initialiser_base()


@app.route("/health")
def health():
    # Utilisé par Docker et Kubernetes pour savoir si le service fonctionne.
    try:
        executer("SELECT 1")
    except psycopg2.Error:
        return jsonify(status="base indisponible"), 503
    return jsonify(status="ok")


@app.route("/salons", methods=["POST"])
def creer_salon():
    for _ in range(10):
        code = "".join(secrets.choice(CARACTERES) for _ in range(4))
        lignes = executer(
            "INSERT INTO salons (code) VALUES (%s) "
            "ON CONFLICT DO NOTHING RETURNING code",
            (code,),
        )
        if lignes:
            return jsonify(code=code), 201
    return jsonify(erreur="Impossible de créer le salon"), 500


@app.route("/salons/<code>")
def lire_salon(code):
    code = code.upper()
    if not FORMAT_CODE.match(code):
        return jsonify(erreur="Salon introuvable"), 404
    lignes = executer("SELECT code FROM salons WHERE code = %s", (code,))
    if not lignes:
        return jsonify(erreur="Salon introuvable"), 404
    return jsonify(code=lignes[0][0])
