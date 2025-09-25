from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String)
    senha = db.Column(db.String)
    isAdmin = db.Column(db.Boolean)
    reservaUser = db.relationship('Reserva', backref='user', lazy=True)

class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String)
    reservaCliente = db.relationship('Reserva', backref='cliente', lazy=True)

class Pacote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destino = db.Column(db.String)
    periodo = db.Column(db.String)
    categoria = db.Column(db.String)
    preco = db.Column(db.Float)
    vagas = db.Column(db.Integer)
    disponivel = db.Column(db.Boolean)
    reservasPacote = db.relationship('Reserva', backref='pacote', lazy=True)

class Reserva(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_cliente = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    id_pacote = db.Column(db.Integer, db.ForeignKey('pacote.id'))
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))
    isActivated = db.Column(db.Boolean)