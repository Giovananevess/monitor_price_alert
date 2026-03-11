import os
import datetime
import pandas as pd
import random
import requests

# Tenta carregar o dotenv para rodar localmente. 
# Se não estiver instalado (como no GitHub Actions), ele ignora e segue em frente.
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# --- CONFIGURAÇÕES (LENDO DAS VARIÁVEIS DE AMBIENTE) ---
# Se houver um arquivo .env, ele pega de lá. Se estiver no GitHub, pega dos Secrets.
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        print("❌ Erro: Token ou Chat ID não configurados nas variáveis de ambiente.")
        return
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensagem}
    
    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            print("✅ Mensagem confirmada pelo Telegram!")
        else:
            print(f"❌ Erro do Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão ao enviar Telegram: {e}")
        
# --- SIMULAÇÃO DE EXTRAÇÃO (PARA VALIDAR O PIPELINE) ---
def capturar_dados_simulado():
    preco_simulado = round(random.uniform(3500.0, 4200.0), 2)
    return {
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "produto": "Smart TV Samsung 65 QLED (Simulado)",
        "preco": preco_simulado
    }

# --- PERSISTÊNCIA (PARTICIONAMENTO PROFISSIONAL) ---
def salvar_historico_particionado(novo_dado):
    hoje = datetime.datetime.now()
    caminho = f"data/year={hoje.year}/month={hoje.month:02d}/day={hoje.day:02d}/"
    
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        
    arquivo = os.path.join(caminho, 'precos.csv')
    df_novo = pd.DataFrame([novo_dado])
    
    if os.path.exists(arquivo):
        df_novo.to_csv(arquivo, mode='a', header=False, index=False)
    else:
        df_novo.to_csv(arquivo, index=False)
    print(f"📁 Dados salvos em: {arquivo}")

# --- LÓGICA DE ALERTA ---
def verificar_alerta(preco_atual, preco_desejado, nome_produto):
    if preco_atual <= preco_desejado:
        msg = f"🚨 ALERTA DE PROMOÇÃO!\n\nPRODUTO: {nome_produto}\nPREÇO: R$ {preco_atual}\nStatus: Pipeline rodando com segurança!"
        enviar_telegram(msg)

if __name__ == "__main__":
    print("--- INICIANDO PIPELINE DE TESTE ---")
    try:
        # 1. Captura Simulada
        dados = capturar_dados_simulado()
        
        # 2. Persistência
        salvar_historico_particionado(dados)
        
        # 3. Verificação de Alerta
        verificar_alerta(dados['preco'], 5000.00, dados['produto'])
        
        print("--- PIPELINE FINALIZADO COM SUCESSO ---")
    except Exception as e:
        print(f"❌ Falha crítica no pipeline: {e}")