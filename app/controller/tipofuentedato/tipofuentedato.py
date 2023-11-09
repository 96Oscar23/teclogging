# -*- coding: utf-8 -*-
from app import app,auth,views
import inspect
from flask import render_template, flash, request, redirect, url_for,  g,jsonify
from flask import Blueprint
from app.model import db,Menu
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased
from app.model import db, Tipofuentedato


tipofuentedato = Blueprint('tipofuentedato', __name__,
    template_folder='../templates'
    , static_url_path='assets')

#index
@tipofuentedato.route('/tipofuentedato' , methods=['POST', 'GET'])
@auth.login_required
def tipofuentedato_index ():
    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')
    
    extras = {"titulo" : "Tipo Fuente de Dato","objeto":"tipofuentedato"}

    querytipofuentedatos = Tipofuentedato.query.filter(and_(Tipofuentedato.deleted==False)).order_by(Tipofuentedato.nombre).all()

    return render_template('/tipofuentedato/index.html', extras=extras, tipofuentedatos=querytipofuentedatos)


#CREATE
@tipofuentedato.route('/tipofuentedato/add' , methods=['POST', 'GET'])
@auth.login_required
def tipofuentedato_add():
    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')
    
    extras= {'titulo':'Crear Tipo Fuente de Dato','accion':'Agregar'}

    return render_template('/tipofuentedato/add.html',extras=extras)