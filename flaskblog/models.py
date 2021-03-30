from enum import IntEnum
from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from flaskblog import db, login_manager
from flask_login import UserMixin
from sqlalchemy import func, create_engine
from sqlalchemy.event import listen
from geoalchemy2 import Geometry
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape

# Extends Enum so it can be used in WTForms
class FormEnum(IntEnum):
    @classmethod
    def choices(cls):
        return [(choice, choice.name) for choice in cls]

    @classmethod
    def coerce(cls, item):
        return cls(int(item)) if not isinstance(item, cls) else item

    def __str__(self):
        return str(self.value)

class TypeOfService(FormEnum):
    Offer = 1
    Request = 2

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(20), nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    about_me = db.Column(db.String(1000), nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)    
    posts = db.relationship('Post', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.first_name}', '{self.last_name}', '{self.phone_number}', '{self.address}', '{self.about_me}', '{self.created_at}', '{self.last_login}')"


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(Geometry("POINT", srid=4326, dimension=2, management=True))
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    type_of_service = db.Column(db.Integer, nullable=False)
    category = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def get_service_location_lat(self):
        point = to_shape(self.location)
        return point.x

    def get_service_location_lng(self):
        point = to_shape(self.location)
        return point.y

    def __repr__(self):
        return f"Post('{self.title}', '{self.date_posted}', '{self.location}', '{self.content}')"

    @staticmethod
    def point_representation(lat, lng):
        point = "POINT(%s %s)" % (lat, lng)
        wkb_element = WKTElement(point, srid=4326)
        return wkb_element

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.profile.user.username,
            "title": self.title,
            "location": {
                "lat": self.get_service_location_lat(),
                "lng": self.get_service_location_lng(),
            },
            "content": self.content,
            "service": self.service,
        }

    @staticmethod
    def get_services_within_radius(lat, lng, radius):
        """Return all service posts within a given radius (in meters)"""
        return Post.query.filter(
            func.PtDistWithin(Post.location, func.MakePoint(lat, lng, 4326), radius)
        ).all()