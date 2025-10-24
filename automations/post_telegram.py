import os, csv, requests
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"/"queue.csv"
BOT=os.environ.get("TELEGRAM_BOT_TOKEN",""); CHAT=os.environ.get("TELEGRAM_CHAT_ID","")
def last_done():
    rows=list(csv.DictReader(open(DATA,encoding='utf-8')))
    for r in reversed(rows):
        if r.get("status","").lower()=="done": return r
def send(text, image=None):
    if not BOT or not CHAT: print("Faltan credenciales Telegram"); return
    if image:
        url=f"https://api.telegram.org/bot{BOT}/sendPhoto"
        data={"chat_id":CHAT,"caption":text,"parse_mode":"HTML","photo":image}
    else:
        url=f"https://api.telegram.org/bot{BOT}/sendMessage"
        data={"chat_id":CHAT,"text":text,"parse_mode":"HTML","disable_web_page_preview":False}
    r=requests.post(url, data=data, timeout=30); print("Telegram:", r.status_code)
def main():
    r=last_done()
    if not r: print("Sin post publicado hoy"); return
    product=os.environ.get("PRODUCT_URL",""); url=r.get("url","") or product
    text=f"<b>{r['title']}</b>\n\n{r['body']}\n\n➡️ <a href='{url}'>Accede aquí</a>"
    image=(r.get("image","") or None); send(text,image)
if __name__=="__main__": main()
