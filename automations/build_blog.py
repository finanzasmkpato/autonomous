import csv, os, re, json, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "queue.csv"
SETTINGS = ROOT / "data" / "settings.json"
BLOG = ROOT / "blog"  # ahora publica en /blog directamente
BLOG.mkdir(exist_ok=True)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9áéíóúüñ\s-]', '', text)
    text = re.sub(r'\s+', '-', text).strip('-')
    return text[:80]

def read_settings():
    if SETTINGS.exists():
        return json.loads(SETTINGS.read_text(encoding="utf-8"))
    return {}

def load_queue():
    with open(DATA, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_queue(rows):
    with open(DATA, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def render_post_html(title, body, url, image, tags, product_url, affiliate_tag):
    date = datetime.date.today().isoformat()
    if affiliate_tag and url and ("?" not in url):
        url = f"{url}?tag={affiliate_tag}"
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{body[:150]}">
  <style>
    body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Inter;max-width:900px;margin:0 auto;padding:24px;line-height:1.6;}}
    .muted{{color:#6B7280;font-size:14px;}}
    a.button{{display:inline-block;background:#10B981;color:white;padding:12px 16px;border-radius:10px;text-decoration:none;font-weight:700;margin:10px 0;}}
    img{{max-width:100%;border-radius:12px;border:1px solid #e5e7eb;}}
  </style>
</head>
<body>
  <p class="muted">{date}</p>
  <h1>{title}</h1>
  {"<img src='" + image + "' alt=''>" if image else ""}
  <p>{body}</p>
  {("<a class='button' href='" + (product_url or "#") + "' target='_blank' rel='noopener'>Acceder al pack PRO</a>") if product_url else ""}
  {("<p>Enlace útil: <a href='" + url + "' target='_blank' rel='noopener'>" + url + "</a></p>") if url else ""}
  <p class="muted">Etiquetas: {tags}</p>
  <p><a href='/'>← Volver</a></p>
</body>
</html>"""

def update_blog_index():
    items = []
    for p in sorted(BLOG.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name == "index.html":
            continue
        ts = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        title = p.stem.replace("-", " ").title()
        items.append(f'<div><a href="/blog/{p.name}"><strong>{title}</strong></a> <span class="muted">{ts}</span></div>')
    listing = "\n".join(items)
    idx_path = BLOG / "index.html"
    html = f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Blog — Publicaciones diarias</title></head>
<body style="font-family:system-ui;padding:24px;max-width:900px;margin:auto;">
<h1>Archivo</h1>
{listing or "<p class='muted'>Aún no hay posts.</p>"}
<p><a href="/">← Volver al inicio</a></p>
</body></html>"""
    idx_path.write_text(html, encoding="utf-8")

def inject_env_in_index(product_url, affiliate_tag):
    index_path = ROOT / "index.html"
    if not index_path.exists():
        return
    html = index_path.read_text(encoding="utf-8")
    html = html.replace("{{PRODUCT_URL}}", product_url or "")
    html = html.replace("{{AFFILIATE_TAG}}", affiliate_tag or "")
    index_path.write_text(html, encoding="utf-8")

def main():
    rows = load_queue()
    if not rows:
        print("No hay filas en la cola.")
        return
    # Buscar el primer 'pending'
    for i, r in enumerate(rows):
        if r.get("status", "").strip().lower() == "pending":
            idx = i
            break
    else:
        print("No hay elementos pendientes.")
        return

    r = rows[idx]
    title = r.get("title", "Post del día").strip()
    body = r.get("body", "").strip()
    url = r.get("url", "").strip()
    image = r.get("image", "").strip()
    tags = r.get("tags", "").strip()

    product_url = os.environ.get("PRODUCT_URL", "").strip()
    affiliate_tag = os.environ.get("AFFILIATE_TAG", "").strip()

    slug = slugify(title)
    out = BLOG / f"{slug}.html"
    out.write_text(render_post_html(title, body, url, image, tags, product_url, affiliate_tag), encoding="utf-8")

    update_blog_index()
    inject_env_in_index(product_url, affiliate_tag)

    rows[idx]["status"] = "done"
    save_queue(rows)
    print(f"✅ Generado: {out}")

if __name__ == "__main__":
    main()
