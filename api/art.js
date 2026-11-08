import {authorized,configured,sameOrigin,json} from "../lib/security.js";
const REPO="allstarsbeisebol/allstars-studio";
const GH="https://api.github.com/repos/"+REPO;
const OWNERS=new Set(["liuhelpme","allstarsbeisebol"]);
const ghHeaders=()=>({
 "Authorization":"Bearer "+process.env.ALLSTARS_GITHUB_TOKEN,
 "Accept":"application/vnd.github+json",
 "X-GitHub-Api-Version":"2022-11-28",
 "User-Agent":"ALLSTARS-Studio"
});
const validIssue=issue=>issue?.state==="open"&&
 issue?.title?.startsWith("[ALLSTARS] Criar novo episódio")&&OWNERS.has(issue.user?.login);

export default async function handler(req,res){
 if(req.method!=="POST")return json(res,405,{error:"Método não permitido."});
 if(!sameOrigin(req))return json(res,403,{error:"Origem não autorizada."});
 if(!configured()||!authorized(req))return json(res,401,{error:"Entre no Studio antes de revisar a imagem."});
 const id=String(req.body?.id||"");
 const action=String(req.body?.action||"");
 const revision=Number(req.body?.revision);
 const notes=typeof req.body?.notes==="string"?req.body.notes.trim():"";
 if(!/^[1-9][0-9]{0,8}$/.test(id)||!Number.isSafeInteger(revision)||revision<1||revision>99999)
   return json(res,400,{error:"Pedido ou versão da imagem inválidos."});
 if(!["approve","revise","regenerate"].includes(action))
   return json(res,400,{error:"Escolha aprovar, corrigir ou gerar uma nova imagem."});
 if(notes.length>1200||/[\x00-\x08\x0b\x0c\x0e-\x1f]/.test(notes))
   return json(res,400,{error:"Ajustes devem ter até 1.200 caracteres."});
 if(action==="revise"&&notes.length<5)
   return json(res,400,{error:"Escreva quais detalhes da imagem deseja corrigir."});
 try{
  const headers=ghHeaders();
  const issueRes=await fetch(GH+"/issues/"+id,{headers});
  if(!issueRes.ok)return json(res,502,{error:"Não foi possível verificar o pedido no GitHub."});
  const issue=await issueRes.json();
  if(!validIssue(issue))return json(res,409,{error:"Este pedido não está disponível para revisão."});
  const commentsRes=await fetch(GH+"/issues/"+id+"/comments?per_page=100",{headers});
  if(!commentsRes.ok)return json(res,502,{error:"Não foi possível verificar o estado da imagem."});
  const comments=await commentsRes.json();
  const readyIndex=comments.findLastIndex(c=>/^ALLSTARS_ART_READY REVISION=\d+ TAG=preview-issue-\d+$/.test(String(c.body||"").trim()));
  if(readyIndex<0)return json(res,409,{error:"A prévia ainda está sendo preparada. Atualize a situação."});
  const ready=String(comments[readyIndex].body).match(/REVISION=(\d+) TAG=preview-issue-(\d+)/);
  if(Number(ready[1])!==revision||ready[2]!==id)
    return json(res,409,{error:"A imagem foi atualizada. Revise a versão mais recente antes de agir."});
  if(comments.slice(readyIndex+1).some(c=>/^(ALLSTARS_ART_CHANGE|ALLSTARS_ART_APPROVE)/.test(String(c.body||""))))
    return json(res,409,{error:"Já existe uma ação solicitada para esta versão. Aguarde a atualização."});
  const body=action==="approve"
   ?"ALLSTARS_ART_APPROVE\nREVISION: "+revision
   :"ALLSTARS_ART_CHANGE\nREVISION: "+revision+"\nACTION: "+action+
    "\nFEEDBACK_BASE64: "+Buffer.from(action==="revise"?notes:"","utf8").toString("base64");
  const commentRes=await fetch(GH+"/issues/"+id+"/comments",{
   method:"POST",headers:{...headers,"Content-Type":"application/json"},body:JSON.stringify({body})
  });
  if(!commentRes.ok){
   if(commentRes.status===403)return json(res,503,{error:"O token do GitHub não permitiu solicitar a revisão. Verifique a permissão Issues: Read and write."});
   return json(res,502,{error:"Não foi possível enviar a decisão de aprovação ao GitHub."});
  }
  return json(res,202,{
   accepted:true,
   state:action==="approve"?"rendering":"art_generating",
   message:action==="approve"?"Imagem aprovada. Iniciando a geração do vídeo.":"Solicitação recebida. Preparando outra versão da imagem."
  });
 }catch{return json(res,502,{error:"Falha na comunicação com o GitHub."});}
}
