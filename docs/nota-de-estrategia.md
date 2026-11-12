# Nota de estratégia

## Tempo disponível

O prazo era até quarta 04/11. O trabalho registrado no git vai de 31/10 a 03/11: 55 commits até `2315607` (1 em 31/10, 18 em 02/11, 36 em 03/11; nenhum em 01/11).

## O que priorizei e por quê

Fechei o escopo a partir do mapa de risco (`docs/plano-de-testes.md`, seção 3), que revisei item a item; o diário de IA conta como ele foi montado. O mapa cruza impacto e probabilidade. Fui a fundo em três áreas: o que a tela grava contra o que o usuário vê, privacidade (CPF completo na tela e na API) e validação de CPF e data. O resto ficou em "testar leve", com um ou dois testes que documentam o comportamento. Controle de acesso tem severidade Crítica, mas ficou leve: a ausência de autenticação é binária, e um teste por método já prova.

## O que não testei e por quê

- Não testei carga, estresse nem força bruta porque o ambiente é compartilhado com outras pessoas e uma sonda de volume atrapalharia o trabalho delas; as regras de engajamento proíbem.
- Não testei injeção ativa (SQL, XSS, path traversal) com payload executável porque a base é compartilhada e pode ter dado real; usei só texto inerte, então não afirmo que a aplicação é ou não vulnerável a injeção.
- Não testei outros navegadores nem mobile porque a automação roda só em Chrome headless e o tempo foi para os fluxos de maior risco: o que a tela grava e a exposição de dados pessoais.
- Não testei a fundo acessibilidade porque não há especificação do comportamento pretendido. Os controles sem efeito ("Próximo passo", barra lateral, "...") entram só como BUG-027, sem afirmar qual deveria ser o comportamento.
- Não testei alteração, remoção nem enumeração de registros de terceiros porque mexeria em dado que não é nosso; a prova de "apagar sem autenticação" foi feita num registro criado por mim.

## O que faria com mais tempo

- Pedir ao dono do produto o comportamento pretendido dos controles sem efeito e então testá-los.
- Verificar, com autorização, as dúvidas que ficaram em aberto (plano, seção 2): CORS no navegador e cache de dados pessoais.
- Rodar a suíte de UI em outros navegadores e em tela de celular.

