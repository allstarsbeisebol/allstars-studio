#!/usr/bin/env python3
"""Prompt autoral pronto para usar em outra IA, sem fazer chamadas pagas."""
import argparse,json
from pathlib import Path
from scene_direction import story_scene

def prompt(ep):
    subject=str(ep.get("subject") or ep.get("athlete") or "história do beisebol").strip()[:180]
    title=str(ep.get("title") or subject).strip()[:180]
    hook=str(ep.get("hook") or title).strip()[:220]
    direction=str(ep.get("art_direction_original") or ep.get("art_direction") or title).strip()[:850]
    scene=story_scene(ep)
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
    return f"""PROMPT — ARTE-BASE NARRATIVA ORIGINAL / ALLSTARS · ALÉM DO JOGO

Crie SOMENTE UMA ILUSTRAÇÃO ORIGINAL para esta história, em proporção 9:16
(preferencialmente 1080×1920). Não entregue uma capa pronta, um template ou
um conjunto de cartões numerados.

ASSUNTO EXATO DO EPISÓDIO: {subject}
TÍTULO DO ROTEIRO (NÃO ESCREVER NA IMAGEM): {title}
GANCHO NARRATIVO (NÃO ESCREVER NA IMAGEM): {hook}

CENA PRINCIPAL OBRIGATÓRIA — representa os acontecimentos do episódio:
{scene}

CENA E CONTEXTO ESPECÍFICOS: {direction}

O QUE A IMAGEM PRECISA COMUNICAR
- A personagem ou acontecimento central devem ser reconhecíveis pelo CONTEXTO.
- Mostre uma AÇÃO, pessoas, objetos e ambiente vinculados ao assunto, e não
  cinco quadrados, ícones, placares fictícios ou formas genéricas de beisebol.
- Trate cenas sem fotografia como reinterpretações ILUSTRATIVAS, não provas documentais.
- Preserve coerência de época, equipamento, ambiente e gestos.

ESTILO
Ilustração anime esportiva adulta com acabamento cinematográfico, desenho
de anatomia coerente, iluminação expressiva, profundidade, lineart refinado,
cel-shading e composição dinâmica. Adapte o ambiente ao período histórico:
NÃO imponha um estádio noturno moderno a histórias do início do século XX.
Use azul royal #315FAC, marinho #1A3566, vermelho #CE233E e dourado
#F0C040 como referência de paleta, sem sacrificar a atmosfera histórica.

COMPOSIÇÃO E REAPROVEITAMENTO NO STUDIO
- Faça uma imagem vertical completa, com personagens e cenas, NÃO um wireframe.
- Elementos importantes devem ficar visíveis mesmo com cortes moderados nas bordas.
- Deixe respiro visual natural no alto, embaixo e em partes menos movimentadas
  do enquadramento, mas sem desenhar áreas vazias em forma de caixas.
- NÃO escreva títulos, números decorativos, textos, legendas, logomarcas,
  selos, cartões, diagramas de interface ou marca-d'água.
- O ALLSTARS Studio adicionará DEPOIS: logo oficial em alta definição,
  título tipográfico, áreas de legenda, moldura editorial e recorte 3:4.

REFERÊNCIAS E DIREITOS
- Não copie diretamente imagens, personagens, cenas, uniformes protegidos
  ou material de outros artistas. Use referências visuais apenas como
  inspiração e orientação para criar sua própria composição original.
- Evite anacronismos óbvios. Quando faltar referência exata, ilustre de modo
  plausível e claramente artístico, sem fingir retrato fiel ou cena fotografada.
- Não invente nomes legíveis, marcas, estatísticas, uniformes específicos,
  deficiências, equipamentos especiais ou datas não sustentadas pelo roteiro.
- Evite reproduzir a composição de um pôster ALLSTARS anterior.

{memory_notes}
ENTREGA
Entregue apenas a ILUSTRAÇÃO-BASE em PNG, JPG ou WEBP, sem palavras
dentro da imagem. Não inclua borda, caixa de título ou layout já diagramado.

DEPOIS DE CRIAR
Copie a imagem e cole-a na caixa do ALLSTARS Studio (Ctrl+V),
ou salve e envie o arquivo. Confira a PRÉVIA COMPOSTA pelo Studio,
escolha o enquadramento e só então aprove para gerar o MP4.
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
