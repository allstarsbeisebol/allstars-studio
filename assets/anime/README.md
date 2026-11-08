# Banco de imagens anime aprovadas — ALLSTARS

Cada arte deve ser original, aprovada e vinculada a **um único atleta**. Uma ilustração de Jim Abbott jamais será reutilizada para Roberto Clemente ou outro jogador.

O gerador reconhece automaticamente estes dois arquivos, por exemplo:

- `assets/anime/jim-abbott.webp` (ou .png / .jpg)
- `assets/anime/jim-abbott.json` (metadados de autorização e procedência)

Exemplo de `jim-abbott.json`:

```json
{
  "athlete": "Jim Abbott",
  "file": "jim-abbott.webp",
  "approved": true,
  "visual_type": "original_anime_illustration",
  "source_note": "Arte anime original aprovada para o episódio Jim Abbott; não é fotografia histórica",
  "rights_basis": "Arte original criada para ALLSTARS Studio, sujeita à revisão de publicação"
}
```

Padrão de arquivo: retrato 9:16, pelo menos 480 × 850 px, preferencialmente 1080 × 1920 px. A logo oficial ALLSTARS e a tipografia devem respeitar a Bíblia Visual 2026. O título deve ser confirmado com o roteiro.

O arquivo `brand/anime_direction.json` registra o estilo aprovado pelo responsável do projeto: alto nível de detalhamento, técnica de anime esportivo, emoção e composição cinematográfica. Não copiar personagens existentes de Ace of Diamond, Major ou Big Windup.

**Limitação técnica importante:** a biblioteca `Pillow` é um compositor, não um modelo gerador de imagens. A aprovação de uma arte nesta conversa não injeta automaticamente seus pixels no repositório. É necessário que o arquivo da ilustração tenha sido efetivamente importado no banco de imagens. A API Gemini de geração de imagens não tem nível gratuito no catálogo consultado em novembro de 2026. Por isso, o workflow não solicita imagens pagas automaticamente.

Enquanto não existir arte anime aprovada para um atleta, o sistema continua com fotografia licenciada quando disponível, ou o desenho de contingência atual, que deve ser tratado como **prévia editorial**, não como capa anime premium aprovada.
