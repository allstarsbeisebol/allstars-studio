# ⚾ ALLSTARS Studio — ALÉM DO JOGO

Estúdio online para solicitar e baixar Reels de beisebol, preservando a identidade ALLSTARS 2026.

**Site:** https://allstars-studio-brown.vercel.app/
**Repositório:** https://github.com/allstarsbeisebol/allstars-studio

## Uso pelo navegador
1. Entre no site com a senha do estúdio.
2. Escolha Automático, Atleta, Tema, Notícia, Lista ou Explicativo e informe um assunto se desejar.
3. Cole todos os links de referência no mesmo campo (um por linha, separados por espaço ou junto com texto). O Studio extrai e remove duplicados.
4. Se for necessário, expanda o campo adicional para colar o texto de uma postagem bloqueada por login.
5. Clique em **Conferir meu pedido** e **Preparar prévia da imagem**. Isso cria primeiro o roteiro e a capa, **sem MP4**.
6. Na seção **Aprovar imagem**, amplie a capa e escolha **Solicitar ajustes** (por texto), **Gerar outra versão** ou **Aprovar imagem e produzir vídeo**.
7. Somente a aprovação inicia narração e montagem do Reel. Quando terminar, o Studio oferece MP4, MP3, capa 9:16, capa 3:4, legenda, fontes, roteiro e storyboard.
8. Nos arquivos produzidos, **Ver imagem** abre a capa ampliada, e **Visualizar / Copiar** mostra o roteiro, legenda, fontes e JSON em uma prévia com botão **Copiar texto**. O download original permanece disponível.

**Recuperação:** formulário salvo automaticamente no navegador; a biblioteca permite procurar vídeos anteriores, ordenar e escolher cards/lista. Se o navegador for fechado, um pedido já iniciado poderá ser recuperado pelo identificador armazenado.

## Identidade e produção das imagens
- Cada novo episódio exige arte inédita. A composição gráfica contextual usa assunto, título, gancho, direção de arte, data/identificador da execução e quadros do roteiro; não reaproveita imagens aprovadas de outros episódios.
- A geração de capa e de cenas foi implementada em engine/story_art.py, engine/poster.py e engine/render.py, com metadados em storyboard.json e qualidade_visual.json.
- Novos pedidos via site passam por .github/workflows/art-preview.yml; a capa fica no release temporário preview-issue-N, com revisão numerada. Após aprovação via api/art.js, .github/workflows/produce.yml recupera o MESMO arquivo de capa e o roteiro aprovado para finalizar o vídeo.
- O mecanismo de revisão local é procedural: consegue variar composição, cores (vermelho, azul, dourado) e alguns motivos da ilustração (arremesso, rebatida, lista etc.), mas não gera personagens/cenas anime complexos apenas por texto livre. Solicitações mais sofisticadas ficam documentadas para evolução posterior.
- O sistema não afirma que essa composição gráfica é ilustração anime premium. A referência aprovada de Jim Abbott continua disponível somente como exemplo, não como imagem de novas histórias.
- Para gerar imagens anime premium com IA de forma totalmente automática será necessário um motor de imagem adequado, com direitos e custos verificados. Não se ativa API paga de imagem sem autorização específica.

## Narração e roteiro
- Gemini ajuda a pesquisar e preparar histórias a partir de assunto ou fontes. Os textos seguem revisão editorial obrigatória; fatos extraídos de uma fonte não são automaticamente verificados por uma segunda fonte.
- Todo roteiro de pesquisa com Gemini deve ter hook factual de 8 a 14 palavras no começo da narração; o primeiro quadro do Reel dura aproximadamente três segundos.
- Piper TTS gera narração em português brasileiro e FFmpeg monta o vídeo 9:16; o GitHub Actions executa processamento.
- O modo Automático sem assunto pode utilizar episódios inéditos da biblioteca existente, com hook recuperado do próprio texto sem fabricar fatos.

## Links e orçamento de pesquisa
- A interface não exige clicar em Adicionar link. O tamanho total do conjunto de URLs deve permanecer abaixo de 24.000 caracteres, por segurança.
- O processo analisa ativamente até 16 páginas por execução; outros URLs são preservados no registro como referências não lidas.
- URLs de páginas privadas ou que bloqueiem automação geram uma tentativa adicional de pesquisa pelo mesmo assunto, caso o título/assunto ou a URL seja interpretável. Links originais não lidos são registrados separadamente; não se inventam fatos nem se afirma ter lido uma postagem bloqueada.
- O texto enviado como referência serve para criar uma narrativa nova e autoral da ALLSTARS, nunca para copiar integralmente a publicação de terceiros.
- Nunca confundir link sugerido para pesquisa com fonte que confirma independentemente uma estatística.

## Arquitetura
- Vercel: interface pública estática e APIs de login, geração, status, aprovação da arte, prévia de textos e biblioteca.
- GitHub Actions: etapa de imagem e revisão via Issues; após comentário de aprovação pela API autenticada, etapa de vídeo com Gemini (quando configurado), Piper, Pillow, legendas e FFmpeg.
- GitHub Releases: prévias de capa em releases temporários identificados pelo pedido, e downloads definitivos dos vídeos produzidos.
- GitHub Pages: legado opcional; o endereço principal atual é o da Vercel.
- Segurança: senha e ALLSTARS_GITHUB_TOKEN somente em variáveis de ambiente protegidas. Não colocar chaves no código, issues, anexos ou navegador.

## Custos e publicação
- A composição gráfica e a narração usam ferramentas locais ao GitHub Actions; não dependem de créditos de API de imagem ou áudio. O GitHub, Google e Vercel têm limites e condições de uso.
- A geração de imagem da Gemini API não deve ser presumida gratuita. Consulte https://ai.google.dev/gemini-api/docs/pricing antes de planejar uma integração.
- Os vídeos são PRÉVIAS EDITORIAIS. Confira fatos, voz, direitos das imagens e resultado visual antes de postar. O sistema não publica automaticamente no Instagram.

## Manutenção e testes
- Run: npm run test:syntax; node --test tests/backend.test.js tests/art-editorial.test.js; python -m unittest discover -s tests -p 'test_art_gate.py' -v; python -m unittest discover -s tests -p 'test_source_adaptation.py' -v.
- GitHub Actions: PR executa os testes estáticos e a renderização de teste sem consumir geração de imagens por API paga; revisão real de um pedido no navegador ainda depende de teste autenticado.
- GitHub Actions check.yml valida backend, front, fontes, originalidade, imagens, legendas e renderização FFmpeg.
- Relatório de melhorias e limitações: docs/EVOLUCAO-UX-ARTE-2026-11-08.md.
- Se houver erro HTTP 403 ao criar pedido, verificar as permissões de Issues do token na Vercel; status Ready do deploy não é prova de autenticação de produção.
