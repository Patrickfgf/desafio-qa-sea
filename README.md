# Desafio prático: Analista de Teste (QA)

Testes automatizados (pytest, Selenium e requests) do sistema de cadastro de trabalhadores para segurança do trabalho, cobrindo a interface web e a API REST `/employees`.

## Como rodar

```bash
uv sync --locked
uv run pytest                  # suíte completa
uv run pytest -m unit          # também: api, security, ui, cross, guard
APP_BASE_URL=https://... uv run pytest -m api   # troca o ambiente alvo
```

`APP_BASE_URL` é opcional; o padrão é o ambiente do desafio. Os testes `ui` precisam de Chrome instalado.

> **Atenção.** Os marcadores `api`, `security`, `ui` e `cross` usam um ambiente **vivo e compartilhado**, onde outras pessoas trabalham e os registros contam como dado pessoal potencialmente real. Os testes só criam e apagam registros próprios, com nome iniciado por `QA-AUTO-`, e só tocam em `/` e `/employees`. Os marcadores `unit` e `guard` são offline.

## Entregas

1. Plano de testes: [`docs/plano-de-testes.md`](docs/plano-de-testes.md)
2. Relatório de defeitos: [`docs/relatorio-de-defeitos.md`](docs/relatorio-de-defeitos.md)
3. Código de automação, com CI: esta pasta e [`.github/workflows/ci.yml`](.github/workflows/ci.yml)
4. Diário de uso de IA: [`docs/diario-ia.md`](docs/diario-ia.md)
5. Nota de estratégia: [`docs/nota-de-estrategia.md`](docs/nota-de-estrategia.md)

## Estrutura

```text
docs/        plano, relatório, diário de IA, nota de estratégia e evidências mascaradas
pages/       Page Objects (Selenium)
support/     cliente da API, fábrica de dados sintéticos, máscara de PII, evidência
scripts/     perfil agregado e mascarado da base
tests/       unit, api, security, ui, cross e guard
CLAUDE.md    regras de engajamento para a IA
```

## Números

- Coleta de `uv run pytest --collect-only -q` em 04/11/2026: **181 testes**. Por marcador: unit 114, api 20, ui 28, security 9, cross 9, guard 1.
- Último CI: [execução 41582056702](https://github.com/Patrickfgf/desafio-qa-sea/actions/runs/41582056702), `success`, em 03/11/2026, sobre o commit `f9f3241` da branch `feat/findings-and-deliverables`.

Os defeitos conhecidos são testes `xfail(strict=True)` com o id `BUG-NNN` no motivo; o status de cada um está no relatório.
