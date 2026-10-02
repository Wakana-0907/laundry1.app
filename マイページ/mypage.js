// 主体アプリと同じ蒸発モデルで K0（基準値）を再現し、補正係数の比較に使う
const GAMMA=0.0665,LAMBDA=2.45e6,WIND_HEIGHT=0.6,ABSORB=0.6,VERTICAL=0.5;
function svp(T){return 0.6108*Math.exp(17.27*T/(T+237.3));}
function evapParts(w){
  const es=svp(w.temp),ea=es*w.humid/100,vpd=Math.max(0,es-ea);
  const delta=4098*es/Math.pow(w.temp+237.3,2);
  const hc=5.7+3.8*(w.wind*WIND_HEIGHT);
  const rabs=ABSORB*VERTICAL*w.solar*1000;
  const toG=3600*1000/LAMBDA/(delta+GAMMA);
  return {aero:2*hc*vpd*toG,rad:delta*rabs*toG};
}
const REF_WEATHER={temp:25,humid:50,wind:2.5,solar:0.6},REF_HOURS=2.5;
const K0=(()=>{const p=evapParts(REF_WEATHER);return 180/((p.aero+p.rad)*REF_HOURS);})();
const PRIOR_N=3;

let session=localStorage.getItem('laundry_session');
let isGuest=(session==='__guest__'||!session);
let currentUser=isGuest?null:session;
let users=JSON.parse(localStorage.getItem('laundry_users')||'{}');
let userRec=currentUser?users[currentUser]:null;

function recordsKey(){return 'laundry_records:'+(currentUser||'guest');}
function loadRecords(){try{return JSON.parse(localStorage.getItem(recordsKey())||'[]');}catch(e){return [];}}
function fmtDuration(min){const h=Math.floor(min/60),m=min%60;return `${h>0?h+'時間':''}${m>0||h===0?m+'分':''}`;}

/* ---------- プロフィール ---------- */
function renderProfile(){
  document.querySelector('.app').classList.toggle('is-guest',isGuest);
  if(isGuest){
    document.getElementById('guestBanner').style.display='block';
    document.getElementById('profileCard').style.display='none';
    document.getElementById('accountCard').style.display='none';
  }else{
    document.getElementById('profileCard').style.display='block';
    document.getElementById('accountCard').style.display='block';
    document.getElementById('pUsername').textContent=userRec?.username||'(未設定)';
    document.getElementById('pEmail').textContent=currentUser;
    document.getElementById('pCreated').textContent=userRec?.createdAt
      ?new Date(userRec.createdAt).toLocaleDateString('ja-JP'):'--';
  }
}

/* ---------- 学習状況 ---------- */
function renderLearning(){
  const recs=loadRecords();
  const ks=recs.map(r=>r.k).filter(k=>k>0&&isFinite(k));
  const logSum=PRIOR_N*Math.log(K0)+ks.reduce((s,k)=>s+Math.log(k),0);
  const K=Math.exp(logSum/(PRIOR_N+ks.length));
  const ratio=K/K0;
  const pct=Math.max(4,Math.min(100,50+ (ratio-1)*100));
  document.getElementById('kBar').style.width=pct+'%';
  document.getElementById('kNum').textContent='×'+ratio.toFixed(2);
  if(!ks.length){
    document.getElementById('kNote').textContent='まだ記録がありません。「乾いた！」を記録すると、あなた向けに予測が調整されていきます。';
  }else{
    const dir=ratio>1.05?'ゆっくり乾く傾向':ratio<0.95?'早く乾く傾向':'標準に近い';
    document.getElementById('kNote').textContent=
      `現在の補正係数：基準の×${ratio.toFixed(2)}（${dir}）。記録 ${ks.length} 件から学習しています。`;
  }
}

/* ---------- 過去の記録 ---------- */
function renderRecords(){
  const recs=loadRecords();
  const list=document.getElementById('recordList');
  if(!recs.length){list.innerHTML='<div class="empty-note">まだ記録がありません。</div>';return;}
  list.innerHTML='';
  recs.slice(0,15).forEach(r=>{
    const diff=r.predicted?Math.abs(r.actual-r.predicted):0;
    const big=r.predicted&&diff>60;
    const row=document.createElement('div');
    row.className='record-row'+(big?' diff':'');
    row.innerHTML=`<span class="r-date">${r.date}<br>${r.region}</span>
      <span class="r-detail">予測 ${r.predicted?fmtDuration(r.predicted):'--'}<br>実際 ${fmtDuration(r.actual)}${big?' <strong>(差大)</strong>':''}</span>`;
    list.appendChild(row);
  });
}

/* ---------- アカウント管理 ---------- */
function logout(){
  localStorage.removeItem('laundry_session');
  location.href='login.html';
}
async function hashPassword(password,salt){
  const enc=new TextEncoder().encode(salt+':'+password);
  const buf=await crypto.subtle.digest('SHA-256',enc);
  return Array.from(new Uint8Array(buf)).map(b=>b.toString(16).padStart(2,'0')).join('');
}
function randomSalt(){const a=new Uint8Array(16);crypto.getRandomValues(a);return Array.from(a).map(b=>b.toString(16).padStart(2,'0')).join('');}
async function changePassword(){
  const pwErr=document.getElementById('pwErr'),pwMsg=document.getElementById('pwMsg');
  pwErr.style.display='none';pwMsg.style.display='none';
  const pw=document.getElementById('newPassword').value;
  if(pw.length<6){pwErr.textContent='6文字以上で入力してください。';pwErr.style.display='block';return;}
  const salt=randomSalt(),hash=await hashPassword(pw,salt);
  users[currentUser].salt=salt;users[currentUser].hash=hash;
  localStorage.setItem('laundry_users',JSON.stringify(users));
  document.getElementById('newPassword').value='';
  pwMsg.style.display='block';setTimeout(()=>pwMsg.style.display='none',2000);
}
function deleteAccount(){
  if(!confirm('本当にアカウントを削除しますか？この端末に保存された記録も消えます。'))return;
  delete users[currentUser];
  localStorage.setItem('laundry_users',JSON.stringify(users));
  localStorage.removeItem(recordsKey());
  localStorage.removeItem(defaultsKey());
  localStorage.removeItem('laundry_session');
  location.href='login.html';
}

renderProfile();renderRecords();