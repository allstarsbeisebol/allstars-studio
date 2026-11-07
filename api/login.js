import {authorized,configured,safeEqual,newCookie,sameOrigin,json} from "../lib/security.js";
export default async function handler(req,res){
  if(req.method==="GET"){
    return json(res,200,{authenticated:authorized(req),configured:configured()});
  }
  if(req.method!=="POST")return json(res,405,{error:"Método não permitido."});
  if(!sameOrigin(req))return json(res,403,{error:"Origem não autorizada."});
  if(!configured())return json(res,503,{error:"A conexão inicial do ALLSTARS ainda precisa ser configurada."});
  const password=typeof req.body?.password==="string"?req.body.password:"";
  if(password.length>300||!safeEqual(password,process.env.ALLSTARS_ADMIN_PASSWORD)){
    return json(res,401,{error:"Senha incorreta."});
  }
  res.setHeader("Set-Cookie",newCookie());
  return json(res,200,{authenticated:true});
}
