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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/"
    }
    
    response = requests.get(url, headers=headers, timeout=30)
    # Se o site bloquear, o status não será 200
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar site: Status {response.status_code}")
        
    soup = BeautifulSoup(response.text, 'html.parser')

    # Busca o título de forma mais robusta (procurando a tag h1 de produto)
    titulo_elem = soup.find('h1') or soup.select_one('.ui-pdp-title')
    if not titulo_elem:
        # Debug radical: salva o HTML para você ver o que o GitHub está recebendo
        with open("debug_page.html", "w", encoding='utf-8') as f:
            f.write(response.text)
        raise Exception("Título não encontrado. O site pode ter bloqueado o bot.")

    titulo = titulo_elem.text.strip()

    # Busca o preço tentando múltiplos seletores comuns do ML
    # O seletor 'meta' com property 'twitter:data2' costuma ter o preço limpo
    preco_meta = soup.find('meta', {'property': 'twitter:data2'})
    if preco_meta:
        # O valor vem como "R$ 3.989,23" ou "3989.23"
        valor_texto = preco_meta.get('content').replace('R$', '').replace('.', '').replace(',', '.').strip()
        preco_final = float(valor_texto)
    else:
        # Fallback para o seletor de span caso o meta falhe
        preco_elem = soup.select_one('.andes-money-amount__fraction')
        if not preco_elem:
            raise Exception("Preço não encontrado nos seletores conhecidos.")
        
        preco_inteiro = preco_elem.text.replace('.', '')
        centavos_elem = soup.select_one('.andes-money-amount__cents')
        centavos = centavos_elem.text if centavos_elem else "00"
        preco_final = float(f"{preco_inteiro}.{centavos}")

    return {
        "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "produto": titulo,
        "preco": preco_final
    }

# --- PERSISTÊNCIA ---
import os

def salvar_historico_particionado(novo_dado):
    hoje = datetime.datetime.now()
    # Cria estrutura de pastas: data/year=2026/month=03/day=11/
    caminho = f"data/year={hoje.year}/month={hoje.month:02d}/day={hoje.day:02d}/"
    
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        
    arquivo = os.path.join(caminho, 'precos.csv')
    df_novo = pd.DataFrame([novo_dado])
    
    # Salva ou anexa no arquivo do dia
    if os.path.exists(arquivo):
        df_novo.to_csv(arquivo, mode='a', header=False, index=False)
    else:
        df_novo.to_csv(arquivo, index=False)
 
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
        salvar_historico_particionado(dados)
        verificar_alerta(dados['preco'], meu_preco_alvo, dados['produto'])
        print("Processo finalizado com sucesso.")
    except Exception as e:
        print(f"Erro no pipeline: {e}")