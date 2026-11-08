import {authorized,configured,json} from "../lib/security.js";
const REPO="allstarsbeisebol/allstars-studio";
const API="https://api.github.com/repos/"+REPO;
const FILES=new Set([
 "roteiro.txt","legenda_instagram.txt","fontes.txt","briefing_arte_anime.txt",
 "legendas.srt","pesquisa.json","midia.json","qualidade_visual.json",
 "storyboard.json","legendas_metadata.json"
]);
const MAX_BYTES=240000;
export default async function handler(req,res){
 if(req.method!=="GET")return json(res,405,{error:"Método não permitido."});
 if(!configured()||!authorized(req))return json(res,401,{error:"Entre no Studio para visualizar os arquivos."});
 const tag=String(req.query?.tag||""),file=String(req.query?.file||"");
 if(!/^(?:episodio-[1-9]\d{0,8}|preview-issue-[1-9]\d{0,8}|previa-jim-abbott-anime)$/.test(tag)||!FILES.has(file))
   return json(res,400,{error:"Arquivo inválido."});
 try{
  const h={"Authorization":"Bearer "+process.env.ALLSTARS_GITHUB_TOKEN,"Accept":"application/vnd.github+json","User-Agent":"ALLSTARS-Studio"};
  const release=await fetch(API+"/releases/tags/"+encodeURIComponent(tag),{headers:h});
  if(!release.ok)return json(res,502,{error:"Não foi possível encontrar esta publicação."});
  const d=await release.json();
  const item=(d.assets||[]).find(a=>a.name===file);
  const expected="https://github.com/"+REPO+"/releases/download/"+tag+"/"+file;
  if(!item||item.size>MAX_BYTES||item.size<1||item.browser_download_url!==expected)
   return json(res,404,{error:"Este arquivo de texto não está disponível para pré-visualização."});
  const download=await fetch(expected,{redirect:"follow",headers:{"User-Agent":"ALLSTARS-Studio"}});
  if(!download.ok)return json(res,502,{error:"Não foi possível abrir o conteúdo do arquivo."});
  const bytes=await download.arrayBuffer();
  if(bytes.byteLength>MAX_BYTES)return json(res,413,{error:"Arquivo grande demais para visualizar aqui."});
  const content=new TextDecoder("utf-8",{fatal:false}).decode(bytes);
  return json(res,200,{filename:file,tag,text:content});
 }catch{return json(res,502,{error:"Não foi possível consultar o arquivo agora."});}
}
