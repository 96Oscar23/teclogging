# -*- coding: utf-8 -*-
from app import app, auth, views, generales
import inspect
import sys
import string
import random
from flask import Flask, render_template, flash, request, redirect, url_for, jsonify, make_response, session, abort, Response, g, send_from_directory
from flask import Blueprint

from app.model import db, Usuario, Menu, Rol, RolMenu, Configuracion
from werkzeug.utils import secure_filename
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.engine import Engine
from sqlalchemy.orm import aliased
from sqlalchemy.sql.expression import cast, select
from sqlalchemy.dialects import postgresql
from datetime import datetime, timedelta
from flask_httpauth import HTTPBasicAuth
from functools import wraps
import json
from dateutil import tz
from dateutil.relativedelta import relativedelta
from flask_cors import CORS, cross_origin

# blueprint

from app.controller.menu.menu import menu


authc = Blueprint('authc', __name__,
                  template_folder='../templates', static_url_path='assets')


@authc.route('/', methods=['GET'])
@authc.route('/login', methods=['GET'])
def login():

    extras = {"titulo": "Iniciar Sesión"}

    return render_template('login.html', extras=extras)


@authc.route('/', methods=['POST'])
@authc.route('/login', methods=['POST'])
def login2():

    extras = {"titulo": "Iniciar Sesión"}

    usuario = request.form['useremail']
    usuario2 = request.form['loginpassword']  # password
    session['offset'] = request.form['offset']
    if usuario != "":

        user = Usuario.query.filter(and_(
            Usuario.correo == usuario, Usuario.deleted == False, Usuario.activo == True)).first()

        if user:
            if not user.verify_password(usuario2):

                flash("Contraseña Incorrecta", "danger")
                return render_template('login.html', extras=extras)

            else:
                return acepta_login(user)
        else:
            return render_template('login.html', extras=extras)
    else:
        return render_template('login.html', extras=extras)

# holahola


def acepta_login(user):
    g.user = user
    token = g.user.generate_auth_token(app.config['TOKEN_EXP_TIME'])
    rol_tab = Rol.query.get(user.rolid)
    session['token'] = token
    session['year'] = datetime.utcnow().strftime('%Y')
    session['menu'] = menuusuario(user.rolid)
    session['roluuid'] = rol_tab.uuid
    iniciales = user.nombre[0].upper()
    session['iniciales'] = iniciales
    session['empresa'] = "Servicios N.L."

    if 'menuestado' not in session:
        session['menuestado'] = 1

    return redirect(url_for('dashboard.dashboard_home'))


def opcionpadre(nivel, row, opciones, padreid, rolid):
    # usuario=g.user
    # print(row[2])
    # Menu.id, Menu.nombre, Menu.url, Menu.urlpython, Menu.icono
    icono = ""
    if row[4] != None:
        if len(row[4]) > 0:
            icono = row[4]

    if nivel == 0:
        if row[2] == "" or row[2] == None:
            opciones += f"""
                        <a class="nav-link text-bd-green-1 fw-bolder dropdown-toggle active" href="#navbarVerticalMenu{row[1]}" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenu{row[1]}" aria-expanded="true" aria-controls="navbarVerticalMenu{row[1]}">
                            <i class="{icono}"></i>
                            <span class="nav-link-title" id="menuparentid_{str(row[0])}">{row[1]}</span>
                        </a>
                        <div id="navbarVerticalMenu{row[1]}" class="nav-collapse collapse show" data-bs-parent="#navbarVerticalMenu"
                        """

        else:
            opciones += f"""
                        <a href="{url_for(row[2])}" class="nav-link text-bd-green-1 fw-bolder dropdown-toggle active" href="#navbarVerticalMenu{row[1]}" role="button" data-bs-toggle="collapse" data-bs-target="#navbarVerticalMenu{row[1]}" aria-expanded="true" aria-controls="navbarVerticalMenu{row[1]}">
                            <i class="{icono} me-2"></i>
                            <span class="nav-link-title" id="menuparentid_{str(row[0])}">{row[1]}</span>
                        </a>
                        """

        menu = Menu.query.with_entities(Menu.id, Menu.nombre, Menu.url, Menu.urlpython, Menu.icono)\
            .filter(and_(Menu.deleted == False, Menu.opcionpadreid == row[0], Menu.menu == True))\
            .join(RolMenu, and_(RolMenu.menuid == Menu.id, RolMenu.rolid == rolid, RolMenu.deleted == False))\
            .order_by(Menu.orden, Menu.nombre).all()

        for row2 in menu:
            opciones = opcionpadre(nivel + 1, row2, opciones, row[0], rolid)
        opciones += f"""</div>"""

    if nivel == 1:

        url = ""
        if row[3] == True:
            url = url_for(row[2])
        else:
            url = row[2]
        opciones += f"""<i class="{icono}"></i><a class="nav-link " href="{url}" id="menuitem_{row[0]}">{row[1]}</a>"""

    return opciones


def menuusuario(rolid):
    # usuario=g.user

    menu = Menu.query.with_entities(Menu.id, Menu.nombre, Menu.url, Menu.urlpython, Menu.icono)\
        .filter(and_(Menu.deleted == False, Menu.opcionpadreid == None, Menu.menu == True))\
        .join(RolMenu, and_(RolMenu.menuid == Menu.id, RolMenu.rolid == rolid, RolMenu.deleted == False))\
        .order_by(Menu.orden).all()

    opciones = ""
    print(menu)
    for row in menu:

        opciones = opcionpadre(0, row, opciones, 0, rolid)

    return opciones


@auth.verify_password
def verify_password(username_or_token, password):

    # session_token = session['token']
    if session:
        username_or_token = session['token']
    else:
        username_or_token = request.headers.get('cAuth')
    if username_or_token:
        # print('username_or_token',username_or_token)
        # first try to authenticate by token
        user = Usuario.verify_auth_token(username_or_token)
        if not user:
            return False
        g.user = user
        return True

    return False


# En caso de error de login, redireccionar a login
@auth.error_handler
def auth_error():
    return redirect(url_for('authc.login'))


@app.route('/api/v1/usuario/recuperar/correo/<string:correo>/token/<string:token>', methods=['GET', 'POST'])
def recuperarcorreo(correo, token):
    usuario = Usuario.query.filter(and_(Usuario.correo == correo, Usuario.token_recuperar ==
                                   token, Usuario.deleted == False, Usuario.activo == True)).first()
    extras = {"titulo": "Recuperación de Contraseña"}
    if request.method == 'GET':
        if usuario != None:
            return render_template('reset.html', extras=extras)
        else:
            return redirect("/")
    else:
        if usuario != None:
            password = request.form['newpassword']
            password1 = request.form['repeatpassword']
            if (password == password1):
                usuario.hash_password(password)
                usuario.token_recuperar = ''
                usuario.update()
                if sys.version_info <= (3, 0):
                    extras = {'titulo1': 'ParadoxaLabs', 'titulo2': "Contraseña modificada con éxito".decode(
                        'utf-8'), 'msn': "Su contraseña fue modificada con éxito, ingrese nuevamente a la aplicación.".decode('utf-8'), 'clase': 'success', 'icono': 'fa fa-check'}
                else:
                    extras = {'titulo': 'Recuperación de Contraseña', 'titulo2': "Contraseña modificada con éxito",
                              'msn': "Su contraseña fue modificada con éxito, ingrese nuevamente a la aplicación.", 'clase': 'success', 'icono': 'fa fa-check'}
                return render_template('exitoso.html', extras=extras)
            else:
                flash("La Contraseña y la confirmación no coinciden", "danger")
                return render_template('reset.html', extras=extras)
        else:
            return redirect("/")


@app.route('/seguridad/agregar/<int:rolid>/menuid/<int:menuid>/permiso/<int:permiso>', methods=['POST', 'GET'])
@auth.login_required
def seguridad_agregar(rolid, menuid, permiso):
    # print "si entro"
    # Agregar o Quitar permiso
    if permiso == 1:
        rolmenu = RolMenu(rolid, menuid)
        rolmenu_add = rolmenu.add(rolmenu)
        if not rolmenu_add:
            return jsonify({'estatus': 'ok'})
        else:
            return jsonify({'estatus': 'error'})
    else:
        rolmenu = RolMenu.query\
            .with_entities(RolMenu.id)\
            .filter(and_(RolMenu.deleted == False, RolMenu.rolid == rolid, RolMenu.menuid == menuid)).all()
        for row in rolmenu:
            rm = RolMenu.query.get(row[0])
            rm.deleted = True
            rm.update()
        return jsonify({'estatus': 'ok'})


@app.route('/logout', methods=['GET', 'POST'])
def logout():
    g.user = None
    session['token'] = None
    session['menu'] = None
    return redirect(url_for('authc.login'))


# *dashboard
'''
@app.route('/dashboard')
@auth.login_required
def dashboard():
    usuario = g.user
    # sacamos el rol del usuario
    # rolid = usuario.rolid
    # multiempresa=0
    # if rolid in [1,2]:
    #    multiempresa=1
    # fechas=[]
    # TODO: VALIDAR SI SE REALIZA HARDCODE
    getMenuFileOptions = Menu.query.filter(
        and_(Menu.deleted == False, Menu.opcionpadreid == 20)).all()
    menuListFiles = []
    for menu in getMenuFileOptions:
        menuListFiles.append({
            'id': menu.id,
            'nombre': menu.nombre,
            'url': url_for(menu.url),
        })
    extras = {"titulo": "Inicio"}

    return render_template('dashboard.html', archivos=menuListFiles, extras=extras)
'''


@app.route("/api/v1/web_login", methods=["GET", "POST"])
def web_login():

    usuario = request.json.get('usuario')
    usuario2 = request.json.get('usuario2')
    deviceid = request.json.get('deviceid')

    user = Usuario.query.filter(and_(
        Usuario.correo == usuario, Usuario.activo == True, Usuario.deleted == False)).first()

    if not user or not user.verify_password(usuario2):
        return jsonify({'estatus': 'error', 'msn': 'Usuario invalido.'})
    g.user = user
    token = g.user.generate_auth_token(app.config['TOKEN_EXP_TIME'])
    # grabamos el deviceid en la base de datos

    user.deviceid = deviceid
    up_user = user.update()
    if not up_user:
        # , 'empresa': user.empresa.uuid ,'rolid':user.rolid
        return jsonify({'estatus': 'ok', 'token': token, 'duration': app.config['TOKEN_EXP_TIME'], 'nombre': user.nombre})
    else:
        return jsonify({'estatus': 'error', 'msn': 'Error al grabar ID dispositivo.'})


@app.route("/usuario/cambiarpassword", methods=["GET", "POST"])
@auth.login_required
def usuario_cambiarpassword():
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)

    if permisos == '':
        # print inspect.currentframe().f_code.co_name
        return jsonify({'estatus': 'error', 'msn': app.config['NO_PERMISO_BORRAR']})

    usuarioid = request.json.get('usuarioid')
    password = request.json.get('password')
    usuariodb = views.regresaporuuid(Usuario, usuarioid, usuario.id)
    usuariodb.hash_password(password)
    usuariodb.update()
    return jsonify({'estatus': 'ok', 'msn': app.config['UPD_SUCC']})


@app.route("/api/v1/validatoken/<string:pushtoken>/os/<string:os>/lan/<string:lang>", methods=["GET", "POST"])
@app.route("/api/v1/validatoken/<string:pushtoken>/os/<string:os>", methods=["GET", "POST"])
@auth.login_required
def validatoken(pushtoken, os, lang=''):
    # funcion para validar si el token del servidor es valido y grabamos el token de pushnotification
    usuario = g.user
    usuarioid = usuario.id
    usuariodb = Usuario.query.get(usuarioid)

    # token = g.user.generate_auth_token(app.config['TOKEN_EXP_TIME'])

    usuariodb.tokenpush = pushtoken
    usuariodb.so = os
    usuariodb.idioma = lang
    usuariodb.update()

    token = g.user.generate_auth_token(app.config['TOKEN_EXP_TIME'])

    return jsonify({'estatus': 'ok', 'token': token})


"""
@note funcion para recuperar contraseña
"""


@app.route("/recuperar", methods=["GET", "POST"])
def recuperar():

    extras = {}

    # Agregamos la parte correspondiente del codigo para mostrar el logo o nombre de la empresa segun el url
    dominio = request.base_url
    # dominio="http://equysis.paradoxalabs.com/login"
    dominio = dominio.replace("http://", "").replace("https://", "")\
        .replace("/", "").replace("login", "").replace(" ", "")
    print(dominio + "-")
    logo = "Servicio"

    if request.method == 'POST':

        correo = request.form['useremail']

        if correo == "":
            error = "El correo no puede estar vacío"
            return render_template('recuperar.html', error=error, extras=extras, logo=logo)

        usuario = Usuario.query.filter(and_(
            Usuario.correo == correo, Usuario.deleted == False, Usuario.activo == True)).first()

        if usuario != None:
            # generamos el token
            token = generales.id_generator()
            usuario.token_recuperar = token
            usuario.update()
            # enviamos el correo

            url_recuperar = request.url_root + \
                "/api/v1/usuario/recuperar/correo/"+correo+"/token/"+token

            mensaje = ""

            if sys.version_info <= (3, 0):
                titulo1 = "Recuperar contraseña".decode('utf-8')
                mensaje += """
                    <h1> Hola %s </h1>
                    <br>
                    <tr>
                    <td class="title-dark" width="300">
                    <h2> Recuperar contraseña </h2>
                    </td>
                    </tr>
                    <tr>
                    <td class="item-col quantity">
                    <span>
                    Para continuar con tu recuperación de contraseña, favor de dar click en el siguiente link:</h3>
                    <br>
                    <center>
                    <a href="%s" align="center"> recuperar contraseña </a>
                    </center>
                """.decode('utf-8') % (usuario.nombre, url_recuperar)
            else:
                titulo1 = "Recuperar contraseña"
                mensaje += """
                    <h1> Hola %s </h1>
                    <br>    
                    <tr>
                    <td class="title-dark" width="300">
                    <h2> Recuperar contraseña </h2>
                    </td>
                    </tr>
                    <tr>
                    <td class="item-col quantity">
                    <span>
                    Para continuar con tu recuperación de contraseña, favor de dar click en el siguiente link:</h3>
                    <br>
                    <center>
                    <a href="%s" align="center"> recuperar contraseña </a>
                    </center>
                """ % (usuario.nombre, url_recuperar)

            # controllers.enviar_mail(
            #     correo, titulo1, mensaje, "Recuperar contraseña", None)

            notificaciones.send_mail(
                correo, titulo1, mensaje, None)

            if sys.version_info <= (3, 0):
                extras = {'titulo1': titulo1, 'titulo2': "Correo enviado con éxito".decode(
                    'utf-8'), 'msn': "Siga las instrucciones que fueron enviadas a su correo electrónico para poder ingresar al sistema.".decode('utf-8'), 'clase': 'success', 'icono': 'fa fa-check', 'titulo_title': logo}
            else:
                extras = {'titulo1': titulo1, 'titulo2': "Correo enviado con éxito",
                          'msn': "Siga las instrucciones que fueron enviadas a su correo electrónico para poder ingresar al sistema.", 'clase': 'success', 'icono': 'fa fa-check', 'titulo_title': logo}

            return render_template('exitoso.html', extras=extras)
        else:
            error = 'Error.'
            return render_template('recuperar.html', error=error, logo=logo)

    error = ''

    return render_template('recuperar.html', error=error, extras=extras, logo=logo)
