# Referências de código aberto para o ALLSTARS Studio

Análise editorial/técnica do vídeo enviado sobre projetos de imagem, vídeo e voz. A escolha prioriza **capa esportiva cinematográfica no padrão da Bíblia Visual ALLSTARS 2026**, produção sob demanda com dois botões, execução sem GPU e **sem créditos de API pagos**.

## Adotar como referência arquitetural

- [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo): separar o pipeline em pesquisa/roteiro, voz, seleção de mídia, legendas, composição e exportação; registrar cada etapa e tornar o resultado baixável no site. **Não instalar como dependência geral nem substituir o sistema atual**: o nosso fluxo já tem GitHub Actions, Vercel, Piper e FFmpeg e exige regras visuais de marca mais rígidas.
- [rembg](https://github.com/danielgatis/rembg): preparar recortes de **fotos licenciadas** de jogadores para melhorar o destaque na capa. Só executar quando uma imagem aprovada existir; preferir versão CPU e um modelo cujo **peso** permita o uso pretendido. O pacote MIT não concede automaticamente licença comercial aos pesos dos modelos.
- [faster-whisper](https://github.com/SYSTRAN/faster-whisper): gerar legendas sincronizadas automaticamente com o MP3, com modelo pequeno e CPU int8. Fazer em etapa opcional, com validação de timing, para evitar download grande em toda produção.
- [Piper](https://github.com/OHF-Voice/piper1-gpl): manter como voz principal, aumentar `--length-scale` para 1.14 e `--sentence-silence` para 0.22s. A voz deve ser testada ouvindo áudio real.
- FFmpeg existente: aplicar movimentos lentos de zoom/pan, transições suaves e blocos tipográficos em contraste; sempre exportar 9:16 1080x1920. Priorizar velocidade e qualidade consistente.

## Não incluir na produção gratuita atual

- Modelos texto-para-vídeo pesados (LTX-Video, HunyuanVideo, CogVideoX, Wan, Open-Sora): requerimentos/tempo e possíveis custos de GPU não são apropriados como padrão de GitHub Actions gratuito.
- [FLUX.1 schnell](https://github.com/black-forest-labs/flux): pesos abertos sob Apache-2.0, mas inferência é pesada (12B). Avaliar apenas caso exista infraestrutura compatível/custos explicitamente aprovados. Não confundir com FLUX.1 dev, de licença não comercial.
- Clonagem/transformação de vozes de pessoas reais (RVC, Fish Speech, F5-TTS etc.): não usar sem consentimento, direitos e processo de revisão.
- MusicGen/AudioCraft: música gerada não fica automaticamente livre de restrições de copyright ou dos termos do modelo; usar apenas faixas com direitos conhecidos.

## Critérios de qualidade de cada episódio

1. Usar a **logo original** do usuário, mantendo proporção e área de respiro. Nunca redesenhar.
2. Usar azul #315FAC, navy #1A3566, vermelho #CE233E, dourado #F0C040 e branco #FFFFFF; fontes Barlow Condensed/Barlow ou Oswald como especificado.
3. Montar capa com atleta em destaque **somente quando houver imagem com licença registrada**. Nunca apresentar silhueta genérica como imagem histórica.
4. Hierarquia visual próxima das referências: foto heroica, estádio desfocado, iluminação dramática, pinceladas azul/vermelha, palavras-chave amarelas, textura esportiva, rodapé institucional.
5. Roteiro baseado em fontes verificáveis; não inventar fatos, imagens ou licença. A fonte copiada pelo usuário gera rascunho a revisar.
6. Voz brasileira em tom documental, ligeiramente mais pausada, sem aceleração.
7. Legendas legíveis sincronizadas, sem cobrir rosto e logo.
8. Exportar MP4, PNG de capa, MP3, texto da legenda, roteiro e fontes; preservar botão **Gerar automaticamente** ou **Gerar com link** no painel.
9. Nenhuma dependência nova pode impor **despesa automática** em API ou nuvem.

> Bibliotecas de código aberto são ferramentas, não substitutos de documentação histórica nem autorização de uso de imagens.
