# Diário de uso de IA

Em 03/11 as decisões dos portões foram delegadas à IA e registradas num log de decisões (DEC-01 a DEC-17). ⟪PATRICK: confirme depois da reprodução manual: cada defeito do relatório foi reproduzido por mim à mão antes da entrega⟫

## Onde e para quê

| Etapa | O que a IA fez |
|---|---|
| Design e plano | Rascunhou design, plano de testes e mapa de risco |
| Exploração | Exploradores propuseram candidatos a defeito; verificadores tentaram refutá-los |
| Automação | Escreveu e revisou os testes, os Page Objects e a evidência mascarada |
| Triagem e relatório | Cruzou candidatos, severidades e evidências |
| Cobertura 2025 | Extraiu só nomes de áreas de um repo antigo; as áreas faltantes foram exploradas do zero |
| Documentos | Redigiu estes textos e o README |

## O que a IA errou e como foi corrigido

Seleção de 9 das 20 entradas do diário bruto.

1. Tratou "upload de ASO" como fato, vindo de pesquisa externa. Pego por subagente revisor. Design §4.
2. Sugeriu e-mail à empresa para aprovar os limites do teste. Pego por mim. Design §11.
3. `assert body == sent` fazia o pytest imprimir CPF no relatório. Pego por subagente revisor. Commits e312b75 → a8f1c64.
4. Severidade inflada em 14 candidatos. Pego por verificação adversarial. Exploração §3.2 e §5.1.
5. Um explorador criou 4 registros com `id` inteiro, inapagáveis. Pego pelo próprio explorador e pela checagem de sobras. Exploração §7.3.
6. A redação do print de falha escondia só cards de 3 divs (fail-open). Pego por 3 revisores independentes. Commits 766723a → 4ad8e1d.
7. Um script de sondagem imprimiu o DOM da listagem, com dados de terceiros no contexto da IA. Pego por autorrelato do implementador. Relatório da Task 10.
8. O plano prometia conferir por `?id=` após o DELETE, mas o código não fazia. Pego por crítico de completude. Commit a829cdd.
9. Um verificador enviou um POST vazio e deixou a listagem em branco por segundos. Pego por agente de triagem (Opus), confirmado pelo Claude. Registro apagado; regra nova nos briefs. DEC-13.

## Guarda-corpos

- `CLAUDE.md`: só registros `QA-AUTO-`, só dados sintéticos, sem payload executável, sem carga, nada fora de `/` e `/employees`.
- Guarda de PII: `support/pii.py` mascara CPF, e o teste `guard` falha se `docs/` tiver CPF sem máscara.
- Verificação adversarial: outro agente tenta refutar cada candidato antes de ele chegar ao relatório.
- Portões humanos: reprodução manual dos defeitos, edição final destes textos e a mudança pequena do Portão 3.
