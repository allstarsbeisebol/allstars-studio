# ALLSTARS Studio — sistema visual e movimento (Etapa 1)

## Objetivo
Elevar a qualidade visual sem migrar HTML/CSS/JavaScript, sem dependências de runtime, sem custos de API e sem modificar o fluxo de produção existente.

## Base real
- Projeto contém `index.html` e `index-vercel.html`; o segundo já utiliza Barlow, Barlow Condensed e cores da Bíblia Visual 2026.
- A paleta oficial usada na interface é azul #1A3566 / #315FAC, vermelho #CE233E, dourado #F0C040 e branco.
- Preservar as cinco etapas do assistente aprovado e a continuidade dos pedidos.
- A nova folha `assets/studio-motion.css` é **opt-in**: ainda não é importada em produção; esta etapa não altera o comportamento do site.

## Regras de design
1. Clareza antes de decoração: uma ação primária visível por etapa; secundárias discretas.
2. Hierarquia: títulos Barlow Condensed, corpo Barlow, rótulos curtos e instruções de uma frase.
3. Espaçamento em múltiplos de 4px, alvos de toque com pelo menos 44×44px e bordas consistentes.
4. Feedback por texto + estado, não apenas cor ou ícone; manter `aria-live` nas mensagens assíncronas.
5. Estados: aguardando, gerando, concluído, erro e retomada com mensagens específicas.
6. Movimento de 140–220ms somente para orientar transições; sem loops decorativos.
7. Respeitar `prefers-reduced-motion`, navegação por teclado e `:focus-visible`.
8. Não instalar React Bits no Studio HTML. Reproduzir apenas ideias compatíveis em CSS/JS próprios, após revisão de licença.
9. Taste Skill e Transitions.dev são referências de revisão, não dependências de execução.
10. Não substituir a marca, a pesquisa histórica ou a arte contextual por imagens genéricas.

## Próximas etapas de implementação
- Etapa 2: integrar tokens progressivamente no arquivo efetivamente servido pela Vercel; animar somente avanço/volta, expandir/recolher e mensagens. Preservar `hidden`, foco e histórico.
- Etapa 3: avaliar efeitos editoriais discretos no site público `allstarsbeisebol/site` em PR separado.
- Etapa 4: QA com Playwright desktop/mobile: criação automática, link, navegação cinco etapas, voltar/avançar, recarregar/retomar, falha de API, aprovar imagem, exportação e acessibilidade.
- Validar no Preview antes de merge. Não promover automaticamente para produção.

## Critérios de aceite
- Sem regressão nas cinco etapas ou backend; sem novas dependências e sem custo.
- Contraste legível, foco visível, ausência de rolagem horizontal em 320px e respeito a movimento reduzido.
- Não alegar QA completo antes de executar testes reais no Preview.

## Referências para avaliação
- https://www.tasteskill.dev/
- https://transitions.dev/
- https://reactbits.dev/
- https://github.com/Leonxlnx/taste-skill
- https://github.com/Jakubantalik/transitions.dev
- https://github.com/DavidHDev/react-bits
