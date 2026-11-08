import {authorized,configured,sameOrigin,json} from "../lib/security.js";
import {visualConfigured,reviewImage} from "../lib/visual-storage.js";
export default async function handler(req,res){
 if(req.method!=="POST")return json(res,405,{error:"Método não permitido."});
 if(!sameOrigin(req))return json(res,403,{error:"Origem não autorizada."});
 if(!configured()||!authorized(req))return json(res,401,{error:"Entre no Studio para avaliar imagens."});
 if(!visualConfigured())return json(res,503,{error:"Biblioteca visual ainda não conectada ao servidor."});
 const id=String(req.body?.asset_id||"");
 const decision=String(req.body?.decision||"");
 const rating=req.body?.rating===null||req.body?.rating===undefined?null:Number(req.body?.rating);
 const feedback=typeof req.body?.feedback==="string"?req.body.feedback:"";
 const learn=req.body?.learn===true;
 if(!/^[0-9a-f]{8}-[0-9a-f-]{27,}$/.test(id)||!["approve","reject","note","disable_reference"].includes(decision))
  return json(res,400,{error:"Imagem ou decisão inválidas."});
 if(feedback.length>600||!Number.isSafeInteger(rating??0)|| (rating!==null&&(rating<1||rating>5)))
  return json(res,400,{error:"Informe uma nota de 1 a 5 e observações de até 600 caracteres."});
 if(learn&&decision!=="approve")return json(res,400,{error:"A memória só pode receber imagens aprovadas."});
 try{
  const data=await reviewImage({assetId:id,decision,rating,feedback,learn});
  return json(res,200,data);
 }catch(e){
  if(/inválida|inválido|Somente|memorizar|encontrada/.test(e.message))
   return json(res,400,{error:e.message});
  return json(res,502,{error:"Não foi possível salvar a avaliação no Supabase."});
 }
}
