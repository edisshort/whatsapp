from dotenv import load_dotenv

load_dotenv()

import os
from pathlib import Path

from flask import Flask

from config import Config
from extensions import csrf, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Path(app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")).parent.mkdir(parents=True, exist_ok=True)

    db.init_app(app)
    csrf.init_app(app)

    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.connect import connect_bp
    from routes.contacts import contacts_bp
    from routes.compose import compose_bp, campaigns_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(connect_bp)
    app.register_blueprint(contacts_bp)
    app.register_blueprint(compose_bp)
    app.register_blueprint(campaigns_bp)

    @app.context_processor
    def inject():
        return {"engine_name": Config.ENGINE_LABEL, "engine_mock": Config.ENGINE_MOCK}

    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    application = create_app()
    application.run(host=Config.HOST, port=Config.PORT, debug=os.getenv("FLASK_DEBUG") == "1")
