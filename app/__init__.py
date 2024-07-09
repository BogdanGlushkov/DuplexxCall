from flask import Flask
from .extensions import db
from config import Config


from .User.views import user as user_blueprint
# from .module__2.views import module2 as module2_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # 
    with app.app_context():
        db.create_all()
    
    # 

    app.register_blueprint(user_blueprint)
    # app.register_blueprint(module2_blueprint)

    return app
