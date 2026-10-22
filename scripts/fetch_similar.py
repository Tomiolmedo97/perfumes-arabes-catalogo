#!/usr/bin/env python3
"""Lee la sección 'This perfume reminds me of' (votos de usuarios) de Fragrantica para cada
entrada de data/fragrantica_map.json y guarda la lista cruda en data/fragrantica_similar_raw.json.
La sección se carga con JS, por eso usa Playwright con Chromium visible (requiere DISPLAY, p.ej. xvfb-run).
Uso: python scripts/fetch_similar.py [--all]"""
import json, os, sys, time
from playwright.sync_api import sync_playwright
OUT = "data/fragrantica_similar_raw.json"
M = json.load(open("data/fragrantica_map.json"))
R = json.load(open(OUT)) if os.path.exists(OUT) and "--all" not in sys.argv else {}
todo = sorted({v["fid"]: v["url"] for v in M.values()}.items())
todo = [t for t in todo if t[0] not in R]
JS = """() => { const s=document.querySelector('#similar'); if(!s) return null;
  const t=s.innerText.split('\\n').map(x=>x.trim()).filter(Boolean); const out=[];
  for(let i=0;i<t.length;i++){ if(t[i]==='Compare' && i>=4){ const [b,n,u,d]=t.slice(i-4,i);
     if(/^\\d+$/.test(u)&&/^\\d+$/.test(d)) out.push({brand:b,name:n,up:+u,down:+d}); } }
  return out; }"""
with sync_playwright() as p:
    b = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
    pg = b.new_page()
    for n, (fid, url) in enumerate(todo):
        try:
            pg.goto(url, wait_until="domcontentloaded", timeout=45000)
            for _ in range(14): pg.mouse.wheel(0, 1500); pg.wait_for_timeout(250)
            res = None
            for _ in range(8):
                pg.wait_for_timeout(700); res = pg.evaluate(JS)
                if res: break
            R[fid] = res or []
            print(n, fid, len(R[fid]), flush=True)
        except Exception as e:
            print("FAIL", fid, e, flush=True)
        json.dump(R, open(OUT, "w"), ensure_ascii=False, indent=0)
        time.sleep(2)
    b.close()
