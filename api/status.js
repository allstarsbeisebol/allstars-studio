import {authorized,configured,json} from "../lib/security.js";
const REPO="allstarsbeisebol/allstars-studio";
export default async function handler(req,res){
  if(req.method!=="GET")return json(res,405,{error:"Método não permitido."});
  if(!configured()||!authorized(req))return json(res,401,{error:"Autenticação necessária."});
  const id=String(req.query?.id||"");
  if(!/^[1-9][0-9]{0,8}$/.test(id))return json(res,400,{error:"Pedido inválido."});
  const headers={"Authorization":"Bearer "+process.env.ALLSTARS_GITHUB_TOKEN,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"ALLSTARS-Studio"};
  try{
    const q=await fetch("https://api.github.com/repos/"+REPO+"/issues/"+id,{headers});
    if(!q.ok)return json(res,502,{error:"Não foi possível verificar a produção."});
    const issue=await q.json();
    if(!issue.title?.startsWith("[ALLSTARS] Criar novo episódio")||!["liuhelpme","allstarsbeisebol"].includes(issue.user?.login))return json(res,404,{error:"Pedido não encontrado."});
    const commentsRes=await fetch("https://api.github.com/repos/"+REPO+"/issues/"+id+"/comments?per_page=100",{headers});
    if(!commentsRes.ok)return json(res,502,{error:"Não foi possível consultar a produção."});
    const comments=await commentsRes.json();
    const completed=comments.findLast(c=>/^(Episódio|Vídeo) gerado\./.test(String(c.body||"")));
    if(issue.state==="closed"&&completed){
      const match=String(completed.body||"").match(/episodio-(\d+)/);
      if(!match)return json(res,200,{state:"running",message:"Finalizando arquivos..."});
      const release=await fetch("https://api.github.com/repos/"+REPO+"/releases/tags/episodio-"+match[1],{headers});
      if(!release.ok)return json(res,200,{state:"running",message:"Preparando downloads..."});
      const data=await release.json();
      const assets=Object.fromEntries(data.assets.map(a=>[a.name,a.browser_download_url]));
      return json(res,200,{state:"ready",athlete:data.name,assets,release:data.html_url});
    }
    const failure=comments.findLast(c=>String(c.body||"").startsWith("Não foi possível gerar este episódio"));
    if(failure){
      const body=String(failure.body||"");
      const found=body.match(/Motivo:\s*([\s\S]{1,450}?)\.\s*O pedido não foi substituído/);
      const reason=found?.[1]?.trim();
      const message=reason?
        "Não foi possível gerar: "+reason+".":
        "A geração falhou na chamada ao Gemini. Atualizamos o modelo; tente novamente. Se persistir, confira as permissões e cotas da chave.";
      return json(res,200,{state:"error",message:message.slice(0,480)});
    }
    const artReadyIndex=comments.findLastIndex(c=>/^ALLSTARS_ART_READY REVISION=\d+ TAG=preview-issue-\d+$/.test(String(c.body||"").trim()));
    const artFailedIndex=comments.findLastIndex(c=>String(c.body||"").startsWith("ALLSTARS_ART_FAILED:"));
    const artActionIndex=comments.findLastIndex(c=>/^(ALLSTARS_ART_CHANGE|ALLSTARS_ART_APPROVE)/.test(String(c.body||"")));
    if(artReadyIndex>=0){
      const parsed=String(comments[artReadyIndex].body).match(/REVISION=(\d+) TAG=(preview-issue-\d+)/);
      if(artActionIndex>artReadyIndex&&artFailedIndex<artActionIndex){
        const approved=String(comments[artActionIndex].body).startsWith("ALLSTARS_ART_APPROVE");
        return json(res,200,{state:approved?"rendering":"art_generating",
          message:approved?"Imagem aprovada. Produzindo o vídeo e a narração...":"Preparando a nova versão da imagem..."});
      }
      const release=await fetch("https://api.github.com/repos/"+REPO+"/releases/tags/"+parsed[2],{headers});
      if(!release.ok)return json(res,200,{state:"art_generating",message:"Preparando imagens para conferência..."});
      const data=await release.json();
      const assets=Object.fromEntries((data.assets||[]).filter(a=>["capa.png","capa_perfil_3x4.png","briefing_arte_anime.txt","qualidade_visual.json"].includes(a.name))
        .map(a=>[a.name,a.browser_download_url]));
      const warning=artFailedIndex>artReadyIndex?"A última tentativa de ajuste falhou; a imagem anterior continua disponível para revisão.":"";
      return json(res,200,{state:"art_review",revision:Number(parsed[1]),assets,
        title:data.name||"Prévia ALLSTARS",message:warning||"Confira a capa. Você pode pedir ajustes, gerar outra ou aprovar para produzir o Reel."});
    }
    if(artFailedIndex>=0){
      return json(res,200,{state:"error",message:String(comments[artFailedIndex].body||"").slice(0,380)});
    }
    return json(res,200,{state:"art_generating",message:"Pesquisando o assunto e preparando a primeira imagem para sua aprovação..."});
  }catch{return json(res,502,{error:"Erro ao consultar a produção."});}
}
