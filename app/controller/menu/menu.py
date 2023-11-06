# -*- coding: utf-8 -*-
from app import app,auth,views
import inspect
from flask import render_template, flash, request, redirect, url_for,  g,jsonify
from flask import Blueprint
from app.model import db,Menu
from sqlalchemy import desc, or_, and_, func, event, extract, literal_column, case, Integer, distinct, cast, not_, asc
from sqlalchemy.orm import aliased




menu = Blueprint('menu', __name__,
    template_folder='../templates'
    , static_url_path='assets')


#INDEX
@menu.route('/menu' , methods=['POST', 'GET'])
@auth.login_required
def menu_index ():
    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')      
    #permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    extras = {"titulo" : "Menú","objeto":"menu"}
    #print ("permisos: ",permisos)
    #if permisos=='':
        #return render_template('dashboard.html',objeto=[],extras=extras)

    
    
    opcionpadre = aliased(Menu)
    menus = Menu.query\
    .with_entities(Menu.uuid,Menu.nombre,opcionpadre.nombre.label("opcionpadre"))\
    .filter(Menu.deleted==False)\
    .outerjoin(opcionpadre,opcionpadre.id==Menu.opcionpadreid)\
    .order_by(case([(Menu.opcionpadreid==None,0)],else_=1),opcionpadre.orden,Menu.nombre).all()
    

    return render_template('/menu/index.html', menus=menus, extras=extras)



#CREATE
@menu.route('/menu/add' , methods=['POST', 'GET'])
@auth.login_required
def menu_add():

    #SEGURIDAD
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')
    
    extras= {'titulo':'Crear Opcion Menu','accion':'Agregar'}
    if request.method == 'POST':
        
        opcionpadre=None
        if request.form.get('opcionpadre') !="-1":
            opcionpadredb = views.regresaporuuid(Menu,request.form.get('opcionpadre'),usuario.id)
            opcionpadre = opcionpadredb.id
        urlpython=False
        esMenu=False
        url = request.form['url']
        icono = request.form['icono']
        orden = request.form['orden']
        descripcion = request.form['descripcion']
        if request.form.get('urlpython')=='on':
            urlpython=True
        if request.form.get('menu')=='on':
            esMenu=True
        menu=Menu(request.form['nombre'],opcionpadre,url,urlpython,esMenu, icono,orden,descripcion)
        print(menu.__dict__)
        objeto_add=menu.add(menu)
        if not objeto_add:
            flash(app.config['ADD_SUCC'] ,"success")
            return redirect(url_for('menu.menu_index'))

        else:
            error=objeto_add
            flash(error,"danger")

    
    opcionesMenu = arbolMenu(None)
    
    menu = Menu("",None,"",False,False,"",0,"")
    return render_template('menu/add.html',extras=extras, menu=menu,opcionesMenu=opcionesMenu,title="Agregar Opcion")


#UPDATE
@menu.route('/menu/update/<id>' , methods=['POST', 'GET'])
@auth.login_required
def menu_update (id):
    #SEGURIDAD
    #print("seguridad menu")
    usuario = g.user
    permisos=views.regresaPermisos(inspect.currentframe().f_code.co_name)
    if permisos=='':
        return render_template('dashboard.html')

    
    
    menu = views.regresaporuuid(Menu,id,usuario.id)
    if menu.opcionpadreid !=None:
        #traemos el uuid de la opcion padre, para no usar id de base de datos
        opcionpadre = Menu.query.get(menu.opcionpadreid)
        menu.opcionpadreuuid = str(opcionpadre.uuid)

    param_OpcionPadre = request.form.get('opcionpadre')

    extras= {'titulo':'Editar Opcion Menú','accion':'Editar'}
    if menu == None:
        flash(app.config['NOEXISTE'],"danger")
        return redirect(url_for('menu.menu_index'))
    if request.method == "POST":
        print(request.form['nombre'])
        opcionpadreid=None
        if param_OpcionPadre !="-1":
            opcionpadre = views.regresaporuuid(Menu,param_OpcionPadre,usuario.id)
            opcionpadreid= opcionpadre.id
        urlpython=False
        esMenu=False
        if request.form.get('urlpython')=='on':
            urlpython=True
        if request.form.get('menu')=='on':
            esMenu=True
        menu.nombre        = request.form['nombre']
        menu.opcionpadreid = opcionpadreid
        menu.url           = request.form['url']
        menu.urlpython     = urlpython
        menu.menu          = esMenu
        menu.icono         = request.form['icono']
        menu.orden         = request.form['orden']
        menu.descripcion   = request.form['descripcion']
        #print(objeto.__dict__)
        #print("update")
        objeto_update=menu.update()
        #print(objeto.__dict__)
        #If post.update does not return an error
        if not objeto_update:
            flash(app.config['UPD_SUCC'],"success")
            return redirect(url_for('menu.menu_index'))
        else:
            error=objeto_update
            flash(error,"danger")

    '''
    menuPadre = aliased(Menu)
    opciones= Menu.query\
    .with_entities(Menu.uuid,Menu.nombre,menuPadre.nombre.label("opcionpadre"))\
    .filter(Menu.deleted==False)\
    .filter(Menu.uuid!=id)\
    .outerjoin(menuPadre,menuPadre.id==Menu.opcionpadreid)\
    .order_by(case([(Menu.opcionpadreid==None,0)],else_=1),menuPadre.orden,Menu.nombre).all()
    '''            
    opcionesMenu = arbolMenu(None)
    return render_template('menu/add.html',  menu=menu,extras=extras,opcionesMenu=opcionesMenu)


@menu.route('/menu/delete' , methods=['POST', 'GET'])
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
    menu =views.regresaporuuid(Menu,objid,g.user.id)
    menu.deleted = True
    menu.update()
    msn=app.config['DEL_SUCC']

    #,'uuid':razondelet
    return jsonify({'estatus':'ok','msn':msn})

def arbolMenu(opcionpadreid):
    #funcion para regresar el arbol jerarquico de opciones
    #regresamos el arbol de fases, anidando los hijos a los nodos padres recursivamente
    diccionario=[]
    diccionario= views.arbol_jerarquia(Menu,Menu.opcionpadreid,opcionpadreid\
    ,[Menu.orden,Menu.nombre],and_(1==1),0)
    #print (jsonify({'estatus':diccionario}))
    #print ("diccionario",diccionario)
    
    #print ("app_json",app_json)


    #regresamos las fases como un arreglo unidimensional, concatenando los nombres de los padres
    etapasplano = views.arregloAnidadoArrgloUnidimensional(diccionario,"",0,"")
    
    #print(etapasplano)    
    return etapasplano