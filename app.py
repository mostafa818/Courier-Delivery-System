from flask import Flask
from extensions import db
from routes import main
import os

def create_app():
    app = Flask(__name__)
    
    # Database configuration - using absolute path to be safe or relative to instance path
    # For simplicity in this scratch env, we'll store it in the same dir
    basedir = os.path.abspath(os.path.dirname(__file__))
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'test.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
