from app import app, db
from app.models import User, Pacote, Cliente, Reserva

from flask import render_template, redirect, url_for, flash
from flask_login import login_required, login_required, logout_user, current_user, login_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, FloatField, IntegerField
from wtforms.validators import DataRequired
from wtforms_sqlalchemy.fields import QuerySelectField

from functools import wraps

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.isAdmin:
            flash('Acesso negado. Você precisa ser um administrador.', 'danger')
            return redirect(url_for('homepage'))
        return f(*args, **kwargs)
    return decorated_function

def client_query():
    return Cliente.query

class ReservaForm(FlaskForm):
    cliente = QuerySelectField('Selecione o Cliente', 
                               query_factory=client_query, 
                               get_label='nome', 
                               allow_blank=False,
                               validators=[DataRequired()])
    btnSubmit = SubmitField('Confirmar Reserva')

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

class ReservaForm(FlaskForm):
    cliente = QuerySelectField('Selecione o Cliente', 
                               query_factory=client_query, 
                               get_label='nome', 
                               allow_blank=False,
                               validators=[DataRequired()])
    btnSubmit = SubmitField('Confirmar Reserva')

@app.route('/')
@login_required
def homepage():
    pacotes = Pacote.query.all()
    clientes = Cliente.query.all()
    return render_template('index.html', pacotes=pacotes, clientes=clientes)

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
    
    return render_template('cadastrar_cliente.html', form=form)

@app.route('/NovoPacote', methods=['GET', 'POST'])
def cadastrar_pacote():
    form = PacoteForm()
    
    if form.validate_on_submit():
        new_pacote = Pacote(
            destino=form.destino.data,
            periodo=form.periodo.data,
            categoria=form.categoria.data,
            preco=form.preco.data,
            vagas=form.vagas.data,
            disponivel=True
        )

        db.session.add(new_pacote)
        db.session.commit()
        return redirect(url_for('homepage'))

    return render_template('cadastrar_pacote.html', form=form)

@app.route('/reservar/<int:id_pacote>', methods=['GET', 'POST'])
@login_required
def criar_reserva(id_pacote):
    pacote = Pacote.query.get_or_404(id_pacote)
    form = ReservaForm()

    if form.validate_on_submit():
        if pacote.vagas > 0:
            cliente_selecionado = form.cliente.data
            
            nova_reserva = Reserva(
                id_cliente=cliente_selecionado.id,
                id_pacote=pacote.id,
                id_user=current_user.id
            )
            
            pacote.vagas -= 1
            
            db.session.add(nova_reserva)
            db.session.commit()
            
            flash(f'Reserva para {pacote.destino} confirmada para o cliente {cliente_selecionado.nome}!', 'success')
            return redirect(url_for('homepage'))
        else:
            flash('Não há vagas disponíveis para este pacote.', 'danger')
            return redirect(url_for('homepage'))
            
    return render_template('criar_reserva.html', form=form, pacote=pacote)

@app.route('/gerenciar_reservas')
@login_required
def gerenciar_reservas():
    # Usamos o .join() para poder acessar os nomes do cliente e pacote no template
    reservas = db.session.query(Reserva).join(Cliente).join(Pacote).all()
    return render_template('gerenciar_reservas.html', reservas=reservas)


# Rota para cancelar uma reserva
@app.route('/cancelar_reserva/<int:id_reserva>', methods=['POST'])
@login_required
def cancelar_reserva(id_reserva):
    reserva = Reserva.query.get_or_404(id_reserva)
    
    if reserva.isActivated:
        reserva.isActivated = False
        reserva.pacote.vagas += 1 # Devolve a vaga para o pacote
        db.session.commit()
        flash('Reserva cancelada com sucesso!', 'info')
    else:
        flash('Esta reserva já estava cancelada.', 'warning')
        
    return redirect(url_for('gerenciar_reservas'))