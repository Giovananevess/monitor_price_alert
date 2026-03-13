import os
import datetime
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import requests
import random

load_dotenv()

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# LISTA DE PRODUTOS PARA BUSCA AUTOMÁTICA
PRODUTOS_MONITORAR = [
    {"termo": "iPhone 15 128gb", "preco_alvo": 7800.00},
    {"termo": "PlayStation 5 Slim", "preco_alvo": 6500.00},
    {"termo": "Kindle Paperwhite", "preco_alvo": 900.00}
]

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID: return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": mensagem})
    except:
        print("❌ Erro ao enviar Telegram.")

def salvar_particionado(novo_dado):
    """Mantém o padrão de pastas: data/year=YYYY/month=MM/day=DD/"""
    hoje = datetime.datetime.now()
    caminho = f"data/year={hoje.year}/month={hoje.month:02d}/day={hoje.day:02d}/"
    os.makedirs(caminho, exist_ok=True)
    
    arquivo = os.path.join(caminho, 'precos.csv')
    df_novo = pd.DataFrame([novo_dado])
    
    # Salva mantendo as colunas: data, produto, preco (e link para referência)
    if os.path.exists(arquivo):
        df_novo.to_csv(arquivo, mode='a', header=False, index=False)
    else:
        df_novo.to_csv(arquivo, index=False)
    print(f"💾 Dados salvos em: {arquivo}")



def capturar_preco(termo):
    termo_url = termo.replace(" ", "-")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_url}"
    
    # Criamos um scraper
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # 1. Definimos cabeçalhos que um Chrome real enviaria
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/", # Faz parecer que você veio do Google
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "cross-site",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        # 2. Pequena pausa aleatória para não parecer um robô mecânico
        time.sleep(random.uniform(1, 3))
        
        # 3. Fazemos a requisição com os headers manuais
        response = scraper.get(url_busca, headers=headers, timeout=20)
        
        # Log para você ver no GitHub Actions o que está acontecendo
        print(f"DEBUG: {termo} -> Status: {response.status_code} | Tamanho: {len(response.text)}")
        
        soup = BeautifulSoup(response.text, 'html.parser')

        # Seletor focado nas classes que SEMPRE aparecem nos resultados
        # Tentamos o container de imagem que é muito estável
        item = soup.find("div", {"class": "ui-search-result__wrapper"}) or \
               soup.find("div", {"class": "ui-search-result__content"}) or \
               soup.select_one(".ui-search-layout__item")

        if not item:
            # Se não achou o item, vamos imprimir o título da página para depurar
            page_title = soup.title.string if soup.title else "Sem título"
            print(f"⚠️ Não encontrou item para '{termo}'. Título da página: {page_title}")
            return None

        # Título
        nome = (item.find("h2") or item.find("h3")).text.strip()
        
        # Preço (usando seletor CSS mais direto)
        preco_tag = item.select_one('.andes-money-amount__fraction')
        if not preco_tag:
            return None
            
        preco_raw = preco_tag.text.replace('.', '')
        
        centavos_tag = item.select_one('.andes-money-amount__cents')
        centavos = float(centavos_tag.text) / 100 if centavos_tag else 0.0
        
        preco_final = float(preco_raw) + centavos
        
        # Link
        link_tag = item.find("a", {"class": "ui-search-link"}) or item.find("a")
        link = link_tag['href'] if link_tag else ""

        return {
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "produto": nome,
            "preco": preco_final,
            "link": link
        }
    except Exception as e:
        print(f"⚠️ Erro em {termo}: {e}")
        return None

# def capturar_preco(termo):
#     termo_url = termo.replace(" ", "-")
#     url_busca = f"https://lista.mercadolivre.com.br/{termo_url}"
    
#     scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    
#     try:
#         response = scraper.get(url_busca)
#         soup = BeautifulSoup(response.text, 'html.parser')

#         # Seletor resiliente para o primeiro item
#         item = soup.select_one('div.ui-search-result__wrapper') or \
#                soup.select_one('div.ui-search-result__content')

#         if not item: return None

#         nome = (item.select_one('h2') or item.select_one('h3')).text.strip()
        
#         # Extração de preço
#         preco_raw = item.select_one('span.andes-money-amount__fraction').text.replace('.', '')
#         centavos_tag = item.select_one('span.andes-money-amount__cents')
#         centavos = float(centavos_tag.text) / 100 if centavos_tag else 0.0
#         preco_final = float(preco_raw) + centavos
        
#         link = (item.select_one('a.ui-search-link') or item.select_one('a'))['href']

#         return {
#             "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "produto": nome,
#             "preco": preco_final,
#             "link": link
#         }
#     except Exception as e:
#         print(f"⚠️ Erro ao buscar {termo}: {e}")
#         return None

if __name__ == "__main__":
    print(f"🚀 Iniciando Monitoramento: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    for p in PRODUTOS_MONITORAR:
        print(f"🔎 Buscando: {p['termo']}...")
        dados = capturar_preco(p['termo'])
        
        if dados:
            salvar_particionado(dados)
            print(f"✅ {dados['produto']} | R$ {dados['preco']:.2f}")
            
            # Alerta se o preço for menor ou igual ao alvo definido na lista
            if dados['preco'] <= p['preco_alvo']:
                msg = f"🚨 ALERTA DE PREÇO!\n📦 {dados['produto']}\n💰 R$ {dados['preco']:.2f}\n🔗 {dados['link']}"
                enviar_telegram(msg)
        
        # Espera 2 segundos entre um produto e outro para evitar bloqueio
        time.sleep(2)

    print("\n🏁 Processo finalizado.")