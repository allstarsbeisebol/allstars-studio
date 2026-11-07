import { createHmac, timingSafeEqual } from "node:crypto";

const NAME="allstars_session";
function secret(){return process.env.ALLSTARS_SESSION_SECRET || "";}
export function configured(){
  return Boolean(secret() && process.env.ALLSTARS_ADMIN_PASSWORD && process.env.ALLSTARS_GITHUB_TOKEN);
}
export function safeEqual(a,b){
  const x=Buffer.from(String(a??"")),y=Buffer.from(String(b??""));
  return x.length===y.length && timingSafeEqual(x,y);
}
export function newCookie(){
  const expiry=Date.now()+30*24*3600*1000;
  const body=Buffer.from(JSON.stringify({exp:expiry,role:"admin"})).toString("base64url");
  const sig=createHmac("sha256",secret()).update(body).digest("base64url");
  return NAME+"="+body+"."+sig+"; HttpOnly; Secure; SameSite=Lax; Path=/; Max-Age=2592000";
}
export function authorized(req){
  if(!secret())return false;
  const cookies=(req.headers.cookie||"").split(";").map(v=>v.trim());
  const matched=cookies.find(v=>v.startsWith(NAME+"="));
  if(!matched)return false;
  const val=matched.slice(NAME.length+1);
  const [payload,sig,...rest]=val.split(".");
  if(!payload||!sig||rest.length)return false;
  const expected=createHmac("sha256",secret()).update(payload).digest("base64url");
  if(!safeEqual(sig,expected))return false;
  try{
    const token=JSON.parse(Buffer.from(payload,"base64url").toString("utf8"));
    return token.role==="admin"&&Number.isFinite(token.exp)&&token.exp>Date.now();
  }catch{return false;}
}
export function sameOrigin(req){
  const origin=req.headers.origin;
  if(!origin)return false;
  try{
    const parsed=new URL(origin);
    const expected=req.headers["x-forwarded-host"] || req.headers.host;
    return parsed.protocol==="https:" && parsed.host===expected;
  }catch{return false;}
}
export function json(res,code,body){
  res.setHeader("Cache-Control","no-store");
  res.setHeader("Content-Type","application/json; charset=utf-8");
  return res.status(code).json(body);
}
export function allowedUrl(raw){
  if(typeof raw!=="string"||raw.length>1900)return null;
  try{
    const u=new URL(raw.trim());
    if(u.protocol!=="https:"||!u.hostname||u.username||u.password||u.port)return null;
    if(/^(localhost|\d+\.\d+\.\d+\.\d+)$/i.test(u.hostname)||u.hostname.endsWith(".local"))return null;
    if(u.hostname.startsWith("["))return null;
    return u.toString();
  }catch{return null;}
}
