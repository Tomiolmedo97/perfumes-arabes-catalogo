#!/usr/bin/env python3
"""Regenera public/products.json desde la hoja 'Perfumes Arabes' (Google Sheet STOCK ONLINE).
Uso: python3 scripts/build_data.py [archivo.csv]  (sin argumento descarga el CSV público)."""
import csv, io, json, re, sys, urllib.request, statistics
SHEET = "1Y0D_KSvSZikmsiYq0hFwygfP6-1xeXAuEd5dwwfGe-g"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET}/gviz/tq?tqx=out:csv&sheet=Perfumes%20Arabes"
MARKUP = 15
def num(s):
    s = re.sub(r"[^\d,]", "", s or "").replace(",", ".")
    return float(s) if s else None
def pesos_num(s):
    s = re.sub(r"[^\d]", "", s or "")
    return int(s) if s else None
def clean(n):
    n = re.sub(r"^[\s▪•\-\*]+", "", n); n = re.sub(r"[\s\*]+$", "", n)
    return re.sub(r"\s+", " ", n).strip()
text = open(sys.argv[1], encoding="utf-8").read() if len(sys.argv) > 1 else urllib.request.urlopen(URL).read().decode("utf-8")
rows = list(csv.reader(io.StringIO(text)))
hdr = rows[0][1]
brand = hdr.split("Descripción")[-1].strip() or None  # primera marca queda fusionada en el encabezado
products, rates = [], []
for r in rows[1:]:
    r += [""] * (8 - len(r))
    name, img, usd, ars, estado = r[1].strip(), r[2].strip(), num(r[3]), pesos_num(r[4]), r[5].strip().upper()
    if not name: continue
    if usd is None:  # fila de marca
        brand = clean(name); continue
    if estado != "STOCK": continue
    rate = ars / usd if ars else None
    if rate: rates.append(rate)
    products.append({"id": r[0].strip(), "brand": brand, "name": clean(name), "image": img if img.startswith("http") else "",
                     "usd": usd, "rate": rate})
fallback = statistics.median(rates)
for p in products:
    rate_src = "fila" if p["rate"] else "mediana"
    rate = p.pop("rate") or fallback
    p["usd"] = round(p["usd"] + MARKUP, 2)
    p["ars"] = int(round(p["usd"] * rate / 10) * 10)
    p["rateSource"] = rate_src
json.dump({"products": products, "rates": sorted(set(round(x, 2) for x in rates))}, open("public/products.json", "w"), ensure_ascii=False, indent=1)
print(len(products), "productos,", len({p['brand'] for p in products}), "marcas; tasas:", sorted(set(round(x,2) for x in rates)), "fallback", fallback,
      "sin pesos:", [p["name"] for p in products if p["rateSource"] != "fila"])
