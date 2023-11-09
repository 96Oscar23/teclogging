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


class TipoFuenteDatoMapa(db.Model):
    __tablename__ = 'tipofuentedatomapa'
    id = Column(db.Integer, primary_key=True)

    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
    tipofuentedatoid = Column(Integer, db.ForeignKey(
        'tipofuentedato.id'), nullable=True)
    tipofuentedato = relationship(
        "TipoFuenteDato", foreign_keys=[tipofuentedatoid])
    metrica = Column(Integer, db.ForeignKey('metrica.id'), nullable=True)
    metricaid = relationship("Metrica", foreign_keys=[metrica])
    tipovariable = Column(Integer, db.ForeignKey(
        'tipovariable.id'), nullable=True)
    tipovariableid = relationship("TipoVariable", foreign_keys=[tipovariable])
    inicio = Column(db.String(255), nullable=True)
    fin = Column(db.String(255), nullable=True)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, tipofuentedatoid, metricaid, tipovariableid, inicio, fin):
        self.tipofuentedatoid = tipofuentedatoid
        self.metricaid = metricaid
        self.tipovariableid = tipovariableid
        self.inicio = inicio
        self.fin = fin

    def add(self, tipofuentedatomapa):
        db.session.add(tipofuentedatomapa)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, tipofuentedatomapa):
        db.session.delete(tipofuentedatomapa)
        return session_commit()


class TipoVariable(db.Model):
    __tablename__ = 'tipovariable'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))

    nombre = Column(db.String(255), nullable=False)
    codigo = Column(db.String(255), nullable=False)
    descripcion = Column(db.String(255), nullable=True)
    longitud = Column(db.Integer, nullable=True)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, nombre, codigo, descripcion, longitud):
        self.nombre = nombre
        self.codigo = codigo
        self.descripcion = descripcion
        self.longitud = longitud

    def add(self, tipo):
        db.session.add(tipo)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, tipo):
        db.session.delete(tipo)
        return session_commit()


class Metrica(db.Model):
    __tablename__ = 'metrica'
    id = Column(db.Integer, primary_key=True)
    nombre = Column(db.String(255), nullable=False)
    codigo = Column(db.String(255), nullable=False)
    descripcion = Column(db.String(255), nullable=True)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)
    unidadmedida = Column(Integer, db.ForeignKey(
        'unidadmedida.id'), nullable=True)
    unidadmedidaid = relationship("UniadMedida", foreign_keys=[unidadmedida])

    def __init__(self, nombre, codigo, descripcion, unidadmedidaid):
        self.nombre = nombre
        self.codigo = codigo
        self.descripcion = descripcion
        self.unidadmedidaid = unidadmedidaid

    def add(self, metrica):
        db.session.add(metrica)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, metrica):
        db.session.delete(metrica)
        return session_commit()


class UniadMedida(db.Model):
    __tablename__ = 'unidadmedida'
    id = Column(db.Integer, primary_key=True)

    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    codigo = Column(db.String(255), nullable=False)
    descripcion = Column(db.String(255), nullable=True)
    simbolo = Column(db.String(255), nullable=True)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)
    fecha_deleted = Column(db.TIMESTAMP, nullable=True)

    def __init__(self, nombre, codigo, descripcion, simbolo):
        self.nombre = nombre
        self.codigo = codigo
        self.descripcion = descripcion
        self.simbolo = simbolo

    def add(self, unidadmedida):
        db.session.add(unidadmedida)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, unidadmedida):
        db.session.delete(unidadmedida)
        return session_commit()


class TipoFuenteDato(db.Model):
    __tablename__ = 'tipofuentedato'
    id = Column(db.Integer, primary_key=True)

    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    codigo = Column(db.String(255), nullable=False)
    direccion = Column(db.String(255), nullable=True)
    puerto = Column(db.String(255), nullable=True)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)
    fuentedato = Column(db.Integer, db.ForeignKey(
        'fuentedato.id'), nullable=True)
    fuentedatoid = relationship("FuenteDato", foreign_keys=[fuentedato])

    def __init__(self, nombre, codigo, direccion, puerto, fuentedatoid):
        self.nombre = nombre
        self.codigo = codigo
        self.direccion = direccion
        self.puerto = puerto
        self.fuentedatoid = fuentedatoid

    def add(self, tipofuentedato):
        db.session.add(tipofuentedato)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, tipofuentedato):
        db.session.delete(tipofuentedato)
        return session_commit()

# *FuenteDato
class FuenteDato(db.Model):
    __tablename__ = 'fuentedato'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    codigo = Column(db.String(255), nullable=False)
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

    def __init__(self, nombre, codigo):
        self.nombre = nombre
        self.codigo = codigo

    def add(self, tipodatos):
        db.session.add(tipodatos)
        return session_commit()

    def update(self):
        return session_commit()

    def delete(self, tipodatos):
        db.session.delete(tipodatos)
        return session_commit()


# *usuario usuarios del sistema
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
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
    fecha_creacion = Column(
        db.TIMESTAMP, server_default=db.func.current_timestamp())
    deleted = Column(db.Boolean, server_default='0', default=False)

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

        # s = Serializer(app.config['SECRET_KEY'], expires_in=expiration)
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
        # print ("tocen generado",token)
        # print ("token generado",token)
        # print(jwt.decode(token,key=app.config['SECRET_KEY'],algorithm="HS256"))
        return token

    @staticmethod
    def verify_auth_token(token):
        # print('verify_auth_token',token)
        # s = Serializer(app.config['SECRET_KEY'])
        try:
            # data = s.loads(token)
            data = jwt.decode(
                token,
                app.config['SECRET_KEY'],
                "HS256"
            )
            # print("data",data)
        except:
            # rint("error verify_auth_token")
            return None    # valid token, but expired
        # print ("verify_auth_token",data.get('confirm'))
        # if data.get('confirm') != self.id:
        #    return False
        user = Usuario.query.get(data.get('confirm'))
        return user

    def serialize(self):
        return {
            "id": self.id,
            "uuid": self.uuid,
            "nombre": self.nombre

        }

# *RolMenu


class RolMenu(db.Model):
    __tablename__ = 'rolmenu'
    id = Column(db.Integer, primary_key=True)
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
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
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
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
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
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

    def __init__(self, nombre, opcionpadreid, url, urlpython, menu, icono, orden, descripcion):
        self.nombre = nombre
        self.opcionpadreid = opcionpadreid
        self.url = url
        self.urlpython = urlpython
        self.menu = menu
        self.icono = icono
        self.orden = orden
        self.descripcion = descripcion

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
    uuid = db.Column(UUID(as_uuid=True), unique=True,
                     server_default=sqlalchemy.text("uuid_generate_v4()"))
    nombre = Column(db.String(255), nullable=False)
    valor = Column(db.String(255), nullable=False)
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
        # print(reason)
