from flask import Flask
from .momentjs import momentjs
from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
import os
from flask_migrate import Migrate

app = Flask(__name__)
app.config['TOKEN_EXP_TIME'] = 86400      
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
app.secret_key="fheijeiojfeE!#!"
app.config['SQLALCHEMY_DATABASE_URI']= 'postgresql://teclogging:zr{X7!16@104.248.201.207:5432/teclogging' #desarrollo


app.config['SECRET_KEY'] = 'Lfofeoje8e#3!&'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False     
#app.config['SQLALCHEMY_ECHO'] = True


ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif','GIF','PNG','JPG','JPEG','csv'])
app.config['ALLOWED_EXTENSIONS'] = ALLOWED_EXTENSIONS  


ROOTPATH = os.getcwd()

serverpath = os.path.join(ROOTPATH, 'app')

app.config['SERVERPATH']    = serverpath
app.config['UPLOAD_FOLDER'] = os.path.join(serverpath,'static','images')
app.config['DOCTOSPATH']    = os.path.join(serverpath,'documentos')


app.config['TIME1']      = 'Etc/GMT+6'
app.config['LOCAL_TIME'] = 'America/Mexico_City'
app.config['DOMINIO']    = 'http://localhost:5555'

app.config['ADD_SUCC']    = 'Registro grabado con éxito'  # .decode('utf-8')
app.config['UPD_SUCC']    = 'Registro modificado con éxito'  # .decode('utf-8')
app.config['DEL_SUCC']    = 'Registro eliminado con éxito'  # .decode('utf-8')
app.config['NOEXISTE']    = 'El registro no existe'  # .decode('utf-8')
app.config['DEL_CONFIRM'] = 'Desea eliminar el elemento?'  # .decode('utf-8')
app.config['ANSI_FORMAT'] = "%Y%m%d%H%M%SZ"
app.config['ISO_FORMAT']  = "%Y%m%d%H%M%S"
app.config['SAT_FORMAT']  = "%Y-%m-%dT%H:%M:%S"
app.config['NO_PERMISO_BORRAR']  = "No tienes privilegios suficientes"

#if platform.system()!='Windows':
    #app.config['PATHOPENSSL'] = "/usr/bin/openssl"
#else:
    #app.config['PATHOPENSSL'] = "C:\\software\\GnuWin32\\bin\\openssl.exe"


CORS(app)
auth = HTTPBasicAuth()


db = SQLAlchemy(app)
migrate = Migrate()

#db.init_app(app)
migrate = Migrate(app, db)

app.jinja_env.globals['momentjs'] = momentjs
app.jinja_env.filters['commafy'] = lambda v: "{:,.2f}".format(v)
from app import views
