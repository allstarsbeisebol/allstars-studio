import test from "node:test";
import assert from "node:assert/strict";
import login from "../api/login.js";
import status from "../api/status.js";
import art from "../api/art.js";
import preview from "../api/file-preview.js";

process.env.ALLSTARS_SESSION_SECRET="test-only-secret-012345678901234567890";
process.env.ALLSTARS_ADMIN_PASSWORD="test-only-password";
process.env.ALLSTARS_GITHUB_TOKEN="test-only-token";
const REPO="allstarsbeisebol/allstars-studio";
function response(){
 return {headers:{},code:200,body:null,
  setHeader(name,value){this.headers[name]=value;return this;},
  status(code){this.code=code;return this;},
  json(body){this.body=body;return this;}};
}
function headers(cookie=""){return {host:"allstars-studio.vercel.app",
 "x-forwarded-host":"allstars-studio.vercel.app",
 origin:"https://allstars-studio.vercel.app",cookie};}
async function session(){
 const res=response();await login({method:"POST",headers:headers(),body:{password:process.env.ALLSTARS_ADMIN_PASSWORD}},res);
 assert.equal(res.code,200);
 return res.headers["Set-Cookie"].split(";")[0];
}
const ISSUE={title:"[ALLSTARS] Criar novo episódio por link",user:{login:"allstarsbeisebol"},state:"open"};
const FIRST={body:"ALLSTARS_ART_READY REVISION=1 TAG=preview-issue-53"};
const IMAGE="https://github.com/"+REPO+"/releases/download/preview-issue-53/capa.png";

test("status retorna capa e versão, sem publicar vídeo antes da aprovação",async()=>{
 const cookie=await session(),prior=globalThis.fetch;
 globalThis.fetch=async(url)=>{
   const value=url.endsWith("/issues/53")?ISSUE
    :url.includes("/comments")?[FIRST]
    :{name:"Imagem do pedido 53",assets:[{name:"capa.png",browser_download_url:IMAGE},{name:"selected.json",browser_download_url:"not-exposed"}]};
   return {ok:true,json:async()=>value};
 };
 try{
  const res=response();await status({method:"GET",headers:headers(cookie),query:{id:"53"}},res);
  assert.equal(res.code,200);
  assert.equal(res.body.state,"art_review");
  assert.equal(res.body.revision,1);
  assert.equal(res.body.assets["capa.png"],IMAGE);
  assert.equal(res.body.assets["selected.json"],undefined);
 }finally{globalThis.fetch=prior;}
});

test("status: aprovação muda para renderização, não para nova capa",async()=>{
 const cookie=await session(),prior=globalThis.fetch;
 globalThis.fetch=async(url)=>({ok:true,json:async()=>
   url.endsWith("/issues/53")?ISSUE:[FIRST,{body:"ALLSTARS_ART_APPROVE\nREVISION: 1"}]});
 try{
  const res=response();await status({method:"GET",headers:headers(cookie),query:{id:"53"}},res);
  assert.equal(res.code,200);assert.equal(res.body.state,"rendering");
 }finally{globalThis.fetch=prior;}
});

test("aprovação envia comentário GitHub somente para revisão atual",async()=>{
 const cookie=await session(),prior=globalThis.fetch;let comment;
 globalThis.fetch=async(url,options={})=>{
  if(options.method==="POST"){
   comment=JSON.parse(options.body);return {ok:true,json:async()=>({id:1})};
  }
  return {ok:true,json:async()=>url.endsWith("/issues/53")?ISSUE:[FIRST]};
 };
 try{
  const res=response();
  await art({method:"POST",headers:headers(cookie),body:{id:53,action:"approve",revision:1}},res);
  assert.equal(res.code,202);
  assert.equal(res.body.state,"rendering");
  assert.equal(comment.body,"ALLSTARS_ART_APPROVE\nREVISION: 1");
 }finally{globalThis.fetch=prior;}
});

test("corrigir imagem preserva feedback codificado e recusa revisão ultrapassada",async()=>{
 const cookie=await session(),prior=globalThis.fetch;let comment;
 globalThis.fetch=async(url,options={})=>{
  if(options.method==="POST"){comment=JSON.parse(options.body);return {ok:true,json:async()=>({id:1})};}
  return {ok:true,json:async()=>url.endsWith("/issues/53")?ISSUE:[FIRST]};
 };
 try{
  const note="Quero a bola em destaque com uma composição vermelha.";
  const res=response();
  await art({method:"POST",headers:headers(cookie),body:{id:53,action:"revise",notes:note,revision:1}},res);
  assert.equal(res.code,202);
  assert.match(comment.body,/ACTION: revise/);
  const encoded=comment.body.split("FEEDBACK_BASE64: ")[1];
  assert.equal(Buffer.from(encoded,"base64").toString("utf8"),note);
  const stale=response();
  await art({method:"POST",headers:headers(cookie),body:{id:53,action:"approve",revision:2}},stale);
  assert.equal(stale.code,409);
 }finally{globalThis.fetch=prior;}
});

test("prévia de texto autentica e disponibiliza somente arquivo permitido",async()=>{
 const cookie=await session(),prior=globalThis.fetch,tag="episodio-123";
 const assetUrl="https://github.com/"+REPO+"/releases/download/"+tag+"/roteiro.txt";
 globalThis.fetch=async(url)=>url.includes("/releases/tags/")?
   {ok:true,json:async()=>({assets:[{name:"roteiro.txt",size:44,browser_download_url:assetUrl}]})}:
   {ok:true,arrayBuffer:async()=>new TextEncoder().encode("Roteiro original ALLSTARS!").buffer};
 try{
  const res=response();
  await preview({method:"GET",headers:headers(cookie),query:{tag,file:"roteiro.txt"}},res);
  assert.equal(res.code,200);assert.equal(res.body.filename,"roteiro.txt");
  assert.match(res.body.text,/ALLSTARS/);
  const bad=response();
  await preview({method:"GET",headers:headers(cookie),query:{tag,file:"selected.json"}},bad);
  assert.equal(bad.code,400);
 }finally{globalThis.fetch=prior;}
});
