# ALLSTARS Studio — Evolução editorial e UX, 08/11/2026

## Objetivos
- Um pedido pelo site, com assunto e múltiplos links colados sem botões adicionais.
- Reel com narração, MP4, capa inédita por geração, legenda e fontes.
- Hook factual nos três segundos iniciais.
- Sem compra implícita de créditos de API; preservar o fluxo e a Bíblia Visual ALLSTARS 2026.

## Arte original contextual e qualidade
- engine/story_art.py compõe uma cena contextual nova por execução e cena a partir do tema, título, gancho, direção editorial e identificador de produção.
- engine/request_select.py exige arte inédita em novas execuções. O poster legado de Jim Abbott segue como referência aprovada e teste, nunca como nova arte de outro episódio.
- engine/anime_briefing.py usa o prompt específico derivado de pesquisa; engine/render.py exporta storyboard.json com identificadores das cenas.
- engine/visual_quality.py marca composição contextual como original mas NÃO anime premium. É ilustração gráfica editorial, não foto histórica ou anime gerado por modelo de difusão.
- O acabamento anime premium automático, sem créditos, ainda depende de motor de imagem gratuito adequado e licença apropriada. Não há geração de imagem por API paga nesta etapa.

## Referências e pesquisa
- public/index.html permite colar vários links num único campo, com identificação, deduplicação e revisão antes do pedido.
- api/generate.js e engine/content_request.py limitam o TAMANHO agregado das URLs a 24 mil caracteres; não impõem limite de cinco links.
- engine/from_link.py lê até 16 páginas por produção e preserva as demais URLs com anotação de que não foram lidas.
- Links de busca e artigos lidos para rascunho não são fatos verificados independentemente; conferir antes de publicar.

## Rastreamento das 17 melhorias aprovadas
1. Arte inédita: implementada composição contextual, acabamento anime premium pendente.
2. Links em colagem única: implementado; limite seguro por tamanho do pedido.
3. Hook dos três segundos: prompts exigem primeiro trecho da narração e primeira cena do Reel apresenta gancho.
4. Navegação modular: atalhos para criação, andamento, downloads, biblioteca e avisos.
5. Visão geral: atalhos e status disponíveis; painel de métricas avançado ainda pendente.
6. Formulário progressivo: revisão guiada mantida; ocultação de campos avançados ainda pendente.
7. Rascunho e cancelar: salvamento automático local, limpar e voltar da confirmação.
8. Prévia: capa e vídeo disponíveis após renderização; prévia de roteiro antes de renderizar ainda pendente.
9. Preservar estado: formulário local e pedido em andamento recuperáveis no navegador.
10. Biblioteca: pesquisa, ordenação e paginação local de até 100 Releases.
11. Cards e lista: visualizações alternáveis.
12. Ajuda contextual: títulos e descrições existentes; refino geral de tooltips pendente.
13. Ações por item: ver arquivos e baixar MP4; menu avançado pendente.
14. Avisos contextuais: notificações e avisos do navegador já implementados.
15. Mobile: navegação compacta, formulários fluidos, lista responsiva.
16. Desempenho: imagens lazy, vídeo sob demanda e paginação local; otimização de backend ainda pendente.
17. QA e documentação: tests/backend.test.js, test_reference_batch.py, test_original_art.py e CI.

## Riscos e validação
- Sempre apresentar vídeo como prévia para revisão editorial. Nunca publicar automaticamente no Instagram.
- Confirmar o teste autenticado de geração no site publicado antes de declarar o erro 403 da Vercel/GitHub corrigido.
- Não confundir imagem gráfica exclusiva com anime premium no painel.
- Produção Piper/FFmpeg/GitHub Actions sujeita às cotas e regras das plataformas.
- Em eventual integração com serviços de imagem, exigir aprovação explícita sobre custo, licença e confidencialidade.
