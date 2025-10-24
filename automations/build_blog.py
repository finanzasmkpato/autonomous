import csv, os, re, json, datetime
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT/"data"/"queue.csv"
SETTINGS = ROOT/"data"/"settings.json"
SITE = ROOT/"site"
BLOG = SITE/"blog"
def slugify(t):
    t=t.lower();import re
    t=re.sub(r'[^a-z0-9áéíóúüñ\s-]','',t);t=re.sub(r'\s+','-',t).strip('-');return t[:80]
def render(title,body,url,image,tags,product,aff):
    d=datetime.date.today().isoformat()
    if aff and url and ("?" not in url): url=f"{url}?tag={aff}"
    return f"""<!doctype html><html lang='es'><head><meta charset='utf-8'>
<meta name='viewport' content='width=device-width,initial-scale=1'><title>{title}</title></head>
<body><p style='color:#6B7280'>{d}</p><h1>{title}</h1>
{f"<img src='{image}' alt='' style='max-width:100%'>" if image else ""}
<p>{body}</p>
{f"<p><a href='{product}' target='_blank' rel='noopener'>Acceder al pack PRO</a></p>" if product else ""}
{f"<p><a href='{url}' target='_blank' rel='noopener'>{url}</a></p>" if url else ""}
<p style='color:#6B7280'>Etiquetas: {tags}</p><p><a href='/blog/'>← Volver</a></p></body></html>"""
def update_index():
    items=[]
    for p in sorted(BLOG.glob("*.html"), key=lambda x: x.stat().st_mtime, reverse=True):
        if p.name=="index.html": continue
        ts=datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%Y-%m-%d")
        title=p.stem.replace("-"," ").title()
        items.append(f"<div><a href='/blog/{p.name}'><strong>{title}</strong> — {ts}</a></div>")
    idx = (BLOG/"index.html").read_text(encoding="utf-8")
    idx = idx.replace("<!-- items generated -->","".join(items) or "<p>Aún no hay posts.</p>")
    (BLOG/"index.html").write_text(idx, encoding="utf-8")
def inject_env(product,aff):
    p=SITE/"index.html"; html=p.read_text(encoding="utf-8")
    html=html.replace("{{PRODUCT_URL}}", product or "").replace("{{AFFILIATE_TAG}}", aff or "")
    p.write_text(html, encoding="utf-8")
def main():
    rows=list(csv.DictReader(open(DATA,encoding='utf-8')))
    idx=None
    for i,r in enumerate(rows):
        if r.get("status","").lower()=="pending": idx=i; break
    if idx is None: print("No pending"); return
    r=rows[idx]
    title=r.get("title","Post"); body=r.get("body",""); url=r.get("url",""); image=r.get("image",""); tags=r.get("tags","")
    product=os.environ.get("PRODUCT_URL",""); aff=os.environ.get("AFFILIATE_TAG","")
    out=BLOG/f"{slugify(title)}.html"; out.write_text(render(title,body,url,image,tags,product,aff),encoding="utf-8")
    update_index(); inject_env(product,aff); rows[idx]["status"]="done"
    with open(DATA,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
    print("OK:", out)
if __name__=="__main__": main()
