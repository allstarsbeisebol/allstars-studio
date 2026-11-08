import {authorized,configured,sameOrigin,allowedUrl,json} from "../lib/security.js";
const REPO="allstarsbeisebol/allstars-studio";
async function githubAccessError(response,action){
  const status=response.status;
  if(status===401)return "A conexão com o GitHub precisa ser renovada. Verifique se ALLSTARS_GITHUB_TOKEN está ativa na Vercel.";
  if(status===404)return "O GitHub não encontrou o repositório para este acesso. Confira se o token permite acessar allstarsbeisebol/allstars-studio.";
  if(status!==403&&status!==429)return null;
  const remaining=response.headers?.get?.("x-ratelimit-remaining");
  const retry=response.headers?.get?.("retry-after");
  let message="";
  try{
    const data=await response.json();
    if(typeof data?.message==="string")message=data.message.slice(0,400).toLowerCase();
  }catch{}
  const limited=status===429||remaining==="0"||retry!==null&&retry!==undefined||
    /secondary rate limit|rate limit exceeded|abuse detection|too many requests/.test(message);
  if(limited)return "O GitHub limitou temporariamente as solicitações. Seu pedido não foi iniciado. Aguarde a liberação antes de tentar novamente. Não é necessário criar um token novo.";
  if(/resource not accessible by personal access token|insufficient permission|must have write access|permission to .*denied|integration does not have/.test(message))
    return "O GitHub permitiu consultar, mas não autorizou "+action+". No token ALLSTARS_GITHUB_TOKEN, confira se o proprietário é allstarsbeisebol, o repositório allstars-studio está selecionado e a permissão Issues está em Read and write. Depois salve na Vercel e publique novamente.";
  return "O GitHub recusou "+action+" (403), mas não informou claramente se foi permissão ou limite temporário. Confira se a permissão Issues está em Read and write e, se já estiver, evite criar outro token imediatamente: consulte o status do GitHub ou tente novamente mais tarde.";
}

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
  const rawUrls=Array.isArray(req.body?.urls)?req.body.urls:[req.body?.url||""];
  if(rawUrls.length>5||rawUrls.some(x=>typeof x!=="string"))return json(res,400,{error:"Informe no máximo 5 links de referência."});
  const urls=rawUrls.map(x=>x.trim()).filter(Boolean);
  const sources=urls.map(allowedUrl);
  if(sources.some(x=>!x)||new Set(sources).size!==sources.length)return json(res,400,{error:"Use links HTTPS públicos diferentes, sem repetição."});
  const referenceText=typeof req.body?.reference_text==="string"?req.body.reference_text.trim():"";
  if(referenceText.length>8000)return json(res,400,{error:"O texto colado deve ter no máximo 8.000 caracteres."});
  if(mode==="link"&&!sources.length&&!referenceText)return json(res,400,{error:"Informe um link ou cole um texto de referência."});
  if(!sources.length&&!referenceText&&contentType!=="auto"&&!subject)return json(res,400,{error:"Digite o assunto que deseja transformar em Reel."});

  const token=process.env.ALLSTARS_GITHUB_TOKEN;
  const headers={"Authorization":"Bearer "+token,"Accept":"application/vnd.github+json","X-GitHub-Api-Version":"2022-11-28","User-Agent":"ALLSTARS-Studio"};
  try{
    // Evitar novos pedidos se já houver produção sob demanda aguardando conclusão.
    const open=await fetch("https://api.github.com/repos/"+REPO+"/issues?state=open&per_page=100",{headers});
    if(!open.ok){
      const explanation=await githubAccessError(open,"consultar os pedidos");
      return json(res,503,{error:explanation||"Não foi possível consultar os pedidos no GitHub ("+open.status+")."});
    }
    const items=await open.json();
    if(items.some(item=>!item.pull_request&&typeof item.title==="string"&&item.title.startsWith("[ALLSTARS] Criar novo episódio"))){
      return json(res,409,{error:"Já existe um episódio em produção. Conclua esse pedido antes de iniciar outro."});
    }
    const extras="TIPO: "+contentType+"\nASSUNTO: "+subject+"\n";
    const withReferences=sources.length>0||referenceText.length>0;
    const sourceLines=sources.map(url=>"LINK: "+url).join("\n");
    const pasted=referenceText?"TEXTO_BASE64: "+Buffer.from(referenceText,"utf8").toString("base64")+"\n":"";
    const body="MODO: "+(withReferences?"link":"auto")+"\n"+extras+(sourceLines?sourceLines+"\n":"")+pasted+"\n"+
      (withReferences?"Criar vídeo com base nas referências fornecidas, sem inventar fatos.":subject?"Pesquisar o assunto e exigir fontes verificáveis.":"Gerar próxima história inédita da biblioteca ALLSTARS.");
    const issue=await fetch("https://api.github.com/repos/"+REPO+"/issues",{method:"POST",headers:{...headers,"Content-Type":"application/json"},body:JSON.stringify({title:mode==="link"?"[ALLSTARS] Criar novo episódio por link":"[ALLSTARS] Criar novo episódio",body})});
    if(!issue.ok){
      const status=issue.status;
      const explanation=await githubAccessError(issue,"criar o pedido de vídeo");
      if(explanation)return json(res,503,{error:explanation});
      if(status===422)return json(res,502,{error:"O GitHub rejeitou os dados deste pedido. Revise o assunto, os links e o texto fornecido."});
      return json(res,502,{error:"Não foi possível iniciar o gerador no GitHub ("+status+")."});
    }
    const data=await issue.json();
    return json(res,202,{accepted:true,request_id:data.number,message:"Produção solicitada. O progresso será atualizado aqui."});
  }catch(e){return json(res,502,{error:"Não foi possível conectar ao gerador. Confira as configurações de integração."});}
}
