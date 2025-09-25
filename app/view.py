from app import app, db
from app.models import User

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_required, logout_user, current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    nome = StringField('nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Enviar')
    


@app.route('/')
@login_required
def homepage():    
    return render_template('index.html')

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage.html'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.senha == form.senha.data:
            login_user(user)
            return redirect(url_for('homepage'))
        else:
            flash('Login failed. Check your email and password.', 'danger')
        
    return render_template('login.html', form=form)

@app.route('/Cadastro')
def cadastro

@app.route('/Sair')
def logout():
    logout_user()
    return redirect(url_for('login'))