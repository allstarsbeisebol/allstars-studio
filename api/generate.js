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
      if(open.status===401||open.status===403)return json(res,503,{error:"A credencial GitHub configurada na Vercel não consegue consultar o novo repositório allstarsbeisebol/allstars-studio ("+open.status+"). Atualize ALLSTARS_GITHUB_TOKEN no projeto ALLSTARS Beisebol e autorize este repositório."});
      if(open.status===404)return json(res,503,{error:"O token da Vercel não tem acesso ao repositório allstarsbeisebol/allstars-studio. Autorize o novo repositório no GitHub."});
      throw Error("Não foi possível consultar pedidos.");
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
      if(status===401)return json(res,503,{error:"O token GitHub configurado na Vercel é inválido ou expirou (401). Atualize ALLSTARS_GITHUB_TOKEN."});
      if(status===403)return json(res,503,{error:"O GitHub recusou criar o episódio (403). Autorize ALLSTARS_GITHUB_TOKEN a escrever Issues no repositório allstarsbeisebol/allstars-studio. No token Fine-grained: Repository access = allstarsbeisebol/allstars-studio; Issues = Read and write."});
      if(status===404)return json(res,503,{error:"O token GitHub não enxerga o novo repositório allstarsbeisebol/allstars-studio (404). Conceda acesso ao repositório no token."});
      if(status===422)return json(res,502,{error:"O GitHub rejeitou o conteúdo do pedido (422). Verifique se Issues está habilitado e tente novamente."});
      if(status===429)return json(res,503,{error:"O GitHub limitou temporariamente as solicitações (429). Tente novamente após a liberação."});
      return json(res,502,{error:"Não foi possível iniciar o gerador no GitHub ("+status+")."});
    }
    const data=await issue.json();
    return json(res,202,{accepted:true,request_id:data.number,message:"Produção solicitada. O progresso será atualizado aqui."});
  }catch(e){return json(res,502,{error:"Não foi possível conectar ao gerador. Confira as configurações de integração."});}
}
