/**
 * Navegação do ALLSTARS Studio em HTML/CSS/JS puro.
 * Somente a interface muda: o backend mantém o gate de aprovação da arte.
 */
export const wizardSteps=["Conteúdo","Referências","Conferência","Imagem","Resultado"];
export const wizardScreens=["home","content","references","confirm","progress","art","result","library","alerts"];
export function wizardStep(screen){
 switch(screen){
  case "content":return 0;
  case "references":return 1;
  case "confirm":return 2;
  case "progress":
  case "art":return 3;
  case "result":return 4;
  default:return -1;
 }
}
export function panelForScreen(screen){
 return ["content","references"].includes(screen)?"editor":screen;
}
export function normalizeWizardScreen(screen){
 return wizardScreens.includes(screen)?screen:"home";
}
export function resumeDraftScreen(screen){
 return screen==="references"?"references":"content";
}
export function routeWizardScreen(requested,pending){
 const screen=normalizeWizardScreen(requested);
 // Depois de abrir um Issue não existe mais "editar o formulário original".
 // Voltar não pode abrir um pedido duplicado ou descartar o andamento.
 if(pending&&["content","references","confirm"].includes(screen))return "progress";
 if(!pending&&["progress","art"].includes(screen))return "home";
 return screen;
}
export function stageFromIssueState(state){
 if(state==="art_review")return "art";
 if(state==="ready")return "result";
 if(state==="rendering"||state==="art_generating")return "progress";
 if(state==="error")return "progress";
 return "progress";
}
