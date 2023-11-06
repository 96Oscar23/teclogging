# -*- coding: utf-8 -*-
from app import app, auth, views
import inspect
from flask import render_template, flash, request, redirect, url_for,  g, jsonify
from flask import Blueprint
from app.model import db, Usuario, Rol
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased


usuario = Blueprint('usuario', __name__,
                    template_folder='../templates', static_url_path='assets')


# INDEX
@usuario.route('/usuario', methods=['POST', 'GET'])
@auth.login_required
def usuario_index():
    # SEGURIDAD
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos == '':
        return render_template('dashboard.html')

    extras = {"titulo": "Usuarios", "objeto": "usuario"}

    usuarios = Usuario.query.with_entities(
        Usuario.nombre,
        Usuario.correo,
        Usuario.uuid,
        Usuario.activo,
        Rol.nombre.label("rol")
    ).outerjoin(
        Rol, Rol.id == Usuario.rolid
    ).filter(
        Usuario.deleted == False
    ).order_by(Usuario.nombre).all()

    return render_template('usuario/index.html', usuarios=usuarios,  extras=extras)


# CREATE
@usuario.route('/usuario/add', methods=['POST', 'GET'])
@auth.login_required
def usuario_add():
    # SEGURIDAD
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos == '':
        return render_template('dashboard.html')

    print("usuario: ", usuario.__dict__)
    if request.method == 'POST':
        if request.form.get('contrasena') == request.form.get('confirmar'):
            roldb = None
            param_rol = request.form.get('rolid')
            if param_rol != -1:

                rol = views.regresaporuuid(
                    Rol, request.form.get('rolid'), usuario.id)
                roldb = rol.id
            empresauario = usuario.empresaloginid
            print("empresauario: ", empresauario)

            objeto = Usuario(
                nombre=request.form.get('nombre'),
                correo=request.form.get('useremail'),
                password=request.form.get('contrasena'),
                token_registro=None,
                validado=True,
                correo_registro=True,
                activo=True if request.form.get('activo') == "on" else False,
                rolid=roldb,

            )
            print(objeto.__dict__)
            usuario_add = objeto.add(objeto)

            objeto.empresaloginid = usuario.empresaloginid
            objeto.update()

            eur = EmpresaUsuarioRol(
                usuario.empresaloginid, objeto.id, roldb)
            eur.add(eur)

            if not usuario_add:
                flash(app.config['ADD_SUCC'], "success")
                return redirect(url_for('usuario.usuario_index'))

            else:
                error = usuario_add
                flash(error, "danger")
                return redirect(url_for('usuario.usuario_add'))

        else:
            flash("La contraseña y la confirmación deben coincidir", "danger")
            return redirect(url_for('usuario.usuario_add'))

    extras = {"titulo": "Crear Usuario", 'accion': 'Agregar'}

    usuario = Usuario("", "", "", "", False, "", True, 0)
    roles = Rol.query.filter(and_(Rol.deleted == False)
                             ).order_by(Rol.nombre).all()

    return render_template('usuario/add.html', usuario=usuario, extras=extras, roles=roles)


# UPDATE
@usuario.route('/usuario/update/<id>', methods=['POST', 'GET'])
@auth.login_required
def usuario_update(id):
    # SEGURIDAD
    usuarioSesion = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos == '':
        return render_template('dashboard.html')

    # Check if the post exists:
    usuario = Usuario.query.with_entities(
        Usuario.nombre,
        Usuario.correo,
        Usuario.uuid,
        Usuario.activo,
        Rol.nombre.label("rol"),
        Rol.uuid.label("rolid"),
    ).outerjoin(
        Rol, Rol.id == Usuario.rolid
    ).filter(
        Usuario.uuid == id
    ).first()

    if usuario == None:
        flash(app.config['NOEXISTE'], "danger")
        return redirect(url_for('usuario.usuario_index'))
    if request.method == "POST":
        usuario = views.regresaporuuid(Usuario, id, usuarioSesion.id)
        usuario.nombre = request.form.get('nombre')
        usuario.correo = request.form.get('useremail')
        roldb = None
        param_rol = request.form.get('rolid')
        if str(param_rol) != "-1":
            rol = views.regresaporuuid(
                Rol, request.form.get('rolid'), usuarioSesion.id)
            roldb = rol.id
        usuario.rolid = roldb
        activo = False
        if request.form.get('activo') == 'on':
            activo = True
        usuario.activo = activo

        usuario_update = usuario.update()
        # If post.update does not return an error
        if not usuario_update:
            flash(app.config['UPD_SUCC'], "success")
            return redirect(url_for('usuario.usuario_index'))
        else:
            error = usuario_update
            flash(error, "danger")
    # bodegas = Bodega.query.filter(Bodega.deleted==False).order_by(Bodega.nombre).all()
    extras = {'titulo': 'Modificar Usuario', 'accion': 'Editar'}
    roles = Rol.query.filter(and_(Rol.deleted == False)
                             ).order_by(Rol.nombre).all()
    return render_template('usuario/add.html', usuario=usuario, extras=extras, roles=roles)


@usuario.route('/usuario/delete', methods=['POST', 'GET'])
@auth.login_required
def usuario_delete():
    usuario = g.user
    permisos = views.regresaPermisos(inspect.currentframe().f_code.co_name)

    if permisos == '':
        # print inspect.currentframe().f_code.co_name
        return jsonify({'estatus': 'error', 'msn': app.config['NO_PERMISO_BORRAR']})

        # aqui recibimos los datos del ajax como json

    objid = request.json.get("objid")

    # borrar razon
    deletera = views.regresaporuuid(Usuario, objid, g.user.id)
    deletera.deleted = True
    deletera.update()
    msn = app.config['DEL_SUCC']

    # ,'uuid':razondelet
    return jsonify({'estatus': 'ok', 'msn': msn})


@usuario.route('/usuario/password', methods=['POST', 'GET'])
@auth.login_required
def usuario_password():

    msn = "prueba"

    tipoflash = "success"

    extras = {"titulo": "Cambio de contraseña"}

    if request.method == "POST":

        usuario = g.user  # usuario de la sesion

        last = request.form['loginpassword']
        password = request.form['contrasena']
        confirmation = request.form['confirmar']

        if password == confirmation:
            if usuario.verify_password(last):
                if len(password) > 7:
                    usuario.hash_password(password)
                    usuario.update()
                    msn = "Contraseña modificada."

                else:
                    msn = "La Contraseña debe de ser de 7 caracteres mínimo."
                    tipoflash = "danger"
            else:

                msn = "Contraseña incorrecta."
                tipoflash = "danger"

        else:
            msn = "Error: La Contraseña y la Confirmación no coinciden."
            tipoflash = "danger"

        flash(msn, tipoflash)

    return render_template('/usuario/password.html', extras=extras)


@usuario.route('/usuario/validacorreo', methods=['POST', 'GET'])
@auth.login_required
def usuario_validacorreo():
    usuario = g.user

    correo = str(request.json.get('correo'))
    usuario = Usuario.query.filter(
        and_(Usuario.deleted == False, Usuario.correo == correo)).first()
    estatus = "error"
    if usuario == None:
        estatus = "ok"
    return jsonify({'estatus': estatus})


# api para buscar usuarios
@usuario.route('/api/usuario/buscar', methods=['POST', 'GET'])
@auth.login_required
def api_usuario_buscar():

    _estatus = "ok"
    _msn = ""

    texto = request.json.get('texto')
    rol_cuadrilla = request.json.get('caso')

    texto = "%"+texto+"%"
    texto = texto.lower()

    #consultamos el rol cuadrilla.
    rol = Rol.query.filter(and_(Rol.deleted == False, Rol.id == 2)).first()

    if rol == None:
        _estatus = "error"
        _msn = "No se encontró el rol cuadrilla."
        return jsonify({'estatus': _estatus, 'msn': _msn})

    usuarios = Usuario.query.filter(and_(Usuario.deleted == False), or_(func.lower(Usuario.nombre).like(
        texto), func.lower(Usuario.correo).like(texto))).order_by(Usuario.nombre)

    
    if rol_cuadrilla == '2':
        usuarios = usuarios.filter(Usuario.rolid==rol.id).all()
    else:
        usuarios = usuarios.all()
    list_usuarios = []

    for usuario in usuarios:
        list_usuarios.append({
            "id": usuario.uuid,
            "nombre": usuario.nombre,
            "correo": usuario.correo,
        })

    return jsonify({'estatus': _estatus, 'msn': _msn, "datos": list_usuarios})
