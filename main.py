from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from db import db
from models import Usuario, Jogador, Tabela_geral, Tabela_carreira, Tabela_jogos_temporada
from funcoes import grafico_rosca, grafico_jogos_temporada, carregar_dados_db, converter_em_dict, grafico_carreira
import pandas as pd
from io import BytesIO
import base64
import os

app = Flask(__name__)
app.secret_key = 'teste'
lm = LoginManager(app)
lm.login_view = 'login'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
db.init_app(app)

with app.app_context():
    db.create_all()  # Garante que as tabelas existam
    
df = carregar_dados_db()
df['nascimento'] = pd.to_datetime(df['nascimento'])
# foto
df['foto_base64'] = df['foto_binaria'].apply(
    lambda b: base64.b64encode(b).decode('utf-8') if b else None
    )
        
@app.context_processor
def inject_now():
    from datetime import datetime
    return {'now': lambda: datetime.now()}

@lm.user_loader
def user_loader(id):
    usuario = db.session.query(Usuario).filter_by(id=id).first()
    return usuario

def foto(id):
    linha = df[df['id']==id]
    blob = linha.iloc[0]['foto_binaria']
    return send_file(BytesIO(blob), mimetype="image/png" )

@app.route('/')
@login_required
def home():
    total_jogadores = Jogador.query.count()
    jogadores = df[df['nascimento']>'1995'].head(50).sample(3)
    
    labels= ['sub20', 'sub23', '24-28', '29-33', '34+']
    valores= [len(df.loc[df['nascimento']> '2005']), len(df.loc[(df['nascimento']> '2002') & (df['nascimento']<'2005')]),
              len(df.loc[(df['nascimento']> '1997') & (df['nascimento']<'2002')]), 
              len(df.loc[(df['nascimento']> '1992') & (df['nascimento']<'1997')]),
              len(df.loc[(df['nascimento']<'1992')])]
    grafico = grafico_rosca(labels,valores)
    
    labels= ['Goleiros', 'Defensores', 'Meiocampos', 'Atacantes',]
    valores= [len(df.loc[df['posicao'].str.contains('Goleiro')]),
              len(df.loc[(df['posicao'].str.contains('Defensor') )]), 
              len(df.loc[(df['posicao'].str.contains('Meia') )]),
              len(df.loc[(df['posicao'].str.contains('Atacante'))])]
    grafico1 = grafico_rosca(labels,valores)  
    return render_template('home.html', total=total_jogadores, jogadores=jogadores, grafico=grafico, grafico1=grafico1)

@app.route('/pesquisa', methods=['GET', 'POST'])
@login_required
def pesquisa():
    # Captura de dados do formulário
    termo = request.args.get("nomeForm", "").strip().lower()
    posicao = request.args.get("posicaoForm", "").strip().lower()
    try:
        data_inicial = int(request.args.get("ano_inicio", 1995))
        data_final = int(request.args.get("ano_fim", 2007))
    except ValueError:
        data_inicial, data_final = 1995, 2007

    # Construção da query
    query = Jogador.query
    # Supondo que jogadores é uma lista de objetos Jogador
    anos = sorted({j.nascimento.year for j in Jogador.query.all() if j.nascimento})
    
    if termo:
        query = query.filter(
            (Jogador.apelido.ilike(f"%{termo}%")) |
            (Jogador.nome.ilike(f"%{termo}%"))
        )

    if posicao:
        query = query.filter(Jogador.posicao.ilike(f"%{posicao}%"))

    query = query.filter(Jogador.nascimento.between(f"{data_inicial}-01-01", f"{data_final}-12-31"))

    jogadores = query.all()
    opcoes = query.limit(8).all()
    
    selecionado = None
    tabela_geral = None
    tabela_carreira = None
    tabela_jogos_temporada = None
    grafico, grafico1 = None, None

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        if usuario_id:
            selecionado = Jogador.query.get(usuario_id)
            tabela_geral = Tabela_geral.query.filter_by(cod_jogador=usuario_id).all()
            tabela_carreira = Tabela_carreira.query.filter_by(cod_jogador=usuario_id).all()
            tabela_jogos_temporada = Tabela_jogos_temporada.query.filter_by(cod_jogador=usuario_id).all()
            grafico = grafico_jogos_temporada(usuario_id)
            grafico1 = grafico_carreira(usuario_id)
            tabela_carreira = [converter_em_dict(linha) for linha in tabela_carreira]
            # n_jogos = Tabela_geral.query.filter_by(cod_jogador=usuario_id).filter(Tabela_geral.competicao != None).count()
            # relacionado = tabela_jogos_temporada.count()
    for jogador in query.all():
        if jogador.foto_binaria:
            jogador.foto_base64 = base64.b64encode(jogador.foto_binaria).decode('utf-8')
        else:
            jogador.foto_base64 = None
            
            
    return render_template("pesquisa.html",
                           jogadores=jogadores,
                           termo=termo,
                           anos=anos,
                           opcoes=opcoes,
                           selecionado=selecionado,
                           tabela_geral=tabela_geral,
                           carreira=tabela_carreira,
                           jogos = tabela_jogos_temporada,
                           grafico= grafico,
                           grafico1 = grafico1,
                        #    relacionado = relacionado,
                           )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method =='POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        user = db.session.query(Usuario).filter_by(nome=nome, senha=senha).first()
        if user:
            login_user(user)
            return redirect(url_for('home'))
        flash('Nome ou senha incorreto!', 'danger')
        return redirect(url_for('login'))

@app.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if request.method == 'GET':
        return render_template('registrar.html')
    elif request.method == 'POST':
        nome = request.form['nomeForm']
        senha = request.form['senhaForm']
        
        novo_usuario = Usuario(nome=nome, senha=senha)
        db.session.add(novo_usuario)
        db.session.commit()
        
        login_user(novo_usuario)
        
        return redirect(url_for('home'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

# if __name__=='__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)
    
# # Apenas executa em desenvolvimento
# if __name__ == '__main__':
#     with app.app_context():
#         db.create_all()
#     app.run(debug=True)

# Replit precisa disso para expor o app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 81)) 
    app.run(host='0.0.0.0', port=81)