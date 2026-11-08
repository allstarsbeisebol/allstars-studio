"""Etapa de revisão visual: cria/revisa a arte sem produzir áudio ou vídeo.

Toda revisão reusa o roteiro original e incrementa a variante gráfica.
Não aceita instruções arbitrárias como comandos do shell.
"""
import argparse,base64,json,os,re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"output"
OUTPUT.mkdir(exist_ok=True)

def event_data():
    path=os.getenv("GITHUB_EVENT_PATH","")
    return json.loads(Path(path).read_text(encoding="utf-8")) if path else {}

def message_fields(body):
    lines=str(body or "").splitlines()
    first=lines[0].strip() if lines else ""
    fields={}
    for line in lines[1:]:
        key,sep,value=line.partition(":")
        if sep:fields[key.strip().upper()]=value.strip()
    return first,fields

def revision(body):
    command,fields=message_fields(body)
    if command not in ("ALLSTARS_ART_CHANGE","ALLSTARS_ART_APPROVE"):
        raise ValueError("Comando de arte inválido.")
    number=fields.get("REVISION","")
    if not re.fullmatch(r"[1-9][0-9]{0,4}",number):
        raise ValueError("Versão de arte inválida.")
    return command,int(number),fields

def advance(ep,body):
    command,expected,fields=revision(body)
    if command!="ALLSTARS_ART_CHANGE":raise ValueError("Ação de ajuste inválida.")
    current=int(ep.get("art_revision",0))
    if current!=expected:raise ValueError("Esta versão da arte não está mais disponível para revisão.")
    action=fields.get("ACTION","")
    if action not in ("regenerate","revise"):raise ValueError("Escolha revisar ou gerar uma nova imagem.")
    encoded=fields.get("FEEDBACK_BASE64","")
    try:feedback=base64.b64decode(encoded,validate=True).decode("utf-8").strip() if encoded else ""
    except (ValueError,UnicodeDecodeError) as exc:raise ValueError("Ajuste textual inválido.") from exc
    if len(feedback)>1200 or any(ord(ch)<32 and ch not in "\t\n" for ch in feedback):
        raise ValueError("O ajuste deve ter no máximo 1.200 caracteres.")
    if action=="revise" and len(feedback)<5:
        raise ValueError("Explique o que deseja ajustar na imagem.")
    ep["art_revision"]=current+1
    ep["art_approved"]=False
    ep["art_feedback"]=feedback if action=="revise" else ""
    ep["art_feedback_history"]=(list(ep.get("art_feedback_history") or [])+
        [{"revision":current+1,"action":action,"feedback":feedback[:1200]}])[-15:]
    # Outra geração sem observações volta à direção de arte original.
    ep["art_direction_original"]=ep.get("art_direction_original") or ep.get("art_direction","")
    if action=="revise":
        # Texto editorial acrescentado ao briefing, sem alterar o assunto.
        ep["art_direction"]=(str(ep["art_direction_original"])+"\nAJUSTES DA EDIÇÃO: "+feedback)[:1800]
    else:
        ep["art_direction"]=str(ep["art_direction_original"])[:1800]
    return ep

def approve(ep,body):
    command,expected,_=revision(body)
    if command!="ALLSTARS_ART_APPROVE":raise ValueError("Aprovação inválida.")
    if int(ep.get("art_revision",0))!=expected:
        raise ValueError("A imagem aprovada não corresponde à versão atual.")
    ep["art_approved"]=True
    ep["approved_art_revision"]=expected
    return ep

def prepare(ep,issue_id):
    if not isinstance(issue_id,int) or issue_id<1:raise ValueError("Pedido inválido.")
    ep["art_revision"]=1
    ep["art_feedback"]=""
    ep["art_approved"]=False
    ep["episode_number"]=issue_id
    ep["unique_art_required"]=True
    ep["art_direction_original"]=ep.get("art_direction","")
    return ep

def main():
    p=argparse.ArgumentParser()
    p.add_argument("mode",choices=("prepare","revise","approve"))
    p.add_argument("--episode",default="output/selected.json")
    args=p.parse_args()
    path=Path(args.episode)
    ep=json.loads(path.read_text(encoding="utf-8"))
    event=event_data()
    issue=event.get("issue") or {}
    issue_id=int(issue.get("number") or os.getenv("ALLSTARS_ISSUE_ID","0"))
    if args.mode=="prepare":ep=prepare(ep,issue_id)
    else:ep=(advance if args.mode=="revise" else approve)(ep,(event.get("comment") or {}).get("body",""))
    path.write_text(json.dumps(ep,ensure_ascii=False,indent=2),encoding="utf-8")
    print("ALLSTARS arte:",args.mode,"| pedido",issue_id,"| revisão",ep["art_revision"])

if __name__=="__main__":main()
