import {authorized,configured,json} from "../lib/security.js";
const REPO="allstarsbeisebol/allstars-studio";
const PREFIX="https://github.com/"+REPO+"/releases/download/";
const allowed=new Set(["allstars_reel.mp4","capa.png","capa_perfil_3x4.png","narracao.mp3","legenda_instagram.txt","roteiro.txt","fontes.txt","pesquisa.json","midia.json","briefing_arte_anime.txt","qualidade_visual.json","legendas.srt","legendas_metadata.json"]);
export default async function handler(req,res){
  if(req.method!=="GET")return json(res,405,{error:"Método não permitido."});
  if(!configured()||!authorized(req))return json(res,401,{error:"Entre no Studio para consultar os vídeos anteriores."});
  try{
    const response=await fetch("https://api.github.com/repos/"+REPO+"/releases?per_page=100",{
      headers:{"Authorization":"Bearer "+process.env.ALLSTARS_GITHUB_TOKEN,"Accept":"application/vnd.github+json","User-Agent":"ALLSTARS-Studio"}
    });
    if(!response.ok)return json(res,502,{error:"Não foi possível consultar os vídeos anteriores no GitHub."});
    const releases=await response.json();
    const items=releases.filter(r=>!r.draft&&Array.isArray(r.assets)&&r.assets.some(a=>a.name==="allstars_reel.mp4"))
     .map(r=>{
       const assets={};
       for(const a of r.assets)if(allowed.has(a.name)&&typeof a.browser_download_url==="string"&&a.browser_download_url.startsWith(PREFIX))assets[a.name]=a.browser_download_url;
       const legacy=/^ALLSTARS\\s*-\\s*epis[oó]dio\\s+\\d+$/i.test(String(r.name||""));
       return {tag:r.tag_name,title:legacy?"Vídeo ALLSTARS":String(r.name||"Vídeo ALLSTARS").slice(0,160),
         date:r.published_at||r.created_at,assets,release:r.html_url};
     });
    return json(res,200,{items,has_more:releases.length===100});
  }catch{return json(res,502,{error:"Falha de conexão ao consultar os vídeos anteriores."});}
}
