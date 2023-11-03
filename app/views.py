# -*- coding: utf-8 -*-
from app import app, auth, generales
import string
import random
from flask import session, send_from_directory, jsonify, request
from sqlalchemy.dialects import postgresql
from app.model import db,Rol,RolMenu,Menu
from sqlalchemy import and_, func
from datetime import datetime, timedelta
import os

# blueprint



def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def regresaporuuid(objeto, uuid, usuarioid):
    # funcion que hace un query a la tabla "objeto" filtrando por uuid, objeto es una parametro enviado
    # todo usar usuario id, deberiamos de validar que el usuaroiu pueda consultar el dato
    return objeto.query.filter(and_(objeto.deleted == False, objeto.uuid == uuid)).first()


def regresaPermisos(funcion):
    # regresa los permisos que tiene el rol
    permisos = ''

    roluuid = session['roluuid']
    rolid = 0
    rol = Rol.query.filter(
        and_(Rol.deleted == False, Rol.uuid == roluuid)).first()
    if rol:
        rolid = rol.id

    p = RolMenu.query.with_entities(RolMenu.id, Menu.url)\
        .join(Menu, and_(Menu.id == RolMenu.menuid, Menu.deleted == False))\
        .filter(and_(RolMenu.deleted == False, RolMenu.rolid == rolid,
                     func.lower(Menu.url).like("%"+func.lower(funcion)+"%"))).all()

    # print ("p",len(p))
    for row in p:
        permisos = permisos + row[1]+'-'
    # print ("permiso")
    return permisos


app.jinja_env.globals.update(regresaPermisos=regresaPermisos)

app.debug = True
