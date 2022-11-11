"""Database models."""
from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

try:
    from dashboard.flask_app import *
except:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tests.db'
    print('creating new DB in dashboard/modules/connect..')
    db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    '''
    User account model
    '''

    __tablename__= 'Users'
    __table_args__  = {'extend_existing': True}
    extend_existing=True
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    password = db.Column(db.String(200),
                         primary_key=False, unique=False, nullable=False)
    website = db.Column(db.String(60), index=False, unique=False, nullable=True)
    created_on = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    last_login = db.Column(db.DateTime, index=False, unique=False, nullable=True)
    last_protocol = db.Column(db.String(100), nullable=True, unique=False)

    def set_password(self, password):
        '''
        Create hashed password
        '''
        self.password = generate_password_hash(password, method="sha256")

    def check_password(self, password):
        '''
        Check hashed password
        '''
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f"<User {self.name}>"
