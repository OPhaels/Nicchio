from plataforma import app
from flask import render_template, url_for, request

@app.route('/')
def login():
    return render_template("login.html")

@app.route('/dash/')
def dashboard():
    usuario = 'raphael'
    return render_template("dashboard.html", usuario=usuario)

@app.route('/profile/')
def profile():
    usuario = 'raphael'
    return render_template("profile.html", usuario=usuario)

@app.route('/cadastro/')
def cadastro():
    return render_template("cadastro.html")