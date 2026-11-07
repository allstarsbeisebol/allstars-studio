import {authorized,configured,json} from "../lib/security.js";
const REPO="liuhelpme/allstars-studio";
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
    if(!issue.title?.startsWith("[ALLSTARS] Criar novo episódio")||issue.user?.login!=="liuhelpme")return json(res,404,{error:"Pedido não encontrado."});
    const commentsRes=await fetch("https://api.github.com/repos/"+REPO+"/issues/"+id+"/comments?per_page=100",{headers});
    if(!commentsRes.ok)return json(res,502,{error:"Não foi possível consultar a produção."});
    const comments=await commentsRes.json();
    const completed=comments.findLast(c=>String(c.body||"").includes("Episódio gerado."));
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
    if(failure)return json(res,200,{state:"error",message:"Não foi possível gerar. Confira se o link é acessível e se o Gemini está configurado."});
    return json(res,200,{state:"running",message:"Pesquisando, narrando e montando o Reel..."});
  }catch{return json(res,502,{error:"Erro ao consultar a produção."});}
}
