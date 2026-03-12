import os
import datetime
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import requests

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
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    
    try:
        response = scraper.get(url_busca)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Seletor resiliente para o primeiro item
        item = soup.select_one('div.ui-search-result__wrapper') or \
               soup.select_one('div.ui-search-result__content')

        if not item: return None

        nome = (item.select_one('h2') or item.select_one('h3')).text.strip()
        
        # Extração de preço
        preco_raw = item.select_one('span.andes-money-amount__fraction').text.replace('.', '')
        centavos_tag = item.select_one('span.andes-money-amount__cents')
        centavos = float(centavos_tag.text) / 100 if centavos_tag else 0.0
        preco_final = float(preco_raw) + centavos
        
        link = (item.select_one('a.ui-search-link') or item.select_one('a'))['href']

        return {
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "produto": nome,
            "preco": preco_final,
            "link": link
        }
    except Exception as e:
        print(f"⚠️ Erro ao buscar {termo}: {e}")
        return None

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