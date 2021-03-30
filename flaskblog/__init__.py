from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flaskblog.config import Config
from sqlalchemy import create_engine
from sqlalchemy import event
from sqlalchemy.sql import select
from sqlalchemy.pool import Pool


db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def load_spatialite(dbapi_conn, connection_record):
	dbapi_conn.enable_load_extension(True)
    # Below load extension works inside Docker image
	dbapi_conn.execute('SELECT load_extension("mod_spatialite")')

event.listen(Pool, "connect", load_spatialite)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SPATIALITE_LIBRARY_PATH'] = '/usr/local/lib/mod_spatialite.dylib'       

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from flaskblog.users.routes import users
    from flaskblog.posts.routes import posts
    from flaskblog.main.routes import main
    from flaskblog.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    # Uncomment this to reinitialize the database
    # print('reinitializing the database. All data is dropped, and data structures recreated')
    # with app.app_context():
    #     db.drop_all()
    #     # moved InitSpatialMetaData() here so you only run this expensive operation once, 
    #     # and not every time you load the sqlite extension.
    #     # This command creates all additional views and tables required by
    #     # spatialite and you need to run it only once (and repeat if you drop_all)
    #     db.engine.execute('SELECT InitSpatialMetaData()') 
    #     db.create_all()

    return app
