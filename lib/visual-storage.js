/**
 * ALLSTARS Studio — Supabase visual memory, server-only.
 * No service-role credential is exposed to browsers. The private bucket is
 * accessed through short-lived signed URLs, never through public object URLs.
 */
import {createHash} from "node:crypto";

const PROJECT="alrgqmwnynybawenyugb";
const BUCKET="allstars-visual";
const TABLE_PREFIX="allstars_";
const ORIGIN="https://"+PROJECT+".supabase.co";
const NON_PUBLIC=new Set(["allstars_episodes","allstars_visual_assets","allstars_visual_prompts","allstars_visual_reviews","allstars_style_memory"]);

export function visualConfigured(){
 try{
  const url=new URL(process.env.SUPABASE_URL||"");
  return url.protocol==="https:"&&url.origin===ORIGIN&&
    Boolean(process.env.SUPABASE_SERVICE_ROLE_KEY);
 }catch{return false;}
}
function config(){
 if(!visualConfigured())throw Error("Biblioteca visual não configurada: confira SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY no servidor.");
 return {url:ORIGIN,secret:process.env.SUPABASE_SERVICE_ROLE_KEY};
}
function clean(value,max=160){return String(value||"").replace(/[\x00-\x1f]/g," ").trim().slice(0,max);}
function pathOf(path){
 return String(path).split("/").map(encodeURIComponent).join("/");
}
async function request(url,options={}){
 const {secret}=config();
 const headers={
  "apikey":secret,"Authorization":"Bearer "+secret,
  ...options.headers
 };
 const r=await fetch(url,{...options,headers,signal:AbortSignal.timeout(9000)});
 if(!r.ok){
  const err=new Error("Supabase recusou uma operação da biblioteca ("+r.status+").");
  err.status=r.status;throw err;
 }
 if(r.status===204)return null;
 const responseText=await r.text();
 if(!responseText)return null;
 try{return JSON.parse(responseText);}catch{throw Error("Resposta inesperada do Supabase.");}
}
export async function rest(table,query="",opts={}){
 if(!NON_PUBLIC.has(table))throw Error("Tabela não autorizada.");
 const url=ORIGIN+"/rest/v1/"+table+(query?"?"+query:"");
 const body=opts.body===undefined?undefined:JSON.stringify(opts.body);
 return request(url,{method:opts.method||"GET",body,headers:{
   ...(body?{"Content-Type":"application/json"}:{}),
   ...(opts.prefer?{"Prefer":opts.prefer}:{}),
   ...opts.headers
 }});
}
function single(rows){
 if(!Array.isArray(rows)||!rows[0]?.id)throw Error("Não foi possível registrar a imagem na biblioteca.");
 return rows[0];
}
export async function ensureEpisode({issue,title,subject,status="art_review"}){
 if(!Number.isSafeInteger(Number(issue))||Number(issue)<1)throw Error("Identificador inválido.");
 const row={github_issue_number:Number(issue),title:clean(title),subject:clean(subject),editorial_status:status};
 const result=await rest("allstars_episodes","on_conflict=github_issue_number",{
  method:"POST",prefer:"resolution=merge-duplicates,return=representation",body:[row]
 });
 return single(result);
}
export async function addPrompt({episodeId,promptText,revision,kind="external_ai"}){
 const value=String(promptText||"").trim().slice(0,12000);
 if(!value)return null;
 const body=[{episode_id:episodeId,prompt_type:kind,provider:"allstars",
   prompt_text:value,revision_number:Number(revision)||1}];
 return single(await rest("allstars_visual_prompts","",{method:"POST",prefer:"return=representation",body}));
}
export async function storeImage({issue,title,subject,assetName,image,width,height,sourceKind,revision,fit,promptText}){
 if(!/^(?:external-r\d+-[0-9a-f]{12}\.jpg)$/.test(assetName))
  throw Error("Nome de arquivo externo inválido.");
 if(!["uploaded_original","generated_external"].includes(sourceKind))throw Error("Origem não permitida.");
 if(!Buffer.isBuffer(image)||image.length<5000||image.length>1900000)throw Error("Imagem com tamanho inválido.");
 if(!Number.isInteger(width)||!Number.isInteger(height)||Math.min(width,height)<256||
   width>12000||height>12000||width*height>25000000)throw Error("Dimensões inválidas.");
 const path="issues/"+issue+"/"+(sourceKind==="generated_external"?"external-ai":"uploaded")+"/"+assetName;
 const ep=await ensureEpisode({issue,title,subject});
 const prompt=await addPrompt({episodeId:ep.id,promptText,revision:revision+1});
 await request(ORIGIN+"/storage/v1/object/"+BUCKET+"/"+pathOf(path),{
  method:"POST",body:image,
  headers:{"Content-Type":"image/jpeg","x-upsert":"false","Cache-Control":"max-age=3600"}
 });
 const hash=createHash("sha256").update(image).digest("hex");
 const rows=await rest("allstars_visual_assets","",{
  method:"POST",prefer:"return=representation",body:[{
   episode_id:ep.id,prompt_id:prompt?.id||null,
   source_kind:sourceKind,approval_status:"review",bucket_id:BUCKET,object_path:path,
   mime_type:"image/jpeg",file_bytes:image.length,width_px:width,height_px:height,
   sha256_hex:hash,title:clean(title),rights_basis:"permission",rights_confirmed:true,
   allow_style_reference:false,
   metadata:{github_issue_number:Number(issue),revision:revision+1,fit,github_asset:assetName,
     origin:"editor_upload",prompt_supplied:Boolean(prompt)}
  }]
 });
 return single(rows);
}
export function jpegSize(bytes){
 if(!Buffer.isBuffer(bytes)||bytes.length<100||bytes[0]!==255||bytes[1]!==216)throw Error("JPEG inválido.");
 let i=2;
 while(i<bytes.length-9){
  if(bytes[i]!==255){i++;continue;}
  while(bytes[i]===255)i++;
  const marker=bytes[i++];
  if(marker===216||marker===217||marker===1||(marker>=208&&marker<=215))continue;
  if(marker===218)break;
  if(i+2>bytes.length)break;
  const len=bytes.readUInt16BE(i);
  if(len<2||i+len>bytes.length)break;
  if([192,193,194,195,198,199,201,202,203,205,206,207].includes(marker)){
   if(len<7)break;
   return {height:bytes.readUInt16BE(i+3),width:bytes.readUInt16BE(i+5)};
  }
  i+=len;
 }
 throw Error("JPEG sem dimensões válidas.");
}
export async function signImage(path,expiresIn=900){
 const url=ORIGIN+"/storage/v1/object/sign/"+BUCKET+"/"+pathOf(path);
 const result=await request(url,{
  method:"POST",body:JSON.stringify({expiresIn}),
  headers:{"Content-Type":"application/json"}
 });
 const signed=String(result?.signedURL||result?.signedUrl||"");
 if(!signed.startsWith("/object/sign/"+BUCKET+"/")&&!signed.startsWith("/storage/v1/object/sign/"+BUCKET+"/"))
  throw Error("Endereço assinado inválido.");
 return ORIGIN+(signed.startsWith("/storage/v1")?signed:"/storage/v1"+signed);
}
const VISIBLE_FIELDS="id,episode_id,source_kind,approval_status,object_path,mime_type,file_bytes,width_px,height_px,title,visual_tags,rights_confirmed,allow_style_reference,metadata,created_at,approved_at";
export async function listImages({group="all",limit=18}={}){
 const filters=new URLSearchParams();
 filters.set("select",VISIBLE_FIELDS);
 filters.set("order","created_at.desc");
 filters.set("limit",String(Math.max(1,Math.min(18,Number(limit)||18))));
 if(group==="uploaded")filters.set("source_kind","in.(uploaded_original,edited_variant)");
 if(group==="created")filters.set("source_kind","in.(generated_external,generated_studio)");
 if(group==="reference")filters.set("allow_style_reference","eq.true");
 const rows=await rest("allstars_visual_assets",filters.toString());
 if(!Array.isArray(rows)||!rows.length)return [];
 const unique=[...new Set(rows.map(x=>x.episode_id))];
 const filter="id=in.("+unique.join(",")+")";
 const episodes=await rest("allstars_episodes","select=id,github_issue_number,subject,title&"+filter);
 const byId=new Map((episodes||[]).map(e=>[e.id,e]));
 const results=await Promise.all(rows.map(async asset=>{
  let image_url=null;
  try{image_url=await signImage(asset.object_path);}catch{}
  return {
   id:asset.id,source_kind:asset.source_kind,approval_status:asset.approval_status,
   title:asset.title||byId.get(asset.episode_id)?.title||"Imagem ALLSTARS",
   subject:byId.get(asset.episode_id)?.subject||"",
   issue_number:byId.get(asset.episode_id)?.github_issue_number||null,
   created_at:asset.created_at,rights_confirmed:asset.rights_confirmed,
   allow_style_reference:asset.allow_style_reference,visual_tags:asset.visual_tags||[],
   image_url,revision:Number(asset.metadata?.revision)||null
  };
 }));
 return results;
}
export async function reviewImage({assetId,decision,rating,feedback,learn=false}){
 if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/.test(String(assetId)))throw Error("Imagem inválida.");
 if(!["approve","reject","note","disable_reference"].includes(decision))throw Error("Avaliação inválida.");
 if(rating!==null&&(!Number.isInteger(rating)||rating<1||rating>5))throw Error("Nota inválida.");
 const text=clean(feedback,600);
 if(learn&&(!text||text.length<8||rating===null||rating<4))
  throw Error("Para memorizar, dê nota 4 ou 5 e explique o que funcionou.");
 const rows=await rest("allstars_visual_assets","select=id,episode_id,source_kind,approval_status,rights_confirmed,allow_style_reference&"+"id=eq."+encodeURIComponent(assetId)+"&limit=1");
 const asset=rows?.[0];
 if(!asset)throw Error("Imagem não encontrada.");
 if(learn&&(!["generated_external","generated_studio"].includes(asset.source_kind)||!asset.rights_confirmed))
  throw Error("Somente artes criadas e com direitos confirmados podem alimentar a memória editorial.");
 if(decision==="disable_reference"){
  await rest("allstars_visual_assets","id=eq."+asset.id,{method:"PATCH",body:{allow_style_reference:false}});
  await rest("allstars_style_memory","origin_asset_id=eq."+asset.id,{method:"PATCH",body:{active:false}});
  return {ok:true,message:"Imagem retirada das referências de aprendizado."};
 }
 const status=decision==="approve"?(asset.approval_status==="used_in_video"?"used_in_video":"approved"):decision==="reject"?"rejected":asset.approval_status;
 const patch={approval_status:status};
 if(decision==="approve")patch.approved_at=new Date().toISOString();
 if(decision==="reject")patch.allow_style_reference=false;
 if(learn)patch.allow_style_reference=true;
 await rest("allstars_visual_assets","id=eq."+asset.id,{method:"PATCH",body:patch});
 const review=single(await rest("allstars_visual_reviews","",{method:"POST",prefer:"return=representation",body:[{
  episode_id:asset.episode_id,asset_id:asset.id,decision:decision==="disable_reference"?"note":decision,
  rating,feedback_text:text,reviewed_by:"admin"
 }]}));
 if(decision==="reject"){
  await rest("allstars_style_memory","origin_asset_id=eq."+asset.id,{method:"PATCH",body:{active:false}});
 }
 if(learn){
  await rest("allstars_style_memory","",{method:"POST",body:[{
   origin_asset_id:asset.id,origin_review_id:review.id,preference:"prefer",
   summary:text,confidence:Math.round(rating*20)/100,
   curator_approved:true,active:true
  }]});
 }
 return {ok:true,message:learn?"Imagem aprovada e preferência adicionada à memória editorial.":"Avaliação registrada."};
}
export function visualProjectRef(){return PROJECT;}
