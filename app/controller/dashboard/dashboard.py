# -*- coding: utf-8 -*-
from app import app, auth, views
import inspect
from flask import render_template, flash, request, redirect, url_for,  g, jsonify
from flask import Blueprint
from app.model import db
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased
from app import generales
from datetime import datetime, timedelta
from sqlalchemy.dialects import postgresql

dashboard = Blueprint('dashboard', __name__,
                      template_folder='../templates', static_url_path='assets')


# INDEX
@dashboard.route('/dashboard', methods=['POST', 'GET'])
@auth.login_required
def dashboard_home():
    usuario = g.user
    # permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    # if permisos == '':
    #    return render_template('dashboard.html')

    extras = {"titulo": "Servicios", "objeto": "Servicios"}

    
    fecha_inicio = datetime.now()
    fecha_fin = datetime.now()
    return render_template('dashboard/home.html', extras=extras, ciudades=[],
                           tipoServicios=[], fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)


@dashboard.route('/api/dashboard/home', methods=['POST', 'GET'])
@auth.login_required
def api_dashboard_home():
    usuario = g.user
    fecha_inicio = request.json.get('fecha_inicio')
    fecha_fin = request.json.get('fecha_fin')

    municipios = request.json.get('municipios')
    tiposervicio = request.json.get('tiposervicio')
    _estatus = "ok"
    _msn = "ok"

    datetime_fecha_inicio = datetime.strptime(fecha_inicio, '%Y%m%d')
    datetime_fecha_fin = datetime.strptime(fecha_fin, '%Y%m%d')

    print(datetime_fecha_inicio, datetime_fecha_fin)

    diferencia = datetime_fecha_fin - datetime_fecha_inicio

    dias = diferencia.days
    anios = dias / 365
    meses = dias / 30
    semanas = dias / 7

    rango_grafica = "dias"
    nombre_grafica = generales.nombre_dia_abreviado()

    # consultamos los servicios
    list_servicio = generales.regresaServicios()
    list_tipo_servicio = generales.tipoServiciosPadres()

    lista_servicios_terminados = filter(
        lambda servicio: servicio['estatusservicioid'] == 4, list_servicio)

   

    rango_iterar = dias

    if dias > 365:
        rango_grafica = "anios"
        nombre_grafica = generales.generar_anios()
        rango_iterar = anios
    elif dias > 30:
        rango_grafica = "meses"
        nombre_grafica = generales.nombre_mes_abreviado()
        rango_iterar = meses

    elif dias > 7:
        rango_grafica = "semanas"
        nombre_grafica = generales.nombre_dia_abreviado()
        rango_iterar = semanas

    fecha_iterar = datetime_fecha_inicio
    diccionario_fecha = {}
    for item in range(0, int(rango_iterar)):

        # print("itermos: ", item)

        if dias > 365:
            key = fecha_iterar.year
        elif dias > 30:
            key = fecha_iterar.strftime("%B")
        elif dias > 7:
            key = fecha_iterar.strftime("%U")
        elif dias > 1:
            key = fecha_iterar.strftime("%A")

        if key not  in diccionario_fecha:
            diccionario_fecha[key] = 0
            

        if dias > 365:
            fecha_iterar = fecha_iterar + timedelta(days=365)
        elif dias > 30:
            fecha_iterar = fecha_iterar + timedelta(days=30)
        elif dias > 7:
            fecha_iterar = fecha_iterar + timedelta(days=7)
        elif dias > 1:
            fecha_iterar = fecha_iterar + timedelta(days=1)

    print("diccionario_fecha: ", diccionario_fecha)
    diccionario_datos_grafica = {}
    for tipo in list_tipo_servicio:
        if key not in diccionario_datos_grafica:
            diccionario_datos_grafica[tipo.codigo] = {
                "nombre": tipo.nombre, "data": diccionario_fecha}

    print ("################################ diccionario_datos_grafica: ", diccionario_datos_grafica)

    estatus_terminado = EstatusServicio.query.filter(
        EstatusServicio.codigo == "finalizado").first()

    municipios_query = Ciudad.query.filter(and_(Ciudad.deleted == False)).all()

    municipios_list = []

    for municipio in municipios_query:
        municipios_list.append(
            dict(id=municipio.id, nombre=municipio.nombre, cantidad=0, ubicacion=[]))

    print("consultamos servicios")
    servicio_query = Servicio.query.filter(and_(Servicio.deleted == False))


    if len(municipios) > 0:
        print("entramos a municipios")
        servicio_query = servicio_query.filter(Servicio.ciudadid == municipios)

    # print("tiposervicio: ", tiposervicio)
    if tiposervicio != '' and tiposervicio != '0':
        # print("entramos a tiposervicio")
        servicio_query = servicio_query.filter(
            Servicio.tiposervicioid == tiposervicio)

    servicio_terminado = servicio_query.filter(
        Servicio.estatusservicioid == estatus_terminado.id).count()

    servicio_pendiente = servicio_query.filter(
        Servicio.estatusservicioid != estatus_terminado.id).count()

    servicios_totales = servicio_query.count()

    porcentaje_terminado = 0

    if servicios_totales > 0:
        porcentaje_terminado = round(
            (servicio_terminado * 100) / servicios_totales, 2)

    objeto_data = []

    objeto_data.append({"servicio_terminado": servicio_terminado, "servicio_pendiente": servicio_pendiente,
                       "servicios_totales": servicios_totales, "porcentaje_terminado": porcentaje_terminado})

    list_municipios_servicios = []
    datos_grafica = {}

    # llenamos con indices el arreglo para los datos de la grafica

    ubicaciones = []

    # print("llevamos aqui")
    # print(str(servicio_query.statement.compile(dialect=postgresql.dialect())))
    # print("llevamos aqui", len(servicio_query.all()))
    for servicio in servicio_query.all():

        ubicaciones.append(dict(latitud=servicio.latitud,
                           longitud=servicio.longitud))

        if servicio.ciudadid != None:

            # buscamos si el id del servicio existe en la lista de municipios
            existe = list(
                filter(lambda municipio: municipio['id'] == servicio.ciudadid, municipios_list))
            # print("existe: ", existe)
            for row in existe:
                index = None
                # si existe sumamos uno a la cantidad
                if len(list_municipios_servicios) > 0:
                    index = next((index for index, d in enumerate(
                        list_municipios_servicios) if d["ciudadid"] == servicio.ciudadid), -1)

                # print ("index: ", index)
                # print("list_municipios_servicios: ", list_municipios_servicios)
                if index != None and index != -1:
                    # print("editamos", index)
                    aux = list_municipios_servicios[index]

                    aux["cantidad"] = aux["cantidad"] + 1
                    list_municipios_servicios[index] = aux
                else:
                    # print("Agregamos")
                    list_municipios_servicios.append(
                        dict(ciudadid=servicio.ciudadid, cantidad=1, nombre=row['nombre']))

    
    for item in lista_servicios_terminados:
        print ("item: ", item)
        key = item["fecha_fin"].strftime("%A")
        if dias > 365:
            key = item["fecha_fin"].year
        elif dias > 30:
            key = item["fecha_fin"].strftime("%B")
        elif dias > 7:
            key = item["fecha_fin"].strftime("%U")
        # elif dias > 1:
            # key = item["fecha_fin"].strftime("%A")

        print("key: ", key)

        if key in diccionario_datos_grafica:
            print("existe")
            diccionario_datos_grafica[key] = diccionario_datos_grafica[key] + 1

    # print("list_municipios_servicios: ", list_municipios_servicios)
    # print("diccionario_datos_grafica: ", diccionario_datos_grafica)

    list_diccionario_datos_grafica = []
    for key, value in diccionario_datos_grafica.items():
        list_diccionario_datos_grafica.append(dict(key=key, value=value))

    return jsonify({"estatus": _estatus, "msn": _msn, "data": objeto_data, "ubicaciones": ubicaciones,
                    "municipios": list_municipios_servicios, "grafica": list_diccionario_datos_grafica})
