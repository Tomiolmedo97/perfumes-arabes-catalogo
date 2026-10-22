# Catálogo Perfumes Árabes
Sitio estático (public/). Datos: `python3 scripts/build_data.py` regenera public/products.json desde la hoja "Perfumes Arabes" (solo Estado=STOCK, +USD 15, pesos = (usd+15) × (Pesos/Usd de la fila), redondeado a $10).

## Imágenes
`data/fragrantica_map.json` (ID o nombre -> URL Fragrantica, id de imagen, archivo local). `python3 scripts/fetch_images.py` descarga las faltantes a public/img (webp 400px). build_data.py las vuelve a asignar al refrescar.

## Carrito
`public/cart.js` (lógica pura: totales y mensaje de WhatsApp) + `public/app.js`; se guarda en localStorage.

## Notas olfativas
`python3 scripts/fetch_details.py` scrapea Fragrantica solo para entradas del mapa (match confiable) que aún no estén en `data/fragrantica_details.json` (traducciones en `data/es_terms.txt`). build_data.py las incorpora a products.json.

**Similar a:** `scripts/fetch_similar.py` (requiere Playwright con navegador visible/Xvfb; Fragrantica no sirve esa sección en headless) lee la sección "This perfume reminds me of" de cada fid nuevo y la guarda en `data/fragrantica_similar_raw.json`. Luego `python3 scripts/make_similar.py` filtra a casas de diseñador/nicho (lista en el script, votos up>=5 y up>down, top 2) y escribe `"similar"` en `data/fragrantica_details.json` (fetch_details.py lo conserva). Filtros de género/aroma se calculan en build_data.py.
