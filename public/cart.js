// Lógica pura del carrito (también usada en tests con node)
(function(g){
  const ars=n=>"$"+Math.round(n).toLocaleString("es-AR");
  const usd=n=>"USD "+(Math.round(n*100)/100).toLocaleString("es-AR");
  function totals(items){return items.reduce((t,i)=>({qty:t.qty+i.qty,usd:t.usd+i.usd*i.qty,ars:t.ars+i.ars*i.qty}),{qty:0,usd:0,ars:0})}
  const ZONES={CABA:5000,GBA:12000};
  function buildMessage(items,zone){
    const t=totals(items),ship=ZONES[zone]||0;
    const lines=items.map(i=>`• ${i.qty} x ${String(i.brand).toUpperCase()} - ${String(i.name).toUpperCase()} | ${ars(i.ars)} c/u (${usd(i.usd)}) | Subtotal: ${ars(i.ars*i.qty)} (${usd(i.usd*i.qty)})`);
    return ["Hola! Quiero hacer este pedido:","",...lines,"",`Subtotal productos (${t.qty} unidades): ${ars(t.ars)} (${usd(t.usd)})`,
      `Envío ${zone}: ${ars(ship)} (pesos)`,`TOTAL FINAL: ${ars(t.ars+ship)} (pesos)`].join("\n");
  }
  g.Cart={ars,usd,totals,buildMessage,ZONES};
  if(typeof module!=="undefined")module.exports=g.Cart;
})(typeof window!=="undefined"?window:globalThis);
