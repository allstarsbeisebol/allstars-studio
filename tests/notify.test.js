import test from "node:test";
import assert from "node:assert/strict";
import {PREF_KEY,browserAvailable,alertsEnabled,enableAlerts,announceIssue} from "../public/notify.js";

function memoryStorage(){
  const map=new Map();
  return {
    getItem(key){return map.get(key)??null;},
    setItem(key,value){map.set(key,String(value));},
    removeItem(key){map.delete(key);}
  };
}
function FakeNotification(title,options){
  FakeNotification.entries.push({title,options,notification:this});
  this.title=title;this.options=options;
  this.close=()=>{this.closed=true;};
}
FakeNotification.entries=[];
FakeNotification.permission="default";
FakeNotification.requestPermission=async()=>"granted";

test("permite notificações somente após permissão explícita",async()=>{
  const store=memoryStorage();
  assert.equal(browserAvailable(FakeNotification),true);
  assert.equal(alertsEnabled(store),false);
  let result=announceIssue({
    issueId:123,kind:"ready",title:"Episódio pronto",body:"Baixe agora",
    storage:store,NotificationImpl:FakeNotification
  });
  assert.equal(result.sent,false);
  assert.equal(FakeNotification.entries.length,0);
  const enabled=await enableAlerts({NotificationImpl:FakeNotification,storage:store});
  assert.equal(enabled.enabled,true);
  assert.equal(store.getItem(PREF_KEY),"yes");
});

test("notificação é emitida uma vez e abre downloads ao clicar",async()=>{
  const store=memoryStorage();
  FakeNotification.entries=[];
  FakeNotification.permission="granted";
  store.setItem(PREF_KEY,"yes");
  let clicked=0;
  const args={issueId:300,kind:"ready",title:"Vídeo pronto",body:"Baixe o Reel",
    storage:store,NotificationImpl:FakeNotification,onClick:()=>clicked++};
  const first=announceIssue(args);
  assert.equal(first.sent,true);
  assert.equal(FakeNotification.entries.length,1);
  const second=announceIssue(args);
  assert.equal(second.reason,"already_notified");
  assert.equal(FakeNotification.entries.length,1);
  FakeNotification.entries[0].notification.onclick();
  assert.equal(clicked,1);
  assert.equal(FakeNotification.entries[0].notification.closed,true);
});

test("avisos de erro não são confundidos com avisos de sucesso",()=>{
  const store=memoryStorage();
  FakeNotification.entries=[];
  FakeNotification.permission="granted";
  store.setItem(PREF_KEY,"yes");
  assert.equal(announceIssue({
    issueId:301,kind:"error",title:"Erro",body:"A produção falhou",
    storage:store,NotificationImpl:FakeNotification
  }).sent,true);
  assert.equal(announceIssue({
    issueId:301,kind:"ready",title:"Pronto",body:"Baixar",
    storage:store,NotificationImpl:FakeNotification
  }).sent,true);
  assert.equal(FakeNotification.entries.length,2);
});

test("navegador sem API não impede popup interno",async()=>{
  const store=memoryStorage();
  assert.equal(browserAvailable(undefined),false);
  const result=await enableAlerts({NotificationImpl:null,storage:store});
  assert.equal(result.enabled,false);
  assert.equal(announceIssue({
    issueId:2,kind:"ready",title:"Pronto",body:"Baixar",
    storage:store,NotificationImpl:null
  }).sent,false);
});

test("permissão bloqueada não cria notificação",async()=>{
  const store=memoryStorage();
  FakeNotification.entries=[];
  FakeNotification.permission="denied";
  FakeNotification.requestPermission=async()=>"denied";
  const result=await enableAlerts({NotificationImpl:FakeNotification,storage:store});
  assert.equal(result.reason,"denied");
  assert.equal(announceIssue({
    issueId:5,kind:"ready",title:"Pronto",body:"Baixar",
    storage:store,NotificationImpl:FakeNotification
  }).sent,false);
  assert.equal(FakeNotification.entries.length,0);
});
