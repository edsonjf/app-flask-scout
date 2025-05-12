import requests
import json
from datetime import datetime
from db import db
from models import Jogador, Tabela_geral, Tabela_carreira, Tabela_jogos_temporada
from main import app
import base64
from time import sleep

def converter_float(valor):
    try:
        return float(valor.split()[0])  # Ex: '0 c' -> 0.0
    except (ValueError, AttributeError):
        return None
def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def safe_bool(value):
    if value in ['S', 's', '1', True]: return True
    if value in ['N', 'n', '0', False]: return False
    return None  # fallback for '-'

# 🔁 Função que importa os dados do JSON remoto
def importar_jogadores_do_github():
    with app.app_context():
        # Dados do repositório
        usuario_github = "edsonjf"          # Ex: "octocat"
        repositorio_github = "dados-a2-2025"  # Ex: "Hello-World"

        # URL base da API
        url = f"https://api.github.com/repos/{usuario_github}/{repositorio_github}/contents/"
        print('Importando dados...')
        
        # Fazer requisição
        with requests.get(url) as res:
            arquivos = json.loads(res.content)
        
        # Dicionário para armazenar o conteúdo
        dados_json = {}

        # Iterar pelos arquivos
        for arquivo in arquivos:
            sleep(0.1)
            print(arquivo['name'])
            download_url = arquivo['download_url']
            
            conteudo_res = requests.get(download_url)

            if conteudo_res.status_code == 200:
                time = json.loads(conteudo_res.content)  # ou .json() se for JSON
                
                for cod in time.keys():
                    dados_json[cod] = time[cod]
                else:
                    pass
        
        for k, v in dados_json.items():
            # if not db.session.get(Jogador, int(k)):
            jogador = Jogador(
                id=int(k),
                apelido = v['apelido'],
                nome=v['nome'],
                foto_binaria= base64.b64decode(v['foto']),
                posicao=v['posicao'],
                clube=v['clube'],
                altura=converter_float(v.get('altura')),
                pe = v['pe'],
                peso =converter_float(v.get('peso')),
                nascimento=datetime.strptime(v['nascimento'], '%Y-%m-%d').date(),
                nacionalidade = v['nacionalidade'],
                naturalidade = v['naturalidade'],
            )
            db.session.merge(jogador)
            print(v['apelido'])
                
        
            # if v['tabela'] is not None:
            for linha in v.get('tabela') or []:
                
                    tabela_geral = Tabela_geral(
                        jogador_id=jogador.id,
                        cod_jogador = int(k),
                        competicao = linha['Competicao'],
                        jogos=linha['Jogos'],
                        minutos = linha['Minutos'],
                        gols = linha['Gols'],
                        assistencias=linha['Ass'],
                    )
                    db.session.add(tabela_geral)
        
            # if v['carreira'] is not None:
            for linha in v.get('carreira') or []:
                
                    tabela_carreira = Tabela_carreira(
                        jogador_id=jogador.id,
                        # cod_jogador = int(k),
                        ano = linha['Ano'],
                        time=linha['Time'],
                        jogos = linha['Jogos'],
                        gols = linha['Gols'],
                        assistencias=linha['Ass'],
                    )
                    db.session.add(tabela_carreira)
        
            # if v['tab_descricao_jogos'] is not None:
            for linha in v.get('tab_descricao_jogos') or []:
                
                    tabela_jogos_temporada = Tabela_jogos_temporada(
                        jogador_id=jogador.id,
                        # cod_jogador = int(k),
                        resultado = linha['Unnamed: 0'],
                        data= datetime.strptime(linha['Unnamed: 1'], '%Y-%m-%d').date(),
                        competicao = linha['Unnamed: 2'],
                        fase = linha['Unnamed: 3'],
                        clube=linha['Unnamed: 4'],
                        local = linha['Unnamed: 5'],
                        adversario=linha['Unnamed: 6'],
                        placar = linha['Unnamed: 7'],
                        minutagem = safe_int(linha['T']),
                        tempo_substituicao= linha['78'],
                        amarelo = safe_bool(linha['R']),
                        vermelho=safe_bool(linha['R.1']),
                        gols = linha['Q'],
                        assistencias = linha['B'],
                    )
                    db.session.add(tabela_jogos_temporada)
            # db.session.add(jogador) # add para adicionar
            # db.session.add_all([tabela_geral, tabela_carreira, tabela_jogos_temporada])

            
            
            # db.session.merge(tabela_geral)
            # db.session.merge(tabela_carreira)
            # db.session.merge(tabela_jogos_temporada) # merge para atualizar

        db.session.commit()
        db.session.remove()
    print('Dados importados com sucesso.')


if __name__ == '__main__':
    importar_jogadores_do_github()