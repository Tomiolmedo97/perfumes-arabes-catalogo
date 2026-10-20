#!/usr/bin/env python3
"""Descarga imágenes de Fragrantica (fimgs.net) para cada entrada de data/fragrantica_map.json
y las guarda como webp ~400px en public/img/. Omite las ya descargadas."""
import json, os, time, io, urllib.request
from PIL import Image
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
m = json.load(open("data/fragrantica_map.json"))
for k, v in m.items():
    out = os.path.join("public", v["image"])
    if os.path.exists(out): continue
    url = f"https://fimgs.net/mdimg/perfume/375x500.{v['fid']}.jpg"
    try:
        data = urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA, "Referer": "https://www.fragrantica.com/"}), timeout=20).read()
        im = Image.open(io.BytesIO(data)).convert("RGB"); im.thumbnail((400, 400))
        bg = Image.new("RGB", (400, 400), "white"); bg.paste(im, ((400 - im.width) // 2, (400 - im.height) // 2))
        bg.save(out, "WEBP", quality=78); print("ok", k)
    except Exception as e:
        print("FAIL", k, url, e)
    time.sleep(0.7)
