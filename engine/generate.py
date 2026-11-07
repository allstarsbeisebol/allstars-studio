#!/usr/bin/env python3
"""Cria um rascunho NOVO sem custos de API, a partir de uma fila editorial.
Os textos são propostas sujeitas a checagem; fontes apontam para pesquisa, não para fatos automaticamente verificados.
"""
import json, re, datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
history_file=root/"data/history.json"
history=json.loads(history_file.read_text(encoding="utf-8"))
# Cada texto é diferente. Ampliar esta fila ou implementar pesquisa externa na próxima etapa.
ideas=[
{"athlete":"Roberto Clemente","title":"3000 REBATIDAS. E UMA MISSÃO MAIOR QUE O BEISEBOL.",
"narration":"Roberto Clemente deixou uma marca que vai muito além de suas três mil rebatidas. Ídolo do Pittsburgh Pirates, ele enfrentou preconceito e barreiras culturais como estrela porto-riquenha nas Grandes Ligas. Sua dedicação também apareceu longe do campo. Após um terremoto na Nicarágua, Clemente participou de uma missão humanitária de ajuda às vítimas. A viagem terminou tragicamente, quando o avião caiu no fim de 1972. A história dele é lembrada por excelência esportiva, solidariedade e compromisso com outras pessoas. No beisebol, números ajudam a contar uma carreira. Mas existem legados que nenhuma estatística consegue medir. O que torna Roberto Clemente tão importante para gerações de fãs?",
"sources":["https://baseballhall.org/hall-of-famers/clemente-roberto"]},
{"athlete":"Roy Campanella","title":"QUANDO O CAMPO DEIXOU DE SER UMA OPÇÃO.",
"narration":"Roy Campanella já era um dos grandes catchers de sua época quando um acidente de carro interrompeu sua carreira. Campeão com o Brooklyn Dodgers, o jogador ficou paralisado após a colisão em 1958. Sua história, porém, não se limita ao acidente. Campanella continuou ligado ao esporte, e sua trajetória ajudou a mudar a forma como torcedores viam os atletas e suas vidas depois do campo. O que significa reconstruir a própria identidade quando aquilo que você faz melhor já não é possível? Campanella enfrentou essa pergunta em uma época que oferecia muito menos recursos de reabilitação. Sua influência permaneceu mesmo depois do último jogo.",
"sources":["https://baseballhall.org/hall-of-famers/campanella-roy"]},
{"athlete":"Larry Doby","title":"O SEGUNDO NOME TAMBÉM ENFRENTOU A PRIMEIRA BARREIRA.",
"narration":"Quando se fala em integração racial no beisebol, um nome costuma abrir a conversa: Jackie Robinson. Mas Larry Doby também enfrentou uma barreira histórica. Ele se tornou o primeiro jogador negro da Liga Americana na era moderna, pelo Cleveland Indians, em 1947. A pressão não terminou com sua estreia. Havia hostilidade, isolamento e a obrigação injusta de provar o próprio valor todos os dias. Doby transformou a oportunidade em uma carreira de destaque e conquistou uma World Series. Sua história nos lembra que mudanças históricas não acontecem em um único estádio, nem dependem de um único protagonista. Quanto a história do beisebol perde quando lembramos apenas dos primeiros mais famosos?",
"sources":["https://baseballhall.org/hall-of-famers/doby-larry"]},
{"athlete":"Minnie Miñoso","title":"UM PIONEIRO QUE NÃO CABIA EM UMA SÓ GERAÇÃO.",
"narration":"Minnie Miñoso conquistou seu espaço em uma liga que ainda enfrentava as consequências da segregação racial. Nascido em Cuba, o jogador precisou construir sua carreira atravessando fronteiras, culturas e barreiras sociais. No Chicago White Sox, foi lembrado pelo estilo agressivo, pela habilidade e pela energia com que jogava. Sua trajetória também se tornou referência para gerações de atletas latino-americanos que chegaram depois. A superação aqui não está em um único momento dramático. Ela aparece na persistência de continuar competindo, sendo respeitado e abrindo portas ao longo de muitos anos. Como medir o impacto de um jogador que ajudou tantos outros a acreditar que poderiam pertencer à MLB?",
"sources":["https://baseballhall.org/hall-of-famers/minoso-minnie"]},
{"athlete":"Satchel Paige","title":"A MLB CHEGOU TARDE PARA CONHECER SUA LENDA.",
"narration":"Satchel Paige já era uma lenda do montinho antes de receber uma chance nas Grandes Ligas. Durante décadas, a segregação impediu que grandes talentos das Negro Leagues competissem em igualdade de condições. Paige se destacou com arremessos, presença e uma confiança que se tornou parte de sua história. Quando finalmente chegou à MLB, já tinha uma idade incomum para um estreante. Mesmo assim, mostrou que sua habilidade não poderia ser reduzida à data em que lhe permitiram entrar. Sua carreira é uma lembrança de quanto talento o esporte desperdiçou ao manter portas fechadas. Imagine como os recordes do beisebol seriam diferentes se ele tivesse tido a mesma oportunidade desde o início.",
"sources":["https://baseballhall.org/hall-of-famers/paige-satchel"]},
{"athlete":"Rube Foster","title":"ELE NÃO ESPEROU PERMISSÃO PARA CONSTRUIR UMA LIGA.",
"narration":"Antes de muitas das maiores mudanças do beisebol profissional, Rube Foster já enxergava o esporte como algo maior que o desempenho no campo. Arremessador, técnico e organizador, ele ajudou a construir uma estrutura para jogadores negros em uma época de segregação. Em 1920, sua liderança foi fundamental na criação da Negro National League. Foster precisou enfrentar um sistema que negava oportunidades e encontrou uma resposta na organização coletiva. Seu legado não é apenas o de um atleta talentoso. É o de alguém que transformou resistência em instituições e criou novos caminhos para outros jogadores. Quantos nomes da história do beisebol ainda merecem reconhecimento pelo que construíram fora das quatro linhas?",
"sources":["https://baseballhall.org/hall-of-famers/foster-rube"]}
]
used={s.casefold().strip() for s in history.get("covered",[])+history.get("drafted",[])}
choice=next((a for a in ideas if a["athlete"].casefold() not in used),None)
if choice is None:
    raise SystemExit("A fila de histórias inéditas terminou. Amplie a lista editorial antes de gerar outro episódio; não repetimos roteiros.")
athlete=choice["athlete"]
slug=re.sub("[^a-z0-9]+","-",athlete.lower()).strip("-")
draft={**choice,"id":datetime.date.today().isoformat()+"-"+slug,
       "screens":["A HISTÓRIA POR TRÁS DO NOME","QUANDO O JOGO MUDOU","ALÉM DAS ESTATÍSTICAS","O LEGADO CONTINUA"],
       "caption":choice["title"]+" ⚾ Qual parte dessa trajetória merece ser mais lembrada? #ALLSTARSBeisebol #AlemDoJogo #MLB #Beisebol",
       "approved":False,"media_approved":False,
       "editorial_status":"RASCUNHO — verificar integralmente fatos e fontes antes de publicar"}
folder=root/"data/drafts";folder.mkdir(parents=True,exist_ok=True)
path=folder/(draft["id"]+".json")
path.write_text(json.dumps(draft,ensure_ascii=False,indent=2),encoding="utf-8")
history.setdefault("drafted",[]).append(athlete)
history_file.write_text(json.dumps(history,ensure_ascii=False,indent=2),encoding="utf-8")
print("Rascunho criado:",path)
