import test from "node:test";
import assert from "node:assert/strict";
import login from "../api/login.js";
import upload from "../api/art-upload.js";

process.env.ALLSTARS_SESSION_SECRET="test-only-secret-012345678901234567890";
process.env.ALLSTARS_ADMIN_PASSWORD="test-only-password";
process.env.ALLSTARS_GITHUB_TOKEN="test-only-token";
const ISSUE={title:"[ALLSTARS] Criar novo episódio",user:{login:"allstarsbeisebol"},state:"open"};
const READY={body:"ALLSTARS_ART_READY REVISION=1 TAG=preview-issue-53"};
const JPEG=Buffer.concat([Buffer.from([0xff,0xd8,0xff,0xe0]),Buffer.alloc(7000,76),Buffer.from([0xff,0xd9])]).toString("base64");
function response(){return {
  code:200,body:null,headers:{},
  setHeader(k,v){this.headers[k]=v;return this;},
  status(v){this.code=v;return this;},json(b){this.body=b;return this;}
};}
function headers(cookie=""){return {
  host:"allstars-studio.vercel.app",
  "x-forwarded-host":"allstars-studio.vercel.app",
  origin:"https://allstars-studio.vercel.app",cookie
};}
async function cookie(){
 const res=response();
 await login({method:"POST",headers:headers(),body:{password:process.env.ALLSTARS_ADMIN_PASSWORD}},res);
 assert.equal(res.code,200);
 return res.headers["Set-Cookie"].split(";")[0];
}
function params(image=JPEG){return {id:53,revision:1,fit:"contain",rightsConfirmed:true,image};}
function mock(status=201,comments=[READY]){
 const calls=[];const old=globalThis.fetch;
 globalThis.fetch=async(url,opt={})=>{
  calls.push({url,options:opt});
  if(url.includes("/issues/53/comments")&&opt.method==="POST")return {ok:true,status:201,json:async()=>({id:22})};
  if(url.startsWith("https://uploads.github.com/"))return {ok:status===201,status,json:async()=>({id:55})};
  if(url.endsWith("/issues/53"))return {ok:true,json:async()=>ISSUE};
  if(url.includes("/issues/53/comments"))return {ok:true,json:async()=>comments};
  if(url.includes("/releases/tags/"))return {ok:true,json:async()=>({id:432,assets:[]})};
  throw Error("Unexpected GitHub call "+url);
 };
 return {calls,restore:()=>globalThis.fetch=old};
}
test("capa externa: envia JPEG para release de prévia e registra revisão",async()=>{
 const token=await cookie();const m=mock();
 try{
  const res=response();
  await upload({method:"POST",headers:headers(token),body:params()},res);
  assert.equal(res.code,202);
  assert.equal(res.body.state,"art_generating");
  const asset=m.calls.find(x=>x.url.startsWith("https://uploads.github.com/"));
  assert.ok(asset);
  assert.match(asset.url,/\/releases\/432\/assets\?name=external-r2-[a-f0-9]{12}\.jpg/);
  assert.equal(asset.options.headers["Content-Type"],"image/jpeg");
  assert.ok(Buffer.isBuffer(asset.options.body));
  const comment=m.calls.find(x=>x.url.endsWith("/issues/53/comments")&&x.options.method==="POST");
  assert.ok(comment);
  assert.match(JSON.parse(comment.options.body).body,/ACTION: external\nIMAGE_ASSET: external-r2-[a-f0-9]{12}\.jpg\nFIT: contain/);
 }finally{m.restore();}
});
test("capa externa: bloqueia decisão sobre versão ultrapassada",async()=>{
 const token=await cookie();const m=mock();
 try{
  const res=response();
  await upload({method:"POST",headers:headers(token),body:{...params(),revision:2}},res);
  assert.equal(res.code,409);
  assert.equal(m.calls.some(c=>c.url.startsWith("https://uploads.github.com/")),false);
 }finally{m.restore();}
});
test("capa externa: exige confirmação dos direitos e rejeita conteúdo inválido",async()=>{
 const token=await cookie();
 for(const body of [
   {...params(),rightsConfirmed:false},
   {...params(),image:Buffer.from("isto não é uma imagem").toString("base64")},
   {...params(),fit:"../../private"},
   {...params(),image:"X".repeat(3_000_000)}
 ]){
  const res=response();
  await upload({method:"POST",headers:headers(token),body},res);
  assert.ok([400,413].includes(res.code),String(res.code));
 }
});
test("capa externa: orienta permissão Contents quando GitHub bloqueia upload",async()=>{
 const token=await cookie();const m=mock(403);
 try{
  const res=response();
  await upload({method:"POST",headers:headers(token),body:params()},res);
  assert.equal(res.code,503);
  assert.match(res.body.error,/Contents: Read and write/);
  assert.equal(m.calls.some(c=>c.url.endsWith("/issues/53/comments")&&c.options.method==="POST"),false);
 }finally{m.restore();}
});
test("capa externa: impede concorrência ao alterar uma imagem ainda sendo revisada",async()=>{
 const token=await cookie(),m=mock(201,[READY,{body:"ALLSTARS_ART_CHANGE\nREVISION: 1\nACTION: revise"}]);
 try{
  const res=response();await upload({method:"POST",headers:headers(token),body:params()},res);
  assert.equal(res.code,409);
 }finally{m.restore();}
});
