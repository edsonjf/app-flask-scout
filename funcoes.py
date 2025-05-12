import io
import base64
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Usa backend que não depende do sistema gráfico
import matplotlib.pyplot as plt
import unicodedata
from models import Tabela_jogos_temporada, Tabela_carreira
import numpy as np

def converter_em_dict(obj):
    return {col.name: getattr(obj, col.name) for col in obj.__table__.columns}
# DAtaframe
# Caminho para o arquivo .db (ajuste conforme necessário)
def carregar_dados_db():
    conn = sqlite3.connect('instance/database.db')
    cursor = conn.cursor()

    # Verifica se a tabela jogadores existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='jogadores';")
    if cursor.fetchone():
        df = pd.read_sql_query("SELECT * FROM jogadores", conn)
        return df
    else:
        print("Tabela 'jogadores' ainda não existe.")
        return pd.DataFrame()
    if not df.empty:
        df['nascimento'] = pd.to_datetime(df['nascimento'])

def grafico_rosca(labels: list, valores: list):
    def func_abs(pct, all_vals):
        total = sum(all_vals)
        valor = int(round(pct * total / 100.0))
        return f'{valor}'  # ou f'{valor} ({pct:.1f}%)' para valor + porcentagem

    fig, ax = plt.subplots()
    wedges, texts, autotexts = ax.pie(
        valores,
        labels=labels,
        startangle=90,
        autopct=lambda pct: func_abs(pct, valores),
        wedgeprops=dict(width=0.5)
    )

    ax.axis('equal')

    img = io.BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight')
    img.seek(0)
    grafico_base64 = base64.b64encode(img.getvalue()).decode('utf8')
    plt.close()
    return grafico_base64

def remover_acentos(texto):
    if isinstance(texto, str):
        return ''.join(
            c for c in unicodedata.normalize('NFD', texto)
            if unicodedata.category(c) != 'Mn'
        )
    return texto

def grafico_carreira(jogador_id):
    partidas = Tabela_carreira.query.filter_by(jogador_id=jogador_id).order_by(Tabela_carreira.ano).all()
    partidas = [converter_em_dict(linha) for linha in partidas]
    for item in partidas:
        if isinstance(item['ano'], str):
            item['ano'] = int(item['ano'].split('/')[0])
    partidas = sorted(partidas, key=lambda x: x['ano'])
    if not partidas:
        return None
    
    jogos = [p['jogos'] for p in partidas if isinstance(p['jogos'], int)]
    times = [p['time'] for p in partidas if isinstance(p['time'], str)]
    anos = [p['ano'] for p in partidas if isinstance(p['ano'], int)]
    ass = [p['assistencias'] for p in partidas if isinstance(p['assistencias'], int)]
    gols = [p['gols'] for p in partidas if isinstance(p['gols'], int)]
    if not times:
        return None
    
    # Largura da barra
    bar_width = 0.35
    
    # Posições no eixo x
    index = np.arange(len(times))
        
    # Criar o gráfico com matplotlib
    fig, ax = plt.subplots()
    bar1 = ax.bar(x=index, height=jogos, width=bar_width, label='Jogos')
    bar2 = ax.bar(x=index + bar_width, height=gols, width=bar_width, label='Gols')
    bar3 = ax.bar(x=index + 2* bar_width, height=ass, width=bar_width, label='Assistências')
    # ax.barh(times, jogos, color='blue')
    ax.set_title(f'Jogos por Clube – ')
    ax.set_xlabel('Jogos')
    # ax.set_ylabel('Minutos')
    # ax.set_ylim(0, max(times + [90]) + 10)
    
    # Labels de 'times' e 'anos' no eixo x
    ax.set_xticks(index + bar_width)
    ax.set_xticklabels([f"{time} - {ano}" for time, ano in zip(times, anos)])
    plt.xticks(rotation=45, ha='right')
    
    ax.xaxis.set_tick_params(labelsize=5)
    ax.yaxis.set_tick_params(labelsize=8)  # Ajustando o tamanho da fonte dos rótulos do eixo Y
    plt.tight_layout()

    # Salvar imagem em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # buf.close()
    plt.close()
    return image_base64

def grafico_jogos_temporada(jogador_id):
    partidas = Tabela_jogos_temporada.query.filter_by(jogador_id=jogador_id).order_by(Tabela_jogos_temporada.data).all()
    dados_dict = [converter_em_dict(linha) for linha in partidas]
    
    if not partidas:
        return None
    
    adversarios = [item['adversario'] for item in dados_dict]
    minutagem = [item['minutagem'] for item in dados_dict]
    minutagem = [0 if x == None else x for x in minutagem]

    if not adversarios:
        return None
    
    # Criar o gráfico
    fig, ax = plt.subplots()
    ax.barh(adversarios, minutagem, color='blue')

    # Personalizar
    # plt.grid(axis='y')
    # Criar o gráfico com matplotlib
    
    ax.set_title(f'Minutagem por Jogo – ')
    ax.set_xlabel('Minutos')
    ax.set_ylabel('Adversários')
    # ax.set_ylim(0, max(times + [90]) + 10)
    plt.xticks(rotation=0)
    plt.tight_layout()

    # Salvar imagem em memória
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    # buf.close()
    plt.close()
    return image_base64

