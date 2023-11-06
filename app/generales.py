from app import app
from app.model import Configuracion, db,  Usuario
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import cv2
import tempfile
from flask import render_template
from app import app
import platform
import string
import random
import os


def creaFolder(DOCTOSPATH, empresaid, folder):
    # rutina para crear un directorio en el directorio especial de la empresa
    pathcliente = os.path.join(DOCTOSPATH, str(empresaid))

    try:
        os.makedirs(pathcliente)
        # print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory ", pathcliente,  " already exists")

    pathfinal = os.path.join(pathcliente, folder)
    try:
        os.makedirs(pathfinal)
        # print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory ", pathfinal,  " already exists")
    return pathfinal


def creaFolders(folder):
    try:
        os.makedirs(folder)
        # print("Directory " , dirName ,  " Created ")
    except FileExistsError:
        print("Directory ", folder,  " already exists")

    return "ok"


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in app.config['ALLOWED_EXTENSIONS']


def id_generator(size=32, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.SystemRandom().choice(chars) for _ in range(size))


def fechaActual():
    return datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


# funcion para generar los años de un rango de fechas
def generar_anios(fecha_inicio, fecha_fin):
    anios = []
    anio_inicio = fecha_inicio.year
    anio_fin = fecha_fin.year
    for anio in range(anio_inicio, anio_fin+1):
        anios.append(anio)
    return anios


def nombre_mes_complet():
    list_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre",
                  "Octubre", "Noviembre", "Diciembre"]

    return list_meses


def nombre_mes_abreviado():
    list_meses = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep",
                  "Oct", "Nov", "Dic"]

    return list_meses


def nombre_dia_completo():
    list_dias = ["Lunes", "Martes", "Miercoles",
                 "Jueves", "Viernes", "Sabado", "Domingo"]

    return list_dias


def nombre_dia_abreviado():
    list_dias = ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"]

    return list_dias


def nombre_semana():
    list_semana = ["Semana 1", "Semana 2", "Semana 3", "Semana 4"]

    return list_semana
