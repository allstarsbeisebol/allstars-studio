/** Avisos do ALLSTARS Studio. Nenhum serviço de push nem API paga é necessário. */
export const PREF_KEY="allstars-browser-alerts-v1";
const SEEN_PREFIX="allstars-alert-seen-";

export function browserAvailable(NotificationImpl=globalThis.Notification){
  return typeof NotificationImpl==="function" && typeof NotificationImpl.requestPermission==="function";
}

export function alertsEnabled(storage=globalThis.localStorage){
  try{return storage?.getItem(PREF_KEY)==="yes";}catch{return false;}
}

export async function enableAlerts({NotificationImpl=globalThis.Notification,storage=globalThis.localStorage}={}){
  if(!browserAvailable(NotificationImpl))return {enabled:false,reason:"unsupported"};
  try{
    const permission=NotificationImpl.permission==="granted"?"granted":await NotificationImpl.requestPermission();
    const enabled=permission==="granted";
    try{storage?.setItem(PREF_KEY,enabled?"yes":"no");}catch{}
    return {enabled,reason:enabled?"enabled":permission==="denied"?"denied":"dismissed"};
  }catch{return {enabled:false,reason:"unsupported"};}
}

export function announceIssue({issueId,kind,title,body,onClick,NotificationImpl=globalThis.Notification,storage=globalThis.localStorage}){
  const key=SEEN_PREFIX+String(issueId)+"-"+String(kind);
  try{
    if(storage?.getItem(key)==="yes")return {sent:false,reason:"already_notified"};
    // A marcação também evita vários avisos após atualizar/reabrir a aba.
    storage?.setItem(key,"yes");
  }catch{}
  if(!alertsEnabled(storage)||!browserAvailable(NotificationImpl)||NotificationImpl.permission!=="granted"){
    return {sent:false,reason:"not_enabled"};
  }
  try{
    const n=new NotificationImpl(title,{
      body,
      tag:"allstars-"+issueId+"-"+kind,
      requireInteraction:kind==="ready",
      silent:false
    });
    if(typeof onClick==="function"){
      n.onclick=()=>{onClick();if(typeof n.close==="function")n.close();};
    }
    return {sent:true,reason:"sent"};
  }catch{
    // Toast no site continua sendo entregue mesmo se o navegador bloquear notificações.
    return {sent:false,reason:"blocked"};
  }
}
