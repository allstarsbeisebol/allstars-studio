"""Checagens editoriais conservadoras, sem fingir confirmação externa de fatos."""
import re, unicodedata

YEAR=re.compile(r"(?<!\d)(?:18|19|20)\d{2}(?!\d)")
def normalized(value):
    text=unicodedata.normalize("NFKD",str(value)).encode("ascii","ignore").decode("ascii")
    return re.sub(r"\s+"," ",text.lower()).strip()

def verify_reference(article,episode):
    """Falha se faltou atleta no texto; sinaliza datas inventadas e apoio ausente."""
    text=str(article.get("text",""))
    title=str(article.get("title",""))
    name=str(episode.get("athlete","")).strip()
    if len(name)<4:raise ValueError("O artigo não permitiu identificar o nome do atleta.")
    source=normalized(title+" "+text)
    surname=normalized(name).split()[-1]
    # Não aceitar nome de pessoa sem relação observável com a matéria.
    if len(surname)<4 or not re.search(r"\b"+re.escape(surname)+r"\b",source):
        raise ValueError("O nome do atleta não foi encontrado na matéria fornecida.")
    generated=" ".join(str(episode.get(k,"")) for k in ("title","narration"))
    generated+=" "+" ".join(str(s) for s in episode.get("screens",[]))
    source_years=set(YEAR.findall(title+" "+text))
    generated_years=set(YEAR.findall(generated))
    unmatched=sorted(generated_years-source_years)
    check={
      "source_article_title":title,
      "athlete_mentioned_in_source":True,
      "years_present_in_source":sorted(source_years),
      "years_in_generated_script":sorted(generated_years),
      "unsupported_years":unmatched,
      "evidence_paragraphs":episode.get("evidence_paragraphs",[]),
      "checked_rules":["atleta citado no texto","anos do roteiro confrontados com o artigo","parágrafos de apoio solicitados à IA"],
      "verified_independently":False,
      "notice":"Checagem de consistência da matéria; não confirma fatos por segunda fonte."
    }
    if unmatched:
        raise ValueError("O rascunho mencionou anos não encontrados na matéria: "+", ".join(unmatched)+". Nenhum episódio foi gerado.")
    check["status"]="CONSISTENTE COM A FONTE — REVISÃO HISTÓRICA PENDENTE"
    if not check["evidence_paragraphs"]:
        check["status"]="REFERÊNCIAS INSUFICIENTES — REVISÃO HISTÓRICA PENDENTE"
    return check
