"""Direção de arte vinculada ao ASSUNTO e à NARRATIVA, antes do layout.

Nunca entrega o título como se fosse descrição de cena. Não diz que uma
interpretação desenhada reproduz fotografia ou reunião histórica.
"""
from __future__ import annotations
import re,unicodedata

def clean(text):
    return " ".join(str(text or "").split())[:650]

def normalize(text):
    return unicodedata.normalize("NFKD",str(text)).encode("ascii","ignore").decode("ascii").lower()

def is_league_story(ep):
    subject=normalize(" ".join(str(ep.get(k,"")) for k in ("subject","athlete","title","art_direction")))
    return ("rube foster" in subject or any(x in subject for x in (
        "fundacao da liga","criacao de uma liga","fundou a liga",
        "negro national league","fundacao da negro","fundacao de liga",
        "fundacao das ligas","fundar uma liga","criar uma liga",
        "fundar liga","construir uma liga","organizou a liga")))

def story_scene(ep):
    subject=clean(ep.get("subject") or ep.get("athlete") or "história do beisebol")
    direction=clean(ep.get("art_direction") or "")
    title=clean(ep.get("title") or "")
    if is_league_story(ep):
        if "rube foster" in normalize(subject+" "+title):
            return (
              "Reinterpretação editorial histórica de Andrew 'Rube' Foster "
              "como dirigente visionário, na reunião de proprietários que culminou na "
              "fundação da Negro National League, em 1920. Composição dramática "
              "de uma reunião de organizadores do beisebol negro nos EUA no início do século XX: "
              "figura adulta central, de terno e roupa da época, inclinada sobre mesa "
              "de negociações com uma carta fundadora em papel sem letras legíveis; "
              "outros proprietários presentes, expressão de determinação, vislumbre de "
              "campo de beisebol ao fundo. Atmosfera histórica, contraste entre "
              "limitações enfrentadas e projeto coletivo. Não mostrar cinco cartões numerados, "
              "placares, diagramas genéricos ou objetos de tecnologia moderna. "
              "Cena ILUSTRATIVA e autoral, não reprodução documental da reunião nem "
              "pretensão de semelhança facial com Foster sem referência.")
        return (
          f"Cena narrativa ligada a {subject}: liderança e organização de uma liga, "
          "representada por pessoas de época reunidas ao redor de mesa com documentos "
          "sem textos legíveis, campo de beisebol ao fundo e atmosfera de decisão coletiva. "
          "A cena deve parecer uma ilustração histórica, não um infográfico numerado. "
          "Evite atribuir nomes, locais, datas ou rostos específicos sem fonte."
        )
    if any(x in normalize(subject+" "+title+" "+direction) for x in ("no-hitter","sem rebatida","arremesso","pitcher")):
        return (f"Cena editorial de arremesso ligada a {subject}: "
                "arremessador em movimento plausível, campo e base, bola e tensão do momento; "
                "perspectiva de jogo e época indicada no roteiro. "
                "Não invente uniformes, mãos ou anatomia especial não confirmados.")
    if any(x in normalize(subject+" "+title+" "+direction) for x in ("contrato","justica","direito","free agent","salario")):
        return (f"Cena ligada a {subject}: decisão ou conflito fora do campo, "
                "documentos de negociação sobre mesa, pessoa central em postura decidida "
                "e estádio ao fundo, sem texto legível e sem inventar assinaturas.")
    if any(x in normalize(subject+" "+title+" "+direction) for x in ("home run","rebatida","rebatedor","homerun")):
        return (f"Cena esportiva específica de {subject}: rebatedor e movimento de rebatida "
                "em posição anatomicamente plausível, perspectiva baixa do diamante, "
                "público ao fundo e iluminação coerente com a época.")
    if direction and normalize(direction)!=normalize(title):
        return (
          f"Reinterprete o cenário específico já descrito no roteiro: {direction}. "
          f"O protagonista, acontecimento e ação devem remeter diretamente a {subject}; "
          "evite molduras, números decorativos, cartazes prontos ou ícones genéricos."
        )
    return (
       f"Crie uma cena narrativa original para o assunto exato: {subject}. "
       f"Enredo central descrito pelo título: {title}. "
       "Escolha uma ação concreta amparada pelo roteiro; destaque pessoas, "
       "objetos e ambiente compatíveis com a história, sem painéis numerados, "
       "ícones aleatórios ou marca textual. Se o material não sustentar detalhes "
       "exatos de um rosto ou local, use interpretação visual não documental."
    )
