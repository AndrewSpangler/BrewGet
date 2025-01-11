import os
import datetime
import logging
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.datastructures import ImmutableDict
from ...main import db

PermissionsMap = {
    -1 : "EVERYONE",
    0 : "NO ACCESS",
    1 : "MACHINE",
    5 : "USER",
    10: "ADMIN",
    15: "OWNER",
}

class PermissionsLevel:
    EVERYONE = 1 # Everyong can access
    NO_ACCESS = 0 # No access
    USER = 5 # Data lookup pages
    ADMIN = 10 # Add and edit users
    OWNER = 15

class User(UserMixin, db.Model):
    """User object with flask_login UserMixin"""
    __tablename__ = "User"
    __bind_key__ = "user_db"
    id = db.Column(db.Integer, primary_key=True)
    permission_integer = db.Column(db.Integer, default=PermissionsLevel.USER)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    must_change_password = db.Column(db.Boolean, default=False)
    selected_theme = db.Column(db.String(100), default="default")
    def set_password(self, password:str) -> None:
        self.password = generate_password_hash(password)
    def check_password(self, password:str) -> bool:
        return check_password_hash(self.password, password)
    @property
    def is_admin(self):
        return self.permission_integer >= PermissionsLevel.ADMIN

class SecretKey(db.Model):
    __tablename__ = "SecretKey"
    __bind_key__ = "user_db"
    """Table to store wtf secret key and flask secret key"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(24), nullable=False)

def init_db(app):
    with app.app_context():
        logging.info("Initializing Users db")
        db.create_all(bind_key=["user_db"])
        # Check if secret key exists in database, generate one if necessary
        # This key is used to maintain user sessions across application restarts
        # It is also used to reduce the chance of impersonation attacks
        secret_key = SecretKey.query.get(1)
        if secret_key is None:
            key_value = os.urandom(24)
            secret_key = SecretKey(id=1, key=key_value)
            db.session.add(secret_key)
            db.session.commit()
        key_value = secret_key.key
        app.secret_key = key_value
        # Do the same as described above for flask wtf forms CSRF protection 
        wtf_secret_key = SecretKey.query.get(2)
        if wtf_secret_key is None:
            wtf_key_value = os.urandom(24)
            wtf_secret_key = SecretKey(id=2, key=wtf_key_value)
            db.session.add(wtf_secret_key)
            db.session.commit()
        wtf_key_value = wtf_secret_key.key
        app.config["WTF_CSRF_SECRET_KEY"] = wtf_key_value
        db.session.commit()

        app.models.user = ImmutableDict()
        for obj in (User, SecretKey, PermissionsLevel):
            setattr(app.models.user, obj.__name__, obj)
        app.models.user.PermissionsMap = PermissionsMap
    