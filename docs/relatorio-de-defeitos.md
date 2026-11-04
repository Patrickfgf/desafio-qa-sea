# Relatório de defeitos

> **Status:** todo defeito abaixo foi verificado por automação (Selenium e requests). A verificação é de 03/11/2026, exceto BUG-001, BUG-006, BUG-007 e BUG-012, que vêm de uma verificação automatizada anterior, sem data registrada. A coluna "Reproduzido à mão" registra a reprodução manual, hoje **pendente** para todos (o que não for reproduzido sai do relatório, junto com o teste e a evidência). Nenhum defeito é afirmado como reproduzido à mão antes disso. BUG-023 e BUG-024 vêm da checagem de cobertura, e BUG-025 a BUG-028 da exploração, ambas de 03/11/2026; seguem a mesma regra, exceto o BUG-028, que o Patrick reproduziu à mão em 03/11/2026.
>
> **Numeração:** os ids BUG-015 e BUG-022 não são usados (retirados; o BUG-015 virou observação, ver "Observações").
>
> **Como as evidências foram geradas:** por scripts de verificação não versionados, que usam `support.evidence` e o mascaramento do repositório; as evidências de interface foram copiadas dos logs dessas verificações.

**Ambiente de todos os defeitos:** `https://analista-teste.seatecnologia.com.br/` (interface e `/employees`), 03/11/2026 (BUG-001, BUG-006, BUG-007 e BUG-012: verificação anterior, sem data), Chrome headless (interface) e `requests` (API). Base compartilhada: só registros sintéticos com nome `QA-AUTO-`, apagados em seguida. CPF mascarado (`123.***.***-09`) ou descrito, nunca em claro, nas evidências.

## Escalas

Severidade é o impacto técnico; prioridade é a urgência de negócio (as mesmas de `plano-de-testes.md`, seção 3.1).

| Severidade | Critério |
|---|---|
| Crítica | perda ou exposição de dados em larga escala, sem pré-condição |
| Alta | dado gravado ou exposto de forma errada em fluxo principal, ou controle de acesso ausente |
| Média | comportamento incorreto com contorno, ou efeito limitado a clientes da API |
| Baixa | cosmético, usabilidade, má prática sem dano demonstrado |

| Prioridade | Critério |
|---|---|
| P1 | corrigir primeiro: afeta todo cadastro ou expõe dados pessoais |
| P2 | corrigir na sequência: afeta parte dos usuários ou os clientes da API |
| P3 | pode esperar: baixo impacto no fluxo |

## Resumo (por prioridade)

| ID | Título | Categoria | Severidade | Prioridade | Automatizado | Reproduzido à mão |
|---|---|---|---|---|---|---|
| BUG-001 | Checkbox não usa EPI grava usesEpi invertido | Funcional (tela → payload) | Alta | P1 | `tests/cross/test_ui_vs_api.py::test_uses_epi_flag_matches_checkbox` | pendente |
| BUG-002 | API expõe CPF, RG e nascimento sem autenticação | Privacidade / LGPD | Alta | P1 | `tests/security/test_security.py::test_record_does_not_expose_full_cpf` | pendente |
| BUG-003 | Listagem exibe o CPF completo no card | Privacidade / LGPD | Alta | P1 | `tests/cross/test_ui_vs_api.py::test_listing_card_masks_cpf` | pendente |
| BUG-004 | API cria, altera e apaga registros sem autenticação | Segurança (controle de acesso) | Alta | P1 | `tests/security/test_security.py::test_create_requires_authentication` | pendente |
| BUG-005 | Registro sem state.employee deixa a listagem em branco | Funcional (listagem) | Alta | P1 | manual | pendente |
| BUG-006 | Selects exibem padrão que não é gravado ao salvar | Funcional (tela → payload) | Média | P2 | `tests/cross/test_ui_vs_api.py::test_default_selects_are_saved_as_displayed` | pendente |
| BUG-007 | Anexo do ASO não é enviado nem persistido | Funcional (tela → payload) | Média | P2 | `tests/cross/test_ui_vs_api.py::test_aso_file_is_persisted` | pendente |
| BUG-008 | CPF aceito sem validação de conteúdo | Validação | Média | P2 | `tests/api/test_validation.py::test_create_rejects_invalid_cpf_checksum` | pendente |
| BUG-009 | CPF digitado com máscara é truncado sem aviso | Validação (tela) | Média | P2 | `tests/ui/test_form_validation.py::test_formatted_cpf_is_not_silently_truncated` | pendente |
| BUG-010 | Data de nascimento sem validação de intervalo | Validação | Média | P2 | `tests/api/test_validation.py::test_create_rejects_future_birth_date` | pendente |
| BUG-011 | API não valida schema, tipos nem campos extras | Contrato da API | Média | P2 | `tests/api/test_validation.py::test_create_rejects_missing_required_fields` | pendente |
| BUG-012 | Adicionar outra atividade salva e fecha o formulário | Funcional (formulário) | Média | P2 | `tests/ui/test_form_controls.py::test_add_another_activity_does_not_submit` | pendente |
| BUG-013 | Listagem busca dados em paralelo ao POST e fica velha | Funcional (listagem) | Média | P2 | `tests/ui/test_form_controls.py::test_listing_refetch_happens_after_post_completes` | pendente |
| BUG-014 | PATCH em state apaga os campos não enviados | Contrato da API | Média | P2 | `tests/api/test_validation.py::test_patch_preserves_unsent_fields` | pendente |
| BUG-024 | Enter descarta o cadastro sem salvar | Funcional (formulário) | Média | P2 | `tests/ui/test_form_controls.py::test_enter_in_text_field_does_not_discard_the_form` | pendente |
| BUG-028 | Listagem mostra só os primeiros cards e não rola | Funcional (listagem) | Média | P2 | `tests/ui/test_navigation_controls.py::test_every_listing_card_is_reachable_by_scrolling` | sim (Patrick, 03/11) |
| BUG-016 | Select de EPI volta ao padrão ao digitar o CA | Usabilidade | Baixa | P3 | `tests/ui/test_form_controls.py::test_epi_select_keeps_choice_after_typing_ca` | pendente |
| BUG-017 | Adicionar EPI não tem ação nem foco por teclado | Funcional (formulário) | Baixa | P3 | `tests/ui/test_form_controls.py::test_add_epi_adds_another_epi_block` | pendente |
| BUG-018 | Paginação inconsistente em casos-limite | Contrato da API | Baixa | P3 | `tests/api/test_validation.py::test_pagination_beyond_last_page_returns_empty_data` | pendente |
| BUG-019 | JSON malformado devolve 500 em vez de 400 | Tratamento de erro | Baixa | P3 | `tests/api/test_validation.py::test_malformed_json_returns_400` | pendente |
| BUG-020 | CORS inválido (*,*) e POST text/plain aceito | Segurança | Baixa | P3 | `tests/security/test_security.py::test_cors_allow_origin_is_single_value` | pendente |
| BUG-021 | Sem cabeçalhos de segurança e com x-powered-by | Segurança | Baixa | P3 | `tests/security/test_security.py::test_security_headers_present` | pendente |
| BUG-023 | Obrigatórios aceitam só espaços | Validação (tela) | Baixa | P3 | `tests/ui/test_form_validation.py::test_required_fields_reject_whitespace_only` | pendente |
| BUG-025 | CA aceita símbolos | Validação | Baixa | P3 | `tests/api/test_validation.py::test_create_rejects_symbols_in_ca_number` | pendente |
| BUG-026 | Bloco "A etapa está concluída?" cobre cards da listagem | Layout | Baixa | P3 | `tests/ui/test_navigation_controls.py::test_step_block_does_not_overlap_the_listing` | pendente |
| BUG-027 | Navegação e controles sem efeito | Funcional (interface) | Baixa | P3 | `tests/ui/test_navigation_controls.py::test_navigation_control_reacts_to_click` | pendente |

Todos os testes automatizados são `xfail(strict=True)` com o ID do defeito na razão. Quando a tabela cita um teste, os demais do mesmo defeito estão na seção dele. Cada premissa de "esperado" abaixo é inferência (sem documentação do sistema); as premissas estão em `plano-de-testes.md`, seção 2.

---

## Prioridade P1

### BUG-001 — Checkbox não usa EPI grava usesEpi invertido

- **Categoria:** funcional (tela → payload). **Severidade:** Alta. **Prioridade:** P1.
- **Ambiente:** interface, verificação automatizada anterior (sem data registrada), Chrome headless.
- **Pré-condições:** lista aberta; registro de teste com nome `QA-AUTO-`.
- **Passos:**
  1. Clicar em "Adicionar Funcionário" e preencher os campos obrigatórios com dados fictícios.
  2. Marcar "O trabalhador não usa EPI." e salvar.
  3. Repetir sem marcar a opção (com CA preenchido).
  4. Ler cada registro com `GET /employees?id=<id>` e conferir `usesEpi`.
- **Esperado:** marcado grava `usesEpi: false`; desmarcado grava `true` (premissa 1).
- **Obtido:** marcado grava `true` e `caNumber` vazio; desmarcado grava `false`. Nenhum caminho pela tela grava o valor certo.
- **Evidência:** [BUG-001](evidencias/BUG-001-usesepi-invertido.txt) · [print](evidencias/ui/BUG-001.png) · [vídeo](evidencias/ui/BUG-001.mp4)
- **Teste automatizado:** `tests/cross/test_ui_vs_api.py::test_uses_epi_flag_matches_checkbox` (parametrizado nos dois estados).

### BUG-002 — API expõe CPF, RG e nascimento sem autenticação

- **Categoria:** privacidade / LGPD. **Severidade:** Alta. **Prioridade:** P1.
- **Ambiente:** `/employees`, 03/11/2026, `requests`.
- **Pré-condições:** registro de teste criado pela API. Nenhuma credencial.
- **Passos:**
  1. `POST /employees` com um registro sintético `QA-AUTO-` (sem `id`).
  2. `GET /employees/<id>` sem credencial.
  3. `GET /employees?id=<id>` sem credencial.
  4. Apagar o registro e confirmar por `?id=`.
- **Esperado:** 401/403 sem credencial, ou ao menos CPF mascarado ou omitido (premissa 8).
- **Obtido:** 200 com CPF de 11 dígitos, RG e data de nascimento completos, `cache-control: public` e `access-control-allow-origin: *,*`. A listagem completa serve o mesmo, inclusive inativos: nas medições agregadas, 7 de 7 e 11 de 11 registros traziam os três campos (a evidência abaixo mostra só o registro de teste; o CPF está mascarado no arquivo).
- **Evidência:** [BUG-002](evidencias/BUG-002-api-expoe-pii-sem-autenticacao.txt)
- **Testes automatizados:** `tests/security/test_security.py::test_record_does_not_expose_full_cpf`, `::test_list_requires_authentication` (usa `?id=` do registro próprio).
- **Impacto LGPD:** dado pessoal exposto a qualquer visitante, sem minimização (art. 6º, III e VII, e art. 46). Não há prova de que os registros de terceiros sejam reais; a exposição é do mecanismo.

### BUG-003 — Listagem exibe o CPF completo no card

- **Categoria:** privacidade / LGPD. **Severidade:** Alta. **Prioridade:** P1.
- **Ambiente:** interface, 03/11/2026, Chrome headless.
- **Pré-condições:** registro de teste criado pela API.
- **Passos:**
  1. Abrir a listagem.
  2. Localizar o card do registro `QA-AUTO-` (só o próprio).
  3. Ler o CPF mostrado.
- **Esperado:** CPF mascarado ou parcial no card.
- **Obtido:** os 11 dígitos aparecem sem nenhum asterisco, iguais ao CPF gravado.
- **Evidência:** [BUG-003](evidencias/BUG-003-listagem-cpf-completo.txt) · [print](evidencias/ui/BUG-003.png) · [vídeo](evidencias/ui/BUG-003.mp4) (CPF mascarado no arquivo).
- **Teste automatizado:** `tests/cross/test_ui_vs_api.py::test_listing_card_masks_cpf`.
- **Impacto LGPD:** a tela mostra o CPF de todos os cadastrados a quem abrir a página.

### BUG-004 — API cria, altera e apaga registros sem autenticação

- **Categoria:** segurança (controle de acesso). **Severidade:** Alta. **Prioridade:** P1.
- **Ambiente:** `/employees`, 03/11/2026, `requests`.
- **Pré-condições:** nenhuma credencial; registro de teste.
- **Passos:**
  1. `POST /employees` com registro sintético `QA-AUTO-`.
  2. `PUT /employees/<id>` com outro corpo completo `QA-AUTO-`.
  3. `DELETE /employees/<id>`.
  4. Confirmar por `?id=` que o registro sumiu.
- **Esperado:** 401/403 nas três escritas (premissa 8).
- **Obtido:** 201, 200 e 200. Qualquer cliente anônimo altera ou apaga qualquer registro (só o próprio foi tocado nos testes).
- **Evidência:** [BUG-004](evidencias/BUG-004-escrita-sem-autenticacao.txt)
- **Testes automatizados:** `tests/security/test_security.py::test_create_requires_authentication`, `::test_update_requires_authentication`, `::test_delete_requires_authentication`.
- **Impacto LGPD:** integridade e disponibilidade dos dados pessoais sem controle (art. 46). É o gatilho de baixo custo do BUG-005.

### BUG-005 — Registro sem state.employee deixa a listagem em branco

- **Categoria:** funcional (listagem), com origem em contrato da API (BUG-004 e BUG-011). **Severidade:** Alta. **Prioridade:** P1.
- **Ambiente:** interface e API, 03/11/2026, Chrome headless.
- **Pré-condições:** nenhuma. Defeito de efeito global: **não repetir sem necessidade** e apagar logo após uma única carga.
- **Passos:**
  1. `POST /employees` com `{"qa":"QA-AUTO-manual","state":{}}` (sem `id`; o marcador na raiz permite achar a sobra).
  2. Abrir a listagem uma única vez.
  3. Apagar o registro com `DELETE /employees/<id>` e confirmar por `?id=`.
- **Esperado:** a listagem ignora o registro malformado, ou a API o rejeita.
- **Obtido:** POST 201; a tela desmonta (corpo vazio, `#root` sem filhos, sem contador), com `TypeError ... reading 'isActive'` no console (a evidência registra 3 erros SEVERE, dois deles `TypeError` listados). A mesma evidência marca o botão "Adicionar" como visível no instante da checagem; a triagem o descreve sumindo depois. ⟪PATRICK: confirme na reprodução manual se o botão some e quantos erros aparecem⟫ Vale para todos os usuários enquanto o registro existir.
- **Evidência:** [BUG-005](evidencias/BUG-005-listagem-em-branco.txt) (da verificação automatizada de 03/11; não reexecutada para o relatório).
- **Teste automatizado:** manual, por decisão: cada execução do CI deixaria a tela em branco para terceiros, e o registro não carrega o prefixo `QA-AUTO-`.
- **Observação:** um POST com corpo vazio também cria um registro `{id}` (não verificado como gatilho da tela em branco).

---

## Prioridade P2

### BUG-006 — Selects exibem padrão que não é gravado ao salvar

- **Categoria:** funcional (tela → payload). **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** interface, verificação automatizada anterior (sem data registrada), Chrome headless.
- **Pré-condições:** registro de teste; nenhum select tocado.
- **Passos:**
  1. Abrir o formulário; os selects mostram "Cargo 01", "Ativid 01" e "Capacete de segurança".
  2. Preencher os demais campos sem abrir os selects e salvar.
  3. Ler o registro por `?id=`.
- **Esperado:** gravar o que a tela mostra, ou exigir escolha (premissa 2).
- **Obtido:** `role` vazio e `activity`/`epi` ausentes. Escolher outra opção no select grava o valor, mas clicar na opção que já aparece ("Cargo 01") continua gravando `role: ""` (reproduzido à mão pelo Patrick em 03/11, registro `QA-AUTO-P1-006b`): o valor exibido por padrão não é gravado nem quando o usuário o escolhe de propósito.
- **Evidência:** [BUG-006](evidencias/BUG-006-selects-padrao-nao-gravado.txt) · [print](evidencias/ui/BUG-006.png) · [vídeo](evidencias/ui/BUG-006.mp4)
- **Teste automatizado:** `tests/cross/test_ui_vs_api.py::test_default_selects_are_saved_as_displayed`.

### BUG-007 — Anexo do ASO não é enviado nem persistido

- **Categoria:** funcional (tela → payload). **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** interface, verificação automatizada anterior (sem data registrada), Chrome headless.
- **Pré-condições:** arquivo `.pdf` sintético pequeno.
- **Passos:**
  1. No formulário, escolher o arquivo em "Atestado de Saúde Ocupacional (opcional)"; o nome aparece.
  2. Preencher o restante e salvar, observando a rede.
  3. Ler o registro por `?id=`.
- **Esperado:** arquivo enviado ou referenciado (premissa 3; sem especificação, pode ser recurso não implementado).
- **Obtido:** um único POST `application/json` sem multipart; o registro não guarda referência ao arquivo, e o usuário acredita que anexou.
- **Evidência:** [BUG-007](evidencias/BUG-007-aso-nao-enviado.txt) · [print](evidencias/ui/BUG-007.png) · [vídeo](evidencias/ui/BUG-007.mp4)
- **Teste automatizado:** `tests/cross/test_ui_vs_api.py::test_aso_file_is_persisted`.

### BUG-008 — CPF aceito sem validação de conteúdo

- **Categoria:** validação. **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** `/employees`, 03/11/2026, `requests` (e interface para as letras).
- **Pré-condições:** registro sintético `QA-AUTO-`.
- **Passos:**
  1. `POST` com `cpf: "abcdefghijk"`.
  2. `POST` com CPF de 11 dígitos e dígito verificador errado.
  3. Apagar os registros e confirmar.
- **Esperado:** 400/422 (premissa 4).
- **Obtido:** 201 nos dois, gravados como enviados. Sem unicidade de CPF.
- **Evidência:** [BUG-008](evidencias/BUG-008-cpf-sem-validacao.txt)
- **Testes automatizados:** `tests/api/test_validation.py::test_create_rejects_invalid_cpf_checksum`, `::test_create_rejects_cpf_with_letters`; `tests/ui/test_form_validation.py::test_cpf_field_rejects_letters`.

### BUG-009 — CPF digitado com máscara é truncado sem aviso

- **Categoria:** validação (tela). **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** interface, 03/11/2026, Chrome headless.
- **Pré-condições:** nenhuma.
- **Passos:**
  1. No campo CPF (`maxlength=11`), digitar tecla a tecla um CPF com pontos e traço (14 caracteres).
  2. Salvar sem mensagem e abrir o registro por `?id=`.
- **Esperado:** gravar os 11 dígitos ou avisar.
- **Obtido:** o campo corta nos 11 primeiros caracteres, sem os dois últimos dígitos e o traço; nenhum aviso; o CPF gravado fica incompleto. Controle com 11 caracteres grava normalmente.
- **Evidência:** [BUG-009](evidencias/BUG-009-cpf-mascarado-truncado.txt) · [print](evidencias/ui/BUG-009.png) · [vídeo](evidencias/ui/BUG-009.mp4)
- **Teste automatizado:** `tests/ui/test_form_validation.py::test_formatted_cpf_is_not_silently_truncated`.

### BUG-010 — Data de nascimento sem validação de intervalo

- **Categoria:** validação. **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** `/employees` e interface, 03/11/2026.
- **Pré-condições:** registro sintético `QA-AUTO-`.
- **Passos:**
  1. API: `POST` com `birthDay: "2099-12-31"`.
  2. Interface: no campo `type=date` (sem `min` nem `max`), digitar 2099-12-31 e depois 0001-01-01, e salvar.
  3. Apagar os registros.
- **Esperado:** rejeitar data futura e idade implausível (premissa 5).
- **Obtido:** 201 na API e gravação nos 4 casos da interface, como digitado.
- **Caso extremo (sessão exploratória do Patrick, 03/11):** o campo aceita ano de 6 dígitos. Pela interface, `14/04/275760` foi persistido como `birthDay: "275760-04-14"` (registro `QA-AUTO-P1-001a`, lido por `?state.employee.name=`). Sem `max`, o `input type=date` do Chrome vai até o ano 275760, o limite do `Date` do JavaScript; nem a tela nem a API rejeitam, e um ano assim quebra quem consome o dado depois (cálculo de idade, relatório, exportação).
- **Evidência:** [BUG-010](evidencias/BUG-010-data-nascimento-sem-intervalo.txt) · [print do ano de 6 dígitos](evidencias/ui/BUG-010-ano-6-digitos.png)
- **Testes automatizados:** `tests/api/test_validation.py::test_create_rejects_future_birth_date`; `tests/ui/test_form_validation.py::test_birth_date_rejects_future` (só 2099-12-31).

### BUG-011 — API não valida schema, tipos nem campos extras

- **Categoria:** contrato da API. **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** `/employees`, 03/11/2026, `requests`.
- **Pré-condições:** registros sintéticos `QA-AUTO-`; todo corpo mantém `state.employee` (ver BUG-005).
- **Passos:**
  1. `POST` só com `name`.
  2. `POST` com `role: "Cargo 99"`, `epi: "nao-existe"` e `isActive: "false"` (texto).
  3. `POST` com campo extra `isAdmin: true`.
  4. `PUT` só com `name` em registro próprio e ler o resultado.
- **Esperado:** 400/422 em 1 a 3; campos desconhecidos descartados; PUT incompleto rejeitado (premissa 6).
- **Obtido:** 201 em todos, gravados como enviados (inclusive `isAdmin`); o PUT apaga todos os outros campos.
- **Evidência:** [BUG-011](evidencias/BUG-011-api-sem-schema.txt)
- **Testes automatizados:** `tests/api/test_validation.py::test_create_rejects_missing_required_fields`, `::test_create_rejects_out_of_domain_values`, `::test_create_rejects_unknown_fields`, `::test_put_rejects_missing_required_fields`.
- **Observação:** `PUT {}`, `PUT {"foo":"bar"}` e `PATCH {"state":null}` também removem `state.employee`, o que dispara o BUG-005; por isso ficam só como passo manual.

### BUG-012 — Adicionar outra atividade salva e fecha o formulário

- **Categoria:** funcional (formulário). **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** interface, verificação automatizada anterior (sem data registrada), Chrome headless.
- **Pré-condições:** formulário preenchido; nome `QA-AUTO-`.
- **Passos:**
  1. Preencher o formulário.
  2. Clicar em "Adicionar outra atividade".
  3. Conferir se o formulário fechou e se existe registro com o nome.
- **Esperado:** abrir outro bloco de atividade (premissa 10).
- **Obtido:** o botão é `type=submit` dentro do form: salva, fecha e cria 1 registro.
- **Evidência:** [BUG-012](evidencias/BUG-012-adicionar-atividade-salva.txt) · [print](evidencias/ui/BUG-012.png) · [vídeo](evidencias/ui/BUG-012.mp4)
- **Teste automatizado:** `tests/ui/test_form_controls.py::test_add_another_activity_does_not_submit`.

### BUG-013 — Listagem busca dados em paralelo ao POST e fica velha

- **Categoria:** funcional (listagem). **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** interface, 03/11/2026, Chrome headless.
- **Pré-condições:** nome `QA-AUTO-`; aba de rede observada.
- **Passos:**
  1. Salvar um cadastro novo, observando a rede.
  2. Verificar se o card aparece sem recarregar.
  3. Repetir 4 vezes.
- **Esperado:** a listagem é buscada depois do POST terminar.
- **Obtido:** o `GET /employees` sai junto com o POST, e a lista ficou velha em 1 de 4 tentativas da evidência (só indicativo). Recarregando, o card aparece.
- **Evidência:** [BUG-013](evidencias/BUG-013-listagem-busca-paralela.txt) · [print](evidencias/ui/BUG-013.png) · [vídeo](evidencias/ui/BUG-013.mp4)
- **Teste automatizado:** `tests/ui/test_form_controls.py::test_listing_refetch_happens_after_post_completes` (só a ordem de rede, que é constante).
- **Observação:** a forma literal "nenhum GET depois do POST, lista sempre velha" foi refutada; este é o defeito reformulado.

### BUG-014 — PATCH em state apaga os campos não enviados

- **Categoria:** contrato da API. **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** `/employees`, 03/11/2026, `requests`.
- **Pré-condições:** registro sintético completo.
- **Passos:**
  1. `POST` do registro completo.
  2. `PATCH /employees/<id>` com `{"state":{"employee":{"isActive":false}}}`.
  3. `GET /employees/<id>`.
- **Esperado:** os outros campos permanecem (mescla em profundidade) ou o PATCH é rejeitado (premissa 7).
- **Obtido:** só `isActive` sobra; `name`, `cpf` e os demais somem (merge raso, comportamento padrão do servidor; a tela não usa PATCH).
- **Evidência:** [BUG-014](evidencias/BUG-014-patch-apaga-campos.txt)
- **Teste automatizado:** `tests/api/test_validation.py::test_patch_preserves_unsent_fields`.

### BUG-024 — Enter descarta o cadastro sem salvar

- **Categoria:** funcional (formulário). **Severidade:** Média. **Prioridade:** P2.
- **Ambiente:** interface, checagem de cobertura de 03/11/2026, Chrome headless. **Pré-condições:** formulário preenchido com registro de teste `QA-AUTO-`.
- **Passos:** (1) abrir "+ Adicionar Funcionário" e preencher tudo; (2) com o cursor no campo Nº do CA (ou em Nome), apertar Enter, sem clicar em "Salvar"; (3) olhar a rede e conferir por nome exato se algo foi gravado.
- **Esperado:** Enter salva como o botão "Salvar", ou não faz nada; nunca descarta os dados em silêncio (premissa 2).
- **Obtido:** o formulário fecha, a listagem volta, nenhum POST é enviado e nada é gravado (3 de 3 execuções). Causa provável: o primeiro botão `type=submit` do formulário é a seta de voltar, sem `type="button"`. Há contorno: clicar em "Salvar".
- **Evidência:** [BUG-024](evidencias/BUG-024-enter-descarta-cadastro.txt) · [print](evidencias/ui/BUG-024.png) · [vídeo](evidencias/ui/BUG-024.mp4) (vem da checagem de cobertura de 03/11)
- **Teste automatizado:** `tests/ui/test_form_controls.py::test_enter_in_text_field_does_not_discard_the_form`.

### BUG-028 — Listagem mostra só os primeiros cards e não rola

- **Categoria:** funcional (listagem). **Severidade:** Média. **Prioridade:** P2 (o usuário não alcança a maioria dos funcionários pela tela; o contorno só vale com poucos ativos).
- **Ambiente:** interface, 03/11/2026, Chrome (à mão, MacBook) e Chrome headless (Selenium) em 1470x840, 1470x956, 1366x768 e 1920x1080. Sem especificação do sistema: o "esperado" é inferência.
- **Pré-condições:** base com mais cards do que cabem na área da lista (a base compartilhada já tem dezenas; o teste cria 12 registros `QA-AUTO-`).
- **Passos:**
  1. Abrir `/` e, opcionalmente, ligar "Ver apenas ativos".
  2. Olhar quantos cards aparecem no bloco "Funcionário(s)" e comparar com o contador "Ativos X/Y".
  3. Girar a roda do mouse sobre a lista; tentar também PageDown, End, ArrowDown, Space e Tab.
- **Esperado:** a lista rola (ou pagina) e todo card fica ao alcance do usuário.
- **Obtido:**
  - À mão (Patrick, 03/11), com 10 ativos ("Ativos 10/37"): só 3 cards aparecem e a roda do mouse não faz nada.
  - O DOM tem todos os cards (39, ou 9 a 10 com o filtro), mas só aparecem 4 em 1470x956, 3 em 1366x768 e 6 em 1920x1080; em 1470x840 com o filtro saem 3 inteiros, como no relato. A tela do MacBook é 1470x956, e com as barras do Chrome o viewport real fica perto de 1470x840.
  - O contêiner da lista tem `height` igual ao viewport menos 284 px e `overflow-y: hidden`; o `scrollHeight` é de 1109 a 1207 px (9 a 10 cards) ou de 4005 a 4103 px (39 cards) contra 672 px de `clientHeight`. Nenhum outro ancestral rola e a página inteira não rola.
  - Roda do mouse, gesto de toque, PageDown, End, ArrowDown, Space e arrastar a seleção além da borda não mudam o `scrollTop`; nenhum card recebe foco no Tab. Só `scrollTop` ou `scrollIntoView` feitos por script rolam o contêiner.
  - Efeito colateral: cards novos entram no fim da lista, justamente na área cortada; nos 6 registros criados na medição, nenhum ficou visível.
  - Contorno: zoom-out do Chrome (medido em 1470x840 com 9 ativos: 90% mostra 4 cards, 75% mostra 6, 67% mostra 8, 50% mostra todos). Sem o filtro, com 39 cards, nem 25% mostra tudo (29 visíveis): com a base inteira não há contorno.
- **Evidência:** [print](evidencias/ui/BUG-028-listagem-cortada.png) · [vídeo](evidencias/ui/BUG-028-listagem-cortada.mp4) (1470x840, "Ativos 16/45", 16 cards no DOM e 3 visíveis, 4 giros de roda e PageDown/End sem efeito; texto de terceiros ocultado por `█████`).
- **Teste automatizado:** `tests/ui/test_navigation_controls.py::test_every_listing_card_is_reachable_by_scrolling` (1470x840, roda do mouse real sobre a lista, afirma que o último de 12 cards próprios chega à área visível).
- **Fonte:** sessão exploratória do Patrick (03/11). **Reproduzido à mão:** sim (Patrick, 03/11).
- **Observação:** o bloco "A etapa está concluída?" sobrepõe 11 a 37 px de dois cards conforme o viewport (BUG-026).

---

## Defeitos de baixa prioridade (P3)

Severidade Baixa e prioridade P3 em todos; as premissas de "esperado" estão em `plano-de-testes.md`, seção 2. BUG-016 a BUG-023 não têm passo a passo completo: cada um traz o que acontece, como ver, a evidência e o teste. BUG-025 a BUG-027 trazem os passos.

### BUG-016 — Select de EPI volta ao padrão ao digitar o CA

Categoria: usabilidade. Depois de escolher "Luvas descartáveis" e digitar o CA, o select volta a mostrar "Capacete de segurança"; o valor gravado continua o escolhido (2 de 2 execuções, numa só ordem de preenchimento). Como ver: escolher o EPI, digitar o CA, olhar o select (interface, 03/11/2026).
Evidência: [BUG-016](evidencias/BUG-016-select-epi-volta-ao-padrao.txt) · [print](evidencias/ui/BUG-016.png) · [vídeo](evidencias/ui/BUG-016.mp4). Teste: `tests/ui/test_form_controls.py::test_epi_select_keeps_choice_after_typing_ca`.

### BUG-017 — Adicionar EPI não tem ação nem foco por teclado

Categoria: funcional (formulário). O clique em "Adicionar EPI" não cria outro bloco nem envia requisição; o elemento é um `span` sem `tabindex` nem `role`, fora da ordem de Tab. Como ver: com o checkbox "não usa EPI" desmarcado, clicar e contar os selects de EPI (interface, 03/11/2026).
Evidência: [BUG-017](evidencias/BUG-017-adicionar-epi-inerte.txt) · [print](evidencias/ui/BUG-017.png) · [vídeo](evidencias/ui/BUG-017.mp4). Teste: `tests/ui/test_form_controls.py::test_add_epi_adds_another_epi_block` (o teclado é acessibilidade, só observação).

### BUG-018 — Paginação inconsistente em casos-limite

Categoria: contrato da API. `_page=2` e `_page=999` com `_per_page=1` devolvem a última página em vez de `data` vazio; `_page=0` ou `abc` devolve array puro; `_per_page=-1` dá `pages` negativo. Como ver: `GET /employees?id=<id>&_page=999&_per_page=1` com registro próprio (03/11/2026, `requests`).
Evidência: [BUG-018](evidencias/BUG-018-paginacao-limites.txt). Teste: `tests/api/test_validation.py::test_pagination_beyond_last_page_returns_empty_data`.

### BUG-019 — JSON malformado devolve 500 em vez de 400

Categoria: tratamento de erro. O 500 vem com a mensagem crua do parser, sem `Content-Type`. Como ver: `POST /employees` com corpo `not json` e `Content-Type: application/json`; nada é criado (nunca usar corpo vazio) (03/11/2026, `requests`).
Evidência: [BUG-019](evidencias/BUG-019-json-malformado-500.txt). Teste: `tests/api/test_validation.py::test_malformed_json_returns_400`.

### BUG-020 — CORS inválido (*,*) e POST text/plain aceito

Categoria: segurança. `OPTIONS` com `Origin` externo devolve `access-control-allow-origin: *,*` (duplicado, inválido) e 204; o POST `text/plain` devolve 201 e grava como JSON. O efeito do `*,*` num navegador não foi observado. Como ver: `OPTIONS` e `POST text/plain` com registro `QA-AUTO-`, apagado depois (03/11/2026, `requests`).
Evidência: [BUG-020](evidencias/BUG-020-cors-invalido.txt). Testes: `tests/security/test_security.py::test_cors_allow_origin_is_single_value`, `::test_create_rejects_non_json_content_type`.

### BUG-021 — Sem cabeçalhos de segurança e com x-powered-by

Categoria: segurança. Faltam CSP, HSTS, X-Frame-Options, X-Content-Type-Options e Referrer-Policy, e há `x-powered-by: tinyhttp`; em `/`, `cache-control: no-store,public`. Como ver: `HEAD /` e `HEAD /employees`; nada é criado (03/11/2026, `requests`).
Evidência: [BUG-021](evidencias/BUG-021-sem-cabecalhos-de-seguranca.txt). Teste: `tests/security/test_security.py::test_security_headers_present`.

### BUG-023 — Obrigatórios aceitam só espaços

Categoria: validação (tela). RG com 3 espaços, CA com 3 espaços e CPF com 11 espaços salvam, e a API grava os espaços (2 de 2 execuções); o `required` nativo só exige "não vazio". Mesma família do BUG-008 e do BUG-011. Como ver: preencher o cadastro `QA-AUTO-` com um desses campos só de espaços, um caso por vez, e ler o registro por nome exato (checagem de cobertura de 03/11/2026).
Evidência: [BUG-023](evidencias/BUG-023-obrigatorios-aceitam-espacos.txt) · [print](evidencias/ui/BUG-023.png) · [vídeo](evidencias/ui/BUG-023.mp4). Teste: `tests/ui/test_form_validation.py::test_required_fields_reject_whitespace_only` (um caso por campo).

### BUG-025 — CA aceita símbolos

- **Categoria:** validação. **Severidade:** Baixa. **Prioridade:** P3.
- **Ambiente:** interface, 03/11/2026, Chrome headless (1366x900). Sem especificação do sistema: o "esperado" é inferência.
- **Passos:**
  1. Abrir o formulário e preencher um cadastro `QA-AUTO-` com dados fictícios.
  2. Digitar `@!#$&&$#` em "Número do CA" e salvar.
  3. Ler o registro por nome exato (ou `GET /employees?id=` do registro criado pela API).
- **Esperado:** rejeitar (400/422 na API, mensagem na tela) ou aceitar só dígitos (regra a confirmar com a especificação). Mesma família do BUG-008 e do BUG-011, mas campo e regra distintos.
- **Obtido:** nenhuma mensagem; `caNumber` gravado como `@!#$&&$#`. O input é `type=text`, sem `pattern` nem `maxlength`; a API aceita o mesmo valor (201).
- **Evidência:** [BUG-025](evidencias/BUG-025-ca-number-simbolos.txt) · [print](evidencias/ui/BUG-025.png) · [vídeo](evidencias/ui/BUG-025.mp4)
- **Testes automatizados:** `tests/api/test_validation.py::test_create_rejects_symbols_in_ca_number`; `tests/ui/test_form_validation.py::test_ca_number_field_rejects_symbols`.
- **Reproduzido à mão:** pendente.

### BUG-026 — Bloco "A etapa está concluída?" cobre cards da listagem

- **Categoria:** layout. **Severidade:** Baixa. **Prioridade:** P3.
- **Ambiente:** interface, 03/11/2026, Chrome headless (1920x1080). Sem especificação do sistema: o "esperado" é inferência.
- **Passos:**
  1. Abrir `/` em 1920x1080 com a lista cheia (8 cadastros `QA-AUTO-` criados pela API).
  2. Medir o retângulo do bloco "A etapa está concluída? Sim/Não" (`position:absolute` dentro do painel da listagem, 278x62 px) e o dos cards, com a lista rolada ao início e ao fim.
- **Esperado:** o bloco não cobrir a listagem.
- **Obtido:** o bloco cobre cards; a 1920x1080 o ícone de pontos de um card fica inteiramente sob o bloco (`elementFromPoint` devolve o bloco). Qual card é coberto depende do tamanho da lista.
- **Evidência:** [print](evidencias/ui/BUG-026.png) · [vídeo](evidencias/ui/BUG-026.mp4)
- **Teste automatizado:** `tests/ui/test_navigation_controls.py::test_step_block_does_not_overlap_the_listing` (lê só geometria, contagens).
- **Reproduzido à mão:** pendente.

### BUG-027 — Navegação e controles sem efeito

- **Categoria:** funcional (interface). **Severidade:** Baixa (sobe para Média se o escopo exigir editar e excluir pela tela). **Prioridade:** P3.
- **Ambiente:** interface, 03/11/2026, Chrome headless (1366x900). Sem especificação do sistema: o "esperado" é inferência.
- **Passos:** abrir `/` (com 1 card `QA-AUTO-` criado pela API, para os "..."), levar o ponteiro a cada controle abaixo e clicar com ponteiro real; medir cursor sob o ponteiro, mutações do DOM, URL, requisições novas e menus ou diálogos abertos.
- **Esperado:** algum efeito ao clicar (menu, tela, ação) ou, se o controle é decorativo, que não pareça clicável.
- **Obtido:** em todos os grupos, clique sem efeito (0 mutações, URL igual, 0 requisições, 0 menus ou diálogos):
  - **6 ícones da barra lateral:** `div` sem `role` nem `tabindex`, fora da ordem de Tab; mãozinha no hover. O 2º ícone continua sempre ativo, o destaque não acompanha o clique.
  - **"..." dos cards:** mãozinha no hover; nenhum menu nem modal; não há como editar nem excluir um funcionário pela interface. (Medido só no card `QA-AUTO-` nosso.)
  - **"Próximo passo":** mãozinha no hover; o clique não muda nada, e Enter com o botão focado também não.
  - **9 passos "ITEM 1" do indicador de etapas:** o rótulo é o mesmo nos 9 (esperado numeração distinta ou o nome da etapa; sem especificação, pode ser texto provisório); sem clique e sem mãozinha (cursor padrão).
- **Evidência:** barra lateral [print](evidencias/ui/BUG-027-barra-lateral.png) · [vídeo](evidencias/ui/BUG-027-barra-lateral.mp4); "..." [print](evidencias/ui/BUG-027-pontinhos.png) · [vídeo](evidencias/ui/BUG-027-pontinhos.mp4); "Próximo passo" [print](evidencias/ui/BUG-027-proximo-passo.png) · [vídeo](evidencias/ui/BUG-027-proximo-passo.mp4); indicador de etapas [print](evidencias/ui/BUG-027-indicador-etapas.png) · [vídeo](evidencias/ui/BUG-027-indicador-etapas.mp4).
- **Teste automatizado:** `tests/ui/test_navigation_controls.py::test_navigation_control_reacts_to_click` (parametrizado nos quatro grupos; um card próprio, sem ler dado de terceiros).
- **Observação:** o cursor de mão vem de regras CSS `:hover { cursor: pointer }`: sem o ponteiro sobre o elemento, `getComputedStyle(...).cursor` devolve `auto`, o que esconde o problema; com o hover, o cursor é `pointer`. O "Próximo passo" antes constava só como observação (nota de estratégia e plano de testes).
- **Reproduzido à mão:** pendente.

---

## Observações (não são defeitos)

Itens vistos na interface que não entram como defeito: sem impacto funcional ou sem especificação para dizer o que seria o correto.

- **"CONCLUIDO" sem acento:** o rótulo sob o 1º item do indicador aparece sem acento nos dois estados do switch "A etapa está concluída?". Sem impacto funcional; o enunciado não pede revisão de texto.
- **Opções "Ativid 01" a "Ativid 05" e "Calçado de Segurança":** "Ativid 0N" é nome provisório, mas consistente (select, valor gravado e card repetem o mesmo texto). "Calçado de Segurança" tem o S maiúsculo, diferente das outras quatro opções de EPI. É só cosmético: o EPI é gravado por um código próprio (ex.: `epi: "protetor-auditivo"`, registro `QA-AUTO-P1-006c`), não pelo texto exibido, então a grafia não afeta o dado.
- **Título da aba "Vite + React + TS":** é o título do template, sem o nome do produto. Sem impacto para o usuário.
- **Contador "Ativos X/Y" não acompanha o filtro "Ver apenas ativos":** com o filtro ligado, a lista passa de 15 para 8 cards e o contador segue "Ativos 8/15" (conta a base, não o filtro). O comportamento pretendido é desconhecido.
- **Cadastro novo nasce inativo:** o switch "O trabalhador está ativo ou inativo?" abre mostrando "Inativo" e grava `isActive: false`, então a tela mostra o que grava. O cadastro some do filtro "Ver apenas ativos" até o usuário ligar o switch. O comportamento pretendido não é especificado: padrão "ativo" seria preferência de produto, não defeito (ex-BUG-015, decisão do Patrick em 03/11 na reprodução manual).

---

## Observações do ambiente

- **Base volátil.** Em 31/10 a base passou de 3.698 para 2 registros em menos de 1 hora, sem ação nossa. Compatível com um `DELETE` sem autenticação (BUG-004), mas a causa não é demonstrável. Um registro próprio também sumiu em segundos. Por isso cada teste cria e apaga o próprio dado, e o teardown tolera 404.
- **`id` de tipo misto.** O servidor gera `id` string de 4 hexadecimais, mas aceita `id` do cliente (inteiro ou texto) e mantém o tipo. Em 02/11, quatro registros `QA-AUTO-E2` criados com `id` numérico por um explorador (para testar a H10, antes de a regra existir) responderam 404 na rota por id. Em 03/11 os 2 que restavam tinham `id` string e foram apagados por `DELETE` comum; "`id` inteiro inalcançável" não foi reproduzido nem refutado depois. Os testes nunca criam `id` inteiro.
- **Órfãos `QA-AUTO-E2` resolvidos.** Dos quatro registros citados acima, só 2 restavam em 03/11, ambos com `id` string; um `DELETE /employees/<id>` comum os apagou (confirmado por `?id=` e pela contagem). Os outros 2 sumiram sem ação nossa (base volátil). Detalhe em `work/orfaos/pesquisa.md` (fora do repositório).
- **Dúvidas em aberto (não viram defeito sem reprodução).** (1) O `access-control-allow-origin: *,*` bloqueia leitura cross-origin num navegador? Exigiria uma página de outra origem. (2) Proxies cacheiam dados pessoais por causa de `cache-control: public`? Exigiria um proxy no caminho. (3) Há dado real na base e com qual base legal? Desconhecido; por isso os registros de terceiros são tratados como reais e só aparecem aqui em agregados.
