import {randomBytes} from "node:crypto";
import {authorized,configured,sameOrigin,json} from "../lib/security.js";

const REPO="allstarsbeisebol/allstars-studio";
const GH="https://api.github.com/repos/"+REPO;
const OWNERS=new Set(["liuhelpme","allstarsbeisebol"]);
const MAX_IMAGE_BYTES=1_900_000; // JPEG otimizado no navegador; JSON abaixo do limite serverless.
const headers=()=>({
  "Authorization":"Bearer "+process.env.ALLSTARS_GITHUB_TOKEN,
  "Accept":"application/vnd.github+json",
  "X-GitHub-Api-Version":"2022-11-28",
  "User-Agent":"ALLSTARS-Studio"
});
function responseOk(image){
  // Não confiar apenas no MIME enviado: JPEG real, com marcador de início e fim.
  return image.length>5000&&image.length<=MAX_IMAGE_BYTES&&
    image[0]===0xff&&image[1]===0xd8&&image[2]===0xff&&
    image[image.length-2]===0xff&&image[image.length-1]===0xd9;
}
export default async function handler(req,res){
  if(req.method!=="POST")return json(res,405,{error:"Método não permitido."});
  if(!sameOrigin(req))return json(res,403,{error:"Origem não autorizada."});
  if(!configured()||!authorized(req))return json(res,401,{error:"Entre no Studio antes de enviar uma imagem."});
  const id=String(req.body?.id||"");
  const revision=Number(req.body?.revision);
  const fit=String(req.body?.fit||"contain");
  if(!/^[1-9][0-9]{0,8}$/.test(id)||!Number.isSafeInteger(revision)||revision<1||revision>99999)
    return json(res,400,{error:"Pedido ou versão inválidos."});
  if(!["contain","cover","blur"].includes(fit))return json(res,400,{error:"Escolha um enquadramento válido."});
  if(req.body?.rightsConfirmed!==true)
    return json(res,400,{error:"Confirme que você tem permissão para utilizar esta imagem."});
  const raw=String(req.body?.image||"");
  if(raw.length>Math.ceil(MAX_IMAGE_BYTES*4/3)+8||raw.length<6000||
      !/^[A-Za-z0-9+/]+={0,2}$/.test(raw))
    return json(res,413,{error:"Imagem muito grande ou inválida. Envie até 1,9 MB após otimização."});
  let image;
  try{image=Buffer.from(raw,"base64");}catch{return json(res,400,{error:"Arquivo de imagem inválido."});}
  if(!responseOk(image))return json(res,400,{error:"A imagem precisa ser um JPEG válido. Escolha PNG/JPG/WEBP: o Studio fará a conversão antes do envio."});
  try{
    const h=headers();
    const issueReq=await fetch(GH+"/issues/"+id,{headers:h});
    if(!issueReq.ok)return json(res,502,{error:"Não foi possível conferir o pedido."});
    const issue=await issueReq.json();
    if(issue.state!=="open"||!issue.title?.startsWith("[ALLSTARS] Criar novo episódio")||
       !OWNERS.has(issue.user?.login))
      return json(res,409,{error:"Este pedido não permite alterar a capa."});

    const commentsReq=await fetch(GH+"/issues/"+id+"/comments?per_page=100",{headers:h});
    if(!commentsReq.ok)return json(res,502,{error:"Não foi possível consultar a revisão atual."});
    const comments=await commentsReq.json();
    const readyIndex=comments.findLastIndex(c=>/^ALLSTARS_ART_READY REVISION=\d+ TAG=preview-issue-\d+$/.test(String(c.body||"").trim()));
    if(readyIndex<0)return json(res,409,{error:"A primeira capa ainda não está pronta. Confira o andamento do pedido."});
    const latest=String(comments[readyIndex].body).match(/REVISION=(\d+) TAG=preview-issue-(\d+)/);
    if(Number(latest[1])!==revision||latest[2]!==id)
      return json(res,409,{error:"A capa mudou. Atualize a página para conferir a revisão mais recente."});
    const after=comments.slice(readyIndex+1);
    const cmdIndex=after.findLastIndex(c=>/^(ALLSTARS_ART_CHANGE|ALLSTARS_ART_APPROVE)/.test(String(c.body||"")));
    const failedIndex=after.findLastIndex(c=>String(c.body||"").startsWith("ALLSTARS_ART_FAILED:"));
    if(cmdIndex>=0&&failedIndex<cmdIndex)
      return json(res,409,{error:"Já existe uma decisão para esta capa. Aguarde a próxima versão."});

    const tag="preview-issue-"+id;
    const releaseReq=await fetch(GH+"/releases/tags/"+tag,{headers:h});
    if(!releaseReq.ok)return json(res,502,{error:"Ainda não foi possível acessar a área de revisão da capa."});
    const release=await releaseReq.json();
    if(!Number.isSafeInteger(release.id))return json(res,502,{error:"Registro de prévia inválido."});
    const asset="external-r"+(revision+1)+"-"+randomBytes(6).toString("hex")+".jpg";
    const target="https://uploads.github.com/repos/"+REPO+"/releases/"+release.id+
      "/assets?name="+encodeURIComponent(asset);
    const uploaded=await fetch(target,{
      method:"POST",
      headers:{"Authorization":"Bearer "+process.env.ALLSTARS_GITHUB_TOKEN,
        "Accept":"application/vnd.github+json","Content-Type":"image/jpeg",
        "Content-Length":String(image.length),"User-Agent":"ALLSTARS-Studio"},
      body:image
    });
    if(!uploaded.ok){
      if(uploaded.status===403||uploaded.status===401)
        return json(res,503,{error:"Para enviar a imagem ao GitHub, o token ALLSTARS_GITHUB_TOKEN da Vercel precisa da permissão Contents: Read and write. A permissão Issues continua necessária."});
      return json(res,502,{error:"O GitHub não recebeu a imagem ("+uploaded.status+"). Nenhuma produção foi liberada."});
    }
    const comment="ALLSTARS_ART_CHANGE\nREVISION: "+revision+
      "\nACTION: external\nIMAGE_ASSET: "+asset+"\nFIT: "+fit;
    const created=await fetch(GH+"/issues/"+id+"/comments",{
      method:"POST",headers:{...h,"Content-Type":"application/json"},
      body:JSON.stringify({body:comment})
    });
    if(!created.ok)return json(res,502,{error:"Imagem enviada, mas a solicitação de revisão não foi registrada. Não aprove outra capa até conferir o pedido."});
    return json(res,202,{accepted:true,state:"art_generating",
      message:"Imagem recebida. Preparando a capa e a versão para Instagram, antes de produzir o MP4."});
  }catch{return json(res,502,{error:"Não foi possível enviar a imagem agora. Confira a conexão e tente novamente."});}
}
