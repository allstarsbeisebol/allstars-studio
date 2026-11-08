# ALLSTARS Studio — uso com dois botões

## Painel integrado (Vercel)

Endereço: https://allstars-studio.vercel.app/

1. Faça login no estúdio (apenas quando solicitado).
2. Clique **Gerar automaticamente** ou cole uma URL e clique **Gerar com este link**.
3. Acompanhe o status no próprio painel.
4. Baixe vídeo MP4, capa PNG, áudio MP3, legenda e fontes no mesmo lugar.

## Avisos de produção

Depois de solicitar um episódio, o estúdio consulta o andamento automaticamente. Ao concluir, exibe uma mensagem em destaque com **Ver downloads**; em caso de falha, apresenta **Ver detalhes**.

Para receber uma notificação do navegador:
1. Na página inicial, clique **🔔 Ativar avisos do navegador**.
2. Quando o navegador perguntar, escolha **Permitir**. É uma permissão opcional.
3. Gere o episódio normalmente. O aviso será exibido mesmo quando o estúdio estiver em outra aba, **desde que a página permaneça aberta**.
4. Para desativar a opção dentro do estúdio, clique novamente em **Avisos ativados — desativar**.

Se a permissão for negada ou o navegador não oferecer suporte, a mensagem dentro da página continuará funcionando. O estúdio registra qual pedido já foi notificado para evitar repetir o aviso após atualizar a aba. Se você fechar e voltar depois, a página consulta o pedido em andamento quando for aberta novamente.

**Limitação importante:** o sistema atual não oferece Web Push quando todas as abas estiverem fechadas. Isso exigiria um serviço de notificações com inscrição do navegador e processamento no servidor. A versão atual não usa serviços pagos de notificação.


A versão integrada exige um **backend seguro**; GitHub Pages sozinho não pode disparar tarefas privadas sem autenticação. Não é necessário navegar pelo GitHub Actions para uso normal.

## Conexão inicial — somente uma vez

- Abra [Environment Variables do projeto Vercel](https://vercel.com/liuhelpme-4965s-projects/allstars-studio/settings/environment-variables).
- Já existe um segredo interno criado: `ALLSTARS_SESSION_SECRET`. **Não altere nem divulgue.**
- Adicione `ALLSTARS_ADMIN_PASSWORD` com uma senha forte escolhida por você. Target: **Production**. Tipo: **Encrypted**.
- Crie um [GitHub fine-grained Personal Access Token](https://github.com/settings/personal-access-tokens/new), limitando o acesso à conta `liuhelpme`, **somente** ao repositório `allstars-studio`, com permissão de repositório **Issues: Read and write** (Metadata: Read já vem por padrão). Cole o token somente na variável `ALLSTARS_GITHUB_TOKEN` da Vercel, target Production, tipo Encrypted. **Nunca** cole o token em chat, Issue, link, arquivo público ou no HTML.
- Faça um novo deploy de produção após salvar as variáveis. Quando o endpoint `/api/login` responder `{"configured":true}` e a senha permitir login, os dois botões funcionarão no site.
- Para o modo **Com link**, também é necessário colocar `GEMINI_API_KEY` em [GitHub Actions Secrets](https://github.com/liuhelpme/allstars-studio/settings/secrets/actions). A chave é criada no [Google AI Studio](https://aistudio.google.com/apikey); confira os limites gratuitos e opções de faturamento antes de ativar.

**Não é necessário enviar senha, token ou chave de API ao ChatGPT.** São segredos privados, armazenados apenas nas configurações dos respectivos serviços. O token do GitHub vence de acordo com a duração escolhida; substitua-o na Vercel quando expirar.

## Segurança e limites

- O acesso do painel usa sessão assinada em cookie HttpOnly e exige senha administrativa.
- O backend possui credenciais exclusivamente no lado do servidor e cria GitHub Issues restritas ao repositório. Apenas Issues da conta `liuhelpme` acionam o fluxo.
- A API rejeita links que não sejam HTTPS e não transmite senhas ou tokens em URLs.
- Falhas de leitura ou geração baseada em link **não** são substituídas por outro atleta.
- O modo automático atual utiliza uma biblioteca editorial limitada, não pesquisa livremente na internet.
- O fluxo por link cria **rascunhos baseados no texto da página**, sem validação factual independente.
- O serviço usa GitHub Actions para Piper TTS e FFmpeg; limites e quotas gratuitas se aplicam.
- A Vercel Hobby tem restrições de uso comercial. Confirme a modalidade adequada caso o ALLSTARS Studio seja usado em atividade comercial.
- Imagens históricas exigem licenças. A presença de uma foto ou marca em um site não autoriza copiá-la para um Reel.
- Não publica diretamente no Instagram.

## Arquitetura

- Interface: `public/index.html` (Vercel).
- Autenticação: `api/login.js` e `lib/security.js`.
- Solicitação segura: `api/generate.js`.
- Progresso e downloads: `api/status.js`.
- Produção: `.github/workflows/produce.yml`.
- Seleção e artigo: `engine/request_select.py`, `engine/produce_select.py`, `engine/from_link.py`.
- Mídia: `engine/cover.py`, `engine/speech.py`, `engine/render.py`.
- Testes: `tests/backend.test.js` e workflow `check.yml`.
- Documentação da marca: `ALLSTARS - Bíblia Visual 2026.md` e `brand/identity.json`.

O GitHub Pages antigo permanece acessível até a nova conexão estar operando. A produção permanece sob demanda, sem agendamento semanal ativo.
