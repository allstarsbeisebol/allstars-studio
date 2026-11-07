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
    if(url.endsWith("/issues/99"))data={title:"[ALLSTARS] Criar novo episódio",user:{login:"liuhelpme"},state:"closed"};
    else if(url.includes("/comments"))data=[{body:"Episódio gerado. Consulte .../episodio-9."}];
    else data={name:"Episódio 9",html_url:"https://github.com/liuhelpme/allstars-studio/releases/tag/episodio-9",assets:[{name:"allstars_reel.mp4",browser_download_url:"https://github.com/example.mp4"}]};
    return {ok:true,json:async()=>data};
  };
  try{
    const res=response();
    await status({method:"GET",headers:headers(cookie),query:{id:"99"}},res);
    assert.equal(res.code,200);assert.equal(res.body.state,"ready");
    assert.equal(res.body.assets["allstars_reel.mp4"],"https://github.com/example.mp4");
  }finally{globalThis.fetch=original;}
});
