# ⚾ ALLSTARS STUDIO — ALÉM DO JOGO

## Identidade visual oficial ALLSTARS 2026

Referência obrigatória: [ALLSTARS - Bíblia Visual 2026.md](ALLSTARS%20-%20B%C3%ADblia%20Visual%202026.md) e 14 pranchas JPG da raiz do repositório. A paleta foi centralizada em [`brand/identity.json`](brand/identity.json), com azul `#315FAC`, azul escuro `#1A3566`, vermelho `#CE233E`, dourado `#F0C040` e branco `#FFFFFF`. O renderizador agora utiliza a paleta e as diretrizes de composição. As pranchas NÃO são inseridas automaticamente nos vídeos, porque são referências visuais e podem conter demonstrações do logotipo. Não redesenhar nem deformar a marca. As fontes Barlow Condensed, Oswald e Barlow são as oficiais, mas a renderização atual usa a fonte condensada de fallback até a instalação segura das famílias oficiais.


## Uso simples — produção completa automática

1. Abra https://liuhelpme.github.io/allstars-studio/
2. Clique **Produzir episódio completo**. O GitHub pedirá que você entre na sua conta e clique **Run workflow → Run workflow**. **Ainda não é literalmente um clique**: o GitHub Pages não pode executar ações autenticadas diretamente sem um backend seguro.
3. Ao terminar, retorne ao painel e clique **Atualizar downloads**.
4. Baixe o MP4, MP3, legenda e referências nos botões do site.

**Automático:** toda segunda-feira, às 10h (Brasília, sem horário de verão), o workflow tentará gerar o próximo episódio sem intervenção manual. Os arquivos ficam nos [GitHub Releases](https://github.com/liuhelpme/allstars-studio/releases) e o último é apontado por `latest.json`.

**Avisos:** O sistema usa uma biblioteca pequena de roteiros pré-escritos, não faz pesquisa factual independente em tempo real. O vídeo produzido é **prévia editorial**: revisão dos fatos, direitos e qualidade da narração continua obrigatória antes de postar. Quando a fila de histórias acabar, a execução falhará intencionalmente em vez de repetir atletas. O serviço gratuito pode ter limites e a execução não foi validada ponta a ponta nesta versão.

---



Painel editorial para produzir vídeos verticais de beisebol, com **GitHub Pages + GitHub Actions + Piper TTS + FFmpeg**, sem API de áudio paga.

**Status:** primeira versão publicada no repositório. A execução dos workflows no GitHub e a publicação Pages precisam ser ativadas/testadas na conta. Não há publicação automática no Instagram nem verificação factual automática.

## 1. Ativar site (somente uma vez)

1. Acesse **Settings → Pages**: https://github.com/liuhelpme/allstars-studio/settings/pages
2. Em **Build and deployment → Source** escolha **Deploy from a branch**.
3. Em **Branch** escolha **main** e pasta **/(root)**.
4. Clique em **Save**.
5. Após a publicação, acesse **https://liuhelpme.github.io/allstars-studio/**.

## 2. Gerar um novo rascunho (sem API)

1. Acesse **Actions → ALLSTARS | Novo rascunho semanal**.
2. Clique **Run workflow → Run workflow**.
3. Quando terminar, o rascunho estará em `data/drafts/`; o histórico fica em `data/history.json`.
4. Revise todas as afirmações em fontes confiáveis antes de aproveitar.

O workflow também está agendado para **segunda-feira às 10h de Brasília**. O processamento depende dos limites e disponibilidade do GitHub Actions. **A fila inicial tem seis histórias distintas**; ao terminar, a tarefa falhará em vez de inventar uma repetição. Ampliaremos essa biblioteca editorial.

## 3. Gerar áudio e vídeo

1. Acesse `data/episode.json` e clique no lápis **Edit**: https://github.com/liuhelpme/allstars-studio/edit/main/data/episode.json
2. Atualize atleta, título, narração, textos, fontes e legenda. Se estiver usando um rascunho, copie seu conteúdo para esse arquivo.
3. Salve via **Commit changes**.
4. Acesse **Actions → ALLSTARS | Gerar audio e Reel MP4**: https://github.com/liuhelpme/allstars-studio/actions/workflows/render.yml
3. Selecione **ultimo-rascunho** (ou **episodio-principal**, se você editou manualmente o arquivo principal). Depois de conferir os fatos e os direitos, marque a confirmação de revisão e clique em **Run workflow**.
4. Quando ficar verde, abra a execução e baixe o **Artifact `allstars-episodio-pronto`**. Contém `.mp4`, `.mp3`, legenda, roteiro e fontes.

**Atenção:** a caixa de confirmação documenta sua revisão; o programa não substitui a pesquisa humana. Não há upload direto do editor web para o repositório, por segurança. O editor salva localmente e exporta JSON.

## 4. Ferramentas gratuitas

- [OHF Piper](https://github.com/OHF-Voice/piper1-gpl) — TTS local (software GPL-3.0).
- Voz `pt_BR-faber-medium` — [MODEL_CARD](https://huggingface.co/rhasspy/piper-voices/blob/main/pt/pt_BR/faber/medium/MODEL_CARD); dataset indicado CC0. Conferir a licença atual antes de uso.
- [FFmpeg](https://ffmpeg.org/) — processamento multimídia; verificar a licença da compilação e dos codecs.
- [Pillow](https://python-pillow.github.io/) — cartelas gráficas.
- [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:Reusing_content_outside_Wikimedia) — fotos individuais **somente com licenças verificadas**.

As capas e cartelas gráficas do MVP são desenhadas automaticamente: **não contém fotografias de arquivo**. Não use imagens da MLB, AP ou Getty sem licença.

## 5. Limitações da versão inicial

- GitHub Pages só hospeda o painel. O trabalho pesado roda nos Actions.
- O site **não tem um botão com acesso direto seguro à API privada do GitHub**. Os botões abrem os workflows, exigindo seu login e a confirmação no próprio GitHub.
- O histórico de rascunhos é registrado no repositório e evita escolher o mesmo atleta da fila. Ainda não deduplica similaridade semântica.
- O editor do site não sincroniza sozinho os campos com `data/episode.json`.
- Não existe ainda pesquisa automática de fatos na web, legendagem palavra a palavra, geração de fotos históricas nem publicação no Instagram.
- O GitHub Actions e serviços externos têm cotas. Em repositório público, ações com runners padrão costumam ser gratuitas, mas acompanhe as políticas e limites atuais.
- A aplicação gera roteiro, voz, vídeo e legenda a partir de dados cadastrados; o piloto exige revisão antes de uso.

## Estrutura

- `index.html` — painel web / GitHub Pages
- `data/episode.json` — conteúdo ativo para renderização
- `data/history.json` — exclusão de atletas já abordados e rascunhados
- `engine/generate.py` — fila de rascunhos sem créditos de API
- `engine/speech.py` — voz pt-BR com Piper
- `engine/render.py` — vídeo vertical com Pillow + FFmpeg
- `.github/workflows/weekly.yml` — criação semanal de rascunhos
- `.github/workflows/render.yml` — áudio + vídeo quando solicitado

Projeto inicial ALLSTARS Beisebol. Uso comercial e publicação condicionados à checagem de direitos e fatos.
