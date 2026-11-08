import test from "node:test";
import assert from "node:assert/strict";
import {jpegSize,visualConfigured,storeImage,listImages,reviewImage} from "../lib/visual-storage.js";
import visualApi from "../api/visual-library.js";
import reviewApi from "../api/visual-review.js";
import login from "../api/login.js";

const PROJECT="alrgqmwnynybawenyugb";
const PREFIX="https://"+PROJECT+".supabase.co";
const EP="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa";
const ASSET="bbbbbbbb-bbbb-4bbb-bbbb-bbbbbbbbbbbb";
const REVIEW="cccccccc-cccc-4ccc-cccc-cccccccccccc";

process.env.ALLSTARS_SESSION_SECRET="test-only-secret-012345678901234567890";
process.env.ALLSTARS_ADMIN_PASSWORD="test-only-password";
process.env.ALLSTARS_GITHUB_TOKEN="test-only-token";
process.env.SUPABASE_URL=PREFIX;
process.env.SUPABASE_SERVICE_ROLE_KEY="test-supabase-service-role-for-mocks-only";

const sample=Buffer.concat([Buffer.from([
 0xff,0xd8,0xff,0xe0,0x00,0x10,0x4a,0x46,0x49,0x46,0x00,0x01,0x01,0x00,0x00,0x01,0x00,0x01,0x00,0x00,
 0xff,0xc0,0x00,0x11,0x08,0x07,0x80,0x04,0x38,0x03,0x01,0x11,0x00,0x02,0x11,0x00,0x03,0x11,0x00,
 0xff,0xd9
]),Buffer.alloc(100,0)]);

function reply(data){return {ok:true,status:200,text:async()=>JSON.stringify(data)};}
function response(){
 return {headers:{},code:200,body:null,
  setHeader(n,v){this.headers[n]=v;return this;},
  status(n){this.code=n;return this;},
  json(v){this.body=v;return this;}};
}
function headers(cookie=""){return {
 host:"allstars-studio.vercel.app",
 "x-forwarded-host":"allstars-studio.vercel.app",
 origin:"https://allstars-studio.vercel.app",cookie
};}
async function cookie(){
 const r=response();
 await login({method:"POST",headers:headers(),body:{password:process.env.ALLSTARS_ADMIN_PASSWORD}},r);
 assert.equal(r.code,200);return r.headers["Set-Cookie"].split(";")[0];
}
function mocked(callback){
 const old=globalThis.fetch, calls=[];
 globalThis.fetch=async(url,opts={})=>{
  calls.push({url:String(url),method:opts.method||"GET",body:opts.body,headers:opts.headers});
  return callback(String(url),opts);
 };
 return {calls,restore:()=>globalThis.fetch=old};
}
test("configuração exige o projeto correto e nunca permite origem arbitrária",()=>{
 assert.equal(visualConfigured(),true);
 const good=process.env.SUPABASE_URL;
 process.env.SUPABASE_URL="https://outro.supabase.co";
 assert.equal(visualConfigured(),false);
 process.env.SUPABASE_URL=good;
});
test("metadados JPEG são extraídos do próprio arquivo",()=>{
 const size=jpegSize(sample);
 assert.deepEqual(size,{width:1080,height:1920});
 assert.throws(()=>jpegSize(Buffer.from("foo")),/JPEG inválido/);
});
test("upload privado registra episódio, prompt e origem separada",async()=>{
 const m=mocked((url,opts)=>{
  if(url.includes("/rest/v1/allstars_episodes"))return reply([{id:EP}]);
  if(url.includes("/rest/v1/allstars_visual_prompts"))return reply([{id:REVIEW}]);
  if(url.includes("/storage/v1/object/allstars-visual/issues/"))return reply({Key:"uploaded"});
  if(url.includes("/rest/v1/allstars_visual_assets"))return reply([{id:ASSET}]);
  throw Error("Unexpected "+url);
 });
 try{
  const image=Buffer.alloc(7000,77);
  const stored=await storeImage({issue:53,title:"ALLSTARS episódio",subject:"Jim Abbott",
   assetName:"external-r2-abcdef123456.jpg",image,width:1080,height:1920,revision:1,
   fit:"cover",sourceKind:"generated_external",promptText:"Prompt\ncom\nlinhas"});
  assert.equal(stored.id,ASSET);
  const assetCall=m.calls.find(c=>c.url.includes("/rest/v1/allstars_visual_assets"));
  const body=JSON.parse(assetCall.body)[0];
  assert.equal(body.source_kind,"generated_external");
  assert.equal(body.allow_style_reference,false);
  assert.equal(body.rights_confirmed,true);
  assert.match(body.object_path,/issues\/53\/external-ai\/external-r2-/);
  assert.equal(JSON.parse(m.calls.find(c=>c.url.includes("/rest/v1/allstars_visual_prompts")).body)[0].prompt_text,
   "Prompt\ncom\nlinhas");
  assert.equal(m.calls.some(c=>String(c.headers?.Authorization||"").includes("test-supabase")),true);
 }finally{m.restore();}
});
test("galeria separa geradas e cria link privado temporário",async()=>{
 const m=mocked((url,opts)=>{
  if(url.includes("/rest/v1/allstars_visual_assets"))return reply([{
   id:ASSET,episode_id:EP,source_kind:"generated_studio",approval_status:"review",
   title:"Uma arte",object_path:"issues/53/r1-studio.jpg",
   created_at:"2026-11-08T00:00:00Z",rights_confirmed:true,allow_style_reference:false,metadata:{revision:1}
  }]);
  if(url.includes("/rest/v1/allstars_episodes"))return reply([{id:EP,title:"A arte",subject:"Beisebol",github_issue_number:53}]);
  if(url.includes("/storage/v1/object/sign/allstars-visual"))
   return reply({signedURL:"/object/sign/allstars-visual/issues/53/r1-studio.jpg?token=test-signed-token"});
  throw Error("Unexpected "+url);
 });
 try{
  const rows=await listImages({group:"created"});
  assert.equal(rows.length,1);
  assert.equal(rows[0].source_kind,"generated_studio");
  assert.match(rows[0].image_url,/\/storage\/v1\/object\/sign\/allstars-visual\//);
  assert.ok(m.calls.find(c=>c.url.includes("source_kind=in.%28generated_external%2Cgenerated_studio%29")));
 }finally{m.restore();}
});
test("memória editorial exige confirmação e imagem criada, não fotografia enviada",async()=>{
 const m=mocked((url,opts)=>{
  if(url.includes("/rest/v1/allstars_visual_assets")&&(opts.method||"GET")==="GET")
   return reply([{id:ASSET,episode_id:EP,source_kind:"generated_external",approval_status:"review",
     rights_confirmed:true,allow_style_reference:false}]);
  if(url.includes("/rest/v1/allstars_visual_reviews"))return reply([{id:REVIEW}]);
  if(url.includes("/rest/v1/allstars_visual_assets"))return reply(null);
  if(url.includes("/rest/v1/allstars_style_memory"))return reply(null);
  throw Error("Unexpected "+url);
 });
 try{
  const value=await reviewImage({assetId:ASSET,decision:"approve",rating:5,
   feedback:"Usar contraste forte e iluminação coerente com a época.",learn:true});
  assert.equal(value.ok,true);
  const memory=m.calls.find(c=>c.url.includes("/rest/v1/allstars_style_memory"));
  assert.ok(memory);
  assert.equal(JSON.parse(memory.body)[0].active,true);
  assert.equal(JSON.parse(memory.body)[0].curator_approved,true);
  const update=m.calls.find(c=>c.method==="PATCH"&&c.url.includes("allstars_visual_assets"));
  assert.equal(JSON.parse(update.body).allow_style_reference,true);
 }finally{m.restore();}
});
test("endpoints bloqueiam acesso anônimo",async()=>{
 for(const [fn,method] of [[visualApi,"GET"],[reviewApi,"POST"]]){
  const r=response();
  await fn({method,headers:headers(),query:{group:"all"},body:{asset_id:ASSET,decision:"approve"}},r);
  assert.equal(r.code,401);
 }
});
test("listagem de imagens avisa quando servidor ainda não configurou chave",async()=>{
 const token=await cookie(),original=process.env.SUPABASE_SERVICE_ROLE_KEY;
 delete process.env.SUPABASE_SERVICE_ROLE_KEY;
 try{
  const r=response();await visualApi({method:"GET",headers:headers(token),query:{}},r);
  assert.equal(r.code,200);assert.equal(r.body.configured,false);
 }finally{process.env.SUPABASE_SERVICE_ROLE_KEY=original;}
});
