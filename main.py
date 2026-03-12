import os
import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# --- CONFIGURAÇÕES ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# COLOQUE AQUI O LINK DO PRODUTO QUE VOCÊ QUER MONITORAR
URL_PRODUTO = "https://www.mercadolivre.com.br/apple-iphone-15-512-gb-preto-distribuidor-autorizado/p/MLB1027172666?pdp_filters=item_id%3AMLB3583817811&matt_tool=38524122#origin=share&sid=share&wid=MLB3583817811"
PRECO_DESEJADO = 7000.00  

def enviar_telegram(mensagem):
    if not TOKEN or not CHAT_ID:
        print("❌ Erro: Credenciais do Telegram não encontradas.")
        return
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    params = {"chat_id": CHAT_ID, "text": mensagem}
    try:
        requests.get(url, params=params)
        print("✅ Alerta enviado ao Telegram!")
    except Exception as e:
        print(f"❌ Erro ao conectar com Telegram: {e}")

def capturar_preco_real(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        print(f"🔍 Acessando produto no Mercado Livre...")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extraindo Nome (ajustado para a classe atual do ML)
        nome = soup.find("h1", {"class": "ui-pdp-title"}).text.strip()

        # Extraindo Preço (buscando na meta tag que é mais estável)
        preco_meta = soup.find("meta", {"itemprop": "price"})
        if preco_meta:
            preco = float(preco_meta["content"])
        else:
            # Fallback caso a meta tag falhe
            preco_texto = soup.find("span", {"class": "andes-money-amount__fraction"}).text
            preco = float(preco_texto.replace('.', '').replace(',', '.'))

        print(f"📦 Produto: {nome}")
        print(f"💰 Preço atual: R$ {preco}")

        return {
            "data": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "produto": nome,
            "preco": preco
        }
    except Exception as e:
        print(f"❌ Erro ao capturar dados do site: {e}")
        return None

def salvar_historico(novo_dado):
    hoje = datetime.datetime.now()
    # Estrutura de Data Lake (Ano/Mês/Dia)
    caminho = f"data/year={hoje.year}/month={hoje.month:02d}/day={hoje.day:02d}/"
    
    if not os.path.exists(caminho):
        os.makedirs(caminho)
        
    arquivo = os.path.join(caminho, 'precos.csv')
    df_novo = pd.DataFrame([novo_dado])
    
    if os.path.exists(arquivo):
        df_novo.to_csv(arquivo, mode='a', header=False, index=False)
    else:
        df_novo.to_csv(arquivo, index=False)
    print(f"📁 Dados persistidos em: {arquivo}")

# --- EXECUÇÃO PRINCIPAL ---
if __name__ == "__main__":
    print("🚀 INICIANDO MONITORAMENTO REAL...")
    
    dados = capturar_preco_real(URL_PRODUTO)
    
    if dados:
        salvar_historico(dados)
        
        if dados['preco'] <= PRECO_DESEJADO:
            msg = (f"🚨 PROMOÇÃO ENCONTRADA!\n\n"
                   f"📦 {dados['produto']}\n"
                   f"💵 Preço: R$ {dados['preco']}\n"
                   f"🔗 Link: {URL_PRODUTO}")
            enviar_telegram(msg)
        else:
            print(f"ℹ️ O preço (R$ {dados['preco']}) ainda está acima de R$ {PRECO_DESEJADO}. Sem alerta.")
    
    print("🏁 PIPELINE FINALIZADO.")