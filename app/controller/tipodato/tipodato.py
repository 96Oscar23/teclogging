# -*- coding: utf-8 -*-
from app import app, auth, views
import inspect
from app.model import db, TipoVariable, Metrica, TipoFuenteDatoMapa, TipoDato
from flask import render_template, flash, request, redirect, url_for, g, jsonify
from flask import Blueprint

tipodato = Blueprint(
    "tipodato", __name__, template_folder="../templates", static_url_path="assets"
)

# INDEX


@tipodato.route("/tipodato", methods=["POST", "GET"])
@auth.login_required
def tipodato_index():
    # SEGURIDAD
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    # if permisos == '':
    #     return render_template('dashboard.html')

    return render_template("tipodato/index.html")

@tipodato.route("/tipodato/get/<uuid>", methods=["POST", "GET"])
@auth.login_required
def get(uuid):
    tipo_fuente_dato_mapa = []

    query_metrica = Metrica.query.with_entities(
        Metrica.id, Metrica.nombre, Metrica.longitud
    ).filter(
        Metrica.deleted == False,
    ).all()

    data = []

    for metrica in query_metrica:
        data.append({"id": metrica.id, "nombre": metrica.nombre, "longitud": metrica.longitud})

    return jsonify({"estatus": "ok", "data": tipo_fuente_dato_mapa})

@tipodato.route("/tipodato/select", methods=["POST", "GET"])
@auth.login_required
def get_select():

    metricas = []

    query_metricas = Metrica.query.with_entities(
        Metrica.id, Metrica.nombre
    ).all()

    for metrica in query_metricas:
        metricas.append({"id": metrica.id, "nombre": metrica.nombre, "longitud": metrica.id + 1})

    return jsonify({"estatus": "ok", "data": {"metricas": metricas}})


@tipodato.route("/tipodato/save", methods=["POST", "GET"])
@auth.login_required
def guardar():
    data = request.json.get("datos")

    print(data)

    return jsonify({"estatus": "ok", "data": {}})
