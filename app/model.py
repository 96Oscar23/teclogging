from sqlalchemy.sql.expression import text
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy
from sqlalchemy.orm import relationship, backref
from sqlalchemy import Column, Integer, DateTime, Float, Table, desc, Boolean, Text, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from passlib.apps import custom_app_context as pwd_context
from app import db
from app import app
import jwt
from datetime import datetime
from dateutil.relativedelta import relativedelta
import uuid


#*empresausuariorol 
class EmpresaUsuarioRol(db.Model):
    __tablename__ = 'empresausuariorol'
    id = Column(db.Integer, primary_key=True)
    empresaid= Column(Integer, db.ForeignKey('empresa.id'),nullable=False)
    empresa = relationship("Empresa",foreign_keys=[empresaid])
    usuarioid= Column(Integer, db.ForeignKey('usuario.id'),nullable=False)
    usuario = relationship("Usuario",foreign_keys=[usuarioid])
    rolid= Column(Integer, db.ForeignKey('rol.id'),nullable=False)
    rol = relationship("Rol",foreign_keys=[rolid])
    fecha_creacion=Column(db.TIMESTAMP,server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean,server_default='f', default=False)
    fecha_deleted = Column(db.TIMESTAMP,nullable=True)
    def __init__(self,empresaid,usuarioid, rolid):
        self.empresaid = empresaid
        self.rolid = rolid
        self.usuarioid = usuarioid
       
    def add(self,usuariorol):
        db.session.add(usuariorol)
        return session_commit()
 
    def update(self):
        return session_commit()
 
    def delete(self,usuariorol):
        db.session.delete(usuariorol)
        return session_commit()  

# *Empresa
class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(250), nullable=False)
    codigo = Column(db.String(10), nullable=True)
    empresaid = Column(Integer, db.ForeignKey('empresa.id'), nullable=True)
    empresa = relationship("Empresa", foreign_keys=[empresaid])
    tipoempresaid = Column(Integer, db.ForeignKey(
        'tipoempresa.id'), nullable=False)
    tipoempresa = relationship("TipoEmpresa", foreign_keys=[tipoempresaid])
    direccion = Column(db.String(250), nullable=True)
    logo = Column(db.String(250), nullable=True)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)
    # Se agrega la siguiente columna por si se modifica el registro y asi avisar pymePOS
    modificacion = Column(db.TIMESTAMP)
    fecha_deleted = Column(db.TIMESTAMP, nullable=True)

    def __init__(self, nombre, empresaid, tipoempresaid, direccion, logo):
        self.nombre = nombre
        self.empresaid = empresaid
        self.tipoempresaid = tipoempresaid
        self.direccion = direccion
        self.logo = logo
        

    def add(self, empresa):
        empresa.modificacion = datetime.utcnow()
        db.session.add(empresa)
        return session_commit()

    def update(self):
        self.modificacion = datetime.utcnow()
        return session_commit()

    def delete(self, empresa):
        db.session.delete(empresa)
        return session_commit()

# *TipoEmpresa 1 empresa , 2 cliente, 3 proveedor, 4 empresa sucursal, 5 cliente sucursal, 6 proveedor sucursal
class TipoEmpresa(db.Model):
    __tablename__ = 'tipoempresa'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def add(self, tipoempresa):
        db.session.add(tipoempresa)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, tipoempresa):
        db.session.delete(tipoempresa)
        return session_commit()

# *usuario usuarios del sistema
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    correo = Column(db.String(255), nullable=False)
    password = Column(db.String(255), nullable=False)
    token_recuperar = Column(db.String(255), nullable=True)
    token_registro = Column(db.String(255), nullable=True)
    validado = Column(db.Boolean, server_default='0', default=False)
    correo_registro = Column(db.Boolean, server_default='0', default=False)
    activo = Column(db.Boolean, server_default='0', default=False)
    ultimo_login = Column(db.TIMESTAMP)
    rolid = Column(Integer, db.ForeignKey('rol.id'), nullable=True)
    rol = relationship("Rol", foreign_keys=[rolid])
    empresaloginid= Column(Integer, db.ForeignKey('empresa.id'),nullable=True) #ultima empresa a la que se logeo
    empresalogin = relationship("Empresa",foreign_keys=[empresaloginid])
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)
    fecha_deleted = Column(db.TIMESTAMP, nullable=True)
    # Se agrega la siguiente columna por si se modifica el registro y asi avisar pymePOS
    modificacion = Column(db.TIMESTAMP)

    def __init__(self, nombre, correo, password, token_registro, validado, correo_registro, activo, rolid):

        self.nombre = nombre
        self.correo = correo
        self.hash_password(password)
        self.token_registro = token_registro
        self.validado = validado
        self.correo_registro = correo_registro
        self.activo = activo
        self.rolid = rolid
        

    def add(self, usuario):
        usuario.modificacion = datetime.utcnow()
        db.session.add(usuario)
        return session_commit()

    def update(self):
        self.modificacion = datetime.utcnow()
        return session_commit()

    def delete(self, usuario):
        db.session.delete(usuario)
        return session_commit()

    def hash_password(self, password):
        self.password = pwd_context.encrypt(password)

    def hash_passwordcer(self, password):
        self.passwordcer = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)

    def generate_auth_token(self, expiration=86400):
        
        #s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
        token = jwt.encode(
            {
                "confirm": self.id,
                "exp": datetime.utcnow()
                       + relativedelta(seconds=expiration)
            },
            key=app.config['SECRET_KEY'],
            algorithm="HS256"
        )

        if isinstance(token, bytes):
            token = token.decode('utf-8')
        #print ("tocen generado",token)
        #print ("token generado",token)
        #print(jwt.decode(token,key=app.config['SECRET_KEY'],algorithm="HS256"))
        return token

    @staticmethod
    def verify_auth_token(token):
        #print('verify_auth_token',token)
        #s = Serializer(app.config['SECRET_KEY'])
        try:
            #data = s.loads(token)
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                "HS256"
            )
            #print("data",data)
        except:
            #rint("error verify_auth_token")
            return None    # valid token, but expired
        #print ("verify_auth_token",data.get('confirm'))
        #if data.get('confirm') != self.id:
        #    return False
        user = Usuario.query.get(data.get('confirm'))
        return user
    def serialize(self):
        return {
            "id"    : self.id,
            "uuid"  : self.uuid,
            "nombre": self.nombre

        }

# *RolMenu
class RolMenu(db.Model):
    __tablename__ = 'rolmenu'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    rolid = Column(Integer, db.ForeignKey('rol.id'), nullable=True)
    rol = relationship("Rol", foreign_keys=[rolid])
    menuid = Column(Integer, db.ForeignKey('menu.id'), nullable=True)
    menu = relationship("Menu", foreign_keys=[menuid])
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, rolid, menuid):
        self.rolid = rolid
        self.menuid = menuid

    def add(self, rol):
        db.session.add(rol)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, rol):
        db.session.delete(rol)
        return session_commit()

# *ROL
class Rol(db.Model):
    __tablename__ = 'rol'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, nombre):
        self.nombre = nombre

    def add(self, rol):
        db.session.add(rol)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, rol):
        db.session.delete(rol)
        return session_commit()

# *menu
class Menu(db.Model):
    __tablename__ = 'menu'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    descripcion = Column(db.String(255), nullable=True)

    opcionpadreid = Column(Integer, db.ForeignKey('menu.id'), nullable=True)
    opcionpadre = relationship("Menu", foreign_keys=[opcionpadreid])
    url = Column(db.String(255), nullable=True)
    urlpython = Column(db.Boolean, server_default='0', default=False)
    menu = Column(db.Boolean, server_default='0', default=False)
    icono = Column(db.String(255), nullable=True)
    orden = Column(db.Integer)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, nombre, opcionpadreid, url, urlpython, menu, icono, orden,descripcion):
        self.nombre        = nombre
        self.opcionpadreid = opcionpadreid
        self.url           = url
        self.urlpython     = urlpython
        self.menu          = menu
        self.icono         = icono
        self.orden         = orden
        self.descripcion   = descripcion

    def add(self, marca):
        db.session.add(marca)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, marca):
        db.session.delete(marca)
        return session_commit()


# *configuracion
class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True, server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    valor = Column(db.String(255), nullable=False)
    empresaid = Column(Integer, db.ForeignKey('empresa.id'), nullable=True)
    empresa = relationship("Empresa", foreign_keys=[empresaid])
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)
    fecha_deleted = Column(db.TIMESTAMP, nullable=True)

    def __init__(self, nombre, valor, empresaid):
        self.nombre = nombre
        self.valor = valor
        self.empresaid = empresaid

    def add(self, configuracion):
        db.session.add(configuracion)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, configuracion):
        db.session.delete(configuracion)
        return session_commit()

def session_commit():
    try:
        db.session.commit()
    except SQLAlchemyError as e:
        reason = str(e)
        #print(reason)
