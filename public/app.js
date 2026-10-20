const WA="https://wa.me/5491130249702";
const norm=s=>s.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
const ars=n=>"$"+n.toLocaleString("es-AR");
const esc=s=>s.replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
fetch("products.json").then(r=>r.json()).then(({products})=>{
  const main=document.getElementById("catalog"),brands=[];
  for(const p of products){let b=brands.find(x=>x.name===p.brand);if(!b)brands.push(b={name:p.brand,items:[]});b.items.push(p)}
  main.innerHTML=brands.map(b=>`<section data-brand><h2>${esc(b.name)}</h2><div class="grid">${b.items.map(p=>{
    const msg=encodeURIComponent(`Hola! Quiero pedir el perfume ${p.brand} - ${p.name} (${ars(p.ars)}).`);
    return `<article class="card" data-n="${esc(norm(p.name+" "+p.brand))}"><div class="img">${p.image?`<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">`:"✦"}</div>
    <div class="body"><div class="name">${esc(p.name)}</div><div class="price">${ars(p.ars)}<span class="usd">USD ${p.usd}</span></div>
    <a class="pedir" href="${WA}?text=${msg}" target="_blank" rel="noopener">Pedir</a></div></article>`}).join("")}</div></section>`).join("");
  const q=document.getElementById("q"),none=document.getElementById("none");
  q.addEventListener("input",()=>{const t=norm(q.value.trim());let any=false;
    main.querySelectorAll("section").forEach(s=>{let v=0;s.querySelectorAll(".card").forEach(c=>{const ok=!t||c.dataset.n.includes(t);c.hidden=!ok;v+=ok});s.hidden=!v;any||=v>0});
    none.hidden=any});
});
