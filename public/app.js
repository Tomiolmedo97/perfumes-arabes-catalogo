const WA="https://wa.me/5491130249702",KEY="pa_cart_v1";
const {ars,usd,totals,buildMessage,ZONES}=Cart;let zone=localStorage.getItem("pa_zone")||"";
const norm=s=>s.normalize("NFD").replace(/[\u0300-\u036f]/g,"").toLowerCase();
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let byKey={},cart=[];
try{cart=JSON.parse(localStorage.getItem(KEY))||[]}catch{cart=[]}
const $=id=>document.getElementById(id);
function save(){localStorage.setItem(KEY,JSON.stringify(cart));render()}
function add(k,q){const p=byKey[k];if(!p)return;const it=cart.find(i=>i.key===k);
  if(it)it.qty+=q;else cart.push({key:k,brand:p.brand,name:p.name,usd:p.usd,ars:p.ars,qty:q});save();toast(`Agregado: ${p.name}`)}
function setQty(k,q){const it=cart.find(i=>i.key===k);if(!it)return;it.qty=q;if(q<=0)cart=cart.filter(i=>i.key!==k);save()}
function render(){
  cart=cart.filter(i=>byKey[i.key]||!Object.keys(byKey).length);
  cart.forEach(i=>{const p=byKey[i.key]||byKey[String(i.key).toUpperCase()];if(p){i.key=p.key;i.name=p.name;i.brand=p.brand;i.usd=p.usd;i.ars=p.ars}});
  const t=totals(cart);$("count").textContent=t.qty;$("count").hidden=!t.qty;
  $("items").innerHTML=cart.length?cart.map(i=>`<li><div class="ci-name">${esc(i.name)}<small>${esc(i.brand)} · ${ars(i.ars)} c/u</small></div>
   <div class="qty"><button data-d="-1" data-k="${esc(i.key)}" aria-label="Restar">−</button><span>${i.qty}</span><button data-d="1" data-k="${esc(i.key)}" aria-label="Sumar">+</button></div>
   <div class="ci-sub">${ars(i.ars*i.qty)}<button class="rm" data-rm="${esc(i.key)}">Quitar</button></div></li>`).join(""):'<li class="empty">Tu carrito está vacío.</li>';
  const ship=ZONES[zone]||0;
  document.querySelectorAll("input[name=zone]").forEach(r=>r.checked=r.value===zone);
  $("tot").innerHTML=`<div><span>Productos</span><strong>${ars(t.ars)}</strong><small>${usd(t.usd)}</small></div>
   <div><span>Envío${zone?" "+zone:""}</span><strong>${zone?ars(ship):"—"}</strong><small>pesos</small></div>
   <div class="final"><span>Total</span><strong>${ars(t.ars+ship)}</strong><small>pesos</small></div>`;
  $("zhint").hidden=!!zone||!cart.length;
  const ok=cart.length&&zone;$("send").classList.toggle("off",!ok);
  $("send").href=ok?`${WA}?text=${encodeURIComponent(buildMessage(cart,zone))}`:"#";
}
let tt;function toast(m){const e=$("toast");e.textContent=m;e.classList.add("on");clearTimeout(tt);tt=setTimeout(()=>e.classList.remove("on"),1600)}
const open=v=>{document.body.classList.toggle("cart-open",v)};
$("cartBtn").onclick=()=>open(true);$("close").onclick=$("shade").onclick=()=>open(false);
document.querySelectorAll("input[name=zone]").forEach(r=>r.onchange=()=>{zone=r.value;localStorage.setItem("pa_zone",zone);render()});
$("clear").onclick=()=>{if(cart.length&&confirm("¿Vaciar el carrito?")){cart=[];save()}};
$("items").onclick=e=>{const b=e.target.closest("button");if(!b)return;
  if(b.dataset.rm)setQty(b.dataset.rm,0);else{const it=cart.find(i=>i.key===b.dataset.k);if(it)setQty(it.key,it.qty+ +b.dataset.d)}};
fetch("products.json").then(r=>r.json()).then(({products})=>{
  const main=$("catalog"),brands=[];
  for(const p of products){p.name=p.name.toUpperCase();p.brand=p.brand.toUpperCase();p.key=p.id||p.name;byKey[p.key]=p;let b=brands.find(x=>x.name===p.brand);if(!b)brands.push(b={name:p.brand,items:[]});b.items.push(p)}
  main.innerHTML=brands.map(b=>`<section><h2>${esc(b.name)}</h2><div class="grid">${b.items.map(p=>{
    const msg=encodeURIComponent(`Hola! Quiero pedir el perfume ${p.brand} - ${p.name} (${ars(p.ars)}).`);
    return `<article class="card" tabindex="0" data-k="${esc(p.key)}" data-n="${esc(norm(p.name+" "+p.brand))}"><div class="img">${p.image?`<img src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy">`:"<span>✦</span>"}</div>
    <div class="body"><div class="name">${esc(p.name)}</div><div class="price">${ars(p.ars)}<span class="usd">USD ${p.usd}</span></div>
    <div class="actions"><div class="qty sm"><button data-s="-1" aria-label="Menos">−</button><input type="number" min="1" value="1" inputmode="numeric" aria-label="Cantidad"><button data-s="1" aria-label="Más">+</button></div>
    <button class="add" data-add="${esc(p.key)}">Agregar</button></div>
    <a class="pedir" href="${WA}?text=${msg}" target="_blank" rel="noopener">Pedir por WhatsApp</a></div></article>`}).join("")}</div></section>`).join("");
  main.onclick=e=>{const b=e.target.closest("button");
    if(!b){if(e.target.closest("a,input"))return;const c=e.target.closest(".card");if(c)openModal(c.dataset.k);return}const card=b.closest(".card"),inp=card.querySelector("input");
    if(b.dataset.s)inp.value=Math.max(1,(+inp.value||1)+ +b.dataset.s);
    if(b.dataset.add){add(b.dataset.add,Math.max(1,parseInt(inp.value)||1));inp.value=1}};
  main.onkeydown=e=>{if(e.key==="Enter"&&e.target.classList.contains("card"))openModal(e.target.dataset.k)};
  const q=$("q"),none=$("none");
  q.addEventListener("input",()=>{const t=norm(q.value.trim());let any=false;
    main.querySelectorAll("section").forEach(s=>{let v=0;s.querySelectorAll(".card").forEach(c=>{const ok=!t||c.dataset.n.includes(t);c.hidden=!ok;v+=ok});s.hidden=!v;any||=v>0});
    none.hidden=any});
  render();
});
render();

const GEN={women:"Femenino",men:"Masculino","women and men":"Unisex"};
let lastFocus;
function openModal(k){const p=byKey[k];if(!p)return;const d=p.details;lastFocus=document.activeElement;
  const msg=encodeURIComponent(`Hola! Quiero pedir el perfume ${p.brand} - ${p.name} (${ars(p.ars)}).`);
  const chips=xs=>xs.map(x=>`<span>${esc(x)}</span>`).join("");
  let info="";
  if(d){const n=d.notes,rows=[["Salida",n.top],["Corazón",n.middle],["Fondo",n.base],["Notas",n.notes]].filter(r=>r[1]&&r[1].length);
    info=`<p class="desc">${esc(d.description)}</p>${d.accords.length?`<h4>Acordes principales</h4><div class="chips">${chips(d.accords)}</div>`:""}
    ${rows.map(([t,xs])=>`<h4>${t}</h4><div class="chips light">${chips(xs)}</div>`).join("")}<p class="src">Notas: Fragrantica</p>`}
  else info=`<p class="desc">Consultanos por WhatsApp por las notas de este perfume.</p>`;
  $("mbody").innerHTML=`<div class="m-img">${p.image?`<img src="${esc(p.image)}" alt="${esc(p.name)}">`:"<span>✦</span>"}</div>
   <div class="m-head"><small class="m-brand">${esc(p.brand)}${d&&GEN[d.gender]?" · "+GEN[d.gender]:""}${d&&d.year?" · "+d.year:""}</small>
   <h3 id="mtitle">${esc(p.name)}</h3><div class="price">${ars(p.ars)}<span class="usd">USD ${p.usd}</span></div></div>
   <div class="m-info"><div class="actions"><div class="qty sm"><button data-s="-1" aria-label="Menos">−</button><input id="mq" type="number" min="1" value="1" aria-label="Cantidad"><button data-s="1" aria-label="Más">+</button></div>
   <button class="add" id="madd">Agregar</button></div>
   <a class="pedir" href="${WA}?text=${msg}" target="_blank" rel="noopener">Pedir por WhatsApp</a>${info}</div>`;
  $("mbody").querySelectorAll("[data-s]").forEach(b=>b.onclick=()=>{$("mq").value=Math.max(1,(+$("mq").value||1)+ +b.dataset.s)});
  $("madd").onclick=()=>{add(k,Math.max(1,parseInt($("mq").value)||1));closeModal()};
  $("modal").scrollTop=0;document.body.classList.add("modal-open");$("mclose").focus({preventScroll:true})}
function closeModal(){document.body.classList.remove("modal-open");if(lastFocus)lastFocus.focus()}
$("mclose").onclick=$("mshade").onclick=closeModal;
document.addEventListener("keydown",e=>{if(e.key==="Escape"){if(document.body.classList.contains("modal-open"))closeModal();else open(false)}});
