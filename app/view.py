from app import app, db
from app.models import User, Pacote, Cliente

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_required, logout_user, current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired

class UserForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    btnSubmit = SubmitField('Confirmar')
    
class ClienteForm(FlaskForm):
    nome = StringField('Cliente', validators=[DataRequired()])
    cpf = StringField('CPF', validators=[DataRequired()])
    btnSubmit = SubmitField('Confirmar')
    
class PacoteForm(FlaskForm):
    destino = StringField('Destino', validators=[DataRequired()])
    periodo = StringField('Periodo', validators=[DataRequired()])
    categoria = StringField('Categoria', validators=[DataRequired()])
    preco = FloatField('Preço', validators=[DataRequired()])
    vagas = IntegerField('Numero de Vagas Disponiveis', validators=[DataRequired()])
    btnSubmit = SubmitField('Confirmar')

@app.route('/')
@login_required
def homepage():
    return render_template('index.html')

@app.route('/Login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.senha == form.senha.data:
            login_user(user)
            return redirect(url_for('homepage'))
        else:
            flash('Não deu o certo, verifique o email e a senha', 'danger')
        
    return render_template('login.html', form=form)

@app.route('/Cadastro', methods=['GET', 'POST'])
def cadastro():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    
    form = UserForm()
    
    if form.validate_on_submit():
        user_existente = User.query.filter_by(email=form.email.data).first()
        if user_existente:
            flash('Este usuario já existe!', 'danger')
            return redirect(url_for('cadastro'))
        new_user = User(
            email=form.email.data,
            senha=form.senha.data,
            isAdmin=False
        )
            
        db.session.add(new_user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso! Faça o login.', 'success')
        return redirect(url_for('homepage'))
        
    return render_template('cadastro.html', form=form)

@app.route('/Sair')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/NovoCliente', methods=['GET', 'POST'])
def cadastrar_cliente():
    form = ClienteForm()
    
    if form.validate_on_submit():
        new_cliente = Cliente(
            nome=form.nome.data,
            cpf=form.cpf.data
        )
        
        db.session.add(new_cliente)
        db.session.commit()
        return redirect(url_for('homepage'))
    
    return render_template('cadastrar_cliente.html')

@app.route('/NovoPacote', methods=['GET', 'POST'])
def cadastrar_pacote():
    form = PacoteForm()
    
    if form.validate_on_submit():
        new_pacote = Pacote(
            destino=form.destino.data,
            periodo=form.periodo.data,
            categoria=form.categoria.data,
            preco=form.preco.data,
            vagas=form.vaga.data,
            disponivel=True
        )

        db.session.add(new_pacote)
        db.session.commit()
        return redirect(url_for('homepage'))

    return render_template('cadastrar_pacote.html', form=form)