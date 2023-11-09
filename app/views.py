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
from app.controller.tipodato.tipodato import tipodato
from app.controller.configuracion.configuracion import configuracion
from app.controller.rol.rol import rol
from app.controller.menu.menu import menu
from app.controller.tipofuentedato.tipofuentedato import tipofuentedato

app.register_blueprint(authc)
app.register_blueprint(dashboard)
app.register_blueprint(usuario)
app.register_blueprint(tipodato)
app.register_blueprint(configuracion)
app.register_blueprint(rol)
app.register_blueprint(menu)
app.register_blueprint(tipofuentedato)

def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def regresaporuuid(objeto, uuid, usuarioid):
    # funcion que hace un query a la tabla "objeto" filtrando por uuid, objeto es una parametro enviado
    # todo usar usuario id, deberiamos de validar que el usuaroiu pueda consultar el dato
    return objeto.query.filter(and_(objeto.deleted == False, objeto.uuid == uuid)).first()


def regresaPermisos(funcion):
    #     # regresa los permisos que tiene el rol
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


def comilla(texto):
    texto = texto.replace(
        '"', "**COMILLADOBLE**").replace("'", "**COMILLASIMPLE**")
    return texto

def arregloAnidadoArrgloUnidimensional(diccionario, textopadre, ordenpadre, idpadre):
    # funcion para convertir un diccionario con nodos anidados a un arreglo unidimensional
    # de esto
    # [fase 1,hijos[Fase 11,Fase 21]],[fase 2,hijos=[]],[fase 3,hijos=[fase 33]]
    # a esto
    # fase 1
    # fase 1/Fase 11
    # fase 1/Fase 21
    # Fase 2
    # Fase 3/fase 33

    # id=str(dato.uuid),valor=dato.nombre,nivel=nivel,hijos=nieto

    plano = []
    for elemento in diccionario:
        # print (elemento)
        nombre = elemento["valor"].replace("/", "")
        id = elemento["id"]
        if textopadre != "":
            nombre = textopadre + "/" + nombre
        orden = 1
        if "orden" in elemento["atributos"]:
            orden = elemento["atributos"]["orden"]
            plano.append(dict(id=elemento["id"], nombre=nombre, nivel=elemento["nivel"], orden=orden,
                         ordenpadre=ordenpadre, idpadre=idpadre, atributos=elemento["atributos"]))
        if "hijos" in elemento:
            hijos = arregloAnidadoArrgloUnidimensional(
                elemento['hijos'], nombre, orden, id)
            for hijo in hijos:
                plano.append(hijo)
    return plano

def arbol_jerarquia(TABLA, columnaFiltro, valorFiltro, columnaOrden, queryFijo, nivel):
    # *arbol
    # Tabla es la tabla al que le haremos el query
    # columnaFiltro es la columna a filtrar
    # valorFiltro es el id a filtrar en el parametro columnaFiltro, si es 0 no filtra
    # columnaOrden columna del order by
    # empresaid es la empresa del usuario logueado
    # queryFijo El query que se va a ejecutar en todos los niveles

    # diccionario es el diccionario donde se van a ir guardando las jerarquias

    # funciona para regresar el diccionario de jerarquias de una tabla, podria reutilizarse en el menu o cualquier
    # tabla que tenga jerarquias entre ella misma

    # nos sirve para por ejemplo en la tabla tipoproducto, regresar todo el arbol de jerarquias
    # diccionario=[]
    # print (valorFiltro)
    # filtros de cajon
    queryA = TABLA.query.filter(and_(TABLA.deleted == False))

    # if queryFijo !=None:
    # print ("fijo")
    queryA = queryA.filter(queryFijo)

    if valorFiltro != 0:
        queryA = queryA.filter(columnaFiltro == valorFiltro)
    else:
        queryA = queryA.filter(columnaFiltro == None)
    # print (str(queryA.statement.compile(dialect=postgresql.dialect())))
    for x in columnaOrden:
        queryA = queryA.order_by(x)

    datos = queryA.all()
    hijos = []

    # vamos a regresar todos los atributos de la tabla, excepto ID y _sa_instance_state
    for dato in datos:
        atributos = {}
        # print (type(dato.__dict__.keys()))
        for columna in dato.__dict__:
            if columna not in ['id', '_sa_instance_state', 'uuid', 'deleted', 'fecha_creacion']:
                valor = dato.__dict__[columna]
                if type(valor) is datetime:
                    # print (dato.nombre)
                    # print (dato.uuid)
                    # print (valor)
                    valor = valor.strftime("%Y%m%d%H%M%S")
                    # print (valor)
                if type(valor) == str:
                    valor = comilla(valor)
                atributos[columna] = valor

            # print (dato.__dict__[columna])
        #    print (dato.columna)
        #    print(columna, '->', dato[columna])

            # print (dato[columna])
        # print (atributos)
        nieto = []
        nieto = arbol_jerarquia(TABLA, columnaFiltro,
                                dato.id, columnaOrden, queryFijo, nivel+1)
        # print ("------dato.nombre: ",dato.nombre)
        # print ("------dato.nombre: ",comilla(dato.nombre))
        hijos.append(dict(id=str(dato.uuid), valor=comilla(
            dato.nombre), nivel=nivel, hijos=nieto, atributos=atributos))
        # vamos por los hijos del elemento

    return hijos



app.jinja_env.globals.update(regresaPermisos=regresaPermisos)

app.debug = True
