# ⚾ ALLSTARS STUDIO — ALÉM DO JOGO

Aplicativo [ALLSTARS Studio](https://liuhelpme.github.io/allstars-studio/) para criar Reels verticais com narração, capa e legenda, sob demanda, sem instalar programas.

## Como usar

**Sem link**: abra o site, clique **Criar episódio → Criar sem link** e confirme **Submit new issue** no GitHub autenticado como `liuhelpme`. O sistema escolhe uma história inédita da biblioteca atual.

**Com link**: cole um endereço HTTPS de artigo público, clique **Criar episódio com este link** e confirme **Submit new issue** no GitHub. O workflow lê o artigo e utiliza Gemini para preparar um rascunho **baseado naquela fonte**. Se não houver texto legível, a chave Gemini não estiver configurada ou o atleta já estiver no histórico, o fluxo para com erro; nunca substitui automaticamente o link por outra história.

Ao concluir, volte ao site e clique **Ver último episódio** / **Atualizar**. Baixe MP4, MP3, capa PNG, legenda e arquivo de fontes. O site utiliza links do GitHub Releases; os vídeos são prévias para revisão antes da publicação no Instagram.

**Não existe agendamento semanal ativo**. A produção acontece somente mediante solicitação manual. Para proteger a conta, o GitHub Pages (site estático) ainda requer uma confirmação de pedido no GitHub. Um acionamento estritamente com um clique, sem sair do site, depende de um backend autenticado.

## Configuração única para gerar a partir de links

O modo por link exige uma chave do Google AI Studio. No repositório, abra [Settings → Secrets and variables → Actions](https://github.com/liuhelpme/allstars-studio/settings/secrets/actions), crie um **Repository secret** chamado exatamente `GEMINI_API_KEY` e cole sua chave. **Nunca** inclua a chave no site, no código ou em issues. Consulte as cotas e os modelos gratuitos disponíveis no Google; o uso gratuito não é ilimitado.

Alguns sites bloqueiam leitura automatizada, exigem login ou não disponibilizam texto. Nesses casos, o sistema reporta a falha em vez de fabricar conteúdo. A geração de texto é assistida por IA, **não é checagem histórica independente**.

## Fontes prioritárias

Registradas em [data/research_sources.json](data/research_sources.json):

- [Baseball-Reference](https://www.baseball-reference.com/)
- [MLB Players](https://www.mlb.com/players)
- [StatMuse MLB](https://www.statmuse.com/mlb/players)
- [National Baseball Hall of Fame](https://baseballhall.org/)

As fontes complementares são entregues como sugestões de pesquisa, não como provas de que alegações foram verificadas. Respeitar licenças e restrições de acesso dos sites.

## Identidade da marca

A [Bíblia Visual ALLSTARS 2026](ALLSTARS%20-%20B%C3%ADblia%20Visual%202026.md) e as 14 pranchas JPG são referências. O [arquivo de identidade](brand/identity.json) centraliza as cores e regras. Para inserir a marca original na capa, disponibilizar `brand/logo.png` com transparência e proporções preservadas. O gerador não cria logotipo alternativo. Fotografias de atletas exigem licença e metadados de autorização.

## Tecnologia

GitHub Pages (painel), GitHub Actions (produção), Piper TTS (narração local), Pillow (capa), FFmpeg (Reel e MP3), Gemini opcional (roteiro a partir de link). A execução em GitHub Actions está sujeita aos limites e políticas do GitHub.

Arquivos essenciais: `index.html`, `.github/workflows/produce.yml`, `engine/request_select.py`, `engine/from_link.py`, `engine/produce_select.py`, `engine/cover.py`, `engine/speech.py`, `engine/render.py`, `engine/publish_manifest.py`, `latest.json`.

**Status:** o fluxo anterior de produção sem link foi validado. O fluxo por link ainda requer teste de execução real com `GEMINI_API_KEY`. Todo vídeo continua sujeito a revisão de fatos, direitos e qualidade.
