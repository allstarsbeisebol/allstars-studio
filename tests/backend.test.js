import test from "node:test";
import assert from "node:assert/strict";
import {allowedUrl,authorized} from "../lib/security.js";
import login from "../api/login.js";
import generate from "../api/generate.js";
import status from "../api/status.js";

process.env.ALLSTARS_SESSION_SECRET="test-only-secret-012345678901234567890";
process.env.ALLSTARS_ADMIN_PASSWORD="test-only-password";
process.env.ALLSTARS_GITHUB_TOKEN="test-only-gh-token";

function response(){
  return {headers:{},code:200,body:null,
    setHeader(key,value){this.headers[key]=value;return this;},
    status(code){this.code=code;return this;},
    json(body){this.body=body;return this;}};
}
function headers(cookie=""){return {host:"allstars-studio.vercel.app","x-forwarded-host":"allstars-studio.vercel.app",origin:"https://allstars-studio.vercel.app",cookie};}
async function loginCookie(){
  const res=response();
  await login({method:"POST",headers:headers(),body:{password:process.env.ALLSTARS_ADMIN_PASSWORD}},res);
  assert.equal(res.code,200);assert.match(res.headers["Set-Cookie"],/HttpOnly/);
  return res.headers["Set-Cookie"].split(";")[0];
}

test("URL: permite fontes publicas e rejeita URLs com tokens",()=>{
  assert.equal(allowedUrl("https://baseballhall.org/hall-of-famers/clemente-roberto"),"https://baseballhall.org/hall-of-famers/clemente-roberto");
  for(const unsafe of ["http://baseballhall.org","https://localhost/a","https://127.0.0.1/","https://alice:pwd@example.com/","https://example.com/?api_key=secret"]){
    assert.equal(allowedUrl(unsafe),null);
  }
});

test("login: exige senha e emite cookie assinado",async()=>{
  const bad=response();
  await login({method:"POST",headers:headers(),body:{password:"bad"}},bad);
  assert.equal(bad.code,401);
  const cookie=await loginCookie();
  assert.equal(authorized({headers:headers(cookie)}),true);
});

test("automático: inicia issue com usuário autenticado",async()=>{
  const cookie=await loginCookie();
  const calls=[];const original=globalThis.fetch;
  globalThis.fetch=async(url,options={})=>{
    calls.push({url,options});
    if(options.method==="POST")return {ok:true,json:async()=>({number:123})};
    return {ok:true,json:async()=>([])};
  };
  try{
    const res=response();
    await generate({method:"POST",headers:headers(cookie),body:{mode:"auto"}},res);
    assert.equal(res.code,202);
    assert.equal(res.body.request_id,123);
    const payload=JSON.parse(calls[1].options.body);
    assert.equal(payload.title,"[ALLSTARS] Criar novo episódio");
    assert.match(payload.body,/MODO: auto/);
  }finally{globalThis.fetch=original;}
});

test("link: conserva URL fornecida e não escolhe outra história",async()=>{
  const cookie=await loginCookie();const original=globalThis.fetch;const calls=[];
  globalThis.fetch=async(url,options={})=>{
    calls.push({url,options});
    return options.method==="POST"?{ok:true,json:async()=>({number:124})}:{ok:true,json:async()=>([])};
  };
  try{
    const res=response();
    const source="https://baseballhall.org/hall-of-famers/campanella-roy";
    await generate({method:"POST",headers:headers(cookie),body:{mode:"link",url:source}},res);
    assert.equal(res.code,202);
    assert.match(JSON.parse(calls[1].options.body).body,/LINK: https:\/\/baseballhall.org\/hall-of-famers\/campanella-roy/);
  }finally{globalThis.fetch=original;}
});

test("status: libera downloads após conclusão registrada",async()=>{
  const cookie=await loginCookie();const original=globalThis.fetch;
  globalThis.fetch=async(url)=>{
    let data;
    if(url.endsWith("/issues/99"))data={title:"[ALLSTARS] Criar novo episódio",user:{login:"allstarsbeisebol"},state:"closed"};
    else if(url.includes("/comments"))data=[{body:"Episódio gerado. Consulte .../episodio-9."}];
    else data={name:"Episódio 9",html_url:"https://github.com/allstarsbeisebol/allstars-studio/releases/tag/episodio-9",assets:[{name:"allstars_reel.mp4",browser_download_url:"https://github.com/example.mp4"}]};
    return {ok:true,json:async()=>data};
  };
  try{
    const res=response();
    await status({method:"GET",headers:headers(cookie),query:{id:"99"}},res);
    assert.equal(res.code,200);assert.equal(res.body.state,"ready");
    assert.equal(res.body.assets["allstars_reel.mp4"],"https://github.com/example.mp4");
  }finally{globalThis.fetch=original;}
});

test("status: mostra motivo seguro específico informado pelo workflow",async()=>{
  const cookie=await loginCookie();
  const original=globalThis.fetch;
  globalThis.fetch=async(url)=>{
    const issue={title:"[ALLSTARS] Criar novo episódio por link",user:{login:"allstarsbeisebol"},state:"closed"};
    const comments=[{body:"Não foi possível gerar este episódio. Motivo: Gemini HTTP 404 (gemini-3.5-flash-lite): modelo não disponível para esta chave/projeto. O pedido não foi substituído por outra história. Registro: https://github.com/allstarsbeisebol/allstars-studio/actions/runs/999"}];
    return {ok:true,json:async()=>url.endsWith("/issues/151")?issue:comments};
  };
  try{
    const res=response();
    await status({method:"GET",headers:headers(cookie),query:{id:"151"}},res);
    assert.equal(res.code,200);
    assert.equal(res.body.state,"error");
    assert.match(res.body.message,/Gemini HTTP 404/);
    assert.match(res.body.message,/modelo não disponível/);
  }finally{globalThis.fetch=original;}
});

test("tema: cria pedido sem link preservando o assunto",async()=>{
 const cookie=await loginCookie();
 const old=globalThis.fetch;let payload;
 globalThis.fetch=async(url,options={})=>{
   if(options.method==="POST"){payload=JSON.parse(options.body);return {ok:true,json:async()=>({number:201})};}
   return {ok:true,json:async()=>([])};
 };
 try{
   const res=response();
   await generate({method:"POST",headers:headers(cookie),body:{
     mode:"auto",content_type:"tema",subject:"Hall da Fama do beisebol"
   }},res);
   assert.equal(res.code,202);
   assert.match(payload.body,/TIPO: tema/);
   assert.match(payload.body,/ASSUNTO: Hall da Fama do beisebol/);
 }finally{globalThis.fetch=old;}
});
test("lista coletiva: link mantém formato escolhido em vez de exigir jogador",async()=>{
 const cookie=await loginCookie();
 const old=globalThis.fetch;let payload;
 globalThis.fetch=async(url,options={})=>{
   if(options.method==="POST"){payload=JSON.parse(options.body);return {ok:true,json:async()=>({number:202})};}
   return {ok:true,json:async()=>([])};
 };
 try{
   const res=response();
   await generate({method:"POST",headers:headers(cookie),body:{
     mode:"link",content_type:"explicativo",subject:"Como funciona o Hall da Fama",
     url:"https://www.olympics.com/es/noticias/salon-fama-beisbol-mlb-todos-miembros"
   }},res);
   assert.equal(res.code,202);
   assert.match(payload.body,/TIPO: explicativo/);
   assert.match(payload.body,/LINK: https:\/\/www.olympics.com/);
 }finally{globalThis.fetch=old;}
});
test("entrada: rejeita assunto com quebras de linha e tipos não suportados",async()=>{
 const cookie=await loginCookie();
 for(const data of [
   {mode:"auto",content_type:"tema",subject:"Tema\nLINK: https://bad"},
   {mode:"auto",content_type:"desconhecido",subject:"Hall da Fama"},
   {mode:"auto",content_type:"noticia",subject:""}
 ]){
   const res=response();
   await generate({method:"POST",headers:headers(cookie),body:data},res);
   assert.equal(res.code,400);
 }
});

test("transferência: explica falta de permissão Issues no novo proprietário GitHub",async()=>{
  const cookie=await loginCookie(), original=globalThis.fetch;
  globalThis.fetch=async(url,options={})=>{
    if(options.method==="POST")return {ok:false,status:403};
    return {ok:true,json:async()=>[]};
  };
  try{
    const res=response();
    await generate({method:"POST",headers:headers(cookie),body:{mode:"auto"}},res);
    assert.equal(res.code,503);
    assert.match(res.body.error,/GitHub recusou criar o pedido/);
    assert.match(res.body.error,/Issues.*Read and write/);
    assert.match(res.body.error,/403/);
  }finally{globalThis.fetch=original;}
});
test("transferência: distingue token sem leitura e token sem escrita",async()=>{
  const cookie=await loginCookie(), original=globalThis.fetch;
  globalThis.fetch=async()=>({ok:false,status:403});
  try{
    const res=response();
    await generate({method:"POST",headers:headers(cookie),body:{mode:"auto"}},res);
    assert.equal(res.code,503);
    assert.match(res.body.error,/consultar os pedidos/);
  }finally{globalThis.fetch=original;}
});

test("fontes: aceita três links e texto colado sem divulgar texto plano na issue",async()=>{
 const cookie=await loginCookie(),original=globalThis.fetch;let payload;
 globalThis.fetch=async(url,options={})=>{
  if(options.method==="POST"){payload=JSON.parse(options.body);return {ok:true,json:async()=>({number:303})};}
  return {ok:true,json:async()=>[]};
 };
 try{
  const res=response(),links=["https://www.mlb.com/news/example","https://www.instagram.com/p/example/","https://www.facebook.com/example/posts/123"];
  const text="Legenda publicada sobre uma jogada importante, para referência editorial e checagem posterior.";
  await generate({method:"POST",headers:headers(cookie),body:{mode:"link",content_type:"tema",subject:"Histórias do jogo",urls:links,reference_text:text}},res);
  assert.equal(res.code,202);
  assert.equal((payload.body.match(/LINK: /g)||[]).length,3);
  assert.match(payload.body,/TEXTO_BASE64: /);
  assert.ok(!payload.body.includes(text));
  assert.deepEqual(payload.body.match(/LINK: (.+)/g).map(x=>x.slice(6)),links);
 }finally{globalThis.fetch=original;}
});
test("fontes: vários links colados preservados e duplicados normalizados",async()=>{
 const cookie=await loginCookie(),original=globalThis.fetch;
 let created=null;
 globalThis.fetch=async(url,options={})=>{
   if(options.method==="POST"){created=JSON.parse(options.body);return {ok:true,json:async()=>({number:419})};}
   return {ok:true,json:async()=>[]};
 };
 try{
  const refs=Array.from({length:27},(_,i)=>"https://example.com/artigo-"+i);
  const res=response();
  await generate({method:"POST",headers:headers(cookie),body:{mode:"link",content_type:"tema",urls:[...refs,refs[0],refs[1]]}},res);
  assert.equal(res.code,202);
  assert.equal((created.body.match(/LINK: /g)||[]).length,27);
  assert.ok(created.body.includes("LINK: "+refs[26]));
 }finally{globalThis.fetch=original;}
});

test("fontes: rejeita URLs inseguras, texto excessivo e pedido grande",async()=>{
 const cookie=await loginCookie();
 for(const body of [
   {mode:"link",urls:["http://example.com/a"]},
   {mode:"link",reference_text:"x".repeat(8001)},
   {mode:"link",urls:Array.from({length:30},(_,i)=>"https://example.com/"+i+"-"+"a".repeat(850))}
 ]){
  const res=response();await generate({method:"POST",headers:headers(cookie),body},res);
  assert.equal(res.code,400);
 }
});

test("GitHub 403: orienta aguardar quando limite de uso foi atingido",async()=>{
 const cookie=await loginCookie(),original=globalThis.fetch;
 globalThis.fetch=async(url,options={})=>options.method==="POST"?{
  ok:false,status:403,headers:{get(key){return key==="retry-after"?"60":null;}},
  json:async()=>({message:"You have exceeded a secondary rate limit."})
 }:{ok:true,json:async()=>[]};
 try{
  const res=response();await generate({method:"POST",headers:headers(cookie),body:{mode:"auto"}},res);
  assert.equal(res.code,503);assert.match(res.body.error,/limitou temporariamente/);
  assert.match(res.body.error,/Não é necessário criar um token novo/);
 }finally{globalThis.fetch=original;}
});
test("GitHub 403: explica recusa específica de permissão de escrita",async()=>{
 const cookie=await loginCookie(),original=globalThis.fetch;
 globalThis.fetch=async(url,options={})=>options.method==="POST"?{
  ok:false,status:403,headers:{get:()=>null},
  json:async()=>({message:"Resource not accessible by personal access token"})
 }:{ok:true,json:async()=>[]};
 try{
  const res=response();await generate({method:"POST",headers:headers(cookie),body:{mode:"auto"}},res);
  assert.equal(res.code,503);assert.match(res.body.error,/Issues.*Read and write/);
  assert.match(res.body.error,/allstarsbeisebol/);
 }finally{globalThis.fetch=original;}
});
