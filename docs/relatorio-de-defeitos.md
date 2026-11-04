# Relatório de defeitos

> **Método:** defeitos visíveis na interface reproduzidos à mão; os que dependem da API para serem provocados ou provados (BUG-002, 004, 005, 011, 014, 018, 019, 020 e 021) ficam com a automação, que repete a checagem determinística a cada CI com evidência HTTP, e foram reverificados ao vivo em 04/11 por um verificador e um cético independentes; os demais passaram pelo verificador em 03/11 (exceto os listados no diário). Evidências geradas por scripts de verificação não versionados, com `support.evidence` e o mascaramento do repositório. Os ids BUG-015 (virou observação) e BUG-022 não são usados.

**Ambiente:** `https://analista-teste.seatecnologia.com.br/` (interface e `/employees`), 03/11/2026 (BUG-001, 006, 007 e 012: verificação anterior, sem data; defeitos de API reauditados em 04/11), Chrome headless e `requests`. Nos passos, todo registro é sintético, com nome `QA-AUTO-`, criado sem `id` e apagado no fim com confirmação por `GET /employees?id=<id>` ("ler por `?id=`"). CPF mascarado (`123.***.***-09`) nas evidências.

## Escalas

Severidade é o impacto técnico; prioridade é a urgência de negócio (as mesmas de `plano-de-testes.md`, seção 3.1).

| Severidade | Critério |
|---|---|
| Crítica | perda ou exposição de dados em larga escala, sem pré-condição |
| Alta | dado gravado ou exposto de forma errada em fluxo principal, controle de acesso ausente, ou fluxo principal indisponível para todos |
| Média | comportamento incorreto com contorno, ou efeito limitado a clientes da API |
| Baixa | cosmético, usabilidade, má prática sem dano demonstrado |

| Prioridade | Critério |
|---|---|
| P1 | corrigir primeiro: afeta todo cadastro ou expõe dados pessoais |
| P2 | corrigir na sequência: afeta parte dos usuários ou os clientes da API |
| P3 | pode esperar: baixo impacto no fluxo |

## Resumo (por prioridade)

| ID | Título | Categoria | Severidade | Prioridade | Automatizado |
|---|---|---|---|---|---|
| BUG-001 | Checkbox não usa EPI grava usesEpi invertido | Funcional (tela → payload) | Alta | P1 | `tests/cross/test_ui_vs_api.py::test_uses_epi_flag_matches_checkbox` |
| BUG-002 | API expõe CPF, RG e nascimento sem autenticação | Privacidade / LGPD | Alta | P1 | `tests/security/test_security.py::test_record_does_not_expose_full_cpf` |
| BUG-003 | Listagem exibe o CPF completo no card | Privacidade / LGPD | Alta | P1 | `tests/cross/test_ui_vs_api.py::test_listing_card_masks_cpf` |
| BUG-004 | API cria, altera e apaga registros sem autenticação | Segurança (controle de acesso) | Alta | P1 | `tests/security/test_security.py::test_create_requires_authentication` (+ `update` em PUT/PATCH e `delete`, ver seção) |
| BUG-005 | Registro sem state.employee deixa a listagem em branco | Funcional (listagem) | Alta | P1 | manual |
| BUG-006 | Selects exibem padrão que não é gravado ao salvar | Funcional (tela → payload) | Média | P2 | `tests/cross/test_ui_vs_api.py::test_default_selects_are_saved_as_displayed` |
| BUG-007 | Anexo do ASO não é enviado nem persistido | Funcional (tela → payload) | Média | P2 | `tests/cross/test_ui_vs_api.py::test_aso_file_is_persisted` |
| BUG-008 | CPF aceito sem validação de conteúdo | Validação | Média | P2 | `tests/api/test_validation.py::test_create_rejects_invalid_cpf_checksum` |
| BUG-009 | CPF digitado com máscara é truncado sem aviso | Validação (tela) | Média | P2 | `tests/ui/test_form_validation.py::test_formatted_cpf_is_not_silently_truncated` |
| BUG-010 | Data de nascimento sem validação de intervalo | Validação | Média | P2 | `tests/api/test_validation.py::test_create_rejects_future_birth_date` |
| BUG-011 | API não valida schema, tipos nem campos extras | Contrato da API | Média | P2 | `tests/api/test_validation.py::test_create_rejects_missing_required_fields` |
| BUG-012 | Adicionar outra atividade salva e fecha o formulário | Funcional (formulário) | Média | P2 | `tests/ui/test_form_controls.py::test_add_another_activity_does_not_submit` |
| BUG-013 | Listagem busca dados em paralelo ao POST e fica velha | Funcional (listagem) | Média | P2 | `tests/ui/test_form_controls.py::test_listing_refetch_happens_after_post_completes` |
| BUG-024 | Enter descarta o cadastro sem salvar | Funcional (formulário) | Média | P2 | `tests/ui/test_form_controls.py::test_enter_in_text_field_does_not_discard_the_form` |
| BUG-028 | Listagem mostra só os primeiros cards e não rola | Funcional (listagem) | Média | P2 | `tests/ui/test_navigation_controls.py::test_every_listing_card_is_reachable_by_scrolling` |
| BUG-014 | PATCH em state apaga os campos não enviados | Contrato da API | Baixa | P3 | `tests/api/test_validation.py::test_patch_preserves_unsent_fields` |
| BUG-016 | Select de EPI volta ao padrão ao digitar o CA | Usabilidade | Baixa | P3 | `tests/ui/test_form_controls.py::test_epi_select_keeps_choice_after_typing_ca` |
| BUG-017 | Adicionar EPI não tem ação nem foco por teclado | Funcional (formulário) | Baixa | P3 | `tests/ui/test_form_controls.py::test_add_epi_adds_another_epi_block` |
| BUG-018 | Paginação inconsistente em casos-limite | Contrato da API | Baixa | P3 | `tests/api/test_validation.py::test_pagination_beyond_last_page_returns_empty_data` |
| BUG-019 | JSON malformado devolve 500 em vez de 400 | Tratamento de erro | Baixa | P3 | `tests/api/test_validation.py::test_malformed_json_returns_400` |
| BUG-020 | CORS inválido (*,*) e POST text/plain aceito | Segurança | Baixa | P3 | `tests/security/test_security.py::test_cors_allow_origin_is_single_value` |
| BUG-021 | Sem cabeçalhos de segurança e com x-powered-by | Segurança | Baixa | P3 | `tests/security/test_security.py::test_security_headers_present` |
| BUG-023 | Obrigatórios aceitam só espaços | Validação (tela) | Baixa | P3 | `tests/ui/test_form_validation.py::test_required_fields_reject_whitespace_only` |
| BUG-025 | CA aceita símbolos | Validação | Baixa | P3 | `tests/api/test_validation.py::test_create_rejects_symbols_in_ca_number` |
| BUG-026 | Bloco "A etapa está concluída?" cobre cards da listagem | Layout | Baixa | P3 | `tests/ui/test_navigation_controls.py::test_step_block_does_not_overlap_the_listing` |
| BUG-027 | Navegação e controles sem efeito | Funcional (interface) | Baixa | P3 | `tests/ui/test_navigation_controls.py::test_navigation_control_reacts_to_click` |
| BUG-029 | Códigos de EPI gravados com grafia e acentuação inconsistentes | Qualidade de dado / contrato da API | Baixa | P3 | `tests/ui/test_epi_codes.py::test_saved_epi_code_is_an_ascii_slug` |

Todos os testes automatizados são `xfail(strict=True)` com o ID do defeito na razão (no BUG-029, só os 3 casos que quebram a regra; os outros 2 passam e servem de controle); os testes extras de cada defeito estão na entrada dele (sem caminho, no mesmo arquivo do teste da tabela). Todo "esperado" é inferência (não há documentação do sistema); premissas em `plano-de-testes.md`, seção 2.

---

## Prioridade P1

### BUG-001 — Checkbox não usa EPI grava usesEpi invertido (Alta, P1)

1. "Adicionar Funcionário", preencher os obrigatórios, marcar "O trabalhador não usa EPI." e salvar.
2. Repetir sem marcar (com CA preenchido) e ler os dois por `?id=`.

- **Esperado:** marcado grava `usesEpi: false`; desmarcado, `true` (premissa 1).
- **Obtido:** marcado grava `true` e `caNumber` vazio; desmarcado, `false`. Nenhum caminho pela tela grava o valor certo.
- **Evidência:** [BUG-001](evidencias/BUG-001-usesepi-invertido.txt), [print](evidencias/ui/BUG-001.png), [vídeo](evidencias/ui/BUG-001.mp4). **Teste:** `test_uses_epi_flag_matches_checkbox` (os dois estados).

### BUG-002 — API expõe CPF, RG e nascimento sem autenticação (Alta, P1)

1. `POST /employees` com registro sintético.
2. `GET /employees/<id>` e `GET /employees?id=<id>`, sem credencial.

- **Esperado (premissa 8; o enunciado não exige autenticação):** 401/403, ou ao menos CPF mascarado ou omitido.
- **Obtido:** 200 nas duas rotas, com CPF de 11 dígitos igual ao enviado, RG e nascimento completos.
- **Impacto:** dado pessoal exposto a qualquer visitante, sem minimização (LGPD, art. 6º, III e VII, e art. 46); a exposição é do mecanismo (sem prova de que registros de terceiros sejam reais). Alta/P1 somada à escrita anônima (BUG-004); mesma causa do BUG-003 e do BUG-004.
- **Evidência:** [BUG-002](evidencias/BUG-002-api-expoe-pii-sem-autenticacao.txt). **Testes:** `tests/security/test_security.py::test_record_does_not_expose_full_cpf`, `::test_list_requires_authentication` (`?id=` próprio; afirma só status e contagem).

### BUG-003 — Listagem exibe o CPF completo no card (Alta, P1)

1. Criar um registro pela API, abrir a listagem e ler o CPF só no card próprio.

- **Esperado:** CPF mascarado ou parcial. **Obtido:** os 11 dígitos, sem asterisco, iguais ao gravado; a tela mostra o CPF de todos a quem abrir a página.
- **Evidência:** [BUG-003](evidencias/BUG-003-listagem-cpf-completo.txt), [print](evidencias/ui/BUG-003.png), [vídeo](evidencias/ui/BUG-003.mp4). **Teste:** `test_listing_card_masks_cpf`.

### BUG-004 — API cria, altera e apaga registros sem autenticação (Alta, P1)
1. Sem credencial: `POST /employees`; `PUT /employees/<id>` com outro corpo completo (e `PATCH` com uma chave); `DELETE`; ler por `?id=` após cada um.

- **Esperado (premissa 8; o enunciado pede explorar segurança e privacidade da API):** 401/403 em toda escrita.
- **Obtido:** 201 no POST, 200 no PUT, PATCH e DELETE, com alteração e remoção confirmadas. Token inválido em `Authorization` não muda nada, e o preflight não lista `Authorization` em `allow-headers`. Sem noção de dono: um anônimo altera e apaga o registro de outro. Terceiros não foram tocados; o alcance sobre eles é inferência.
- **Impacto:** integridade e disponibilidade dos dados pessoais sem controle (LGPD, art. 46); pré-condição do BUG-005.
- **Evidência:** [BUG-004](evidencias/BUG-004-escrita-sem-autenticacao.txt). **Testes:** `test_create_requires_authentication`, `test_update_requires_authentication`, `test_delete_requires_authentication` (só status; persistência confirmada pelo script).

### BUG-005 — Registro sem state.employee deixa a listagem em branco (Alta, P1)
A tela não tolera registro malformado, e a API o aceita (BUG-004, BUG-011; padrão do json-server). Efeito global: criar, abrir uma vez, apagar logo.

1. `POST /employees` com `{"qa":"QA-AUTO-manual","state":{}}` (marcador na raiz para achar a sobra); abrir a listagem uma vez; apagar.

- **Esperado:** a listagem ignora o registro, ou a API o rejeita.
- **Obtido:** POST 201; a página desmonta (`#root` sem filhos, sem "Adicionar" nem contador), com `TypeError: Cannot read properties of undefined (reading 'employee')` no console (a evidência de 03/11 registrou `reading 'isActive'`, sem anotar o payload). Vale para todo visitante enquanto o registro existir (inferência: GET anônimo; não medido com um segundo cliente).
- **Impacto:** fluxo principal inutilizável para todos por 1 POST anônimo; sem perda de dado, recuperável com DELETE. Ocorreu de fato em 04/11 (registro só com `{"id"}`, de origem não identificada, deixou a listagem em branco para todos até ser removido); um POST de corpo vazio, sem autenticação, cria esse formato (num acidente de verificação, tela em branco por segundos; apagado, sem reprodução controlada).
- **Evidência:** [BUG-005](evidencias/BUG-005-listagem-em-branco.txt) (03/11; reexecutada em 04/11, mesmo efeito). **Teste:** manual, por decisão: cada CI deixaria a tela em branco para terceiros.

---

## Prioridade P2

### BUG-006 — Selects exibem padrão que não é gravado ao salvar (Média, P2)

1. Abrir o formulário (selects mostram "Cargo 01", "Ativid 01", "Capacete de segurança"), preencher o resto sem tocar neles e salvar; ler por `?id=`.

- **Esperado:** gravar o exibido ou exigir escolha (premissa 2).
- **Obtido:** `role` vazio; `activity` e `epi` ausentes. Outra opção grava, mas escolher a já exibida ("Cargo 01") ainda grava `role: ""` (reproduzido à mão pelo Patrick em 03/11, `QA-AUTO-P1-006b`).
- **Evidência:** [BUG-006](evidencias/BUG-006-selects-padrao-nao-gravado.txt), [print](evidencias/ui/BUG-006.png), [vídeo](evidencias/ui/BUG-006.mp4). **Teste:** `test_default_selects_are_saved_as_displayed`.

### BUG-007 — Anexo do ASO não é enviado nem persistido (Média, P2)

1. Escolher um `.pdf` sintético em "Atestado de Saúde Ocupacional (opcional)" (o nome aparece), salvar observando a rede e ler por `?id=`.

- **Esperado:** arquivo enviado ou referenciado (premissa 3; pode ser recurso não implementado).
- **Obtido:** um único POST `application/json`, sem multipart, e o registro sem referência ao arquivo; o usuário acredita que anexou.
- **Evidência:** [BUG-007](evidencias/BUG-007-aso-nao-enviado.txt), [print](evidencias/ui/BUG-007.png), [vídeo](evidencias/ui/BUG-007.mp4). **Teste:** `test_aso_file_is_persisted`.

### BUG-008 — CPF aceito sem validação de conteúdo (Média, P2)

1. `POST` com `cpf: "abcdefghijk"` (e letras pela tela).
2. `POST` com 11 dígitos e dígito verificador errado.

- **Esperado:** 400/422 (premissa 4). **Obtido:** 201 nos dois, gravados como enviados; sem unicidade de CPF.
- **Evidência:** [BUG-008](evidencias/BUG-008-cpf-sem-validacao.txt). **Testes:** `test_create_rejects_invalid_cpf_checksum`, `test_create_rejects_cpf_with_letters`; `tests/ui/test_form_validation.py::test_cpf_field_rejects_letters`.

### BUG-009 — CPF digitado com máscara é truncado sem aviso (Média, P2)

1. No CPF (`maxlength=11`), digitar tecla a tecla um CPF com pontos e traço (14 caracteres), salvar e ler por `?id=`.

- **Esperado:** gravar os 11 dígitos ou avisar.
- **Obtido:** corta nos 11 primeiros caracteres (perde os dois últimos dígitos e o traço), sem aviso; CPF gravado incompleto. Com 11 caracteres grava normalmente.
- **Evidência:** [BUG-009](evidencias/BUG-009-cpf-mascarado-truncado.txt), [print](evidencias/ui/BUG-009.png), [vídeo](evidencias/ui/BUG-009.mp4). **Teste:** `test_formatted_cpf_is_not_silently_truncated`.

### BUG-010 — Data de nascimento sem validação de intervalo (Média, P2)

1. API: `POST` com `birthDay: "2099-12-31"`.
2. Tela: no `type=date` (sem `min` nem `max`), salvar 2099-12-31 e 0001-01-01.

- **Esperado:** rejeitar data futura e idade implausível (premissa 5).
- **Obtido:** 201 na API e gravação nos 4 casos da tela. Caso extremo: `14/04/275760` foi gravado como `birthDay: "275760-04-14"` (`QA-AUTO-P1-001a`, lido por `?state.employee.name=`); sem `max`, o Chrome vai até o ano 275760 (limite do `Date` do JavaScript), e o valor quebra quem consome o dado (idade, relatório, exportação).
- **Evidência:** [BUG-010](evidencias/BUG-010-data-nascimento-sem-intervalo.txt), [print do ano de 6 dígitos](evidencias/ui/BUG-010-ano-6-digitos.png). **Testes:** `test_create_rejects_future_birth_date` (`2099-12-31` e `275760-04-14`); `tests/ui/test_form_validation.py::test_birth_date_rejects_future` (só 2099-12-31).
- **Fonte (caso extremo):** sessão exploratória do Patrick (03/11).

### BUG-011 — API não valida schema, tipos nem campos extras (Média, P2)

Todo corpo mantém `state.employee` (ver BUG-005).

1. `POST` só com `name`.
2. `POST` com `role: "Cargo 99"`, `epi: "nao-existe"` ou `isActive: "false"` (texto), um por POST.
3. `POST` com o campo extra `isAdmin: true`.
4. `PUT` só com `name` em registro próprio.

- **Esperado (premissa 6; a validação pode existir só na tela; domínio inferido das opções da tela):** 400/422 em 1 a 3, extras descartados, PUT incompleto rejeitado.
- **Obtido:** 201 em todos, gravados como enviados (inclusive `isAdmin`); o PUT dá 200 e os campos não enviados somem. Por inferência, `PUT {}`, `PUT {"foo":"bar"}` e `PATCH {"state":null}` disparariam o BUG-005 (não executados, pelo efeito global).
- **Evidência:** [BUG-011](evidencias/BUG-011-api-sem-schema.txt). **Testes:** `test_create_rejects_missing_required_fields`, `test_create_rejects_out_of_domain_values`, `test_create_rejects_unknown_fields`, `test_put_rejects_missing_required_fields`.

### BUG-012 — Adicionar outra atividade salva e fecha o formulário (Média, P2)

1. Preencher o formulário, clicar em "Adicionar outra atividade" e ver se fechou e se há registro.

- **Esperado:** abrir outro bloco de atividade (premissa 10).
- **Obtido:** o botão é `type=submit` dentro do form: salva, fecha e cria 1 registro.
- **Evidência:** [BUG-012](evidencias/BUG-012-adicionar-atividade-salva.txt), [print](evidencias/ui/BUG-012.png), [vídeo](evidencias/ui/BUG-012.mp4). **Teste:** `test_add_another_activity_does_not_submit`.

### BUG-013 — Listagem busca dados em paralelo ao POST e fica velha (Média, P2)
1. Salvar um cadastro observando a rede e ver se o card aparece sem recarregar; repetir 4 vezes.

- **Esperado:** a listagem é buscada depois de o POST terminar.
- **Obtido:** o `GET /employees` sai junto com o POST; lista velha em 1 de 4 (indicativo), certa ao recarregar. À mão (04/11): contador parado sem F5 na 1ª tentativa, POST e GET juntos (33 ms). A forma "nenhum GET depois do POST, lista sempre velha" foi refutada; este é o defeito reformulado.
- **Evidência:** [BUG-013](evidencias/BUG-013-listagem-busca-paralela.txt), [print](evidencias/ui/BUG-013.png), [vídeo](evidencias/ui/BUG-013.mp4). **Teste:** `test_listing_refetch_happens_after_post_completes` (só a ordem de rede, constante).

### BUG-024 — Enter descarta o cadastro sem salvar (Média, P2)

1. Preencher todo o "+ Adicionar Funcionário" e apertar Enter no Nº do CA (ou em Nome), sem clicar em "Salvar".
2. Olhar a rede e buscar o nome exato.

- **Esperado:** Enter salva como "Salvar" ou não faz nada; nunca descarta em silêncio (premissa 2).
- **Obtido:** o form fecha, nenhum POST sai e nada é gravado (3 de 3). Causa provável: o primeiro `type=submit` é a seta de voltar, sem `type="button"`. Contorno: clicar em "Salvar".
- **Evidência:** [BUG-024](evidencias/BUG-024-enter-descarta-cadastro.txt), [print](evidencias/ui/BUG-024.png), [vídeo](evidencias/ui/BUG-024.mp4) (da checagem de cobertura de 03/11). **Teste:** `test_enter_in_text_field_does_not_discard_the_form`.

### BUG-028 — Listagem mostra só os primeiros cards e não rola (Média, P2)
P2: o usuário não alcança a maioria dos funcionários, e o contorno só vale com poucos ativos.

1. Abrir `/` (com ou sem "Ver apenas ativos") e comparar os cards visíveis com "Ativos X/Y".
2. Girar a roda sobre a lista; tentar PageDown, End, ArrowDown, Space e Tab.

- **Esperado:** a lista rola (ou pagina) e todo card fica ao alcance.
- **Obtido:**
  - À mão (Patrick, MacBook, 03/11), "Ativos 10/37": 3 cards visíveis, roda sem efeito.
  - O DOM tem todos (39, ou 9–10 com filtro); visíveis: 4 em 1470x956, 3 em 1366x768, 6 em 1920x1080, 3 em 1470x840 com filtro (≈ viewport real do MacBook).
  - Contêiner com `height` = viewport − 284 px e `overflow-y: hidden` (`scrollHeight` 1109–1207 px com 9–10 cards, 4005–4103 px com 39; `clientHeight` 672 px); nada acima rola.
  - Roda, toque, teclas e arrastar a seleção não mudam o `scrollTop`; Tab não foca cards; só script rola.
  - Cards novos entram na área cortada (0 de 6 visíveis na medição).
  - Contorno: zoom-out (1470x840, 9 ativos: 90% → 4, 75% → 6, 67% → 8, 50% → todos); com 39 cards, nem 25% basta (29).
- **Evidência:** [print](evidencias/ui/BUG-028-listagem-cortada.png), [vídeo](evidencias/ui/BUG-028-listagem-cortada.mp4) (1470x840, "Ativos 16/45", 3 de 16 visíveis, roda e PageDown/End sem efeito; terceiros ocultados por `█████`). **Teste:** `test_every_listing_card_is_reachable_by_scrolling` (1470x840, roda real; o último de 12 cards próprios tem de ficar visível).
- **Fonte:** sessão exploratória do Patrick (03/11). Ver BUG-026 (sobrepõe 11 a 37 px de dois cards).

---

## Prioridade P3 (severidade Baixa)

### BUG-014 — PATCH em state apaga os campos não enviados

1. `POST` de registro completo (11 campos de `build_employee`); `PATCH /employees/<id>` com `{"state":{"employee":{"isActive":false}}}`; `GET /employees/<id>`.

- **Esperado (premissa 7; JSON Merge Patch, RFC 7396):** os outros campos permanecem, ou o PATCH é rejeitado.
- **Obtido:** só `isActive` sobra; somem name, gender, cpf, birthDay, rg, role, usesEpi, activity, epi e caNumber. É a mescla rasa documentada do json-server v1; PATCH na raiz preserva `state.employee`. Rebaixado de Média/P2: comportamento documentado, "esperado" de uma só premissa, sem dano demonstrado.
- **Evidência:** [BUG-014](evidencias/BUG-014-patch-apaga-campos.txt). **Teste:** `test_patch_preserves_unsent_fields`.

### BUG-016 — Select de EPI volta ao padrão ao digitar o CA

1. Escolher "Luvas descartáveis", digitar o CA e olhar o select.

- **Esperado:** manter o EPI escolhido. **Obtido:** volta a mostrar "Capacete de segurança"; o valor gravado segue o escolhido (2 de 2, numa só ordem de preenchimento).
- **Evidência:** [BUG-016](evidencias/BUG-016-select-epi-volta-ao-padrao.txt), [print](evidencias/ui/BUG-016.png), [vídeo](evidencias/ui/BUG-016.mp4). **Teste:** `test_epi_select_keeps_choice_after_typing_ca`.

### BUG-017 — Adicionar EPI não tem ação nem foco por teclado

1. Com "não usa EPI" desmarcado, clicar em "Adicionar EPI" e contar os selects de EPI.

- **Esperado:** novo bloco de EPI. **Obtido:** nenhum bloco nem requisição; é um `span` sem `tabindex` nem `role`, fora do Tab.
- **Evidência:** [BUG-017](evidencias/BUG-017-adicionar-epi-inerte.txt), [print](evidencias/ui/BUG-017.png), [vídeo](evidencias/ui/BUG-017.mp4). **Teste:** `test_add_epi_adds_another_epi_block` (teclado é acessibilidade, só observação).

### BUG-018 — Paginação inconsistente em casos-limite

1. Com registro próprio, `GET /employees?id=<id>&_page=999&_per_page=1` (e `_page=2`).

- **Esperado (boa prática REST):** `data` vazio além da última página e objeto paginado coerente.
- **Obtido:** `_page=2` e `_page=999` devolvem a última página (também com `_per_page=10`); `_page=0` ou `abc` devolve array puro; `_per_page=-1` devolve `pages=-1`, `last=-1`, `items=1` e `data` vazio. Comportamento da biblioteca (json-server v1, `x-powered-by: tinyhttp`).
- **Evidência:** [BUG-018](evidencias/BUG-018-paginacao-limites.txt) (só `_page=2` e `_page=999`). **Teste:** `test_pagination_beyond_last_page_returns_empty_data` (só `_page=2`; os demais manuais).

### BUG-019 — JSON malformado devolve 500 em vez de 400

1. `POST /employees` com corpo `not json` e `Content-Type: application/json` (nunca corpo vazio).

- **Esperado:** 400.
- **Obtido:** 500 com a mensagem crua do parser (`Unexpected token o in JSON at position 1`; truncado, `Unexpected end of JSON input`), sem `Content-Type`; igual com `text/plain`, sem `Content-Type` e em `PATCH`; nada é criado. Provável padrão do json-server v1. Baixa: sem dado errado, sem stack trace nem caminho, contorno trivial.
- **Evidência:** [BUG-019](evidencias/BUG-019-json-malformado-500.txt). **Teste:** `test_malformed_json_returns_400`.

### BUG-020 — CORS inválido (*,*) e POST text/plain aceito
1. `OPTIONS /employees`; depois `POST` com `text/plain`.

- **Esperado:** origem com valor único; POST não JSON rejeitado.
- **Obtido:** toda resposta traz `access-control-allow-origin: *,*` (dois valores num header, inválido), qualquer que seja o `Origin`; no Chromium (04/11), `fetch` de outra origem é bloqueado (`The 'Access-Control-Allow-Origin' header contains multiple values '*,*'`): quebra clientes cross-origin legítimos, sem expor dado (a tela é same-origin). O POST `text/plain` (sem preflight) dá 201 e grava como JSON, mesmo de outra origem (o navegador só não lê a resposta).
- **Causa provável:** o json-server emite só `*`; `*,*` sugere dois emissores (configuração do ambiente). Aceitar `text/plain` é padrão dele; a correção é validar o `Content-Type` na frente. Ganho pequeno: a escrita já é anônima (BUG-004).
- **Evidência:** [BUG-020](evidencias/BUG-020-cors-invalido.txt). **Testes:** `test_cors_allow_origin_is_single_value`, `test_create_rejects_non_json_content_type`.

### BUG-021 — Sem cabeçalhos de segurança e com x-powered-by

1. `HEAD /` e `HEAD /employees` (o teste usa `HEAD /employees` e `GET /`, só a página estática).

- **Esperado (OWASP Secure Headers):** CSP, HSTS, X-Frame-Options, X-Content-Type-Options e Referrer-Policy, sem `x-powered-by`.
- **Obtido:** os cinco ausentes e `x-powered-by: tinyhttp`; em `/`, `cache-control: no-store,public`. Padrão de json-server sem hardening: correção de implantação.
- **Evidência:** [BUG-021](evidencias/BUG-021-sem-cabecalhos-de-seguranca.txt). **Teste:** `test_security_headers_present`.

### BUG-023 — Obrigatórios aceitam só espaços
1. Salvar um cadastro com RG, CA ou CPF só de espaços (um por vez) e ler por nome exato.

- **Esperado:** rejeitar obrigatório só com espaços.
- **Obtido:** RG e CA com 3 espaços e CPF com 11 salvam, e a API grava os espaços (2 de 2); o `required` nativo só exige "não vazio". O CPF recusa 3 espaços e aceita 11 (valida só o tamanho, o que explica também o BUG-008 e o BUG-009), e as pontas não são aparadas (" QA-AUTO-P1-007 " gravado com os espaços). Família do BUG-008 e do BUG-011.
- **Evidência:** [BUG-023](evidencias/BUG-023-obrigatorios-aceitam-espacos.txt), [print](evidencias/ui/BUG-023.png), [vídeo](evidencias/ui/BUG-023.mp4). **Teste:** `test_required_fields_reject_whitespace_only` (um caso por campo).
- **Fonte (CPF com 3 e 11 espaços, pontas):** sessão exploratória do Patrick (03–04/11); o restante, checagem de cobertura de 03/11.

### BUG-025 — CA aceita símbolos

1. Em 1366x900, digitar `@!#$&&$#` em "Número do CA", salvar e ler por nome exato (ou por `?id=`, via API).

- **Esperado:** rejeitar (400/422, mensagem na tela) ou aceitar só dígitos (regra a confirmar).
- **Obtido:** nenhuma mensagem; `caNumber` gravado como `@!#$&&$#`; input `type=text` sem `pattern` nem `maxlength`; a API também aceita (201). Família do BUG-008 e do BUG-011, com campo e regra distintos.
- **Evidência:** [BUG-025](evidencias/BUG-025-ca-number-simbolos.txt), [print](evidencias/ui/BUG-025.png), [vídeo](evidencias/ui/BUG-025.mp4). **Testes:** `test_create_rejects_symbols_in_ca_number`; `tests/ui/test_form_validation.py::test_ca_number_field_rejects_symbols`.

### BUG-026 — Bloco "A etapa está concluída?" cobre cards da listagem

1. Em 1920x1080, com 8 cadastros criados pela API, medir o bloco (`position:absolute`, 278x62 px) e os cards, com a lista no início e no fim.

- **Esperado:** o bloco não cobrir a listagem.
- **Obtido:** cobre; o ícone de pontos de um card fica inteiro sob o bloco (`elementFromPoint` devolve o bloco). Varia com a lista e a área útil: à mão (04/11, zoom 100%) cobre a borda de um card e o topo do seguinte; com zoom reduzido, não cobre.
- **Evidência:** [print](evidencias/ui/BUG-026.png), [vídeo](evidencias/ui/BUG-026.mp4). **Teste:** `test_step_block_does_not_overlap_the_listing` (só geometria).

### BUG-027 — Navegação e controles sem efeito
Baixa; sobe para Média se o escopo exigir editar e excluir pela tela.

1. Em 1366x900, com 1 card próprio, clicar com ponteiro real em cada controle abaixo, medindo cursor, DOM, URL, requisições e menus.

- **Esperado:** algum efeito, ou não parecer clicável.
- **Obtido:** nenhum efeito (0 mutações, URL igual, 0 requisições, 0 menus):
  - **6 ícones da barra lateral:** `div` sem `role` nem `tabindex`, fora do Tab, com mãozinha; o 2º fica sempre ativo.
  - **"..." do card** (só o próprio): mãozinha, sem menu; não há como editar nem excluir pela tela.
  - **"Próximo passo":** mãozinha; nem clique nem Enter fazem nada.
  - **9 passos "ITEM 1":** mesmo rótulo nos 9 (pode ser provisório), sem clique, cursor padrão.
  - A mãozinha vem de `:hover { cursor: pointer }`; sem hover, `getComputedStyle(...).cursor` dá `auto`, o que esconde o problema.
- **Evidência:** barra lateral [print](evidencias/ui/BUG-027-barra-lateral.png), [vídeo](evidencias/ui/BUG-027-barra-lateral.mp4); "..." [print](evidencias/ui/BUG-027-pontinhos.png), [vídeo](evidencias/ui/BUG-027-pontinhos.mp4); "Próximo passo" [print](evidencias/ui/BUG-027-proximo-passo.png), [vídeo](evidencias/ui/BUG-027-proximo-passo.mp4); etapas [print](evidencias/ui/BUG-027-indicador-etapas.png), [vídeo](evidencias/ui/BUG-027-indicador-etapas.mp4). **Teste:** `test_navigation_control_reacts_to_click` (os quatro grupos). O "Próximo passo" antes constava só como observação (nota de estratégia e plano de testes).

### BUG-029 — Códigos de EPI gravados com grafia e acentuação inconsistentes

1. Salvar um cadastro com "Usa EPI" e ler `epi` na Response do `POST /employees` (DevTools); repetir nas 5 opções.

- **Esperado:** regra única e estável, ex.: slug ASCII minúsculo (`oculos-de-protecao`).
- **Obtido:**

  | Rótulo | Código gravado | Problema |
  |---|---|---|
  | Capacete de segurança | `capacete-de-segurança` | `ç` |
  | Luvas descartáveis | `luvas-descartaveis` | nenhum |
  | Óculos de proteção | `oculor-de-proteçao` | grafia ("oculor") e só o `ç` |
  | Calçado de Segurança | `calçado-de-segurança` | todos os acentos |
  | Protetor auditivo | `protetor-auditivo` | nenhum |

- **Impacto:** o código é o dado persistido e o contrato da API: quem consome (relatório, integração, `?epi=`) precisa reproduzir "oculor", e o `ç` exige URL-encoding e quebra comparações entre sistemas que normalizam de outro jeito (agrupar por EPI divergiria); a falta de regra sugere códigos digitados à mão. Baixa: nenhum fluxo da tela falha hoje.
- **Evidência:** [BUG-029](evidencias/BUG-029-codigos-epi-inconsistentes.txt) (registros do Patrick `6461`, `6c6b`, `d6f6`, `e01f`). **Teste:** `test_saved_epi_code_is_an_ascii_slug` (falha em 3 de 5; para "Óculos" exige o prefixo `oculos-`).
- **Fonte:** sessão exploratória do Patrick (04/11); tabela tirada do bundle de `/` e dos registros dele.

---

## Observações (não são defeitos)

- "CONCLUIDO" sem acento sob o 1º item do indicador, nos dois estados do switch "A etapa está concluída?"; sem impacto, e o enunciado não pede revisão de texto.
- "Ativid 01" a "Ativid 05" é nome provisório, mas consistente (select, valor gravado e card repetem o texto); o `S` de "Calçado de Segurança" é cosmético, pois o EPI é gravado por código (ex.: `protetor-auditivo`, `QA-AUTO-P1-006c`), cuja grafia é o BUG-029.
- Aba "Vite + React + TS": título do template, sem o nome do produto.
- O contador "Ativos X/Y" conta a base, não o filtro (15 → 8 cards, contador "Ativos 8/15"); comportamento pretendido desconhecido.
- Cadastro novo nasce inativo (mostra e grava `isActive: false`) e some do filtro de ativos; padrão "ativo" seria preferência de produto (ex-BUG-015, decisão do Patrick em 03/11).

## Observações do ambiente

- **Base volátil:** em 31/10 caiu de 3.698 para 2 registros em menos de 1 hora, sem ação nossa (compatível com `DELETE` anônimo; causa não demonstrável), e um registro próprio sumiu em segundos; por isso cada teste cria e apaga o próprio dado, e o teardown tolera 404.
- **`id` de tipo misto:** o servidor gera `id` de 4 hexadecimais, mas aceita e mantém o do cliente (inteiro ou texto). Em 02/11, quatro `QA-AUTO-E2` com `id` numérico (de um explorador, antes da regra) deram 404 na rota por id; em 03/11 restavam 2, com `id` string, apagados por `DELETE` comum (confirmado); os outros 2 sumiram sozinhos. "`id` inteiro inalcançável" não foi reproduzido nem refutado; os testes nunca usam `id` inteiro.
- **`id` vazio (04/11):** registro com `id` `""` e campos em branco, de origem não identificada; vira card vazio e a rota por id não o alcança.
- **Em aberto:** proxies cacheiam dados pessoais por `cache-control: public` (exigiria um proxy)? Há dado real na base, com qual base legal? Por isso terceiros são tratados como reais e só aparecem em agregados.
