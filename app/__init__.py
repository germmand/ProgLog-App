import os
from flask import Flask, render_template, send_from_directory, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.handlers import db

config = {
    "development": "app.settings.DevelopmentConfig",
    "testing": "app.setting.TestingConfig",
    "production": "app.settings.ProductionConfig",
    "default": "app.settings.DevelopmentConfig"
}

def create_app():
    app = Flask(__name__)
    config_name = os.getenv('FLASK_CONFIGURATION', 'default')
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.errorhandler(404)
    def not_found(error):
        return render_template('404.html'), 404

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route('/', methods=['GET'])
    def root():
        return redirect(url_for('auth.signin'))
    
    from app.mod_auth.controllers import mod_auth as auth_module
    from app.mod_tests.controllers import mod_tests as tests_module
    
    app.register_blueprint(auth_module)
    app.register_blueprint(tests_module)

    return app
