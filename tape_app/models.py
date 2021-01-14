from tape_app import db, login_manager
from flask import current_app as app
from flask_login import UserMixin
from datetime import datetime
import jwt
from time import time

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(60), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    sessions = db.relationship('Session', backref='user', lazy=True)
    first_name = db.Column(db.String(60), default="")
    last_name = db.Column(db.String(60), default="")
    text_notif = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(60), nullable=False, default='user')
    credits = db.Column(db.Integer, default=0)

    def get_reset_token(self, expires_in=1800):
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def verify_reset_token(token):
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except Exception:
            return
        return User.query.get(id)

    def __repr__(self):
        return f"User('{self.id}','{self.username}', '{self.email}', '{self.image_file}', '{self.role}')"

class Session(db.Model):
    __tablename__ = 'sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_name = db.Column(db.String(40), nullable=False)
    zip_file_name = db.Column(db.String(40))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    submitted = db.Column(db.Boolean, default=False)
    credits = db.Column(db.Integer, default=0)

class Sound(db.Model):
    __tablename__ = 'sounds'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('sessions.id'))
    file_name = db.Column(db.String(50), nullable=False)
    options = db.Column(db.String(50), nullable=False)
    machine = db.Column(db.String(50), default='Teac A-2300s (Reel 2 Reel)')
    credits = db.Column(db.Integer, default=0)
    session = db.relationship(
        'Session',
        backref=db.backref('sounds', lazy='dynamic', collection_class=list)
    )

class FreeCreditCode(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), nullable=False)
    credits = db.Column(db.Integer, default=0)
