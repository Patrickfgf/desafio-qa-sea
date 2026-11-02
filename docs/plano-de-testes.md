# Plano de testes

Alvo: sistema de cadastro de trabalhadores para segurança do trabalho, com interface web (cadastro em etapas e listagem) e API REST em `/employees`. Não há documentação formal; este plano parte do comportamento observado.

> **Status: rascunho.** A coluna "Decisão proposta" do mapa de risco (seção 3) é uma proposta, à espera do corte de quem assina o plano. A escala de severidade da seção 3.1 também.

## 1. Escopo

**Dentro do escopo**

- Interface web em `https://analista-teste.seatecnologia.com.br/`: listagem, filtro "Ver apenas ativos", formulário de cadastro (campos, selects, checkbox "não usa EPI", anexo de ASO, botões).
- API `https://analista-teste.seatecnologia.com.br/employees`: GET, POST, PUT, PATCH, DELETE, HEAD, OPTIONS; filtros, ordenação e paginação da coleção.
- Cruzamento interface × API: o que a tela mostra e envia contra o que a API guarda e devolve.
- Segurança e privacidade (LGPD) demonstráveis por requisição e resposta: autenticação, exposição de dados pessoais, CORS, cabeçalhos, tratamento de erro.
- Automação dos fluxos de maior risco (seção 5).

**Fora do escopo** (por regra de engajamento ou por tempo)

- Carga, estresse, força bruta, enumeração de ids e varredura de outros caminhos, hosts ou portas. O ambiente é compartilhado.
- Injeção ativa (SQL, NoSQL, XSS, path traversal) e qualquer payload executável. As sondas são texto inerte (`<b>qa</b>`, aspas, emoji, texto longo).
- TLS e DNS; alteração ou remoção de registro de terceiros.
- Outros navegadores e mobile: só Chrome headless. Acessibilidade e teclado: no máximo observações.

## 2. Premissas e dúvidas

Sem documentação, todo "comportamento esperado" abaixo é **inferência** (rótulos da tela, nomes de campo, boa prática). Cada achado do relatório diz qual premissa o sustenta.

**Premissas**

1. Marcar "O trabalhador não usa EPI." deveria gravar `usesEpi: false`.
2. O que a tela mostra é o que o formulário grava (um select que exibe "Cargo 01" deveria gravar "Cargo 01" ou exigir escolha).
3. O campo "Atestado de Saúde Ocupacional (opcional)", com arquivo escolhido, deveria enviar ou referenciar o arquivo.
4. CPF tem 11 dígitos com dígito verificador válido, tipo texto, formato único.
5. Data de nascimento não é futura e a idade é plausível para um trabalhador.
6. A API deveria validar forma, tipos, valores permitidos e obrigatórios (400/422) e descartar campos desconhecidos. A validação poderia existir só na tela; sem contrato, não dá para afirmar.
7. Um PATCH parcial em `state` deveria mesclar em profundidade ou ser rejeitado.
8. Ler dados pessoais e escrever exigem autenticação, e a listagem traz o mínimo necessário (LGPD, art. 6º, III e VII, e art. 46). O enunciado não diz isso; é expectativa legítima para um cadastro de RH.
9. Funcionário novo nasce Ativo, ou com estado explícito.
10. Os controles fazem o que o rótulo diz ("Adicionar outra atividade", "Adicionar EPI", "Próximo passo", "A etapa está concluída?").
11. O `id` é gerado pelo servidor e é único (duplicata deveria dar 409).
12. Os registros existentes na base contam como dado potencialmente real, mesmo sem prova de que sejam.

**Dúvidas em aberto**

- O select de EPI grava o valor escolhido? Duas observações divergiram; precisa de checagem dirigida antes de virar asserção.
- Com o checkbox desmarcado e CA/EPI vazios, o usuário real vê a mensagem nativa de campo obrigatório, ou o formulário simplesmente não salva?
- Um registro sem `state.employee` quebra a listagem?
- O `access-control-allow-origin: *,*` bloqueia leitura cross-origin num navegador? E proxies cacheiam dados pessoais por causa de `cache-control: public`? Não observado.
- Há dado real na base e com qual base legal? Desconhecido.
- Qual o comportamento pretendido de "Próximo passo" e do switch "A etapa está concluída?"

## 3. Mapa de risco

> **A coluna "Decisão proposta" é uma proposta, à espera do corte do dono do plano.** Legenda: **testar a fundo** = vários casos e camadas (UI e API), com prioridade no relatório; **testar leve** = 1 ou 2 testes que documentam o comportamento (`xfail` quando é defeito); **não testar** = só registrar.

| Área | Impacto | Probabilidade | Risco | Decisão proposta | Por quê |
|---|---|---|---|---|---|
| Mapeamento tela → payload no cadastro (`usesEpi`, defaults dos selects, `isActive` inicial, anexo de ASO) | Alto | Alta | Alto | testar a fundo | dado de segurança do trabalho gravado diferente do que o usuário vê, em todo cadastro; o teste compara o digitado com o GET |
| Privacidade/LGPD: CPF completo na tela e na API, inativos servidos | Alto | Alta | Alto | testar a fundo | dado pessoal sem máscara e sem autenticação nas duas camadas |
| Controle de acesso: escrita sem autenticação | Alto | Alta | Alto | testar leve | propriedade binária e arquitetural; 1 teste por método documenta, mais casos não agregam |
| Validação de CPF e de data (tela e API) | Médio | Alta | Médio-alto | testar a fundo | casos-limite clássicos, baratos de parametrizar na API; o truncamento de CPF com máscara só aparece pela tela |
| Contrato e schema da API (forma, obrigatórios, valores permitidos, campos extras) | Médio | Alta | Médio | testar leve | uma causa raiz (API sem schema): poucos casos representativos, sem dezenas de `xfail` iguais |
| Botões do formulário ("Adicionar outra atividade", "Adicionar EPI") | Médio | Alta | Médio | testar leve | 1 teste por botão; o salvamento prematuro é observável pela rede |
| Listagem: atualização após salvar, filtro de ativos, contador | Médio | Alta | Médio | testar leve | 1 teste de atualização (`xfail`) e 1 do filtro, que roda no navegador |
| Semântica de PUT/PATCH | Médio | Baixa | Baixo-médio | testar leve | comportamento padrão do servidor genérico e a tela não usa PUT/PATCH; 1 teste documenta |
| `id` numérico × texto e `id` duplicado | Médio | Baixa | Baixo | testar leve | o cliente de teste aceita os dois tipos; para id numérico, só leitura |
| Paginação e filtros da coleção | Baixo | Média | Baixo | testar leve | afeta só clientes de API que paginam |
| Tratamento de erro (500 em JSON malformado) | Baixo | Baixa | Baixo | testar leve | status errado, sem vazamento relevante |
| Cabeçalhos de segurança e CORS | Baixo | Alta | Baixo | testar leve | 1 checagem; com a API já pública, o ganho adicional de um atacante é pequeno |
| Unicode e escape do nome (round-trip, `<b>`) | Médio | Baixa | Baixo | testar leve | regressão barata; hoje passa |
| Controles sem efeito, acessibilidade, layout de nome longo | Baixo | Alta | Baixo | não testar | sem especificação do comportamento pretendido; baixo impacto no fluxo de cadastro |
| Carga, força bruta, injeção, caminhos fora de `/employees` | n/a | n/a | n/a | não testar | proibido pelos limites da seção 8 |

### 3.1 Escala de severidade (proposta)

Severidade é o impacto técnico; prioridade é a urgência de negócio, e as duas ficam separadas no relatório.

| Nível | Critério |
|---|---|
| Crítica | perda ou exposição de dados em larga escala, sem pré-condição |
| Alta | dado gravado ou exposto de forma errada em fluxo principal, ou controle de acesso ausente |
| Média | comportamento incorreto com contorno, ou efeito limitado a clientes da API |
| Baixa | cosmético, usabilidade, má prática sem dano demonstrado |

## 4. Técnicas

- **Sessões exploratórias com roteiro.** Cada sessão tem missão, limite de tempo e anotações. Roteiros: (a) cadastro feliz campo a campo, comparando o payload enviado com o digitado; (b) formulário "no escuro": salvar sem tocar nos selects e no switch; (c) cada botão e controle da tela, observando rede e estado; (d) métodos da API um a um, em registro próprio; (e) listagem: atualização, filtro, contador, escape do nome.
- **Partição de equivalência.** CPF: 11 dígitos válidos; dígito verificador errado; 11 dígitos iguais; 10 e 12 dígitos; letras; vazio; número no lugar de texto; `null`; formatado com pontos e traço. Demais campos: valores permitidos pelo select, valor fora do domínio, tipo errado (`"false"` no lugar de `false`).
- **Valor-limite.** CPF: 10, 11 e 12 caracteres (a tela tem `minlength` e `maxlength` de 11). Datas de nascimento: hoje, amanhã, ano 0001, 1900, 2099, 9999-12-31, 30 de fevereiro, formato `dd/mm/aaaa`, vazio. Nome: vazio, só espaços, 300 caracteres sem espaço.
- **Tabela de decisão `usesEpi` × checkbox × `caNumber`.** Mostra o que a tela deveria gravar contra o que grava. "Esperado" vem da premissa 1.

  | Checkbox "não usa EPI" | CA preenchido | Esperado em `usesEpi` | Esperado em `caNumber` | Comportamento da tela |
  |---|---|---|---|---|
  | desmarcado | sim | `true` | CA informado | grava `false` |
  | desmarcado | não | (formulário não salva) | n/a | sem mensagem visível em headless |
  | marcado | campo some | `false` | vazio | grava `true` e `caNumber: ""` |

- **Cruzamento tela × API.** Criar pela tela e conferir na API os campos gravados; criar pela API e conferir na listagem; comparar o corpo do POST com o que o GET devolve depois; inativar e verificar que o funcionário some da tela mas continua na API.
- **Leitura estática do bundle como fonte de hipóteses.** A leitura do JavaScript da página gera hipóteses (por exemplo, defaults só visuais, botão sem `type`, arquivo nunca enviado). Hipótese não é achado: cada uma é confirmada ou derrubada no sistema rodando. Uma delas foi derrubada em parte: um botão que se supunha inerte, na verdade, salva o cadastro.
- **Verificação independente de cada achado antes do relatório.** Todo defeito é reproduzido por um segundo caminho (outro script, ou outra ferramenta) e depois à mão por quem assina o relatório. Se não reproduz, sai do relatório e o teste é corrigido ou removido. Nenhum defeito entra no relatório sem essa reprodução.

## 5. Automatizado × manual

A suíte usa marcadores do pytest: `unit`, `api`, `security`, `ui`, `cross` e `guard`.

| Marcador | O que cobre | Situação |
|---|---|---|
| `unit` | funções puras: validação de CPF, fábrica de dados sintéticos, máscara de dados pessoais, perfil agregado da base | existe |
| `guard` | varre `docs/` e falha se houver CPF sem máscara | existe |
| `api` | ciclo CRUD num registro próprio; contrato (schema) do registro criado; round-trip de nome com acento | existe (parcial) |
| `api` (negativos) | CPF, datas, obrigatórios, valores permitidos; os que a API aceita viram `xfail` com o id do defeito | planejado |
| `security` | escrita sem autenticação (1 teste por método), exposição de dados pessoais, CORS e cabeçalhos | planejado |
| `ui` | cadastro feliz, formulário "no escuro", botões, listagem (Page Objects sobre o Ant Design) | planejado |
| `cross` | criar pela tela e conferir na API, criar pela API e conferir na listagem, inativar | planejado |

Na última coleta (`uv run pytest --collect-only -q`) a suíte tinha 54 testes coletados, ainda sem testes de `ui`, `cross` e `security`.

**Por que automatizar:** regressão barata do que já se sabe (CRUD, contrato, máscara), e cada defeito confirmado vira um `xfail(strict=True, raises=AssertionError)` com o id do defeito: a suíte fica verde e documenta o bug, e se alguém o corrigir o teste passa a falhar, avisando que o plano precisa ser atualizado.

**Por que manter manual:**

- sessões exploratórias, que geram as hipóteses (automação só confirma o que já se sabe procurar);
- avaliação de privacidade e leitura de requisição e resposta, que exigem julgamento;
- tudo o que não tem comportamento esperado definido (controles sem efeito, acessibilidade);
- qualquer operação que mexeria em registro de terceiros: não se automatiza o que não se pode executar.

## 6. Ambiente e dados

- **Alvo:** web `https://analista-teste.seatecnologia.com.br/` e API `https://analista-teste.seatecnologia.com.br/employees`. A base pode ser trocada pela variável de ambiente `APP_BASE_URL`.
- **Navegador:** Chrome headless (Selenium 4). Local: Windows; CI: Ubuntu. O `input type=date` é preenchido em `AAAA-MM-DD`, que funciona independentemente do locale.
- **Ferramentas:** Python 3.12 (fixado em `.python-version`), gerenciado com `uv`; pytest, requests, jsonschema, Faker (pt_BR), pytest-html e ruff.
- **Dados:** sintéticos, gerados com Faker pt_BR e CPF válido gerado por nós. Todo registro criado tem o nome com prefixo `QA-AUTO-` e é apagado no teardown. Nenhum dado real é usado.
- **Base:** compartilhada e volátil. Outras pessoas escrevem nela ao mesmo tempo e ela chegou a mudar de milhares de registros para poucos em menos de uma hora. Nenhum teste depende de contagem global nem de registro alheio.
- **CI:** GitHub Actions, só em `push` e `pull_request` para `main` e em disparo manual (não em todo push de branch, para escrever o mínimo no ambiente compartilhado). Relatório HTML guardado como artefato por 7 dias, apenas com dados mascarados.

## 7. Riscos do próprio teste

| Risco | Mitigação |
|---|---|
| Base compartilhada e volátil: registro some no meio do teste, contagem muda | cada teste cria e apaga o próprio dado; o teardown tolera 404; nenhuma asserção sobre total |
| Registros com `id` numérico não são alcançáveis por id (GET, PUT, PATCH e DELETE dão 404), então não podem ser apagados por nós | os testes nunca criam id numérico; id numérico só em leitura. Alguns registros de teste com esse perfil ficaram na base durante a exploração e dependem do dono do ambiente |
| Teardown que trata 404 como "apagado" esconde sobra quando o id é numérico | conferir por `?id=` depois do DELETE |
| Dados pessoais vazando por mensagem de assert, relatório HTML, artefato de CI ou evidência | `describe()` nas asserções, em vez do corpo cru; máscara antes de salvar; teste de guarda varre `docs/`; artefatos com retenção de 7 dias |
| O CI escreve no ambiente compartilhado | roda só em `push` e `pull_request` para `main` e em disparo manual; escreve só registros `QA-AUTO-` e os apaga |
| Listar a base inteira a cada busca (1,4 MB, sem paginação) | buscar por id ou por nome exato no servidor (`?state.employee.name=`); não há filtro por prefixo |
| Espera flaky no Ant Design (selects e datas não são nativos) | espera explícita, nunca `sleep` |
| Clique interceptado por sobreposição em headless | clique por JavaScript nos botões afetados, documentado no Page Object |

## 8. Limites que me impus

Regras que valem para toda sessão, manual ou automatizada:

1. Só escrevo em registro nosso, com nome com prefixo `QA-AUTO-`, e apago no fim. Nunca altero nem apago registro de outra pessoa; a prova de "apagar sem autenticação" é feita num registro nosso.
2. Só uso dado sintético. Nunca dado de uma pessoa real.
3. Não envio payload executável. As sondas de injeção são texto inerte.
4. Não faço carga, força bruta nem varredura. Só toco em `/` e `/employees`.
5. Mascaro dado pessoal antes de salvar (formato `123.***.***-09`) e nunca despejo a base crua em lugar nenhum, inclusive nas ferramentas de IA que uso.
6. Não leio a lista completa em laço. Busco por id ou por filtro.
7. Trato a base inteira como dado potencialmente real, mesmo sem prova. A gravidade de um achado de privacidade vem da finalidade do sistema, não de saber se os registros de hoje são reais.
8. Analiso o conjunto só por agregados mascarados: contagens, distribuições, quantidade de CPFs inválidos ou duplicados. Amostras, quando necessárias, saem mascaradas.
9. Evidências e artefatos não carregam dado pessoal de terceiros: o print da listagem só sai depois de esconder o que não é nosso, e a máscara é declarada na evidência. Os artefatos do CI ficam 7 dias.
