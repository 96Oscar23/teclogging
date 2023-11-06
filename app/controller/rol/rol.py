# -*- coding: utf-8 -*-
from app import app,auth,views
#from app.controller.menu import menu as controlMenu
import inspect
from flask import render_template, flash, request, redirect, url_for,  g,jsonify
from flask import Blueprint
from app.model import db,Rol,Menu,RolMenu
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased




rol = Blueprint('rol', __name__,
    template_folder='../templates'
    , static_url_path='assets')





#INDEX
@rol.route('/rol' , methods=['POST', 'GET'])
@auth.login_required
def rol_index ():
    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')    
    extras = {"titulo" : "Roles","objeto":"rol"} 
    roles = Rol.query.filter(and_(Rol.deleted==False))\
    .order_by(Rol.nombre).all()
    
    return render_template('rol/index.html', roles=roles, extras = extras)



#CREATE
@rol.route('/rol/add' , methods=['POST', 'GET'])
@auth.login_required
def rol_add():
    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')
    if request.method == 'POST':

        rol = Rol(request.form['nombre'])
        objeto_add=rol.add(rol)
        if not objeto_add:
            flash(app.config['ADD_SUCC'] ,"success")
            return redirect(url_for('rol.rol_index'))
        else:
            error=objeto_add
            flash(error,"error")

    extras= {'titulo':'Crear Rol','accion':'Agregar'}
    rol = Rol("")

    return render_template('rol/add.html', rol=rol, extras=extras, title="Agregar Rol")


#UPDATE
@rol.route('/rol/update/<id>' , methods=['POST', 'GET'])
@auth.login_required
def rol_update (id):
    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')
    rol = views.regresaporuuid(Rol,id,usuario.id)
    if rol == None:
        flash(app.config['NOEXISTE'],"danger")
        return redirect(url_for('rol.rol_index'))
    if request.method == "POST":
        rol.nombre = request.form['nombre']

        rolpadre=None
        if request.form.get('rolpadre') !="0":
            rolpadre= request.form.get('rolpadre')
        rol.rolpadreid=rolpadre

        objeto_update=rol.update()
        #If post.update does not return an error
        if not objeto_update:
            flash(app.config['UPD_SUCC'],"success")
            return redirect(url_for('rol.rol_index'))
        else:
            error=objeto_update
            flash(error,"error")
    extras= {'titulo':'Modificar Rol','accion':'Editar'}

    roles = Rol.query.filter(Rol.deleted==False,Rol.uuid!=id).all()

    #traemos las opciones padres
    opciones= Menu.query.with_entities(Menu.id,Menu.nombre,Menu.opcionpadreid,RolMenu.rolid\
    ,Menu.descripcion)\
        .outerjoin(RolMenu,and_(RolMenu.rolid==rol.id,RolMenu.menuid==Menu.id,RolMenu.deleted==False))\
    .filter(Menu.deleted==False,Menu.opcionpadreid==None).order_by(Menu.orden,Menu.nombre).all()

    dataopciones=[]
    for row in opciones:
        funcione_acomodo_hijas(row,"",rol.id,dataopciones)

    return render_template('rol/add.html',  rol=rol,extras=extras,roles=roles,opciones=dataopciones\
        ,title="Editar Rol")


@rol.route('/rol/delete' , methods=['POST', 'GET'])
@auth.login_required
def menu_delete ():
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    
    if permisos=='':
        #print inspect.currentframe().f_code.co_name
        return jsonify({'estatus':'error','msn':app.config['NO_PERMISO_BORRAR']})
    
        # aqui recibimos los datos del ajax como json
            
    objid = request.json.get("objid")

    #borrar razon
    rol =views.regresaporuuid(Rol,objid,g.user.id)
    rol.deleted = True
    rol.update()
    msn=app.config['DEL_SUCC']

    #,'uuid':razondelet
    return jsonify({'estatus':'ok','msn':msn})

def funcione_acomodo_hijas(elemento,nombrepadre,id,data):
    nombre=''
    if nombrepadre !='':
        nombre = nombrepadre +' / '

    nombre += elemento.nombre

    data.append(dict(id=elemento.id,nombre=elemento.nombre,opcionpadre=nombre\
    ,rolid=elemento.rolid,descripcion=elemento.descripcion))

    #validamos si tiene hijas
    #consultamos las opciones hijas
    hijas = Menu.query.with_entities(Menu.id,Menu.nombre,Menu.opcionpadreid,RolMenu.rolid\
    ,Menu.descripcion)\
            .outerjoin(RolMenu,and_(RolMenu.rolid==id,RolMenu.menuid==Menu.id,RolMenu.deleted==False))\
            .filter(and_(Menu.deleted==False,Menu.opcionpadreid==elemento.id))\
            .order_by(Menu.orden,Menu.nombre).all()

    for raw in hijas:
        data=funcione_acomodo_hijas(raw,nombre,id,data)
        #dataopciones.append(dict(id=raw.id,nombre=raw.nombre,opcionpadre=row.nombre,rolid=raw.rolid))


    return data