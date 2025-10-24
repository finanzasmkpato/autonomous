import csv, os, re, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "queue.csv"
SETTINGS = ROOT / "data" / "settings.json"
BLOG = ROOT / "blog"
BLOG.mkdir(exist_ok=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9áéíóúüñ\s-]', '', text)
    text = re.sub(r'\s+', '-', text).strip('-')
    return text[:80]

def load_queue():
    with open(DATA, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def save_queue(rows):
    with open(DATA, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def render(title, body, url, image, tags, product_url, affiliate_tag):
    d = datetime.date.today().isoformat()
    if affiliate_tag and url and "?" not in url:
        url = f"{url}?tag={affiliate_tag}"
    return f"""<!doctype html><html lang='es'><head>
<meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>{title}</title></head><body style='font-family:system-ui;max-width:900px;margin:auto;padding:24px;'>
<p style='color:#6B7280'>{d}</p><h1>{title}</h1>
{'<img src="'+image+'" style="max-width:100%">' if image else ''}
<p>{body}</p>
{f"<a href='{product_url}' target='_blank'>Acceder al pack PRO</a>" if product_url else ''}
{f"<p><a href='{url}' target='_blank'>{url}</a></p>" if url else ''}
<p style='color:#6B7280'>Etiquetas: {tags}</p>
<p><a href='/'>← Volver</a></p></body></html>"""

def update_index():
    items = []
    for p in sorted(BLOG.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name == "index.html": continue
        date = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        title = p.stem.replace("-", " ").title()
        items.append(f"<div><a href='/blog/{p.name}'>{title}</a> — {date}</div>")
    content = "\n".join(items) or "<p>No hay publicaciones.</p>"
    html = f"""<!doctype html><html lang='es'><head><meta charset='utf-8'><title>Blog</title></head>
<body style='font-family:system-ui;max-width:900px;margin:auto;padding:24px;'>
<h1>Archivo</h1>{content}<p><a href='/'>← Volver</a></p></body></html>"""
    (BLOG / "index.html").write_text(html, encoding="utf-8")

def main():
    rows = load_queue()
    pending = next((i for i, r in enumerate(rows) if r["status"].lower() == "pending"), None)
    if pending is None:
        print("No hay publicaciones pendientes."); return
    r = rows[pending]
    out = BLOG / f"{slugify(r['title'])}.html"
    out.write_text(render(r['title'], r['body'], r['url'], r['image'], r['tags'],
                          os.getenv("PRODUCT_URL",""), os.getenv("AFFILIATE_TAG","")), encoding='utf-8')
    update_index()
    rows[pending]["status"] = "done"
    save_queue(rows)
    print(f"Publicado: {out}")

if __name__ == "__main__":
    main()
