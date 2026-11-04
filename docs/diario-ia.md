# Diário de uso de IA

Ponteiros de seção remetem a notas internas, disponíveis na conversa; onde há, uso o sha do commit.

Defini a tese da entrega. A arquitetura e a stack saíram de uma discussão conjunta enquanto montávamos o design e o plano: a IA propôs e comparou as alternativas (Selenium, Playwright e Cypress), eu questionei e aprovei o design antes de qualquer código, inclusive os três portões humanos e a separação entre rascunhos e entrega. Em 03/11 eu deleguei à IA as decisões que o plano reservava a mim: o corte de risco, a severidade e a prioridade finais, o texto do "não testei" e a estrutura dos PRs. A IA as registrou num log de decisões (DEC-01 a DEC-23) que eu valido. Rodar a Task 12 foi decisão minha. ⟪PATRICK: confirme depois da reprodução manual: cada defeito do relatório foi reproduzido por mim à mão antes da entrega⟫

## Método: por que não um prompt único

Um prompt como "faz o desafio" devolve código plausível e um relatório confiante, sem como saber o que é verdade. Usei *skills*, roteiros que o agente segue passo a passo (as três primeiras do pacote Superpowers; `/resume` e `/end-session` são minhas). Cada uma força uma etapa que um prompt solto pula, e cada etapa pegou erro real (números da lista abaixo):

| Skill ou prática | O que faz | O que pegou aqui |
|---|---|---|
| `brainstorming` | Perguntas e alternativas com trade-off até um design aprovado, antes do código | Limites do ambiente compartilhado definidos antes do primeiro request (erro 2) |
| `writing-plans` | Tasks pequenas, teste primeiro, resultado esperado, checkpoint humano | 15 tasks; cada PR cabe numa revisão |
| *Subagent-driven development* | Um agente implementa cada task, outro revisa | CPF no relatório do pytest (erro 3); print fail-open (erro 6) |
| Verificação adversarial | Exploradores propõem; verificadores tentam refutar (18 dos 27 defeitos) | Severidade inflada em 14 candidatos (erro 4) |
| Modelo por tarefa | Haiku extrai, Sonnet implementa e verifica, Opus faz a revisão final | Revisão final: 1 CRITICAL e 4 HIGH, todos tratados |
| `/resume` e `/end-session` | Log diário no meu Obsidian: feito, pendências, decisões | Troquei de máquina (Windows → Mac) sem perder estado |

Humano no circuito: reproduzi à mão cada defeito e fiz uma sessão exploratória própria, procurando o que a IA não achou. ⟪PATRICK: resultado da sessão exploratória⟫

A IA também leu os bugs e testes de um repositório público de 2025 do mesmo desafio para cruzar com os meus achados; os itens coincidentes foram reproduzidos de novo na versão atual do app.

## O que a IA errou e como foi corrigido

Seleção de 10 das 21 entradas do diário bruto.

1. Tratou "upload de ASO" como fato, vindo de pesquisa externa. Pego por subagente revisor. Design §4.
2. Sugeriu e-mail à empresa para aprovar os limites do teste. Pego por mim. Design §11.
3. `assert body == sent` fazia o pytest imprimir CPF no relatório. Pego por subagente revisor. Commits e312b75 → a8f1c64.
4. Severidade inflada em 14 candidatos. Pego por verificação adversarial. Exploração §3.2 e §5.1.
5. Um explorador criou 4 registros com `id` inteiro, que deram 404 por id em 02/11. Em 03/11 os 2 remanescentes já tinham id string e um DELETE comum os apagou; a IA chegou a reafirmar "inapagável" sem testar de novo, e o teste desmentiu. Pego por autorrelato do explorador e pela checagem de sobras. Exploração §7.3.
6. A redação do print de falha escondia só cards de 3 divs (fail-open). Pego por 3 revisores. Commits 766723a → 4ad8e1d.
7. Um script de sondagem imprimiu o DOM da listagem, com dados de terceiros no contexto da IA. Pego por autorrelato do implementador. Relatório interno da Task 10; regra no CLAUDE.md.
8. O plano prometia conferir por `?id=` após o DELETE, mas o código não fazia. Pego por crítico de completude. Commit a829cdd.
9. Um verificador enviou um POST vazio e deixou a listagem em branco por segundos. Pego pela triagem. Registro 4643 apagado e confirmado por `?id=`; regra nova nos briefs (DEC-13).
10. Classificou como defeito ("tela → payload") o cadastro nascer inativo, sem checar que o switch já mostra "Inativo". Pego por mim na reprodução manual; virou observação.

## Guarda-corpos

- `CLAUDE.md`: só registros `QA-AUTO-`, só dados sintéticos, sem payload executável, sem carga, nada fora de `/` e `/employees`. O teste `guard` falha se `docs/` tiver CPF sem máscara (`support/pii.py`).
- BUG-016, BUG-019, BUG-023, BUG-024 e BUG-025 a BUG-029 não passaram pelo verificador: têm a execução de quem os achou, o teste xfail e a minha reprodução.
