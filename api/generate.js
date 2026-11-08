import {authorized,configured,sameOrigin,allowedUrl,json} from "../lib/security.js";
const REPO="allstarsbeisebol/allstars-studio";
export default async function handler(req,res){
  if(req.method!=="POST")return json(res,405,{error:"Método não permitido."});
  if(!sameOrigin(req))return json(res,403,{error:"Origem não autorizada."});
  if(!configured())return json(res,503,{error:"Falta concluir a configuração única do serviço."});
  if(!authorized(req))return json(res,401,{error:"Entre no estúdio para gerar episódios."});
  const mode=req.body?.mode;
  if(mode!=="auto"&&mode!=="link")return json(res,400,{error:"Escolha uma das duas opções."});
  const types=new Set(["auto","atleta","tema","noticia","lista","explicativo"]);
  const contentType=typeof req.body?.content_type==="string"?req.body.content_type.trim().toLowerCase():"auto";
  if(!types.has(contentType))return json(res,400,{error:"Escolha um tipo de conteúdo válido."});
  const subject=typeof req.body?.subject==="string"?req.body.subject.trim():"";
  if(subject.length>160||/[\r\n\x00-\x1F]/.test(subject))return json(res,400,{error:"O assunto deve ter até 160 caracteres em uma única linha."});
  const rawUrl=typeof req.body?.url==="string"?req.body.url.trim():"";
  const source=rawUrl?allowedUrl(rawUrl):null;
  if(rawUrl&&!source)return json(res,400,{error:"Informe um link HTTPS público válido."});
  if(mode==="link"&&!source)return json(res,400,{error:"Informe o link HTTPS público de uma matéria ou biografia."});
  if(!source&&contentType!=="auto"&&!subject)return json(res,400,{error:"Digite o assunto que deseja transformar em Reel."});

  const token=process.env.ALLSTARS_GITHUB_TOKEN;
  const headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"ALLSTARS-Studio"};
  try{
    // Evitar novos pedidos se já houver produção sob demanda aguardando conclusão.
    const open=await fetch("https://api.github.com/repos/"+REPO+"/issues?state=open&per_page=100",{headers});
    if(!open.ok)throw Error("Não foi possível consultar pedidos.");
    const items=await open.json();
    if(items.some(item=>!item.pull_request&&typeof item.title==="string"&&item.title.startsWith("[ALLSTARS] Criar novo episódio"))){
      return json(res,409,{error:"Já existe um episódio em produção. Conclua esse pedido antes de iniciar outro."});
    }
    const extras="TIPO: "+contentType+"\nASSUNTO: "+subject+"\n";
    const body=(mode==="link"
      ?"MODO: link\n"+extras+"LINK: "+source+"\n\nGerar roteiro baseado nessa fonte, respeitando o tipo escolhido e sem inventar fatos."
      :"MODO: auto\n"+extras+"\n"+(subject?"Criar roteiro sobre o assunto indicado; obter fontes verificáveis.":"Gerar próxima história inédita da biblioteca ALLSTARS."));
    const issue=await fetch("https://api.github.com/repos/"+REPO+"/issues",{method:"POST",headers:{...headers,"Content-Type":"application/json"},body:JSON.stringify({title:mode==="link"?"[ALLSTARS] Criar novo episódio por link":"[ALLSTARS] Criar novo episódio",body})});
    if(!issue.ok){const status=issue.status;return json(res,502,{error:"Não foi possível iniciar o gerador no GitHub ("+status+")."});}
    const data=await issue.json();
    return json(res,202,{accepted:true,request_id:data.number,message:"Produção solicitada. O progresso será atualizado aqui."});
  }catch(e){return json(res,502,{error:"Não foi possível conectar ao gerador. Confira as configurações de integração."});}
}
