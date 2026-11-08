import {authorized,configured,json} from "../lib/security.js";
import {visualConfigured,listImages} from "../lib/visual-storage.js";
export default async function handler(req,res){
 if(req.method!=="GET")return json(res,405,{error:"Método não permitido."});
 if(!configured()||!authorized(req))return json(res,401,{error:"Entre no Studio para consultar a biblioteca visual."});
 if(!visualConfigured())return json(res,200,{configured:false,items:[],
  message:"Biblioteca preparada no Supabase. Configure SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY na Vercel para conectar as imagens."});
 const group=String(req.query?.group||"all");
 if(!["all","created","uploaded","reference"].includes(group))
  return json(res,400,{error:"Filtro de origem inválido."});
 try{
  const items=await listImages({group,limit:18});
  return json(res,200,{configured:true,items,total_shown:items.length,
    message:items.length?"Imagens armazenadas no Supabase, com origem identificada.":"Ainda não há imagens nessa categoria."});
 }catch{return json(res,502,{error:"Não foi possível acessar a biblioteca visual no Supabase."});}
}
