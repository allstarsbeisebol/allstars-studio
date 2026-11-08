"""Gera orientação editorial de arte anime por episódio, sem chamadas de API.

Este arquivo é um briefing para um futuro gerador livre ou para um ilustrador.
Não afirma ter criado ilustração nova.
"""
import argparse,json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser()
p.add_argument("--episode",default="output/selected.json")
p.add_argument("--output",default="output/briefing_arte_anime.txt")
args=p.parse_args()
ep=json.loads(Path(args.episode).read_text(encoding="utf-8"))
style=json.loads((ROOT/"brand/anime_direction.json").read_text(encoding="utf-8"))
athlete=str(ep.get("subject") or ep.get("athlete","")).strip()
if not athlete:raise SystemExit("Assunto ausente no roteiro")
headline=str(ep.get("title","ALÉM DO JOGO")).strip()
hook=str(ep.get("hook") or headline).strip()
research_direction=str(ep.get("art_direction") or "A cena deve representar apenas os fatos explícitos no roteiro e nas fontes.")[:600]
sources=ep.get("sources",[])
is_individual=ep.get("content_type","atleta")=="atleta"
scene_direction=("Criar personagem de anime original adulto em ação coerente com a história; nunca inventar traços reais de uma pessoa sem referência."
                 if is_individual else
                 "Criar cena narrativa anime original e específica para este assunto: estádio, estádio histórico ilustrado, bolas, equipamentos, atletas genéricos não identificáveis ou diagramas esportivos estilizados, conforme o contexto. Nunca inserir jogador real aleatório nem repetir o rosto de Jim Abbott.")
briefing=f"""ALLSTARS STUDIO — DIREÇÃO DE ARTE ANIME APROVADA
Série: ALÉM DO JOGO
Assunto/atleta: {athlete}
Headline do roteiro: {headline}
Gancho narrado nos três segundos iniciais: {hook}
Direção específica DESTA PESQUISA: {research_direction}

FORMATO
Capa vertical 1080x1920 (9:16), compatível com recorte do perfil 3:4.
Logo original ALLSTARS, sem redesenhar; paleta azul royal #315FAC,
navy #1A3566, vermelho #CE233E, dourado #F0C040, branco #FFFFFF.
O título, a logo e o sujeito precisam ser equilibrados no recorte.

DIREÇÃO VISUAL
{style["visual_direction"]}
Personagem de anime original adulto, ação de beisebol anatomicamente correta,
expressão determinada, sombras cel-shading refinadas, estádio noturno
com refletores, profundidade, pinceladas esportivas azul/vermelho,
tipografia grande e legível. Não imitar personagens de séries existentes.
Adotar a linguagem de direção, luz, texturas e enquadramento da prévia Jim Abbott aprovada,\nsem copiar sua composição ou imagem em outras histórias.\nEvitar o visual de desenho infantil, boneco geométrico, silhueta e
posições impossíveis. NÃO inventar características físicas específicas.

VERIFICAÇÃO HISTÓRICA
Representar ação coerente com o roteiro e com a matéria de origem.
Para feitos ligados a deficiência, anatomia ou equipamento especial,
exigir informação explícita na fonte antes de representar visualmente.
Nenhum retrato ilustrado é fotografia histórica.

ÁREA DA NARRAÇÃO
Subtítulos somente entre x=162..918, y=930..1150, até duas linhas.
A arte deve reservar contraste sem competir com rosto, logo ou headline.

FONTES INFORMADAS NO ROTEIRO
{chr(10).join(str(x) for x in sources) or "Não informadas"}

DIREITOS E CUSTOS
Arte contextual original para esta produção, com crédito adequado. Composição local não equivale a anime premium.
Não usar geração paga automaticamente nem copiar key art protegida.
"""
out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(briefing,encoding="utf-8")
print("Briefing da arte anime:",out)
