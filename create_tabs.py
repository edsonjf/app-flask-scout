import os
from db import db
from models import *  # importa seus modelos para criar as tabelas
from main import app

with app.app_context():
    db.drop_all()
    db.create_all()
    print('Tabelas criadas com sucesso..')
