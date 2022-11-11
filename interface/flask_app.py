'''
flask app
'''

from interface.modules.pages.define_all_pages import *

# DataBase
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user

from flask import Flask, render_template, request, redirect, url_for, session
# flask_socketio version 5.0.1
from flask_socketio import SocketIO, emit
import os
op = os.path
opd, opb, opj = op.dirname, op.basename, op.join

app = Flask(__name__)
app.config['UPLOADED_PATH'] = opj(os.getcwd(), 'interface', 'upload')
app.config['PIC_PATH'] = opj(os.getcwd(), 'interface',
                             'static', 'curr_pic', 'frame0.png')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SECRET_KEY'] = 'F34TF$($e34D'
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///CyberScoPy.db'
socketio = SocketIO(app)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# DataBase
db = SQLAlchemy(app)
# admin = Admin(app)
login_manager = LoginManager()

db.init_app(app)
login_manager.init_app(app)
