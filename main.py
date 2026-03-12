import os
import datetime
import pandas as pd
import cloudscraper
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import requests

load_dotenv()

# --- CONFIGURAÇÕES ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PRODUTO_BUSCA = "headfone bluetooth jbl" # Ajuste conforme sua necessidade
PRECO_DESEJADO = 500.00 # Ajuste conforme sua necessidade

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.get(url, params={"chat_id": CHAT_ID, "text": mensagem})
        print("✅ Alerta enviado ao Telegram!")
    except:
        print("❌ Falha ao enviar Telegram.")

def salvar_no_lake(novo_dado):
    hoje = datetime.datetime.now()
    caminho = f"data/year={hoje.year}/month={hoje.month:02d}/day={hoje.day:02d}/"
    os.makedirs(caminho, exist_ok=True)
    arquivo = os.path.join(caminho, 'precos.csv')
    df_novo = pd.DataFrame([novo_dado])
    if os.path.exists(arquivo):
        df_novo.to_csv(arquivo, mode='a', header=False, index=False)
    else:
        df_novo.to_csv(arquivo, index=False)
    print(f"💾 Dados salvos em: {arquivo}")

def buscar_e_capturar_preco(termo):
    termo_formatado = termo.replace(" ", "-")
    url_busca = f"https://lista.mercadolivre.com.br/{termo_formatado}"
    
    scraper = cloudscraper.create_scraper(browser={'browser': 'chrome','platform': 'windows','desktop': True})
    
    try:
        print(f"🔎 Buscando por '{termo}'...")
        response = scraper.get(url_busca)
        soup = BeautifulSoup(response.text, 'html.parser')
        print(f"DEBUG: Título da página recebida: {soup.title.text if soup.title else 'Sem título'}")

        # 1. Tenta encontrar todos os itens da busca
        # O ML usa muito a classe 'ui-search-result__wrapper' ou 'ui-search-result'
        itens = soup.select('div.ui-search-result__wrapper') or \
                soup.select('div.ui-search-result__content') or \
                soup.select('li.ui-search-layout__item')

        if not itens:
            print("❌ Não foi possível encontrar a lista de produtos. O site pode ter bloqueado ou mudado o layout.")
            # Opcional: Salve o HTML para depuração
            # with open("erro_layout.html", "w", encoding="utf-8") as f: f.write(response.text)
            return None

        # Pegamos o primeiro item da lista
        primeiro_item = itens[0]

        # --- EXTRAÇÃO DO TÍTULO ---
        # Procuramos por qualquer h2 ou h3 que geralmente contém o título
        titulo_tag = primeiro_item.select_one('h2') or primeiro_item.select_one('h3')
        nome = titulo_tag.text.strip() if titulo_tag else "Título não encontrado"

        # --- EXTRAÇÃO DO PREÇO ---
        # Procuramos pela classe que contém o valor fracionado (padrão do ML)
        preco_tag = primeiro_item.select_one('span.andes-money-amount__fraction')
        if not preco_tag:
            print("❌ Preço não encontrado dentro do item.")
            return None
        
        preco_inteiro = float(preco_tag.text.replace('.', ''))

        # Centavos
        centavos_tag = primeiro_item.select_one('span.andes-money-amount__cents')
        centavos = float(centavos_tag.text) / 100 if centavos_tag else 0.0

        preco_final = preco_inteiro + centavos
        
        # --- EXTRAÇÃO DO LINK ---
        link_tag = primeiro_item.select_one('a')
        link_final = link_tag['href'] if link_tag and link_tag.has_attr('href') else "Link não encontrado"

        return {
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "produto": nome,
            "preco": preco_final,
            "link": link_final
        }

    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        return None

if __name__ == "__main__":
    dados = buscar_e_capturar_preco(PRODUTO_BUSCA)
    
    if dados:
        print(f"\n📦 Encontrado: {dados['produto']}")
        print(f"💰 Preço: R$ {dados['preco']:.2f}")
        
        salvar_no_lake(dados)
        
        if dados['preco'] <= PRECO_DESEJADO:
            msg = f"🚨 PROMOÇÃO: {dados['produto']}\n💰 R$ {dados['preco']:.2f}\n🔗 {dados['link']}"
            enviar_telegram(msg)
        else:
            print("ℹ️ Preço acima do desejado. Nenhum alerta enviado.")