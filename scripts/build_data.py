#!/usr/bin/env python3
"""Regenera (las imágenes salen de data/fragrantica_map.json + public/img; nuevas: agregar al mapa y correr scripts/fetch_images.py)
 public/products.json desde la hoja 'Perfumes Arabes' (Google Sheet STOCK ONLINE).
Uso: python3 scripts/build_data.py [archivo.csv]  (sin argumento descarga el CSV público)."""
import csv, io, json, re, sys, urllib.request, statistics
SHEET = "1Y0D_KSvSZikmsiYq0hFwygfP6-1xeXAuEd5dwwfGe-g"
URL = f"https://docs.google.com/spreadsheets/d/{SHEET}/gviz/tq?tqx=out:csv&sheet=Perfumes%20Arabes"
MARKUP = 15
# Familias olfativas a partir de los acordes principales (traducidos) de Fragrantica
FAMILIES = {}
for fam, accs in {
    "Dulce/Gourmand": "dulce caramelo vainilla chocolate cacao miel café almendrado avellanado lactónico coco",
    "Amaderado": "amaderado musgoso terroso ahumado",
    "Floral": "floral|floral blanco|floral amarillo|rosa|nardo|iris|violeta|atalcado",
    "Fresco/Cítrico": "cítrico fresco verde aromático herbal lavanda",
    "Especiado": "especiado cálido|especiado fresco|especiado suave|canela",
    "Oriental/Ámbar": "ámbar balsámico cuero almizclado animálico tabaco",
    "Oud": "oud",
    "Frutal": "frutal tropical cereza",
    "Acuático": "acuático marino salado ozónico",
}.items():
    for a in (accs.split("|") if "|" in accs else accs.split()): FAMILIES[a] = fam
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
        brand = clean(name).upper(); continue
    if estado != "STOCK": continue
    rate = ars / usd if ars else None
    if rate: rates.append(rate)
    products.append({"id": r[0].strip(), "brand": brand, "name": clean(name).upper(), "image": img if img.startswith("http") else "",
                     "usd": usd, "rate": rate})
fallback = statistics.median(rates)
import os
FMAP = json.load(open("data/fragrantica_map.json")) if os.path.exists("data/fragrantica_map.json") else {}
for p in products:
    FMAP_CI = {k.upper(): v for k, v in FMAP.items()}
    f = FMAP_CI.get((p["id"] or p["name"]).upper())
    if f and not p["image"] and os.path.exists(os.path.join("public", f["image"])):
        p["image"], p["fragrantica"] = f["image"], f["url"]
DET = json.load(open("data/fragrantica_details.json")) if os.path.exists("data/fragrantica_details.json") else {}
DET_CI = {k.upper(): v for k, v in DET.items()}
for p in products:
    d = DET_CI.get((p["id"] or p["name"]).upper())
    if d: p["details"] = {k: d[k] for k in ("gender", "year", "accords", "notes", "description")}
    if d and d.get("similar"): p["similar"] = d["similar"]
    g = {"women": "mujer", "men": "hombre", "women and men": "unisex"}.get((d or {}).get("gender"))
    if not g:
        n = " " + re.sub(r"[^A-Z]", " ", p["name"]) + " "
        fem = re.search(r" (FEM|FEMA|FEMME|FEMININO|FEMENINO|WOMEN|WOMAN) ", n); mas = re.search(r" (MASC|MASCULINO|MEN|HOMME|MAN) ", n)
        g = "mujer" if fem and not mas else "hombre" if mas and not fem else None
        if g: p["genderSource"] = "nombre"
    if g: p["gender"] = g
    fams = []
    for a in ((d or {}).get("accords") or [])[:3]:
        f = FAMILIES.get(a)
        if f and f not in fams: fams.append(f)
    if fams: p["families"] = fams
for p in products:
    rate_src = "fila" if p["rate"] else "mediana"
    rate = p.pop("rate") or fallback
    p["usd"] = round(p["usd"] + MARKUP, 2)
    p["ars"] = int(round(p["usd"] * rate / 10) * 10)
    p["rateSource"] = rate_src
json.dump({"products": products, "rates": sorted(set(round(x, 2) for x in rates))}, open("public/products.json", "w"), ensure_ascii=False, indent=1)
print(len(products), "productos,", len({p['brand'] for p in products}), "marcas; tasas:", sorted(set(round(x,2) for x in rates)), "fallback", fallback,
      "sin pesos:", [p["name"] for p in products if p["rateSource"] != "fila"])
