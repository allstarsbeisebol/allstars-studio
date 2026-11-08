# Referências para criação por link: ArtCraft, REA, Craft Anything e Ghidra

Análise realizada para o ALLSTARS Studio, que oferece dois botões: **Gerar automaticamente** e **Gerar a partir de link**. Objetivo: Reel vertical com narração pausada, capa na Bíblia Visual 2026, logomarca oficial, MP4/PNG/MP3 e legendas, sem custos automáticos de APIs pagas.

## O que faz sentido

- [ArtCraft](https://github.com/storytold/artcraft), licença Apache-2.0: referência criativa para composição 2D, cena por camadas, primeiro plano/fundo, enquadramento e edição. O aplicativo usa provedores/modelos que podem exigir créditos/serviços externos; não é um serviço gratuito de renderização 100% automatizada no GitHub Actions. **Não instalar como dependência do servidor.**
- [REA](https://github.com/morluto/rea), MIT: fornece ferramentas para agentes inspecionarem funcionamento de programas e websites, com resultados rastreáveis. **Não é um extrator especializado em fatos esportivos**, nem deve ser usado para contornar paywalls ou copiar código de terceiros. Aproveitar o conceito de *evidência + limite + procedência* no módulo editorial.
- [Ghidra — NSA](https://github.com/NationalSecurityAgency/ghidra), licença Apache-2.0: ferramenta de engenharia reversa para inspecionar código compilado, desmontar/descompilar executáveis e automatizar análises via scripts. Pode complementar o **REA** na depuração de componentes binários ou programas fechados, quando houver necessidade legítima de análise. **Não lê notícias esportivas, não gera capas e não monta vídeos**; portanto não incluir em GitHub Actions nem como dependência do ALLSTARS Studio. Sua instalação demanda ambiente próprio (incluindo JDK), e versões específicas podem conter vulnerabilidades descritas nos avisos oficiais.
- [Craft Anything](https://github.com/storytold/craft-anything), código aberto, estágio alpha: pipeline *Study → Build → Check → Ready*. Útil como inspiração para validar a qualidade do resultado; a versão atual trabalha com agentes de programação e reconstrução de sites/apps, não com roteiros jornalísticos. **Não instalar no pipeline de Reel.**

## Mudanças já incorporadas em código

- `engine/article_extract.py`: separa artigo da navegação, prioriza `<article>` e `<main>`, utiliza `schema.org/articleBody` como fallback para páginas com conteúdo estruturado.
- `engine/from_link.py`: permite poucos redirecionamentos somente entre destinos HTTPS públicos revalidados, bloqueia conteúdo insuficiente, preserva a referência e apresenta os trechos como material não confiável ao Gemini.
- Identificadores de parágrafos `P01`, `P02` etc. no prompt para facilitar indicar quais trechos amparam o rascunho. Identificadores não representam checagem factual independente.
- `engine/research.py`: guarda no download `pesquisa.json` o endereço submetido, endereço lido, título, método de extração, tamanho do texto e hash SHA-256; sem republicar o artigo integral.
- `tests/test_article_extract.py`: tests sem API paga para diferenciar conteúdo de menus/rodapés, ler `NewsArticle` em JSON-LD e recusar páginas sem conteúdo.

## Limitações reais

- Páginas bloqueadas, protegidas por login, paywall, somente vídeo, JavaScript sem artigo estruturado ou robots/termos restritivos podem não oferecer texto suficiente.
- Conteúdo encontrado no artigo **não implica verdade**, nem autorização de copiar fotos. A conferência de datas, estatísticas, direitos de imagem e legenda continua necessária antes da publicação.
- O Gemini só é chamado depois que o texto útil é extraído; o serviço pode ter cotas gratuitas. Sem chave válida ou sem conteúdo legível, o pedido falha visivelmente.
- A capacidade de gerar imagens realistas dos atletas sem licença de foto, GPU ou provedor de imagem **não é oferecida** por esses repositórios de maneira gratuita e garantida.
- A integração não adiciona nenhuma configuração ou etapa aos dois botões do site.

## Próximas evoluções propostas (não implementadas)

1. Validação visual automática de sobreposição de textos e área reservada para a marca na capa.
2. Reaproveitamento de fotos licenciadas/cadastradas, com crédito verificável, antes de recorrer à arte editorial.
3. Verificação assistida de fatos centrais consultando os domínios prioritários: Baseball-Reference, MLB Players, StatMuse e Hall of Fame, respeitando regras de acesso e sem declarar verificação que não ocorreu.

Nenhum projeto citado foi incorporado como dependência de tempo de execução. O aprendizado foi aplicado diretamente ao fluxo já existente.
