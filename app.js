const BASE='.';
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const fmt=n=>typeof n==='number'?new Intl.NumberFormat('ja-JP',{maximumFractionDigits:4}).format(n):esc(n);
const qs=new URLSearchParams(location.search);

async function getJson(path){
  const r=await fetch(`${BASE}/${path}?v=${Date.now()}`,{cache:'no-store'});
  if(!r.ok) throw new Error(`${path}: ${r.status}`);
  return r.json();
}
function dayOffset(date,delta){
  const d=new Date(date+'T00:00:00+09:00');
  d.setDate(d.getDate()+delta);
  return new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Tokyo'}).format(d);
}
function toggle(id){document.getElementById(id)?.classList.toggle('open')}
function go(date){location.href=`?date=${date}`}

function renderNews(news=[]){
  return news.map((n,i)=>`<article class="news-item">
    <div class="news-head"><span class="tag">${esc((n.region||'NEWS').toUpperCase())}</span><h3>${esc(n.headline)}</h3></div>
    <div class="summary">${(n.summary||[]).map(s=>`<div class="pair"><div>${esc(s.ja)}</div><div class="en">${esc(s.en)}</div></div>`).join('')}</div>
    <button onclick="toggle('news-${i}')">背景・重要性・出典</button>
    <div id="news-${i}" class="details">
      <div class="label">BACKGROUND</div><div>${esc(n.background)}</div>
      <div class="label">WHY IT MATTERS</div><div>${esc(n.why_it_matters)}</div>
      <div class="label">SOURCES</div><div class="sources">${(n.sources||[]).map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a>`).join('')}</div>
    </div>
  </article>`).join('');
}

function marketRows(m={}){
  const labelMap={fx:'FX',stocks:'STOCKS',rates:'RATES',commodities:'COMMODITIES',crypto:'CRYPTO',cryptos:'CRYPTO',crypto_assets:'CRYPTO',digital_assets:'CRYPTO'};
  return Object.entries(m).filter(([k,v])=>Array.isArray(v)&&v.some(x=>x&&x.symbol&&x.value!=null)&&!['market_moves','moves'].includes(k)).map(([k,arr])=>`<h3>${esc(labelMap[k]||k.replaceAll('_',' ').toUpperCase())}</h3><div class="market-grid">${arr.map(x=>{
    const ch=x.change_pct!=null?`${x.change_pct>0?'+':''}${x.change_pct}%`:x.change_bp!=null?`${x.change_bp>0?'+':''}${x.change_bp}bp`:'';
    return `<div class="market"><div class="symbol">${esc(x.symbol||x.name)}</div><div class="value">${fmt(x.value)}${x.unit?` <span class="unit">${esc(x.unit)}</span>`:''}</div><div class="change">${esc(ch)}</div></div>`;
  }).join('')}</div>`).join('');
}

function culture(c={}){
  const body=c.body||c.bodyMarkdown||c.content||c.text||'';
  const exp=c.explore||c.explore_terms||[];
  return `<h3 class="culture-title">${esc(c.title||'DAILY CULTURE')}</h3><div class="culture-body">${esc(body)}</div>${exp.length?`<div class="label">EXPLORE</div><div class="explore">${exp.map(x=>`<span class="chip">${esc(x)}</span>`).join('')}</div>`:''}`;
}

function quiz(q={}){
  return `<div class="quiz-box"><div class="tag">${esc(q.genre||'DAILY QUIZ')}</div><div class="quiz-q">${esc(q.question)}</div><button class="answer-button" onclick="toggle('quiz-answer')">答えを見る</button><div class="answer" id="quiz-answer"><div class="label">ANSWER</div><div class="answer-text">${esc(q.answer)}</div><div class="label">EXPLANATION</div><div>${esc(q.explanation)}</div>${q.sources?.length?`<div class="label">SOURCES</div><div class="sources">${q.sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.name)}</a>`).join('')}</div>`:''}</div></div>`;
}

function render(d){
  const moves=d.markets?.market_moves||d.markets?.moves||[];
  const app=document.querySelector('#app');
  app.className='';
  app.innerHTML=`<header>
    <div class="kicker">LIFE QUEST / DAILY INTELLIGENCE</div>
    <h1>NEWSPAPER</h1>
    <div class="date">${esc(d.date)} · ${esc(d.timezone||'Asia/Tokyo')}</div>
    <nav><button onclick="go('${dayOffset(d.date,-1)}')">← 前日</button><button onclick="location.href='.'">LATEST</button><button onclick="go('${dayOffset(d.date,1)}')">翌日 →</button></nav>
  </header>
  <section><div class="section-title"><h2>NEWS</h2><span>WORLD + JAPAN</span></div>${renderNews(d.news)}</section>
  <section><div class="section-title"><h2>MARKETS</h2><span>${esc(d.markets?.as_of||'')}</span></div>${marketRows(d.markets)}${moves.length?`<div class="moves"><div class="label">MARKET MOVES</div>${moves.map(x=>`<div class="move"><strong>${esc(x.title||x.asset||x.symbol||'')}</strong><br>${esc(x.body||x.explanation||x.summary||x.reason||'')}</div>`).join('')}</div>`:''}</section>
  <section><div class="section-title"><h2>DAILY CULTURE</h2><span>ONE MORE WAY TO SEE THE WORLD</span></div>${culture(d.daily_culture)}</section>
  <section><div class="section-title"><h2>DAILY QUIZ</h2><span>ONE QUESTION</span></div>${quiz(d.daily_quiz)}</section>`;
  document.title=`NEWSPAPER ${d.date} | 人生クエスト`;
}

async function load(){
  try{
    let path,date=qs.get('date');
    if(date) path=`newspaper/${date}.json`;
    else {const latest=await getJson('newspaper/latest.json');path=latest.path;date=latest.date}
    render(await getJson(path));
  }catch(e){
    const app=document.querySelector('#app');
    app.className='error';
    app.innerHTML=`読み込みに失敗しました。<br><small>${esc(e.message)}</small>`;
  }
}
load();
