from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

load_dotenv()
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    from app.routes.api import api
    app.register_blueprint(api, url_prefix="/api")
    @app.errorhandler(404)
    def not_found(_): return jsonify(error="Recurso no encontrado"), 404
    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        return jsonify(error="Error interno del servidor"), 500
    return app
