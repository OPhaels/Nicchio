from plataforma import db
from datetime import datetime

class Contato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=True)
    senha = db.Column(db.String, nullable=True)
    telefone = db.Column(db.String, nullable=True)
    data_envio = db.Column(db.DateTime, default=datetime.utcnow())
    respondido = db.Column(db.Integer, default=0)