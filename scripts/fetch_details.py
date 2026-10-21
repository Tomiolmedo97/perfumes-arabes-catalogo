#!/usr/bin/env python3
"""Obtiene notas olfativas y acordes desde Fragrantica para cada entrada de data/fragrantica_map.json
y genera data/fragrantica_details.json (mismas claves). Solo procesa entradas nuevas salvo --all.
Caché HTML en .cache/fragrantica/. Traducciones en data/es_terms.txt."""
import json, os, re, sys, time, html, urllib.request
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
CACHE = ".cache/fragrantica"; os.makedirs(CACHE, exist_ok=True)
ES = {}
for line in open("data/es_terms.txt", encoding="utf-8"):
    if line.startswith("#"): continue
    for pair in line.strip().split("|"):
        if "=" in pair: k, v = pair.split("=", 1); ES.setdefault(k.strip().lower(), v.strip())
tr = lambda s: ES.get(s.lower(), s.lower())
def txt(s): return re.sub(r"\s+", " ", html.unescape(re.sub("<[^>]+>", " ", s))).strip()
def get(url, fid):
    p = f"{CACHE}/{fid}.html"
    if not os.path.exists(p) or os.path.getsize(p) < 1000:
        req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        open(p, "wb").write(urllib.request.urlopen(req, timeout=30).read()); time.sleep(1.5)
    return open(p, encoding="utf-8", errors="ignore").read()
def parse(s):
    h = re.search(r"<h1[^>]*>(.*?)</h1>", s, re.S); h1 = txt(h.group(1)) if h else ""
    g = re.search(r"for (women and men|women|men)\s*$", h1)
    y = re.search(r"was launched in (\d{4})", s)
    acc = []
    i = s.find("main accords</h6>")
    if i >= 0:
        blk = s[i:i + 12000]; blk = blk.split("pyramid")[0]
        acc = [txt(x) for x in re.findall(r'<span class="truncate">(.*?)</span>', blk)][:6]
    lv = {}
    for m in re.finditer(r'<pyramid-level-new notes="(\w+)">(.*?)</pyramid-level-new>', s, re.S):
        n = [txt(x) for x in re.findall(r"pyramid-note-label[^>]*>(.*?)</span>", m.group(2), re.S)]
        if n: lv.setdefault(m.group(1), []).extend(n)
    return (g.group(1) if g else None), (int(y.group(1)) if y else None), acc, lv
def lst(xs):
    xs = list(dict.fromkeys(xs))
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " y " + xs[-1]
GEN = {"women": "Fragancia femenina", "men": "Fragancia masculina", "women and men": "Fragancia unisex"}
def describe(g, y, acc, notes):
    parts = [GEN.get(g, "Fragancia")]
    if y: parts[0] += f" lanzada en {y}"
    s = parts[0] + "."
    if acc: s += f" De perfil {lst(acc[:3])}."
    if "top" in notes and "base" in notes:
        s += f" Abre con {lst(notes['top'][:3])}"
        if notes.get("middle"): s += f", su corazón tiene {lst(notes['middle'][:3])}"
        s += f" y se asienta sobre {lst(notes['base'][:3])}."
    elif notes.get("notes"):
        s += f" Destacan {lst(notes['notes'][:4])}."
    return s
if __name__ == "__main__":
    M = json.load(open("data/fragrantica_map.json"))
    out_p = "data/fragrantica_details.json"
    D = json.load(open(out_p)) if os.path.exists(out_p) and "--all" not in sys.argv else {}
    for k, v in M.items():
        if k in D: continue
        try:
            g, y, acc, lv = parse(get(v["url"], v["fid"]))
        except Exception as e:
            print("FAIL", k, e); continue
        notes = {}
        for src, dst in (("top", "top"), ("middle", "middle"), ("base", "base")):
            if lv.get(src): notes[dst] = [tr(n) for n in lv[src]]
        flat = [n for k2, ns in lv.items() if k2 not in ("top", "middle", "base") for n in ns]
        if flat and not notes: notes["notes"] = [tr(n) for n in flat]
        accs = [tr(a) for a in acc]
        if not notes and not accs: print("SIN DATOS", k); continue
        D[k] = {"url": v["url"], "gender": g, "year": y, "accords": accs, "notes": notes, "description": describe(g, y, accs, notes)}
    json.dump(D, open(out_p, "w"), ensure_ascii=False, indent=1)
    print(len(D), "entradas;", sum(bool(d["notes"]) for d in D.values()), "con notas")
    missing = sorted({n for d in D.values() for ns in d["notes"].values() for n in ns if n.lower() not in {x.lower() for x in ES.values()}})
    if missing: print("Sin traducir:", missing)
