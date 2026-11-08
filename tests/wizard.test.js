import test from "node:test";
import assert from "node:assert/strict";
import {wizardSteps,wizardStep,panelForScreen,normalizeWizardScreen,resumeDraftScreen,routeWizardScreen,stageFromIssueState} from "../public/wizard.js";
test("cinco etapas com referências opcionais e arte aprovada",()=>{
 assert.deepEqual(wizardSteps,["Conteúdo","Referências","Conferência","Imagem","Resultado"]);
 assert.equal(wizardStep("content"),0);
 assert.equal(wizardStep("references"),1);
 assert.equal(wizardStep("confirm"),2);
 assert.equal(wizardStep("art"),3);
 assert.equal(wizardStep("progress"),3);
 assert.equal(wizardStep("result"),4);
 assert.equal(wizardStep("library"),-1);
});
test("conteúdo e referências são painéis alternativos, nunca dois formulários",()=>{
 assert.equal(panelForScreen("content"),"editor");
 assert.equal(panelForScreen("references"),"editor");
 assert.equal(panelForScreen("library"),"library");
 assert.equal(resumeDraftScreen("references"),"references");
 assert.equal(resumeDraftScreen("confirm"),"content");
 assert.equal(normalizeWizardScreen("unknown"),"home");
});
test("pedido aberto impede retorno para criar outro issue",()=>{
 for(const state of ["content","references","confirm"])
  assert.equal(routeWizardScreen(state,18),"progress");
 assert.equal(routeWizardScreen("art",18),"art");
 assert.equal(routeWizardScreen("home",18),"home");
 assert.equal(routeWizardScreen("library",18),"library");
 assert.equal(routeWizardScreen("progress",0),"home");
 assert.equal(routeWizardScreen("content",0),"content");
});
test("transições de pedido preservam aprovação explícita",()=>{
 assert.equal(stageFromIssueState("art_generating"),"progress");
 assert.equal(stageFromIssueState("art_review"),"art");
 assert.equal(stageFromIssueState("rendering"),"progress");
 assert.equal(stageFromIssueState("ready"),"result");
 assert.equal(stageFromIssueState("error"),"progress");
});
