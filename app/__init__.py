from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    # Load environment variables from .env file
    load_dotenv()
    
    app = Flask(__name__)
    
    # Needs to be imported inside or after app context loads env
    from app.models.db import init_db
    
    with app.app_context():
        # Only initialize DB if DATABASE_URL is set, avoiding crash during dev setups without DB
        if os.getenv("DATABASE_URL"):
            try:
                init_db()
            except Exception as e:
                print(f"Warning: Database connection failed. Details: {e}")
        else:
            print("Warning: DATABASE_URL not found in environment.")

    from app.routes.views import views_bp
    from app.routes.api import api_bp
    
    app.register_blueprint(views_bp)
    app.register_blueprint(api_bp)

    return app
