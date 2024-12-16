from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from plataforma.routes import register_routes
# Inicializa as variáveis globais
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Cria o objeto Flask
    app = Flask(__name__)

    # Configurações do banco de dados PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Marcal1!@localhost:5432/nicchio'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'kajsnbdpiosh2903'

    # Inicializa o db e o migrate
    db.init_app(app)
    migrate.init_app(app, db)

    # Importa e registra as rotas após a criação do app
    from plataforma.routes import register_routes
    register_routes(app)

    return app
