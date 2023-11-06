# -*- coding: utf-8 -*-
from app import app, auth, views
import inspect
from app.model import db, TipoDato
from flask import render_template, flash, request, redirect, url_for,  g, jsonify
from flask import Blueprint

tipodato = Blueprint('tipodato', __name__,
                     template_folder='../templates', static_url_path='assets')

# INDEX


@tipodato.route('/tipodato', methods=['POST', 'GET'])
@auth.login_required
def tipodato_index():
    # SEGURIDAD
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    # if permisos == '':
    #     return render_template('dashboard.html')

    return render_template('tipodato/index.html')
