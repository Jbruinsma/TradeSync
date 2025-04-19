from flask import Flask
from app.models.avlTree.avl_tree import AVLTree
import os

# Global database instance
user_db = AVLTree()

def create_app(config=None):
    app = Flask(__name__)
    
    if config:
        app.config.from_object(config)
    
    # Create database directory if it doesn't exist
    db_dir = 'database'
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    db_path = os.path.join(db_dir, 'user_database.pkl')
    
    # Load database from file if it exists
    if os.path.exists(db_path):
        try:
            user_db.load_from_file(db_path)
            print("Database loaded successfully")
        except Exception as e:
            print(f"Error loading database: {e}")
    else:
        print("Starting with new empty database")
    
    # Register blueprints
    from .routes.pages import page
    from .routes.auth import auth
    from .routes.api import api
    app.register_blueprint(page)
    app.register_blueprint(auth)
    app.register_blueprint(api)
    
    @app.teardown_appcontext
    def save_database(exception=None):
        """Save database on app shutdown"""
        try:
            user_db.save_to_file(db_path)
        except Exception as e:
            print(f"Error saving database: {e}")
    
    return app