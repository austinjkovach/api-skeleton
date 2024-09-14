from flask import Flask, jsonify
from src.extensions import db
from src.endpoints import home
from src.seeds import seed_database



def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    db.init_app(app)
    # We are doing a create all here to set up all the tables. Because we are using an in memory sqllite db, each
    # restart wipes the db clean, but does have the advantage of not having to worry about schema migrations.
    with app.app_context():
        db.create_all()
        seed_database(app, db)
    app.register_blueprint(home)
    return app