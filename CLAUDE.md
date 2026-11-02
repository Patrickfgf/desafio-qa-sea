# Regras para a IA neste repositório

Este repositório automatiza testes (pytest + Selenium + requests) de um app de cadastro de
funcionários que roda em ambiente **compartilhado e volátil**: outras pessoas usam a mesma base.
Estas regras valem para toda tarefa.

## Regras de engajamento

1. **Escreva só em registro nosso.** Todo registro criado pelos testes tem nome com o prefixo
   `QA-AUTO-` e um teardown que o apaga. Nunca altere nem apague registro alheio.
2. **Só dados sintéticos.** Nada de dado real, nem copiado da base.
3. **Nenhum payload executável.** Nada de `<script>`, handlers de evento ou equivalentes, nem
   em teste de segurança. Use texto inerte que só pareça suspeito.
4. **Sem carga, força bruta ou varredura.** Nenhuma requisição fora de `/` e `/employees`.
5. **PII mascarada antes de salvar**, no formato `123.***.***-09`, e nunca em dump bruto no
   contexto da IA. Use `support/pii.py` (`mask_employee`, `mask_text`).
6. **Nada de `GET /employees` completo em loop.** Busque por `id` ou use filtros.
7. **A base conta como dado potencialmente real.** Trate cada registro que você não criou como
   se fosse de uma pessoa de verdade.
8. **Análise do conjunto só por agregados mascarados** (contagens, distribuições), nunca
   registros individuais de terceiros.
9. **Artefatos sem PII de terceiros**, com retenção de 7 dias no CI.

## Regras de código

- Mensagem de `assert` nunca carrega corpo de resposta cru; use `describe()`.
- Nunca `sleep`; sempre espera explícita (`WebDriverWait`, polling com prazo).
- Bug conhecido: `pytest.mark.xfail(strict=True, raises=AssertionError, reason="BUG-NNN: <título curto>")`.
- Nunca afirme um bug que o Patrick não reproduziu.
- O teardown tolera 404: a base pode ser apagada ou resetada no meio da execução.
- Arquivos sempre em utf-8.
- Nunca crie registro com `id` inteiro (nem envie `id` no POST): o json-server v1 compara o id da
  rota como string, e um registro de id inteiro fica inalcançável e inapagável pela API.
- Ao depurar a listagem, leia só cards `QA-AUTO-` (ou mascare o DOM antes): imprimir o DOM
  inteiro joga dados de terceiros no contexto.

## Git

- Commits em inglês, no padrão conventional commits (`feat:`, `fix:`, `test:`, `docs:`,
  `chore:`, `refactor:`), pequenos e na ordem real do trabalho.
- Nunca commitar direto em `main`.
- Rascunhos, planos e diário bruto ficam fora do repositório: no vault ou em `work/`.
