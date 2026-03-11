import cloudscraper
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import os

# --- CONFIGURAÇÕES ---
TOKEN = "8748353509:AAHTf1OtzXeZKMjqSLta-44E2a00JXOXouE"
CHAT_ID = "7061790855"

def enviar_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        # Criamos um scraper temporário apenas para o envio se necessário, 
        # mas requests simples costuma funcionar para a API do Telegram.
        import requests
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Erro ao enviar para o Telegram: {e}")

# --- EXTRAÇÃO (AGORA COM CLOUDSCRAPER) ---
def capturar_dados(url):
    # O cloudscraper cria uma sessão que simula um navegador real para evitar bloqueios
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    print("Acessando o site...")
    response = scraper.get(url, timeout=30)
    
    if response.status_code != 200:
        raise Exception(f"Erro ao acessar site: Status {response.status_code}")
        
    soup = BeautifulSoup(response.text, 'html.parser')

    # Busca o título
    titulo_elem = soup.find('h1') or soup.select_one('.ui-pdp-title')
    if not titulo_elem:
        # Se falhar, salva o HTML para você investigar depois
        with open("debug_page.html", "w", encoding='utf-8') as f:
            f.write(response.text)
        raise Exception("Título não encontrado. O site pode ter detectado o bot.")

    titulo = titulo_elem.text.strip()

    # Busca o preço (Tentativa 1: Meta tag - mais estável)
    preco_meta = soup.find('meta', {'property': 'twitter:data2'})
    
    if preco_meta:
        valor_texto = preco_meta.get('content').replace('R$', '').replace('.', '').replace(',', '.').strip()
        preco_final = float(valor_texto)
    else:
        # Tentativa 2: Seletores de classe (Fallback)
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

# --- PERSISTÊNCIA PARTICIONADA ---
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

# --- LÓGICA DE ALERTA ---
def verificar_alerta(preco_atual, preco_desejado, nome_produto):
    if preco_atual <= preco_desejado:
        msg = f"🚨 BAIXOU O PREÇO!\n\nPRODUTO: {nome_produto}\nPREÇO AGORA: R$ {preco_atual}\nALVO: R$ {preco_desejado}"
        enviar_telegram(msg)
        print(f"Alerta enviado! Preço atual: R$ {preco_atual}")
    else:
        print(f"Preço de R$ {preco_atual} ainda acima do alvo de R$ {preco_desejado}.")

# --- EXECUÇÃO ---
if __name__ == "__main__":
    url_alvo = "https://www.mercadolivre.com.br/smart-tv-u8100f-crystal-uhd-4k-2025-65-preto-samsung-bivolt/p/MLB48954893"
    meu_preco_alvo = 8000.00 

    print("Iniciando monitoramento...")
    try:
        dados_coletados = capturar_dados(url_alvo)
        salvar_historico_particionado(dados_coletados)
        verificar_alerta(dados_coletados['preco'], meu_preco_alvo, dados_coletados['produto'])
        print("Pipeline finalizado com sucesso.")
    except Exception as e:
        print(f"Erro no pipeline: {e}")