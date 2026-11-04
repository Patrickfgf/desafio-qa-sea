# Diário de uso de IA

Usei o Claude Code do começo ao fim, como agente com *skills* (roteiros passo a passo) em vez de um prompt único: "faz o desafio" devolve código plausível e um relatório confiante, sem como saber o que é verdade.

## Onde e para quê

| Etapa | O que a IA fez | O que eu fiz |
|---|---|---|
| Design e plano | Propôs e comparou Selenium, Playwright e Cypress; quebrou o trabalho em tasks pequenas, teste primeiro | Questionei e aprovei o design antes de qualquer código, inclusive os limites do ambiente compartilhado |
| Exploração e implementação | Exploradores propuseram defeitos; um agente implementou cada task e outro a revisou | Reproduzi à mão os defeitos visíveis na interface |
| Verificação | Verificadores tentaram refutar cada candidato (19 dos 27 defeitos); os 9 defeitos só de API (BUG-002, 004, 005, 011, 014, 018, 019, 020 e 021) foram reverificados ao vivo em 04/11 | Deleguei esses nove à automação (checagem determinística) e rebaixei o BUG-015 a observação |
| Modelo por tarefa | Haiku extrai, Sonnet implementa e verifica, Opus faz a revisão final (1 CRITICAL e 4 HIGH, todos tratados) | Defini o corte de risco, a severidade e a prioridade finais |

Também fiz uma sessão exploratória própria, procurando o que a IA não achou: listagem cortada e sem rolagem (BUG-028), controles sem efeito (BUG-027), códigos de EPI inconsistentes (BUG-029), ano de 6 dígitos (BUG-010), CPF validado só por tamanho e nome sem trim (BUG-023) e o contorno falso do BUG-006. A IA ainda leu bugs de um repositório público de 2025 do mesmo desafio; os itens coincidentes foram reproduzidos de novo na versão atual do app.

## O que a IA errou e como foi corrigido

1. Tratou "upload de ASO" como fato, vindo de pesquisa externa. Pego por subagente revisor.
2. Sugeriu e-mail à empresa para aprovar os limites do teste. Pego por mim; os limites foram definidos por mim e registrados no `CLAUDE.md`.
3. `assert body == sent` fazia o pytest imprimir CPF no relatório. Pego por revisor (commits e312b75 → a8f1c64); agora o `assert` usa `describe()`.
4. Severidade inflada em 14 candidatos. Pego pela verificação adversarial, que a recalibrou.
5. Um explorador criou 4 registros com `id` inteiro, que deram 404 por id; a IA chegou a afirmar "inapagável" sem testar de novo. Os 2 que restavam tinham `id` string e um DELETE comum os apagou. Hoje nenhum teste cria `id` inteiro.
6. A redação do print de falha escondia só cards de 3 divs (fail-open). Pego por 3 revisores (commits 766723a → 4ad8e1d).
7. Um script de sondagem imprimiu o DOM da listagem, com dados de terceiros, no contexto da IA. Pego por autorrelato; a regra de ler só cards `QA-AUTO-` entrou no `CLAUDE.md`.
8. O plano prometia conferir por `?id=` após o DELETE, mas o código não fazia. Pego por crítico de completude (commit a829cdd).
9. Um verificador enviou um POST vazio e deixou a listagem em branco por segundos. Pego na triagem; registro apagado e confirmado por `?id=`, e uma regra nova entrou nos briefs dos verificadores.
10. Classificou como defeito o cadastro nascer inativo, sem checar que o switch já mostra "Inativo". Pego por mim na reprodução manual; virou observação.

## Guarda-corpos

`CLAUDE.md` limita a IA a registros `QA-AUTO-`, dados sintéticos, sem payload executável e só em `/` e `/employees`. O teste `guard` falha se `docs/` tiver CPF sem máscara. BUG-016, 023, 024 e 025 a 029 não passaram pelo verificador: têm a execução de quem os achou, o teste xfail e a minha reprodução.
