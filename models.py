from db import db
from flask_login import UserMixin

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(30), unique=True)
    senha = db.Column(db.String(128))
    
class Jogador(db.Model):
    __tablename__ = 'jogadores'
    
    id = db.Column(db.Integer, primary_key=True)
    apelido = db.Column(db.String(100), nullable=False)
    nome = db.Column(db.String(150), nullable=True)
    foto_binaria = db.Column(db.LargeBinary, nullable=True)
    posicao = db.Column(db.String(80), nullable=True)
    clube = db.Column(db.String(100), nullable=True)
    nascimento = db.Column(db.Date, nullable=True)
    nacionalidade = db.Column(db.String(100), nullable=True)
    naturalidade = db.Column(db.String(100), nullable=True)
    pe = db.Column(db.String(20), nullable=True)
    altura = db.Column(db.Float, nullable=True)
    peso = db.Column(db.Float, nullable=True)
    
    # 1:N - um jogador tem várias linhas na tabela_geral
    geral = db.relationship('Tabela_geral', backref='jogador_ref', lazy=True)
    carreira = db.relationship('Tabela_carreira', backref='jogador_ref', lazy=True)
    jogos = db.relationship('Tabela_jogos_temporada', backref='jogador_ref', lazy=True)
    
class Tabela_geral(db.Model):
    __tablename__ = 'tabela_geral'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    
    cod_jogador = db.Column(db.Integer, nullable=False)
    competicao = db.Column(db.String(50), nullable=True)
    jogos = db.Column(db.Integer, nullable=True)
    minutos= db.Column(db.Integer, nullable=True)
    gols= db.Column(db.Integer, nullable=True)
    assistencias = db.Column(db.Integer, nullable=True)
    
    
class Tabela_carreira(db.Model):
    __tablename__ = 'tabela_carreira'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    
    cod_jogador = db.Column(db.Integer, nullable=False)
    ano = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(40), nullable=True)
    jogos = db.Column(db.Integer, nullable=True)
    gols= db.Column(db.Integer, nullable=True)
    assistencias = db.Column(db.Integer, nullable=True)
    
class Tabela_jogos_temporada(db.Model):
    __tablename__ = 'tabela_jogos_temporada'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    jogador_id = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    
    cod_jogador = db.Column(db.Integer, nullable=False)
    resultado = db.Column(db.String(3), nullable=True)
    data = db.Column(db.Date, nullable=True)
    competicao= db.Column(db.String(40), nullable=True)
    fase = db.Column(db.String(20), nullable=True)
    clube = db.Column(db.String(50), nullable=True)
    local = db.Column(db.String(20), nullable=True)
    adversario= db.Column(db.String(50), nullable=True)
    placar = db.Column(db.String(6), nullable=True)
    minutagem = db.Column(db.Integer, nullable=True)
    tempo_substituicao = db.Column(db.String(10), nullable=True)
    amarelo= db.Column(db.Boolean, nullable=True)
    vermelho = db.Column(db.Boolean, nullable=True)
    gols= db.Column(db.String(3), nullable=True)
    assistencias = db.Column(db.String(3), nullable=True)