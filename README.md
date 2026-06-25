<div align="center">

# 📚 Sistema de Gerenciamento de Biblioteca

Um sistema desktop completo para gerenciamento de acervo, usuários, empréstimos e devoluções, com **Dashboard analítico**, **gráficos estatísticos** e **pesquisa avançada** — construído com **Python** e **CustomTkinter**.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![CustomTkinter](https://img.shields.io/badge/CustomTkinter-5.2%2B-2563eb)
![Matplotlib](https://img.shields.io/badge/Matplotlib-3.8%2B-11557c)
![License](https://img.shields.io/badge/Licen%C3%A7a-MIT-10b981)
![Status](https://img.shields.io/badge/Status-Ativo-success)

</div>

---

## 🖼️ Visão Geral

O sistema oferece uma interface moderna, com **tema claro e escuro**, organizada em 6 módulos principais navegáveis por um menu lateral:

| Módulo | Descrição |
|---|---|
| 🏠 **Dashboard** | Indicadores e gráficos em tempo real sobre todo o acervo |
| 📚 **Acervo de Livros** | Cadastro de livros, com suporte a múltiplos exemplares |
| 👤 **Cadastro de Usuários** | Gerenciamento de leitores da biblioteca |
| 🔄 **Empréstimos e Devoluções** | Balcão de atendimento para movimentações |
| 🔍 **Pesquisa de Livros** | Busca por título ou autor, com exemplares agrupados |
| 📋 **Histórico** | Registro permanente de todas as movimentações realizadas |

> 💡 **Dica:** adicione aqui screenshots do seu sistema em execução (`docs/screenshot-dashboard.png`, etc.) para ilustrar a interface no GitHub.

---

## ✨ Funcionalidades

### 🏠 Dashboard
- Cards com indicadores-chave: títulos no acervo, exemplares disponíveis, exemplares emprestados, usuários cadastrados, empréstimos realizados e taxa de ocupação do acervo (%).
- 3 gráficos estatísticos embutidos (Matplotlib):
  - **Pizza** — situação geral do acervo (disponíveis x emprestados);
  - **Barras** — empréstimos ativos por usuário;
  - **Barras** — livros mais emprestados (com base no histórico completo).
- Gráficos adaptam automaticamente as cores ao alternar entre tema **Dark** e **Light**.

### 📚 Acervo de Livros
- Cadastro de livros com **quantidade de exemplares configurável** — cada exemplar recebe um ID próprio, mantendo o vínculo com o mesmo título e autor.
- Listagem completa com status individual de cada exemplar (Disponível / Emprestado).

### 👤 Usuários
- Cadastro simples de leitores, com visualização de quais livros cada um está com em posse no momento.

### 🔄 Empréstimos e Devoluções
- Registro rápido de empréstimo e devolução por ID.
- **Limite configurável de exemplares simultâneos por usuário** (padrão: 3), evitando que um único leitor monopolize o acervo.
- Validações completas (IDs inexistentes, livro já emprestado, devolução duplicada, etc.).

### 🔍 Pesquisa de Livros
- Pesquisa por **título** ou por **autor**.
- Exemplares iguais (mesmo título + autor) são **agrupados automaticamente**, exibindo total de exemplares, disponíveis e emprestados.

### 📋 Histórico
- Registro **append-only** (nunca apagado) de todas as movimentações: livro, usuário, data do empréstimo, data da devolução e status.
- Base de dados para os gráficos estatísticos do Dashboard.

### ⚙️ Outros
- **Atualização automática em tempo real** — qualquer cadastro, empréstimo ou devolução propaga instantaneamente para todas as telas (Dashboard, gráficos, pesquisa, histórico e listagens), sem necessidade de reiniciar o sistema.
- **Persistência em JSON** (`dados.json`), com migração automática de bases de dados geradas por versões anteriores do sistema.
- Interface responsiva, com rolagem automática, cartões modernos e suporte total a tema claro/escuro.

---

## 🧱 Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) — interface gráfica moderna baseada em Tkinter
- [Matplotlib](https://matplotlib.org/) — gráficos estatísticos embutidos via `FigureCanvasTkAgg`
- `json` (biblioteca padrão) — persistência de dados local

---

## 📂 Estrutura do Projeto

```
Sistema Biblioteca/
├── main.py              # Interface gráfica (telas, navegação, gráficos)
├── emprestimo.py         # Regras de negócio — classe GerenciadorBiblioteca
├── livro.py               # Modelo de dados — classe Livro (exemplar)
├── usuario.py              # Modelo de dados — classe Usuario (leitor)
├── dados.json               # Base de dados local (gerada/atualizada automaticamente)
├── requirements.txt          # Dependências do projeto
└── README.md                  # Este arquivo
```

### Visão da arquitetura

```
┌─────────────────────┐        ┌───────────────────────────┐
│   main.py (UI)        │ ───▶  │  emprestimo.py (regras)     │
│  CustomTkinter +      │        │  GerenciadorBiblioteca       │
│  Matplotlib           │ ◀───  │  (cadastro, empréstimo,        │
└─────────────────────┘        │   devolução, estatísticas,      │
                                │   pesquisa, histórico)           │
                                └───────────────┬───────────────┘
                                                │
                                   ┌────────────┴────────────┐
                                   │   livro.py / usuario.py    │
                                   │       (modelos de dados)     │
                                   └────────────┬────────────┘
                                                │
                                       ┌────────┴────────┐
                                       │   dados.json       │
                                       │  (persistência)      │
                                       └─────────────────┘
```

---

## 🚀 Instalação e Execução

### Pré-requisitos
- Python 3.10 ou superior instalado ([python.org](https://www.python.org/downloads/))

### Passo a passo

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sistema-biblioteca.git
cd sistema-biblioteca/"Sistema Biblioteca"

# 2. (Opcional, mas recomendado) Crie um ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Execute o sistema
python main.py
```

Na primeira execução, caso não exista um `dados.json`, o sistema inicia com o acervo vazio e cria o arquivo automaticamente a cada operação.

---

## 🧪 Como Usar

1. **Cadastre livros** no módulo *Acervo de Livros*, informando título, autor e a quantidade de exemplares desejada.
2. **Cadastre usuários** no módulo *Cadastro de Usuários*.
3. Use o módulo *Empréstimos e Devoluções* informando o **ID do usuário** e o **ID do exemplar** para registrar movimentações.
4. Acompanhe tudo em tempo real pelo **Dashboard**, pesquise exemplares específicos em *Pesquisa de Livros* e consulte o que já aconteceu no *Histórico*.
5. Alterne entre os temas **Dark** e **Light** no rodapé do menu lateral — toda a interface (incluindo os gráficos) se adapta automaticamente.

---

## ⚙️ Configuração

Algumas regras de negócio podem ser ajustadas diretamente no início da classe `BibliotecaUI`, em `main.py`:

```python
class BibliotecaUI:
    # Limite de exemplares emprestados simultaneamente por usuário.
    LIMITE_EMPRESTIMOS_POR_USUARIO = 3
```

O arquivo de persistência também pode ser alterado ao instanciar o gerenciador, em `GerenciadorBiblioteca(arquivo_dados="dados.json")` dentro de `emprestimo.py`.

---

## 🗃️ Modelo de Dados

O arquivo `dados.json` é estruturado da seguinte forma:

```json
{
  "livros": [
    {
      "id_livro": 1,
      "titulo": "Dom Casmurro",
      "autor": "Machado de Assis",
      "disponivel": true,
      "id_usuario_atual": null,
      "data_cadastro": "25/06/2026 10:00"
    }
  ],
  "usuarios": [
    { "id_usuario": 1, "nome": "Ana Maria Silva", "data_cadastro": "25/06/2026 10:01" }
  ],
  "emprestimos": [
    { "id_usuario": 1, "id_livro": 1, "data_emprestimo": "25/06/2026 10:05" }
  ],
  "historico": [
    {
      "id": 1,
      "id_livro": 1,
      "titulo": "Dom Casmurro",
      "autor": "Machado de Assis",
      "id_usuario": 1,
      "nome_usuario": "Ana Maria Silva",
      "data_emprestimo": "25/06/2026 10:05",
      "data_devolucao": null,
      "status": "Emprestado"
    }
  ]
}
```

- `emprestimos` guarda apenas as movimentações **ativas** (ainda não devolvidas).
- `historico` é **permanente** — nada é excluído, apenas atualizado para `"Devolvido"` quando aplicável. É a fonte dos gráficos estatísticos.
- Cada exemplar (`livro`) tem seu próprio ID; exemplares com o mesmo título e autor são agrupados automaticamente nas telas de Pesquisa e Dashboard.

---

## 🗺️ Roadmap / Próximos Passos

- [ ] Exportação de relatórios em PDF/Excel
- [ ] Sistema de reservas para livros emprestados
- [ ] Notificação de atraso na devolução
- [ ] Edição e exclusão de cadastros (livros e usuários)
- [ ] Autenticação de bibliotecários (login)
- [ ] Migração para banco de dados relacional (SQLite/PostgreSQL)

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Faça um *fork* do projeto
2. Crie uma branch para sua funcionalidade (`git checkout -b feature/nova-funcionalidade`)
3. Faça commit das suas alterações (`git commit -m 'Adiciona nova funcionalidade'`)
4. Envie para o seu fork (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

Este projeto está sob a licença MIT. Sinta-se livre para usar, modificar e distribuir.

---

## 👤 Autor

Desenvolvido com 📚 e ☕ para facilitar a gestão de bibliotecas reais.

<div align="center">

**Se este projeto foi útil, considere deixar uma ⭐!**

</div>
