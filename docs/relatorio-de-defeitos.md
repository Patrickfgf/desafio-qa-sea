# Relatório de defeitos

> **Status:** todo defeito abaixo foi verificado por automação (Selenium e requests). A verificação é de 03/11/2026, exceto BUG-001, BUG-006, BUG-007 e BUG-012, que vêm de uma verificação automatizada anterior, sem data registrada. A coluna "Reproduzido à mão" registra a reprodução manual, hoje **pendente** para todos (o que não for reproduzido sai do relatório, junto com o teste e a evidência). Nenhum defeito é afirmado como reproduzido à mão antes disso. BUG-023 e BUG-024 vêm da checagem de cobertura de 03/11/2026 e seguem a mesma regra.
>
> **Nota de cobertura:** as áreas do BUG-023 e do BUG-024 vieram da lista de áreas de um repositório público de 2025 (só os nomes das áreas) e foram exploradas do zero. O BUG-022 (título da aba) foi retirado: a área veio dessa mesma lista, e o único achado possível nela é o valor do título, que o outro repositório já confere.
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
| BUG-015 | Funcionário novo nasce Inativo por padrão | Funcional (tela → payload) | Baixa | P3 | `tests/cross/test_ui_vs_api.py::test_new_employee_defaults_to_active` | pendente |
| BUG-016 | Select de EPI volta ao padrão ao digitar o CA | Usabilidade | Baixa | P3 | `tests/ui/test_form_controls.py::test_epi_select_keeps_choice_after_typing_ca` | pendente |
| BUG-017 | Adicionar EPI não tem ação nem foco por teclado | Funcional (formulário) | Baixa | P3 | `tests/ui/test_form_controls.py::test_add_epi_adds_another_epi_block` | pendente |
| BUG-018 | Paginação inconsistente em casos-limite | Contrato da API | Baixa | P3 | `tests/api/test_validation.py::test_pagination_beyond_last_page_returns_empty_data` | pendente |
| BUG-019 | JSON malformado devolve 500 em vez de 400 | Tratamento de erro | Baixa | P3 | `tests/api/test_validation.py::test_malformed_json_returns_400` | pendente |
| BUG-020 | CORS inválido (*,*) e POST text/plain aceito | Segurança | Baixa | P3 | `tests/security/test_security.py::test_cors_allow_origin_is_single_value` | pendente |
| BUG-021 | Sem cabeçalhos de segurança e com x-powered-by | Segurança | Baixa | P3 | `tests/security/test_security.py::test_security_headers_present` | pendente |
| BUG-023 | Obrigatórios aceitam só espaços | Validação (tela) | Baixa | P3 | `tests/ui/test_form_validation.py::test_required_fields_reject_whitespace_only` | pendente |

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
- **Evidência:** [BUG-001](evidencias/BUG-001-usesepi-invertido.txt)
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
- **Evidência:** [BUG-003](evidencias/BUG-003-listagem-cpf-completo.txt) (CPF mascarado no arquivo).
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
- **Obtido:** `role` vazio e `activity`/`epi` ausentes. Escolhendo no select, o valor é gravado (contorno).
- **Evidência:** [BUG-006](evidencias/BUG-006-selects-padrao-nao-gravado.txt)
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
- **Evidência:** [BUG-007](evidencias/BUG-007-aso-nao-enviado.txt)
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
- **Evidência:** [BUG-009](evidencias/BUG-009-cpf-mascarado-truncado.txt)
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
- **Evidência:** [BUG-010](evidencias/BUG-010-data-nascimento-sem-intervalo.txt)
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
- **Evidência:** [BUG-012](evidencias/BUG-012-adicionar-atividade-salva.txt)
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
- **Evidência:** [BUG-013](evidencias/BUG-013-listagem-busca-paralela.txt)
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
- **Obtido:** o formulário fecha, a listagem volta, nenhuma requisição é enviada e nada é gravado (3 de 3 execuções). Causa provável: o primeiro botão `type=submit` do formulário é a seta de voltar, sem `type="button"`. Há contorno: clicar em "Salvar".
- **Evidência:** [BUG-024](evidencias/BUG-024-enter-descarta-cadastro.txt) (vem da checagem de cobertura de 03/11)
- **Teste automatizado:** `tests/ui/test_form_controls.py::test_enter_in_text_field_does_not_discard_the_form`.

---

## Defeitos de baixa prioridade (P3)

Severidade Baixa e prioridade P3 em todos; as premissas de "esperado" estão em `plano-de-testes.md`, seção 2. Sem passo a passo completo: cada item traz o que acontece, como ver, a evidência e o teste.

### BUG-015 — Funcionário novo nasce Inativo por padrão

Categoria: funcional (tela → payload). Salvar sem tocar no switch grava `isActive: false` e o card some com "Ver apenas ativos"; com o switch ligado funciona. Como ver: salvar um cadastro sem mexer no switch e ler `isActive` por `?id=` (interface, 03/11/2026).
Evidência: [BUG-015](evidencias/BUG-015-novo-nasce-inativo.txt). Teste: `tests/cross/test_ui_vs_api.py::test_new_employee_defaults_to_active`.

### BUG-016 — Select de EPI volta ao padrão ao digitar o CA

Categoria: usabilidade. Depois de escolher "Luvas descartáveis" e digitar o CA, o select volta a mostrar "Capacete de segurança"; o valor gravado continua o escolhido (2 de 2 execuções, numa só ordem de preenchimento). Como ver: escolher o EPI, digitar o CA, olhar o select (interface, 03/11/2026).
Evidência: [BUG-016](evidencias/BUG-016-select-epi-volta-ao-padrao.txt). Teste: `tests/ui/test_form_controls.py::test_epi_select_keeps_choice_after_typing_ca`.

### BUG-017 — Adicionar EPI não tem ação nem foco por teclado

Categoria: funcional (formulário). O clique em "Adicionar EPI" não cria outro bloco nem envia requisição; o elemento é um `span` sem `tabindex` nem `role`, fora da ordem de Tab. Como ver: com o checkbox "não usa EPI" desmarcado, clicar e contar os selects de EPI (interface, 03/11/2026).
Evidência: [BUG-017](evidencias/BUG-017-adicionar-epi-inerte.txt). Teste: `tests/ui/test_form_controls.py::test_add_epi_adds_another_epi_block` (o teclado é acessibilidade, só observação).

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
Evidência: [BUG-023](evidencias/BUG-023-obrigatorios-aceitam-espacos.txt). Teste: `tests/ui/test_form_validation.py::test_required_fields_reject_whitespace_only` (um caso por campo).

---

## Observações do ambiente

- **Base volátil.** Em 31/10 a base passou de 3.698 para 2 registros em menos de 1 hora, sem ação nossa. Compatível com um `DELETE` sem autenticação (BUG-004), mas a causa não é demonstrável. Um registro próprio também sumiu em segundos. Por isso cada teste cria e apaga o próprio dado, e o teardown tolera 404.
- **`id` de tipo misto.** O servidor gera `id` string de 4 hexadecimais, mas aceita `id` do cliente (inteiro ou texto) e mantém o tipo. Registro com `id` inteiro aparece em `?id=` e na listagem, mas `GET`, `PUT`, `PATCH` e `DELETE` em `/employees/<id>` dão 404. Os testes nunca criam `id` inteiro. Os 4 órfãos abaixo foram criados de propósito por um explorador para testar a H10, antes de a regra existir; ficaram inapagáveis pela API.
- **Quatro órfãos nossos.** Quatro registros `QA-AUTO-E2` com `id` inteiro, criados na fase exploratória (ver acima), ficaram inalcançáveis e inapagáveis pela API. Não há como removê-los por outra rota sem enumerar ids (proibido). O e-mail de entrega vai oferecer os ids ao dono do ambiente para remoção.
- **Dúvidas em aberto (não viram defeito sem reprodução).** (1) O `access-control-allow-origin: *,*` bloqueia leitura cross-origin num navegador? Exigiria uma página de outra origem. (2) Proxies cacheiam dados pessoais por causa de `cache-control: public`? Exigiria um proxy no caminho. (3) Há dado real na base e com qual base legal? Desconhecido; por isso os registros de terceiros são tratados como reais e só aparecem aqui em agregados.
