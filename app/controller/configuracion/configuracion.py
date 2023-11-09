# -*- coding: utf-8 -*-
from app import app, auth, views
import inspect
from flask import render_template, flash, request, redirect, url_for,  g, jsonify
from flask import Blueprint
from app.model import db, Configuracion
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased

# blueprint

from app.controller.menu.menu import menu


configuracion = Blueprint('configuracion', __name__,
                          template_folder='../templates', static_url_path='assets')


################# *CONFIGURACION #################
################# *CONFIGURACION #################
################# *CONFIGURACION #################
# INDEX
@configuracion.route('/configuracion', methods=['POST', 'GET'])
@auth.login_required
def configuracion_index():
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos == '':
        return render_template('dashboard.html')

    extras = {"titulo": "Configuración", "objeto": "configuracion"}

    configuraciones = Configuracion.query.filter(Configuracion.deleted == False)\
        .order_by(Configuracion.nombre).all()

    return render_template('configuracion/index.html', configuraciones=configuraciones, extras=extras)


# CREATE
@configuracion.route('/configuracion/add', methods=['POST', 'GET'])
@auth.login_required
def configuracion_add():
    # SEGURIDAD
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos == '':
        return render_template('dashboard.html')

    extras = {'titulo': 'Crear Opcion Configuracion','accion':'Agregar'}
    if request.method == 'POST':

        configuracion = Configuracion(
            request.form['nombre'],
            request.form['valor'], usuario.empresaloginid)

        objeto_add = configuracion.add(configuracion)
        if not objeto_add:
            flash(app.config['ADD_SUCC'], "success")
            return redirect(url_for('configuracion.configuracion_index'))

        else:
            error = objeto_add
            flash(error, "danger")

    configuracion = Configuracion("", "", None)
    return render_template('configuracion/add.html', extras=extras, configuracion=configuracion)


# UPDATE
@configuracion.route('/configuracion/update/<id>', methods=['POST', 'GET'])
@auth.login_required
def configuracion_update(id):
    # SEGURIDAD
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos == '':
        return render_template('dashboard.html')

    configuracion = views.regresaporuuid(Configuracion, id, usuario.id)

    extras = {'titulo': 'Editar Opcion Configuracion','accion':'Editar'}
    if configuracion == None:
        flash(app.config['NOEXISTE'], "danger")
        return redirect(url_for('configuracion.configuracion_index'))
    if request.method == "POST":
        configuracion.nombre = request.form['nombre']
        configuracion.valor = request.form['valor']

        objeto_update = configuracion.update()
        # If post.update does not return an error
        if not objeto_update:
            flash(app.config['UPD_SUCC'], "success")
            return redirect(url_for('configuracion.configuracion_index'))
        else:
            error = objeto_update
            flash(error, "danger")

    return render_template('configuracion/add.html',  configuracion=configuracion, extras=extras)


@configuracion.route('/configuracion/delete', methods=['POST', 'GET'])
@auth.login_required
def configuracion_delete():
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)

    if permisos == '':
        # print inspect.currentframe().f_code.co_name
        return jsonify({'estatus': 'error', 'msn': app.config['NO_PERMISO_BORRAR']})

        # aqui recibimos los datos del ajax como json

    objid = request.json.get("objid")

    # borrar razon
    configuracion = views.regresaporuuid(Configuracion, objid, g.user.id)
    configuracion.deleted = True
    configuracion.update()
    msn = app.config['DEL_SUCC']

    # ,'uuid':razondelet
    return jsonify({'estatus': 'ok', 'msn': msn})
