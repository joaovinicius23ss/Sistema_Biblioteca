# Sistema de Gerenciamento de Biblioteca — Versão Atualizada

Este projeto evolui o sistema original (CustomTkinter) mantendo 100% das
funcionalidades e da identidade visual já existentes, e adicionando:

1. **Dashboard** (agora a tela inicial do sistema)
   - 6 cards com indicadores: títulos no acervo, exemplares disponíveis,
     exemplares emprestados, usuários cadastrados, empréstimos realizados
     e taxa de ocupação do acervo (%).
   - 3 gráficos (Matplotlib embutido via `FigureCanvasTkAgg`):
     - Pizza: situação do acervo (disponíveis x emprestados);
     - Barras: empréstimos ativos por usuário;
     - Barras: livros mais emprestados (histórico completo).
   - Os gráficos se adaptam automaticamente ao tema Dark/Light.

2. **Pesquisa de Livros**
   - Pesquisa por título e por autor, com agrupamento automático de
     exemplares iguais (mesmo título + mesmo autor).
   - Mostra total de exemplares, disponíveis e emprestados por título.

3. **Cadastro de livros com múltiplos exemplares**
   - Novo campo "Quantidade de Exemplares": ao salvar, o sistema cria
     um registro (com ID próprio) para cada exemplar, todos vinculados
     ao mesmo título/autor.

4. **Histórico de Empréstimos**
   - Registro permanente de todas as movimentações (empréstimo e
     devolução), com datas e status, mesmo após a devolução.

5. **Atualização automática em tempo real**
   - Qualquer cadastro, empréstimo ou devolução atualiza automaticamente
     o Dashboard, os gráficos, a pesquisa, o histórico e as listagens —
     sem necessidade de reiniciar o sistema.

6. **Melhorias práticas de funcionamento**
   - Limite configurável de exemplares simultâneos por usuário
     (`LIMITE_EMPRESTIMOS_POR_USUARIO`, padrão = 3), evitando que um
     único leitor monopolize o acervo.
   - Resumo rápido no cabeçalho (total de exemplares, usuários e
     empréstimos ativos).
   - Compatibilidade total com o `dados.json` já existente: o sistema
     migra automaticamente os dados antigos (sem quebrar nada) e ainda
     normaliza agrupamentos de títulos cadastrados com pequenas
     diferenças de capitalização.

## 🗂️ Estrutura de arquivos

```
Sistema Biblioteca/
├── main.py          # Interface gráfica (CustomTkinter + Matplotlib)
├── emprestimo.py     # Regras de negócio: GerenciadorBiblioteca
├── livro.py          # Classe Livro (exemplar do acervo)
├── usuario.py         # Classe Usuario (leitor)
├── dados.json          # Base de dados (JSON), criada/atualizada automaticamente
└── requirements.txt    # Dependências do projeto
```

## ▶️ Como executar

```bash
pip install -r requirements.txt
python main.py
```

## 🧱 Observações técnicas

- Todo o estado é persistido em `dados.json` após cada operação.
- O histórico (`historico`) é uma estrutura *append-only*: nada é
  removido, apenas marcado como "Devolvido" quando aplicável — ideal
  para auditoria e para os gráficos estatísticos.
- O agrupamento de exemplares (pesquisa e estatísticas) é feito por
  título + autor normalizados (sem diferenciar maiúsculas/minúsculas
  ou espaços nas extremidades), então não é necessário migrar o
  `dados.json` manualmente.
