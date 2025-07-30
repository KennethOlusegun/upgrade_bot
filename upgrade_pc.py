import asyncio
import httpx
import re
import gspread
import telegram
import os
import json # Import necessário para ler as credenciais da variável de ambiente
from lxml import html
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# =============== CARREGA VARIÁVEIS DE AMBIENTE ===============
# No Railway, as variáveis são carregadas automaticamente, mas load_dotenv() não causa problemas.
load_dotenv()

# =============== CONFIGURAÇÃO GOOGLE SHEETS (VERSÃO PARA RAILWAY) ===============
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

# Pega o CONTEÚDO do JSON da variável de ambiente do Railway
gcp_credentials_json_str = os.getenv("GCP_CREDENTIALS_JSON")

if not gcp_credentials_json_str:
    # Esta exceção irá parar o script se a variável de credenciais não for encontrada
    raise ValueError("ERRO CRÍTICO: A variável de ambiente GCP_CREDENTIALS_JSON não foi definida no Railway!")

# Converte a string JSON em um dicionário Python
gcp_credentials_dict = json.loads(gcp_credentials_json_str)

# Autentica usando o dicionário em vez de um arquivo
creds = ServiceAccountCredentials.from_json_keyfile_dict(gcp_credentials_dict, scope)
client = gspread.authorize(creds)

GOOGLE_SHEETS_NAME = os.getenv("GOOGLE_SHEETS_NAME_UPGRADE")
GOOGLE_SHEETS_WORKSHEET_UPGRADE = os.getenv("GOOGLE_SHEETS_WORKSHEET_UPGRADE")
sheet = client.open(GOOGLE_SHEETS_NAME).worksheet(GOOGLE_SHEETS_WORKSHEET_UPGRADE)


# =============== CONFIGURAÇÃO TELEGRAM ===============
bot_token = os.getenv("TELEGRAM_BOT_TOKEN_UPGRADE")
chat_id = os.getenv("TELEGRAM_CHAT_ID_UPGRADE")
bot = telegram.Bot(token=bot_token)


# =============== LISTA DE ITENS ===============
# Sua lista de produtos completa
itens = [
    # ... (Cole sua lista completa de itens aqui)
]

# =============== FUNÇÕES ASSÍNCRONAS ===============

async def get_price(url: str, client: httpx.AsyncClient) -> float | None:
    """
    Função assíncrona para buscar o preço usando XPath para maior robustez.
    """
    try:
        r = await client.get(url, follow_redirects=True)
        r.raise_for_status()
        tree = html.fromstring(r.content)
        
        xpath_expressions = [
            "//div[.//text()[contains(., 'vista no PIX')]]/h4/text()",
            '//span[contains(@class, "a-price")]/text()',
        ]
        
        price_text = None
        for expr in xpath_expressions:
            result = tree.xpath(expr)
            if result:
                price_text = result[0].strip()
                print(f"INFO: Preço encontrado com a expressão XPath: {expr}")
                break
        
        if price_text:
            match = re.search(r'[\d\.,]+', price_text)
            if match:
                price_str = match.group(0)
                price_float = float(price_str.replace(".", "").replace(",", "."))
                return price_float

    except httpx.HTTPStatusError as e:
        print(f"ERRO de status HTTP ao acessar {url}: {repr(e)}")
    except Exception as e:
        print(f"ERRO inesperado ao processar a URL {url}: {repr(e)}")
    
    return None

async def rastrear():
    """
    Função principal de rastreio, executada pelo agendador.
    """
    print(f"--- INICIANDO RASTREIO AGENDADO: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---")
    data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
    promocao_encontrada = False

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7"
    }
    
    async with httpx.AsyncClient(headers=headers, timeout=20) as client:
        for item in itens:
            print(f"--- Verificando item: {item['nome']} ---")
            for url in item["urls"]:
                if "LINK-DO-PRODUTO-AQUI" in url:
                    print(f"AVISO: Pulando URL de exemplo para '{item['nome']}': {url}")
                    continue

                preco = await get_price(url, client)
                
                if preco:
                    print(f"  -> Loja: {url.split('/')[2]} | Preço: R$ {preco:.2f}")
                    sheet.append_row([data_hora, item["nome"], preco, url])
                    
                    if preco <= item["preco_alvo"]:
                        msg = (
                            f"🔥 OPORTUNIDADE! 🔥\n\n"
                            f"Produto: {item['nome']}\n"
                            f"Preço: R$ {preco:.2f} (Alvo: R$ {item['preco_alvo']:.2f})\n\n"
                            f"Link: {url}"
                        )
                        await bot.send_message(chat_id=chat_id, text=msg)
                        print(f"ALERTA ENVIADO para {item['nome']}")
                        promocao_encontrada = True
                else:
                    print(f"  -> Preço não encontrado em: {url}")
                    
                await asyncio.sleep(5)
                
            print("-" * (len(item['nome']) + 22))

    if not promocao_encontrada:
        msg_status = "Nenhuma promoção localizada desta vez 😥"
        await bot.send_message(chat_id=chat_id, text=msg_status)
        print("INFO: Nenhuma promoção encontrada. Mensagem de status enviada ao Telegram.")
        
    print(f"--- RASTREIO AGENDADO FINALIZADO: {datetime.now().strftime('%d/%m/%Y %H:%M')} ---")

# =============== EXECUÇÃO COM AGENDAMENTO SEMANAL ===============
async def main():
    """
    Função principal que configura e inicia o agendador.
    """
    scheduler = AsyncIOScheduler(timezone="America/Sao_Paulo")
    scheduler.add_job(rastrear, 'cron', day_of_week='fri', hour=22)
    scheduler.start()
    
    print("✅ Agendador iniciado com sucesso!")
    print("O rastreio será executado automaticamente toda sexta-feira às 22:00.")
    print("Mantenha este serviço rodando para o agendador funcionar.")
    print("Pressione Ctrl+C nos logs para reiniciar, se necessário.")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nAgendador finalizado.")

if __name__ == "__main__":
    asyncio.run(main())