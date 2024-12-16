from plataforma import db
from datetime import datetime
from plataforma import app

class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(200), nullable=False)
    data_envio = db.Column(db.DateTime, default=db.func.now(), nullable=False)