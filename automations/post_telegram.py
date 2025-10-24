import os, csv, requests
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "queue.csv"

BOT = os.getenv("TELEGRAM_BOT_TOKEN", "")
CHAT = os.getenv("TELEGRAM_CHAT_ID", "")
PRODUCT = os.getenv("PRODUCT_URL", "")

def last_done():
    with open(DATA, newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    for r in reversed(rows):
        if r["status"].lower() == "done":
            return r

def send(msg, image=None):
    if not BOT or not CHAT:
        print("Faltan credenciales Telegram"); return
    url = f"https://api.telegram.org/bot{BOT}/sendMessage"
    data = {"chat_id": CHAT, "text": msg, "parse_mode": "HTML"}
    requests.post(url, data=data, timeout=30)

def main():
    r = last_done()
    if not r: print("No hay post publicado."); return
    text = f"<b>{r['title']}</b>\n\n{r['body']}\n\n➡️ <a href='{PRODUCT or r['url']}'>Accede aquí</a>"
    send(text)

if __name__ == "__main__":
    main()
