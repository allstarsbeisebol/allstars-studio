#!/usr/bin/env python3
"""Prompt autoral pronto para usar em outra IA, sem fazer chamadas pagas."""
import argparse,json
from pathlib import Path

def prompt(ep):
    subject=str(ep.get("subject") or ep.get("athlete") or "história do beisebol").strip()[:180]
    title=str(ep.get("title") or subject).strip()[:180]
    hook=str(ep.get("hook") or title).strip()[:220]
    direction=str(ep.get("art_direction_original") or ep.get("art_direction") or title).strip()[:850]
    memory_notes=""
    memory_file=Path("output/style_memory.json")
    if memory_file.is_file():
        try:
            memory_items=json.loads(memory_file.read_text(encoding="utf-8"))
            notes=[]
            for item in memory_items[:8]:
                preference="PRIORIZE" if item.get("preference")=="prefer" else "EVITE"
                summary=" ".join(str(item.get("summary") or "").split())[:220]
                if summary:notes.append("- "+preference+": "+summary)
            if notes:
                memory_notes="\nPREFERÊNCIAS EDITORIAIS APROVADAS (orientações, não imagens para copiar):\n"+"\n".join(notes)+"\n"
        except (OSError,ValueError,TypeError):
            pass
    return f"""PROMPT — ILUSTRAÇÃO ORIGINAL ALLSTARS / ALÉM DO JOGO

Crie uma imagem NOVA, EXCLUSIVA e vertical, proporção 9:16 (idealmente 1080 × 1920 pixels), de alto nível artístico, para um Reel editorial de beisebol. NÃO reaproveite uma imagem genérica de beisebol ou personagens de outra história.

TEMA DO EPISÓDIO: {subject}
TÍTULO DA HISTÓRIA: {title}
GANCHO NOS PRIMEIROS 3 SEGUNDOS: {hook}
CENA E CONTEXTO ESPECÍFICOS: {direction}

DIREÇÃO ARTÍSTICA
Anime esportivo adulto cinematográfico, composição expressiva e plausível para a época e os fatos, poses anatomicamente corretas, cel-shading refinado, linhas detalhadas, iluminação de estádio, perspectiva forte, profundidade e ambiente próprios desta narrativa. Paleta ALLSTARS: azul royal #315FAC, azul marinho #1A3566, vermelho #CE233E, dourado #F0C040, branco.

{memory_notes}
REGRAS
- Crie uma cena única, ligada diretamente ao tema e ao gancho. Nada de poster genérico.
- Não copie imagens, personagens, cenas, uniformes protegidos ou material de outros artistas.
- Não invente fatos visuais, características específicas de pessoas reais ou equipamentos não confirmados.
- NÃO inclua letras, textos, títulos, marcas d'água ou logotipos; a identidade ALLSTARS será aplicada no Studio.
- Preserve área livre para legendas na faixa central e para identidade visual na parte inferior.
- Priorize o assunto principal, a coerência histórica e o impacto visual original.
- Entregue somente a imagem em PNG, JPG ou WEBP, sem explicações dentro da imagem.

DEPOIS DA GERAÇÃO
Copie a imagem criada, volte ao ALLSTARS Studio e cole-a (Ctrl+V) na área de aprovação; também é possível salvar e enviar o arquivo. Confira o corte 9:16 e 3:4 antes de aprovar e gerar o MP4.
"""

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--episode",default="output/selected.json")
    ap.add_argument("--output",default="output/prompt_imagem_ia.txt")
    a=ap.parse_args()
    ep=json.loads(Path(a.episode).read_text(encoding="utf-8"))
    out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(prompt(ep),encoding="utf-8")
    print("Prompt para IA externa:",out)

if __name__=="__main__":main()
