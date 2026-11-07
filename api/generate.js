import {authorized,configured,sameOrigin,allowedUrl,json} from "../lib/security.js";
const REPO="liuhelpme/allstars-studio";
export default async function handler(req,res){
  if(req.method!=="POST")return json(res,405,{error:"Método não permitido."});
  if(!sameOrigin(req))return json(res,403,{error:"Origem não autorizada."});
  if(!configured())return json(res,503,{error:"Falta concluir a configuração única do serviço."});
  if(!authorized(req))return json(res,401,{error:"Entre no estúdio para gerar episódios."});
  const mode=req.body?.mode;
  if(mode!=="auto"&&mode!=="link")return json(res,400,{error:"Escolha uma das duas opções."});
  const source=mode==="link"?allowedUrl(req.body?.url):null;
  if(mode==="link"&&!source)return json(res,400,{error:"Informe o link HTTPS público de uma matéria ou biografia."});
  const token=process.env.ALLSTARS_GITHUB_TOKEN;
  const headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"ALLSTARS-Studio"};
  try{
    // Evitar novos pedidos se já houver produção sob demanda aguardando conclusão.
    const open=await fetch("https://api.github.com/repos/"+REPO+"/issues?state=open&creator=liuhelpme&per_page=100",{headers});
    if(!open.ok)throw Error("Não foi possível consultar pedidos.");
    const items=await open.json();
    if(items.some(item=>!item.pull_request&&typeof item.title==="string"&&item.title.startsWith("[ALLSTARS] Criar novo episódio"))){
      return json(res,409,{error:"Já existe um episódio em produção. Conclua esse pedido antes de iniciar outro."});
    }
    const body=mode==="link"
      ?"MODO: link\nLINK: "+source+"\n\nGerar episódio a partir deste artigo. Não substituir o atleta por outro se a fonte não estiver acessível."
      :"MODO: auto\n\nGerar próxima história inédita da biblioteca ALLSTARS.";
    const issue=await fetch("https://api.github.com/repos/"+REPO+"/issues",{method:"POST",headers:{...headers,"Content-Type":"application/json"},body:JSON.stringify({title:mode==="link"?"[ALLSTARS] Criar novo episódio por link":"[ALLSTARS] Criar novo episódio",body})});
    if(!issue.ok){const status=issue.status;return json(res,502,{error:"Não foi possível iniciar o gerador no GitHub ("+status+")."});}
    const data=await issue.json();
    return json(res,202,{accepted:true,request_id:data.number,message:"Produção solicitada. O progresso será atualizado aqui."});
  }catch(e){return json(res,502,{error:"Não foi possível conectar ao gerador. Confira as configurações de integração."});}
}
