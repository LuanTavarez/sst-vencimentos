# Especificação completa do projeto — SST Vencimentos

> Este documento reúne o prompt completo do sistema, consolidando todas as
> etapas de construção. Use-o para dar contexto a uma nova sessão de IA
> (Claude Code, Claude.ai, etc.) ao continuar evoluindo o projeto.

Atue como um Engenheiro de Software Sênior, Especialista em Segurança do
Trabalho (SST), Business Intelligence (BI), UX/UI e Desenvolvimento
Front-End.

Desenvolva um sistema profissional de Controle de Vencimentos de
Documentação e Treinamentos de Segurança do Trabalho, em um ÚNICO arquivo
HTML — sem instalação, sem servidor, funcionando apenas ao salvar como
"index.html" e abrir no navegador. Todo CSS e JavaScript devem estar
incorporados no próprio arquivo.

## 1. Estrutura de dados — 1 colaborador → N treinamentos

Cada colaborador possui APENAS UM cadastro. Dentro desse cadastro, ele
pode ter quantidade ILIMITADA de treinamentos/documentos vinculados
(nunca duplicar o colaborador para adicionar um novo documento).

Tipos de treinamento/documento a controlar (e permitir criar novos
livremente, sem exigir alteração de código):
ASO (Admissional, Periódico, Retorno ao Trabalho, Mudança de Função,
Demissional), Integração, NR-01, NR-05, NR-06, NR-10, NR-11, NR-12,
NR-18, NR-20, NR-23, NR-33, NR-35, Primeiros Socorros, Brigada de
Incêndio, Operador de Empilhadeira, Plataforma Elevatória (PTA), Ponte
Rolante, Espaço Confinado, Trabalho em Altura, e qualquer outro criado
pelo usuário.

Campos do colaborador: Nome, Matrícula, CPF (opcional), Empresa,
Unidade, Cliente, Contrato, Centro de Custo, Setor, Cargo, Gestor.

Campos de cada treinamento: Tipo, Nº do certificado (opcional, com
upload/anexo do arquivo do certificado), Data de realização, Validade em
meses, Data de vencimento (calculada automaticamente = realização +
validade, com opção de sobrescrever manualmente), Situação (automática
ou manual: Dispensado / Não aplicável / Cancelado), Observações.

## 2. Layout em grade matricial (estilo Excel/Power BI/SAP/TOTVS)

Nenhum treinamento "empilhado" — usar uma grade matricial:
- Cada colaborador ocupa UMA linha.
- Cada tipo de treinamento ocupa UMA COLUNA (dinâmica, conforme os tipos
  cadastrados).
- Célula mostra a data de vencimento + cor/ícone de status, ou um estado
  vazio clicável para adicionar aquele treinamento ao colaborador.
- Primeira coluna (colaborador) e cabeçalho ficam fixos (sticky) durante
  a rolagem, com rolagem horizontal e vertical independentes.
- Clicar em qualquer célula abre um modal focado SÓ naquele tipo,
  permitindo editar, excluir, alterar datas/validade, anexar certificado,
  editar observações, e manter histórico de ocorrências anteriores do
  mesmo tipo (não apenas a mais recente).
- Botão "+" ao lado da última coluna de cada linha para adicionar
  rapidamente um novo treinamento àquele colaborador.
- Botão "+" para adicionar um colaborador novo (com formulário completo
  de dados + lista dinâmica de treinamentos, podendo adicionar quantos
  quiser antes de salvar).

## 3. Cálculos automáticos

- Dias restantes para vencer / dias em atraso.
- Percentual de documentos válidos, vencidos e próximos do vencimento.
- Classificação visual automática por dias restantes:
  🟢 Verde: mais de 60 dias · 🟡 Amarelo: 31–60 dias ·
  🟠 Laranja: 15–30 dias · 🔴 Vermelho: menos de 15 dias ·
  ⚫ Cinza: vencido (ou situação manual).

## 4. Dashboard

Cards automáticos: total de colaboradores, total de treinamentos,
válidos, vencidos, vencendo em 90/60/30/15/7 dias, vencendo hoje, ASOs
vencidos, Integrações vencidas, NRs vencidas, treinamentos vencidos,
percentual de conformidade.

Gráficos (Chart.js), todos recalculados automaticamente a partir de TODOS
os treinamentos cadastrados: vencimentos por mês, por empresa, por
unidade, por cliente, por setor, por gestor, por tipo de treinamento,
colaboradores com mais documentos vencidos, evolução mensal (±6 meses).

## 5. Funcionalidades

Upload de planilha (.xlsx, .xls, .csv) via SheetJS; cadastro manual;
edição e exclusão (por treinamento individual ou do colaborador inteiro);
busca instantânea; filtros avançados (empresa, unidade, cliente, setor,
gestor, situação, isolar coluna/tipo); ordenação por qualquer coluna
(inclusive por vencimento de um tipo específico); paginação; impressão;
exportação para Excel e PDF.

## 6. Alertas inteligentes

Listas separadas por urgência (vencidos, vence hoje, 7, 15, 30 dias),
destacadas visualmente pela cor do status.

## 7. Importação inteligente

Ao importar qualquer planilha, identificar automaticamente colunas
mesmo com nomes diferentes dos esperados (ex: Funcionário = Colaborador
= Empregado; Empresa = Filial; Curso = Treinamento; Validade =
Vencimento), via dicionário de sinônimos com normalização de texto
(minúsculas, sem acento). Mostrar uma tela de revisão do mapeamento antes
de confirmar. Agrupar linhas da planilha pelo mesmo colaborador
(matrícula, ou nome+empresa quando não há matrícula) em vez de duplicar
cadastros, evitando também duplicar o mesmo treinamento já importado.

## 8. Painel de Configurações (dentro do próprio sistema, sem editar código)

Botão de engrenagem sempre visível no menu (não pode ser escondido pelas
próprias configurações de módulos, para não travar o acesso ao painel).

- **Identidade visual:** nome do sistema, subtítulo, rodapé, logotipo
  (upload de imagem), favicon.
- **Aparência:** cor primária, secundária, de acento, do menu lateral, e
  de cada status (verde/amarelo/laranja/vermelho/cinza); tema
  claro/escuro/automático (segue o sistema operacional, reagindo em
  tempo real a mudanças); fonte; tamanho da fonte; raio de borda de
  cards e botões — tudo aplicado imediatamente ao salvar, via variáveis
  CSS centralizadas (nunca cores/fontes hardcoded soltas pelo código).
- **Módulos do menu:** esconder/mostrar cada item de navegação
  individualmente.
- **Tipos de treinamento:** lista com edição inline do nome e da
  validade padrão, exclusão (bloqueada se o tipo estiver em uso, com
  orientação para renomear/excluir os registros antes) e criação de
  novos tipos. Renomear um tipo deve atualizar automaticamente todos os
  treinamentos existentes que o usam.
- **Alertas:** habilitar/desabilitar cada janela de alerta (90/60/30/
  15/7 dias, hoje).
- **Backup:** exportar todos os dados + configurações em .json;
  importar/restaurar esse backup (com confirmação, pois substitui os
  dados atuais); limpar banco de dados local (com dupla confirmação).

## 9. Menu lateral recolhível (estilo trilha de ícones)

Botão que recolhe o menu para uma trilha estreita só com ícones (com
tooltip ao passar o mouse), no estilo de painéis como o do Claude.ai.
Estado recolhido/expandido lembrado entre sessões (localStorage). No
mobile, o menu vira um drawer que abre por cima do conteúdo.

## 10. Senha de acesso ao sistema

- Configurável dentro do painel de Configurações (ativar/desativar,
  definir/trocar senha com confirmação, mínimo de caracteres).
- A senha nunca é salva em texto puro — apenas um hash simples e
  síncrono (não depender de Web Crypto API, para funcionar de forma
  confiável mesmo abrindo o arquivo direto do disco, sem servidor/HTTPS).
- Tela de bloqueio cobre TODO o sistema até a senha correta ser digitada,
  exigida TODA VEZ que a página é carregada/recarregada (sem "lembrar"
  a sessão anterior).
- Para garantir que a trava funcione mesmo se algo no carregamento do
  restante do app falhar: incluir um pequeno script independente,
  posicionado logo após o HTML do conteúdo principal, que roda
  IMEDIATAMENTE ao ser interpretado (antes do script principal no fim da
  página) e já esconde o conteúdo se houver senha ativa salva — sem
  depender de nenhuma outra função do sistema.
- Campo de senha com botão de mostrar/ocultar (ícone de olho). Eliminar
  espaços em branco acidentais (.trim()) tanto ao salvar quanto ao
  conferir a senha digitada. Usar autocomplete="off" nos campos de
  definição de senha para reduzir chance de o navegador substituir o
  valor por uma senha gerada automaticamente.
- Ao salvar uma senha com a exigência ativa, mostrar a tela de bloqueio
  na hora, como prova visual de que funcionou (sem precisar recarregar a
  página para descobrir).
- **Recuperação de acesso (obrigatória, para nunca deixar o usuário sem
  saída):** duas opções na tela de bloqueio — (1) "Esqueci minha senha",
  que após confirmação explícita remove a exigência de senha e leva
  direto para as configurações, permitindo definir uma nova; (2) um
  e-mail de responsável cadastrável nas configurações, que gera um botão
  "Avisar o responsável por e-mail" na tela de bloqueio, abrindo o
  programa de e-mail do usuário (mailto:) com destinatário, assunto e
  corpo pré-preenchidos — deixando claro que isso NÃO envia e-mail
  automaticamente (o sistema não tem servidor), apenas prepara a
  mensagem.
- Documentar/comunicar claramente que essa proteção é um cadeado simples
  de navegador (evita acesso casual), não segurança de nível corporativo.

## 11. Interface

Visual moderno inspirado em Power BI, Microsoft Fabric, SAP, Tableau,
SOC, Senior, TOTVS e sistemas EHS corporativos. Elemento de assinatura:
uma faixa de "segurança" (padrão preto/âmbar) como acento visual sutil,
remetendo ao universo de SST. Responsivo, com animações suaves.

## 12. Tecnologias obrigatórias

HTML5, JavaScript puro (vanilla), Tailwind CSS (CDN), Chart.js (CDN),
SheetJS/XLSX (CDN), Font Awesome (CDN), jsPDF + autotable (CDN) para
exportação em PDF.

## 13. Regras

- Não remover nenhuma funcionalidade existente ao evoluir o sistema.
- Manter compatibilidade com dados já salvos (localStorage).
- Código extremamente organizado, comentado (em português), preparado
  para uso profissional em empresas de SST de qualquer porte.
- Antes de validar/salvar formulários com campos dinâmicos (linhas
  adicionadas/removidas via JS), sincronizar o estado interno
  diretamente a partir dos valores atuais do DOM, para nunca gerar falso
  "campo não preenchido" quando o campo está, na prática, preenchido na
  tela.
- Validar sintaxe de TODOS os blocos <script> do arquivo e a
  integridade de IDs/funções referenciadas (nenhum onclick/onchange
  apontando para função inexistente) antes de considerar concluído.
- Simular os fluxos críticos (classificação por data, importação com
  agrupamento por colaborador, senha salva → recarregar → tela de
  bloqueio aparece → senha correta → libera) com testes simples antes de
  entregar.
