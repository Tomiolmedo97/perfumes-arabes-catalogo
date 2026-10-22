"""Filtra data/fragrantica_similar_raw.json (seccion 'This perfume reminds me of' de Fragrantica)
y guarda hasta 2 referencias de casas de diseñador/nicho en data/fragrantica_details.json -> "similar".
Regla: solo marcas en ALLOW, votos up>=5 y up>down, orden por votos up. No se infiere nada."""
import json, pathlib
D = pathlib.Path(__file__).resolve().parent.parent / "data"
ALLOW = {  # marca Fragrantica (mayus) -> etiqueta
 "MAISON FRANCIS KURKDJIAN":"MFK","CREED":"Creed","TOM FORD":"Tom Ford","DIOR":"Dior","CHRISTIAN DIOR":"Dior",
 "CHANEL":"Chanel","GUERLAIN":"Guerlain","YVES SAINT LAURENT":"YSL","GIORGIO ARMANI":"Armani","PARFUMS DE MARLY":"Parfums de Marly",
 "INITIO PARFUMS PRIVES":"Initio","XERJOFF":"Xerjoff","KILIAN":"Kilian","BY KILIAN":"Kilian","LE LABO":"Le Labo","BYREDO":"Byredo",
 "AMOUAGE":"Amouage","MANCERA":"Mancera","MONTALE":"Montale","NISHANE":"Nishane","ROJA DOVE":"Roja","ROJA PARFUMS":"Roja",
 "CAROLINA HERRERA":"Carolina Herrera","PACO RABANNE":"Rabanne","RABANNE":"Rabanne","JEAN PAUL GAULTIER":"JPG","VERSACE":"Versace",
 "PRADA":"Prada","VALENTINO":"Valentino","GIVENCHY":"Givenchy","LANCÔME":"Lancôme","LANCOME":"Lancôme","HERMÈS":"Hermès","HERMES":"Hermès",
 "DOLCE&GABBANA":"Dolce&Gabbana","DOLCE & GABBANA":"Dolce&Gabbana","GUCCI":"Gucci","BURBERRY":"Burberry","MARC JACOBS":"Marc Jacobs",
 "ARIANA GRANDE":"Ariana Grande","VIKTOR&ROLF":"Viktor&Rolf","VIKTOR & ROLF":"Viktor&Rolf","MUGLER":"Mugler","AZZARO":"Azzaro",
 "MONTBLANC":"Montblanc","HUGO BOSS":"Hugo Boss","RALPH LAUREN":"Ralph Lauren","CALVIN KLEIN":"Calvin Klein","ISSEY MIYAKE":"Issey Miyake",
 "KAYALI FRAGRANCES":"Kayali","KAYALI":"Kayali","SOL DE JANEIRO":"Sol de Janeiro","JO MALONE LONDON":"Jo Malone","DIPTYQUE":"Diptyque",
 "MEMO PARIS":"Memo","ATELIER COLOGNE":"Atelier Cologne","FRÉDÉRIC MALLE":"Frédéric Malle","FREDERIC MALLE":"Frédéric Malle",
 "LOUIS VUITTON":"Louis Vuitton","BVLGARI":"Bvlgari","CARTIER":"Cartier","CHLOÉ":"Chloé","CHLOE":"Chloé","GIARDINI DI TOSCANA":"Giardini di Toscana",
 "PARFUMS DE NICOLAI":"Nicolai","ESCENTRIC MOLECULES":"Escentric Molecules","JULIETTE HAS A GUN":"Juliette Has a Gun","ZADIG & VOLTAIRE":"Zadig & Voltaire",
 "BOND NO 9":"Bond No. 9","CLIVE CHRISTIAN":"Clive Christian","ORTO PARISI":"Orto Parisi","TIZIANA TERENZI":"Tiziana Terenzi","ESTÉE LAUDER":"Estée Lauder",
 "NARCISO RODRIGUEZ":"Narciso Rodriguez","ELIE SAAB":"Elie Saab","MAISON MARGIELA":"Maison Margiela","MIU MIU":"Miu Miu","COACH":"Coach",
 "MICHAEL KORS":"Michael Kors","DAVIDOFF":"Davidoff","LOEWE":"Loewe","SERGE LUTENS":"Serge Lutens","FUGAZZI":"Fugazzi","BDK PARFUMS":"BDK",
 "MAISON CRIVELLI":"Maison Crivelli","BOADICEA THE VICTORIOUS":"Boadicea","MATIÈRE PREMIÈRE":"Matière Première","CASAMORATI 1888":"Casamorati",
 "STÉPHANE HUMBERT LUCAS 777":"SHL 777","RAMON MONEGAL":"Ramon Monegal","THE MERCHANT OF VENICE":"The Merchant of Venice",
 "ROSENDO MATEU OLFACTIVE EXPRESSIONS":"Rosendo Mateu","GOLDFIELD & BANKS AUSTRALIA":"Goldfield & Banks","MISSONI":"Missoni","THOMAS KOSMALA":"Thomas Kosmala","ESCADA":"Escada","DKNY":"DKNY","LACOSTE":"Lacoste","ARMANI":"Armani","ARMANI PRIVÉ":"Armani Privé",
}
def label(b): return ALLOW.get(b.upper().strip())
raw = json.load(open(D/"fragrantica_similar_raw.json")); mp = json.load(open(D/"fragrantica_map.json"))
det = json.load(open(D/"fragrantica_details.json"))
out = {}
for fid, items in raw.items():
    ok = [i for i in items if label(i["brand"]) and i["up"] >= 5 and i["up"] > i["down"]]
    ok.sort(key=lambda i: -i["up"])
    out[str(fid)] = [{"name": i["name"], "brand": label(i["brand"]), "up": i["up"], "down": i["down"]} for i in ok[:2]]
n = 0
for k, m in mp.items():
    if k in det:
        det[k].pop("similar", None)
        s = out.get(str(m.get("fid")))
        if s: det[k]["similar"] = s; n += 1
json.dump(det, open(D/"fragrantica_details.json", "w"), ensure_ascii=False, indent=1)
print("con similar:", n)
