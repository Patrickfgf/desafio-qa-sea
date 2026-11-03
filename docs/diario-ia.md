# Diário de uso de IA

Ponteiros de seção remetem a notas internas, disponíveis na conversa; onde há, uso o sha do commit.

Em 03/11 eu deleguei à IA as decisões que o plano reservava a mim: o corte de risco, a severidade e a prioridade finais, o texto do "não testei" e a estrutura dos PRs. A IA as registrou num log de decisões (DEC-01 a DEC-21) que eu valido. Rodar a Task 12 foi decisão minha. ⟪PATRICK: confirme depois da reprodução manual: cada defeito do relatório foi reproduzido por mim à mão antes da entrega⟫

## Onde e para quê

| Etapa | O que a IA fez |
|---|---|
| Design e plano | Rascunhou design, plano de testes e mapa de risco |
| Exploração | Exploradores propuseram defeitos; verificadores tentaram refutá-los |
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
5. Um explorador criou 4 registros com `id` inteiro, inapagáveis. Pego por autorrelato do explorador e pela checagem de sobras. Exploração §7.3.
6. A redação do print de falha escondia só cards de 3 divs (fail-open). Pego por 3 revisores. Commits 766723a → 4ad8e1d.
7. Um script de sondagem imprimiu o DOM da listagem, com dados de terceiros no contexto da IA. Pego por autorrelato do implementador. Relatório interno da Task 10; regra no CLAUDE.md.
8. O plano prometia conferir por `?id=` após o DELETE, mas o código não fazia. Pego por crítico de completude. Commit a829cdd.
9. Um verificador enviou um POST vazio e deixou a listagem em branco por segundos. Pego pela triagem. Registro 4643 apagado e confirmado por `?id=`; regra nova nos briefs (DEC-13).

## Guarda-corpos

- `CLAUDE.md`: só registros `QA-AUTO-`, só dados sintéticos, sem payload executável, sem carga, nada fora de `/` e `/employees`.
- Guarda de PII: `support/pii.py` mascara CPF, e o teste `guard` falha se `docs/` tiver CPF sem máscara.
- Verificação adversarial: um segundo agente tentou refutar 19 dos 23 defeitos; BUG-016, BUG-019, BUG-023 e BUG-024 só têm a execução de quem os achou e o teste xfail, e dependem da reprodução manual.
- Portões humanos: reprodução manual dos defeitos, edição final destes textos e a mudança pequena do Portão 3.
