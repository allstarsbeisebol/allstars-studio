#!/usr/bin/env python3
"""Smoke de integração ALLSTARS: leitura do Supabase sem alterar dados.

Executar somente a partir de workflow autorizado da branch principal.
Nunca escreve nem imprime o valor da chave de serviço.
"""
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
import visual_sync


def main():
    if not visual_sync.enabled():
        raise SystemExit("ERRO: SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY ausente no GitHub Actions.")
    metadata=visual_sync.api("/storage/v1/bucket/allstars-visual")
    if not isinstance(metadata,dict) or metadata.get("id")!="allstars-visual":
        raise SystemExit("ERRO: bucket ALLSTARS não localizado ou credencial não autorizada.")
    if metadata.get("public") is not False:
        raise SystemExit("ERRO: bucket ALLSTARS deveria permanecer privado.")
    prefs=visual_sync.rest("allstars_style_memory",
        "select=id&active=eq.true&curator_approved=eq.true&limit=1")
    if not isinstance(prefs,list):
        raise SystemExit("ERRO: não foi possível conferir a tabela de memória.")
    print("OK: credencial GitHub Actions válida; Storage privado e banco acessíveis.")
    print("OK: nenhuma imagem enviada, sem escrita e sem geração de conteúdo.")


if __name__=="__main__":
    main()
