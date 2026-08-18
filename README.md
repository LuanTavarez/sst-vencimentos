# SST Vencimentos — Controle de Vencimentos de Documentos Obrigatórios de Segurança do Trabalho

Sistema corporativo em **arquivo único (`index.html`)**, sem instalação, sem servidor.
Basta abrir o arquivo em qualquer navegador.

## Como usar

1. Abra `index.html` no navegador (duplo clique funciona).
2. Todos os dados ficam salvos localmente no navegador (localStorage) — nada é enviado para servidores externos.
3. Comece cadastrando colaboradores manualmente (botão "Novo registro") ou importando uma planilha (Excel/CSV) pelo menu "Importar planilha".

## Principais recursos

- **1 colaborador → N treinamentos**: cada colaborador tem um único cadastro, com quantos treinamentos/documentos forem necessários (ASO, NRs, Integração, Brigada, etc.).
- **Grade matricial**: colaboradores em linhas, tipos de treinamento em colunas — estilo Excel/Power BI/SAP.
- **Dashboard** com KPIs e gráficos (Chart.js), recalculados automaticamente.
- **Classificação automática por vencimento**: 🟢 Verde (+60d) · 🟡 Amarelo (31–60d) · 🟠 Laranja (15–30d) · 🔴 Vermelho (<15d) · ⚫ Cinza (vencido).
- **Importação inteligente** de planilhas, com reconhecimento automático de colunas e agrupamento por colaborador.
- **Exportação** para Excel e PDF, impressão.
- **Painel de Configurações completo**: identidade visual (nome, logo, favicon), aparência (cores, tema claro/escuro/automático, fonte), tipos de treinamento, módulos do menu, janelas de alerta, backup (exportar/importar/limpar).
- **Saúde / INSS (SESMT)**: aba dedicada para afastamentos/atestados, CAT, benefícios previdenciários (auxílio-doença, acidentário etc.) e restrições/readaptação de função — vinculados aos colaboradores já cadastrados, com KPIs, filtros e alertas de reavaliação próxima.
- **Menu lateral recolhível** (trilha de ícones).
- **Senha de acesso opcional**, com tela de bloqueio e recuperação (local ou por e-mail via `mailto:`).

## Estrutura do projeto

```
sst-vencimentos/
├── index.html          # o sistema completo (HTML + CSS + JS, tudo incorporado)
├── README.md            # este arquivo
└── docs/
    └── PROMPT.md         # especificação completa do projeto (para reconstruir/evoluir com IA)
```

## Tecnologias (via CDN, exigem internet na primeira carga)

Tailwind CSS · Chart.js · SheetJS (XLSX) · Font Awesome · jsPDF + AutoTable

## Continuando o desenvolvimento

Este projeto foi construído com o Claude (chat.claude.ai). Para continuar evoluindo
localmente com ajuda de IA diretamente no seu editor/terminal, use o **Claude Code**:
abra a pasta deste projeto nele e peça as próximas alterações — o arquivo `docs/PROMPT.md`
tem a especificação completa para dar contexto rápido a qualquer sessão nova.
