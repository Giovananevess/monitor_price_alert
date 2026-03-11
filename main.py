import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
 
# --- CONFIGURAÇÕES DO TELEGRAM ---
TOKEN = "8748353509:AAHTf1OtzXeZKMjqSLta-44E2a00JXOXouE"
CHAT_ID = "7061790855" # <--- Troque pelo ID que você achou no link acima
 
def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")
 
# --- EXTRAÇÃO ---
def capturar_dados(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
 
    titulo = soup.find('h1', class_='ui-pdp-title').text.strip()
    preco_inteiro = soup.find('span', class_='andes-money-amount__fraction').text
    try:
        centavos = soup.find('span', class_='andes-money-amount__cents').text
    except:
        centavos = "00"
    preco_final = float(f"{preco_inteiro.replace('.', '')}.{centavos}")
    return {
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "produto": titulo,
        "preco": preco_final
    }
 
# --- PERSISTÊNCIA ---
def salvar_historico(novo_dado):
    arquivo = 'historico_precos.csv'
    df_novo = pd.DataFrame([novo_dado])
    try:
        df_antigo = pd.read_csv(arquivo)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    except FileNotFoundError:
        df_final = df_novo
    df_final.to_csv(arquivo, index=False)
 
# --- LÓGICA DE ALERTA ---
def verificar_alerta(preco_atual, preco_desejado, nome_produto):
    if preco_atual <= preco_desejado:
        msg = f"🚨 BAIXOU O PREÇO!\n\nPRODUTO: {nome_produto}\nPREÇO AGORA: R$ {preco_atual}\nALVO: R$ {preco_desejado}"
        enviar_telegram(msg)
        print("Alerta enviado para o Telegram!")
    else:
        print(f"Preço de R$ {preco_atual} ainda acima do alvo.")
 
# --- EXECUÇÃO ---
if __name__ == "__main__":
    url_alvo = "https://www.mercadolivre.com.br/smart-tv-u8100f-crystal-uhd-4k-2025-65-preto-samsung-bivolt/p/MLB48954893?pdp_filters=item_id:MLB5411681946#is_advertising=true&searchVariation=MLB48954893&backend_model=search-backend&position=2&search_layout=grid&type=pad&tracking_id=dd332f79-cf42-409d-af6b-246c18d8eeb0&ad_domain=VQCATCORE_LST&ad_position=2&ad_click_id=MGUyOWIzZTItYTE0Yy00Yjc0LWFlODAtY2QyNTQ0ZTIyNjY3"
    meu_preco_alvo = 8000.00 # Coloque um valor alto (ex: 5000) para testar o envio agora!
 
    print("Iniciando monitoramento...")
    try:
        dados = capturar_dados(url_alvo)
        salvar_historico(dados)
        verificar_alerta(dados['preco'], meu_preco_alvo, dados['produto'])
        print("Processo finalizado com sucesso.")
    except Exception as e:
        print(f"Erro no pipeline: {e}")