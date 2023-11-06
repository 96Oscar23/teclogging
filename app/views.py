# -*- coding: utf-8 -*-
from app import app, auth
import string
import random
from flask import session, send_from_directory, jsonify, request
from sqlalchemy.dialects import postgresql
from app.model import db, Rol, RolMenu, Menu, Usuario
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import os

# blueprint
from app.controller.auth.auth import authc
from app.controller.dashboard.dashboard import dashboard
from app.controller.usuario.usuario import usuario

app.register_blueprint(authc)
app.register_blueprint(dashboard)
app.register_blueprint(usuario)

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def regresaporuuid(objeto, uuid, usuarioid):
    # funcion que hace un query a la tabla "objeto" filtrando por uuid, objeto es una parametro enviado
    # todo usar usuario id, deberiamos de validar que el usuaroiu pueda consultar el dato
    return objeto.query.filter(and_(objeto.deleted == False, objeto.uuid == uuid)).first()


def regresaPermisos(funcion):
    #     # regresa los permisos que tiene el rol
    permisos = ''

#     roluuid = session['roluuid']
#     rolid = 0
#     rol = Rol.query.filter(
#         and_(Rol.deleted == False, Rol.uuid == roluuid)).first()
#     if rol:
#         rolid = rol.id

#     p = RolMenu.query.with_entities(RolMenu.id, Menu.url)\
#         .join(Menu, and_(Menu.id == RolMenu.menuid, Menu.deleted == False))\
#         .filter(and_(RolMenu.deleted == False, RolMenu.rolid == rolid,
#                      func.lower(Menu.url).like("%"+func.lower(funcion)+"%"))).all()

#     # print ("p",len(p))
#     for row in p:
#         permisos = permisos + row[1]+'-'
#     # print ("permiso")
    return permisos


@app.route('/inicializa', methods=['POST', 'GET'])
def inicializa():

    correoadmin = "admin@admin.com"

    # logica para crear el usuario admin si es la primera vez
    usr = Usuario.query.filter(
        and_(Usuario.deleted == False, Usuario.correo == correoadmin)).first()
    if not usr:
        admin = Usuario("admin", correoadmin, "holahola",
                        "token_registro", True, True, True, 1)
        add = admin.add(admin)

    usrpass = Usuario.query.with_entities(Usuario.id).filter(
        Usuario.deleted == False).filter(Usuario.id == -1).all()
    for row in usrpass:
        x = Usuario.query.get(row[0])
        x.hash_password("holahola")
        x.update()

    return "ok"


app.jinja_env.globals.update(regresaPermisos=regresaPermisos)

app.debug = True
