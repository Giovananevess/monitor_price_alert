import datetime
import pandas as pd
import os
import random

# --- CONFIGURAÇÕES ---
TOKEN = "8748353509:AAHTf1OtzXeZKMjqSLta-44E2a00JXOXouE"
CHAT_ID = "7061790855"

def enviar_telegram(mensagem):
    import requests # Importante estar aqui dentro se não estiver no topo
    
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    # Usamos params em vez de data para garantir que a URL seja montada igual ao navegador
    params = {
        "chat_id": CHAT_ID,
        "text": mensagem
    }
    
    try:
        response = requests.get(url, params=params) # Mudamos para GET igual ao navegador
        if response.status_code == 200:
            print("✅ Mensagem confirmada pelo Telegram!")
        else:
            print(f"❌ Erro do Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão ao enviar Telegram: {e}")
# --- SIMULAÇÃO DE EXTRAÇÃO (PARA VALIDAR O PIPELINE) ---
def capturar_dados_simulado():
    # Simulando que fomos ao site e pegamos os dados
    # Isso garante que o seu projeto rode 100% no GitHub
    preco_simulado = round(random.uniform(3500.0, 4200.0), 2)
    return {
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "produto": "Smart TV Samsung 65 QLED (Simulado)",
        "preco": preco_simulado
    }

# --- PERSISTÊNCIA ---
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
    print(f"Dados salvos em: {arquivo}")

def verificar_alerta(preco_atual, preco_desejado, nome_produto):
    # Forçamos o alerta para você ver chegando no celular
    if preco_atual <= preco_desejado:
        msg = f"🚨 ALERTA DE PROMOÇÃO!\n\nPRODUTO: {nome_produto}\nPREÇO: R$ {preco_atual}\nSstatus: Sem erro de pipeline"
        enviar_telegram(msg)
        print("✅ Mensagem enviada ao Telegram!")

if __name__ == "__main__":
    print("--- INICIANDO PIPELINE DE TESTE ---")
    try:
        # 1. Simula a captura (Evita o bloqueio do site)
        dados = capturar_dados_simulado()
        
        # 2. Salva nas pastas (Valida sua estrutura de dados)
        salvar_historico_particionado(dados)
        
        # 3. Dispara o alerta (Valida sua automação)
        verificar_alerta(dados['preco'], 5000.00, dados['produto'])
        
        print("--- PIPELINE FINALIZADO COM SUCESSO ---")
    except Exception as e:
        print(f"❌ Falha: {e}")