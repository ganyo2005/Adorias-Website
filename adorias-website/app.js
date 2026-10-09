
// Django backend base URL. The frontend is served as static files (this
// server); the API/data/session logic lives in the separate Django process.
const API_BASE="http://localhost:8000/api";
const products=window.ADORIAS_CATALOGUE||[];
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const esc=s=>(s??"").toString().replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"}[m]));
const icons={"Cameras & Video":"◉","Lenses":"◎","Lighting & Studio":"✦","Audio":"◖","Live Production":"▦","Tripods & Support":"⌁","Accessories":"＋","Printing & Photo":"▤","Drones & Gimbals":"◇"};
let active="All", query="", shown=24, cart=[], activeBrand="All";
const publicCats=["Cameras & Video","Lenses","Lighting & Studio","Audio","Live Production","Tripods & Support","Accessories","Printing & Photo","Drones & Gimbals"];

function categoryCards(){
 const grid=$("#categoryGrid"); if(!grid)return;
 grid.innerHTML=publicCats.map(c=>`<article class="category" data-cat="${esc(c)}"><div class="icon">${icons[c]||"＋"}</div><div><h3>${esc(c)}</h3><small>Explore equipment →</small></div></article>`).join("");
}
function filtered(){return products.filter(p=>(active==="All"||p.category===active)&&(activeBrand==="All"||p.brand===activeBrand)&&(!query||JSON.stringify(p).toLowerCase().includes(query)))}
function brandBar(list){
 const host=$("#brandFilterBar"); if(!host)return;
 const brands=[...new Set(list.map(p=>p.brand).filter(Boolean))].sort((a,b)=>a.localeCompare(b));
 host.innerHTML=brands.length>1?`<button class="brandChip ${activeBrand==="All"?"active":""}" data-brand="All">All brands</button>`+brands.map(b=>`<button class="brandChip ${activeBrand===b?"active":""}" data-brand="${esc(b)}">${esc(b)}</button>`).join(""):"";
}
function render(){
 const categoryList=products.filter(p=>(active==="All"||p.category===active)&&(!query||JSON.stringify(p).toLowerCase().includes(query)));
 brandBar(categoryList);
 const list=filtered(), grid=$("#productGrid"); if(!grid)return;
 grid.innerHTML=list.slice(0,shown).map(p=>`<article class="product" data-sku="${esc(p.sku)}" tabindex="0" aria-label="View ${esc(p.name)} details">
 <div class="productVisual"><span class="stock">${p.exact?"MODEL VERIFIED":"AVAILABLE RANGE"}</span>${p.image?`<img class="productPhoto" src="${esc(p.image)}" alt="${esc(p.name)}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='block'"><span class="fallbackIcon" style="display:none">${icons[p.category]||"＋"}</span>`:`<span class="fallbackIcon">${icons[p.category]||"＋"}</span>`}</div>
 <div class="productInfo"><small>${esc(p.brand)} · ${esc(p.category)}</small><h3>${esc(p.name)}</h3>
 <div class="productBottom"><strong>${p.model?esc(p.model):"Ask for current options"}</strong><button class="add" data-add="${esc(p.sku)}" title="Add to enquiry">＋</button></div></div></article>`).join("");
}
categoryCards();render();

$("#categoryGrid")?.addEventListener("click",e=>{
 const card=e.target.closest("[data-cat]");if(!card)return;
 active=card.dataset.cat;activeBrand="All";shown=24;
 $$(".filters button").forEach(b=>b.classList.toggle("active",b.dataset.filter===active));
 render();location.hash="products";
});
let detailOpener=null;
function openProductDetail(p){
 const modal=$("#productDetailModal"),host=$("#productDetailContent");if(!modal||!host||!p)return;
 detailOpener=document.activeElement;
 modal.querySelector(".productDetailPanel").scrollTop=0;
 const gallery=[...new Set((p.images?.length?p.images:[p.image]).filter(Boolean))];
 const specs=String(p.keySpecifications||p.specs||"");
 const rows=[
   ["Key specifications",specs],
   ["Lens / mount",p.mount||p.lensMount||p.lens],
   ["Video",p.videoCapabilities||p.video||specs.split(/[•;]/).filter(v=>/video|4k|8k|1080|hdmi|sdi|fps/i.test(v)).join(" • ")],
   ["Compatibility / use",p.compatibility||p.useCases],
   ["Battery",p.battery],
   ["Power / charger",p.charger||p.chargerPower||p.power]
 ].filter(([,v])=>v);
 host.innerHTML=`<div class="detailGallery">
   <div class="detailMainImage">${gallery.length?`<img id="detailMainPhoto" src="${esc(gallery[0])}" alt="${esc(p.name)} — view 1">`:'<p class="detailImagePlaceholder">Product photos are not available yet.</p>'}</div>
   ${gallery.length?`<p class="detailPhotoCount" id="detailPhotoCount">1 / ${gallery.length}${gallery.length===1?' — one photo available':''}</p><div class="detailThumbs" aria-label="Product photos">${gallery.map((im,i)=>`<button type="button" data-detail-img="${esc(im)}" data-view="${i+1}" data-total="${gallery.length}" data-name="${esc(p.name)}" aria-label="Show ${esc(p.name)} view ${i+1}" aria-pressed="${i===0}"><img src="${esc(im)}" alt="View ${i+1}"></button>`).join("")}</div>`:''}
   </div><div class="detailInfo"><div class="detailBrand">${esc(p.brand)}</div><h2 id="detailTitle">${esc(p.name)}</h2>
   ${p.description?`<p>${esc(p.description)}</p>`:''}
   ${rows.length?rows.map(([label,value])=>`<section><h3>${label}</h3><p>${esc(value)}</p></section>`).join(''):'<p>Exact specifications need confirmation.</p>'}
   <div class="detailActions"><button class="btn primary" type="button" data-add="${esc(p.sku)}">Add to enquiry</button><a class="btn ghost" target="_blank" rel="noopener" href="https://wa.me/233249220653?text=${encodeURIComponent("Hi Adorias, I'm interested in "+p.name)}">Ask on WhatsApp</a></div><p id="detailCartStatus" role="status"></p></div>`;
 modal.classList.add("open");modal.setAttribute("aria-hidden","false");document.body.classList.add("detailOpen");
 modal.querySelector('[data-close-detail].productDetailClose')?.focus();
}
function closeProductDetail(){
 const modal=$("#productDetailModal");modal?.classList.remove("open");modal?.setAttribute("aria-hidden","true");document.body.classList.remove("detailOpen");
 if(detailOpener?.isConnected)detailOpener.focus();
}
$("#productGrid")?.addEventListener("click",e=>{
 const add=e.target.closest("[data-add]");if(add){addCart(add.dataset.add);return;}
 const card=e.target.closest(".product[data-sku]");if(card)openProductDetail(products.find(p=>p.sku===card.dataset.sku));
});
$("#productGrid")?.addEventListener("keydown",e=>{
 if((e.key==='Enter'||e.key===' ')&&e.target.matches('.product[data-sku]')){e.preventDefault();openProductDetail(products.find(p=>p.sku===e.target.dataset.sku));}
});
$("#productDetailModal")?.addEventListener("click",e=>{
 if(e.target.closest("[data-close-detail]")){closeProductDetail();return;}
 const thumb=e.target.closest("[data-detail-img]");if(thumb){
   const photo=$("#detailMainPhoto");photo.src=thumb.dataset.detailImg;photo.alt=thumb.dataset.name+' — view '+thumb.dataset.view;
   $$('.detailThumbs button').forEach(b=>b.setAttribute('aria-pressed',String(b===thumb)));
   $("#detailPhotoCount").textContent=thumb.dataset.view+' / '+thumb.dataset.total;
 }
 const add=e.target.closest('[data-add]');if(add){addCart(add.dataset.add);$('#detailCartStatus').textContent='Added to your enquiry.';}
});
document.addEventListener("keydown",e=>{
 const modal=$("#productDetailModal");if(!modal?.classList.contains('open'))return;
 if(e.key==='Escape')closeProductDetail();
 if(e.key==='Tab'){
   const controls=[...modal.querySelectorAll('button,a[href]')];const first=controls[0],last=controls.at(-1);
   if(e.shiftKey&&document.activeElement===first){e.preventDefault();last?.focus();}
   else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first?.focus();}
 }
});
$("#customerFilters")?.addEventListener("click",e=>{const b=e.target.closest("[data-filter]");if(!b)return;active=b.dataset.filter;activeBrand="All";shown=24;$$(".filters button").forEach(x=>x.classList.toggle("active",x===b));render()});
$("#brandFilterBar")?.addEventListener("click",e=>{const b=e.target.closest("[data-brand]");if(!b)return;activeBrand=b.dataset.brand;shown=24;render()});
$("#catalogueSearch")?.addEventListener("input",e=>{query=e.target.value.trim().toLowerCase();activeBrand="All";shown=24;render()});
function openProduct(p){openProductDetail(p);}
function addCart(sku){const p=products.find(x=>x.sku===sku);if(p&&!cart.some(x=>x.sku===sku))cart.push(p);const c=$("#cartCount");if(c)c.textContent=cart.length;renderCart()}
window.addCart=addCart;
function renderCart(){const body=$("#cartItems")||$(".cartItems");if(body)body.innerHTML=cart.map(p=>`<div class="cartLine"><b>${esc(p.name)}</b><small>${esc(p.sku)}</small></div>`).join("")||"<p>No items added yet.</p>"}
$("#cartBtn")?.addEventListener("click",()=>{$("#cartDrawer")?.classList.add("open")});
$$("[data-close],.closeModal,.drawerClose").forEach(b=>b.addEventListener("click",()=>b.closest(".open")?.classList.remove("open")));
$("#specialBtn")?.addEventListener("click",()=>$("#specialModal")?.showModal());
$("#specialModal .modalClose")?.addEventListener("click",()=>$("#specialModal")?.close());
$("#specialForm")?.addEventListener("submit",async e=>{
 e.preventDefault();
 const form=e.target,status=$("#specialFormStatus");
 const payload={
   name:form.elements.name.value.trim(),
   phone:form.elements.phone.value.trim(),
   brand_model:form.elements.brand_model.value.trim(),
   quantity:Number(form.elements.quantity.value)||1,
   notes:form.elements.notes.value.trim()
 };
 if(status)status.textContent="Sending...";
 try{
   const res=await fetch(API_BASE+"/orders/special-order/",{
     method:"POST",
     headers:{"Content-Type":"application/json"},
     credentials:"include",
     body:JSON.stringify(payload)
   });
   if(!res.ok)throw new Error("request failed");
   const data=await res.json();
   form.reset();
   $("#specialModal")?.close();
   window.open(data.whatsapp_url,"_blank");
 }catch(err){
   if(status)status.textContent="Couldn't send the request. Please check your connection and try again.";
 }
});
$(".menuBtn")?.addEventListener("click",()=>$("#mainNav")?.classList.toggle("open"));
const canvas=$("#motionCanvas"),ctx=canvas?.getContext("2d");let dots=[];
function size(){if(!canvas)return;canvas.width=innerWidth;canvas.height=innerHeight;dots=Array.from({length:55},()=>({x:Math.random()*innerWidth,y:Math.random()*innerHeight,r:Math.random()*1.5+.4,s:Math.random()*.25+.08}))}
function motion(){if(!ctx)return;ctx.clearRect(0,0,canvas.width,canvas.height);ctx.fillStyle="rgba(80,130,255,.28)";dots.forEach(d=>{d.y-=d.s;if(d.y<0)d.y=innerHeight;ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,7);ctx.fill()});requestAnimationFrame(motion)}size();motion();addEventListener("resize",size);
addEventListener("mousemove",e=>{const g=$(".cursorGlow");if(g){g.style.left=e.clientX+"px";g.style.top=e.clientY+"px"}});

/* EFIA_CHAT_WIRED_V632 */
function efiaAddBubble(text,who="bot"){
 const chat=$("#chat"); if(!chat)return;
 const d=document.createElement("div");d.className="bubble "+who;
 if(who==="bot") d.innerHTML=efiaFormatReadableV671(text);
 else d.textContent=text;
 chat.appendChild(d);chat.scrollTop=chat.scrollHeight;
}
$("#efiaBtn")?.addEventListener("click",()=>$("#efiaDrawer")?.classList.add("open"));
$("#efiaDrawer .close")?.addEventListener("click",()=>$("#efiaDrawer")?.classList.remove("open"));
const EFIA_FALLBACK="I can help with Adorias equipment, but I don't want to guess. Tell me the exact product or camera model and what you want to use it for.";
async function efiaAsk(q){
 try{
   const res=await fetch(API_BASE+"/efia/chat/",{
     method:"POST",
     headers:{"Content-Type":"application/json"},
     credentials:"include", // keeps the Django session cookie so multi-turn context persists
     body:JSON.stringify({message:q})
   });
   if(!res.ok)return EFIA_FALLBACK;
   const data=await res.json();
   return data.reply||EFIA_FALLBACK;
 }catch(err){
   return "I couldn't reach the Adorias assistant service. Please check your connection and try again.";
 }
}
$("#chatForm")?.addEventListener("submit",async e=>{
 e.preventDefault();const input=$("#chatInput"),q=(input?.value||"").trim();if(!q)return;
 efiaAddBubble(q,"user");input.value="";
 const answer=await efiaAsk(q);
 efiaAddBubble(answer,"bot");
});
$("#efiaDrawer .quick")?.addEventListener("click",e=>{
 const b=e.target.closest("button");if(!b)return;
 const prompts={Camera:"Which camera should I consider?",Lighting:"What lighting options do you carry?",Livestreaming:"What equipment do I need for livestreaming?","Studio setup":"What do I need for a studio setup?"};
 const input=$("#chatInput");if(input){input.value=prompts[b.textContent]||b.textContent;$("#chatForm")?.requestSubmit();}
});


/* V6.61 floating Efia access */
document.addEventListener("DOMContentLoaded",()=>{
  const launcher=document.getElementById("efiaFloatingLauncher");
  if(!launcher) return;
  launcher.addEventListener("click",()=>{
    const existing=document.getElementById("efiaBtn");
    if(existing){ existing.click(); launcher.setAttribute("aria-expanded","true"); return; }
    const drawer=document.querySelector(".efiaDrawer,#efiaDrawer,[data-efia-drawer]");
    if(drawer){ drawer.classList.add("open","active"); drawer.removeAttribute("hidden"); launcher.setAttribute("aria-expanded","true"); }
  });
});


/* === V6.64 Efia launcher visibility === */
function efiaSetLauncherVisible(show){
  const launcher=document.getElementById("efiaFloatingLauncher");
  const hint=document.getElementById("efiaFloatingHint");
  if(launcher) launcher.classList.toggle("efiaLauncherHidden",!show);
  if(hint) hint.classList.toggle("efiaLauncherHidden",!show);
}
document.addEventListener("DOMContentLoaded",()=>{
  const launcher=document.getElementById("efiaFloatingLauncher");
  if(launcher) launcher.addEventListener("click",()=>setTimeout(()=>efiaSetLauncherVisible(false),0));
  const drawer=document.querySelector(".efiaDrawer,#efiaDrawer,[data-efia-drawer]");
  if(drawer){
    const observer=new MutationObserver(()=>{
      const open=drawer.classList.contains("open")||drawer.classList.contains("active")||!drawer.hasAttribute("hidden");
      efiaSetLauncherVisible(!open);
    });
    observer.observe(drawer,{attributes:true,attributeFilter:["class","hidden","style"]});
  }
  document.addEventListener("click",e=>{
    if(e.target.closest(".efiaClose,#efiaClose,[data-efia-close]")) efiaSetLauncherVisible(true);
  });
});


/* === EFIA READABILITY + CONTEXT V6.71 === */
function efiaFormatReadableV671(raw){
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));
  const lines=String(raw||"").split(/\n/).map(x=>x.trim());
  let html="", open=false;
  const close=()=>{if(open){html+="</div>";open=false;}};
  for(const line of lines){
    if(!line){close();continue;}
    let m=line.match(/^(\d+)\.\s+(.+)$/);
    if(m){close();open=true;html+=`<div class="efiaOption"><div class="efiaOptionTitle"><span>${m[1]}</span><strong>${esc(m[2])}</strong></div>`;continue;}
    if(/^(ESSENTIALS|OPTIONAL(?:\s*\/\s*NICE TO HAVE)?|WHY IT WORKS|KEEP IN MIND)$/i.test(line)){
      close();html+=`<div class="efiaSectionTitle">${esc(line)}</div>`;continue;
    }
    if(/^[-•✓]\s*/.test(line)){html+=`<div class="efiaBullet">${esc(line)}</div>`;continue;}
    if(/^Consider:/i.test(line)){html+=`<div class="efiaConsider">${esc(line)}</div>`;continue;}
    html+=`<div class="efiaParagraph">${esc(line)}</div>`;
  }
  close(); return html;
}
window.efiaFormatReadableV671=efiaFormatReadableV671;


