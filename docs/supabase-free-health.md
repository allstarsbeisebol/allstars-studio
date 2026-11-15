# Monitoramento gratuito do Supabase ALLSTARS

O Studio usa GitHub Actions para os pedidos de vídeo; este monitoramento é **independente** e não deve criar ou cancelar episódios.

## Ativação

1. Aguarde o projeto Supabase `alrgqmwnynybawenyugb` voltar a ACTIVE.
2. Execute o SQL abaixo no SQL Editor do projeto (uma vez):
   ```sql
   create or replace function public.allstars_health()
   returns boolean
   language sql
   stable
   security invoker
   set search_path = ''
   as $$
     select exists (select 1 from pg_catalog.pg_database where datname = current_database());
   $$;
   revoke all on function public.allstars_health() from public;
   grant execute on function public.allstars_health() to anon;
   ```
3. Nos GitHub Actions Secrets do repositório, configure `ALLSTARS_SUPABASE_URL` (URL do projeto) e `ALLSTARS_SUPABASE_ANON_KEY` (chave pública/anon; **nunca** service_role).
4. Execute manualmente o workflow `ALLSTARS | Saúde Supabase Free` e confirme o retorno `Consulta SQL de leitura ao Supabase concluída.`

O agendamento diário ocorre às 11h17 UTC (08h17 Brasília). Se faltarem Secrets, a execução registra um aviso e **não valida o banco**. Falhas de conexão/RPC produzem job vermelho.

**Limitações:** GitHub Actions pode atrasar ou deixar de executar cron em períodos de carga/inatividade. Consultas periódicas não garantem impedir a pausa automática do Supabase Free; respeite os termos do serviço. Não use esta verificação como substituto de backup, disponibilidade garantida ou teste de geração de vídeos.
