import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator

# Importação mantida conforme a estrutura original do projeto
from emprestimo import GerenciadorBiblioteca

# Configuração global de inicialização (Tema Escuro padrão)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class BibliotecaUI:

    # Regra prática de biblioteca: limite de exemplares simultâneos por usuário.
    # Evita que um único leitor monopolize o acervo. Ajuste livremente aqui.
    LIMITE_EMPRESTIMOS_POR_USUARIO = 3

    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Gerenciamento de Biblioteca")
        self.root.geometry("1280x800")
        self.root.minsize(1100, 700)

        self.biblioteca = GerenciadorBiblioteca()

        # Controle do termo de pesquisa ativo (para re-renderizar após updates)
        self._modo_pesquisa_atual = ("todos", "")

        # Paleta de Cores (Interface Limpa e Moderna)
        self.COR_MENU_ESCURO = "#1e1e2e"
        self.COR_MENU_CLARO = "#f3f4f6"
        self.COR_DESTAQUE_AZUL = "#3b82f6"
        self.COR_SUCESSO_VERDE = "#10b981"
        self.COR_ALERTA_VERMELHO = "#ef4444"
        self.COR_ROXO = "#8b5cf6"
        self.COR_AMBAR = "#f59e0b"
        self.COR_CIANO = "#06b6d4"

        # Fontes Padronizadas
        self.fonte_titulo = ctk.CTkFont(family="Segoe UI", size=22, weight="bold")
        self.fonte_secao = ctk.CTkFont(family="Segoe UI", size=18, weight="bold")
        self.fonte_normal = ctk.CTkFont(family="Segoe UI", size=14)
        self.fonte_botoes = ctk.CTkFont(family="Segoe UI", size=13, weight="bold")

        # Layout da Grade Principal
        self.root.grid_columnconfigure(0, weight=1)  # Menu Lateral
        self.root.grid_columnconfigure(1, weight=5)  # Painel de Conteúdo
        self.root.grid_rowconfigure(0, weight=1)

        # 1. Menu Lateral de Navegação
        self.criar_menu_lateral()

        # Container Principal Direito
        self.lado_direito = ctk.CTkFrame(self.root, corner_radius=0, fg_color=("#f8f9fa", "#11111b"))
        self.lado_direito.grid(row=0, column=1, sticky="nsew")
        self.lado_direito.grid_columnconfigure(0, weight=1)
        self.lado_direito.grid_rowconfigure(1, weight=1)

        # 2. Cabeçalho Superior
        self.criar_cabecalho()

        # 3. Área de Telas Dinâmicas
        self.container_conteudo = ctk.CTkFrame(self.lado_direito, fg_color="transparent")
        self.container_conteudo.grid(row=1, column=0, sticky="nsew", padx=25, pady=25)
        self.container_conteudo.grid_columnconfigure(0, weight=1)
        self.container_conteudo.grid_rowconfigure(0, weight=1)

        self.telas = {}
        self.criar_todas_as_telas()
        self.mudar_tela("dashboard")
        self.atualizar_cabecalho()

    # ==================================================================
    # ESTRUTURA GERAL DA INTERFACE
    # ==================================================================
    def criar_menu_lateral(self):
        sidebar = ctk.CTkFrame(self.root, width=240, corner_radius=0, fg_color=(self.COR_MENU_CLARO, self.COR_MENU_ESCURO))
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.grid_rowconfigure(7, weight=1)

        # Logo / Título do Sistema
        lbl_logo = ctk.CTkLabel(sidebar, text=" BIBLIOTECA\nPainel de Controle",
                                font=self.fonte_titulo, text_color=(self.COR_DESTAQUE_AZUL, "white"), justify="center")
        lbl_logo.grid(row=0, column=0, padx=20, pady=(30, 35))

        botoes_config = [
            ("dashboard", "🏠  Dashboard"),
            ("livros", "📚  Acervo de Livros"),
            ("usuarios", "👤  Cadastro de Usuários"),
            ("operacoes", "🔄  Empréstimos e Devoluções"),
            ("pesquisa", "🔍  Pesquisa de Livros"),
            ("historico", "📋  Histórico"),
        ]

        self.botoes_navegacao = {}
        for idx, (chave, texto) in enumerate(botoes_config, start=1):
            btn = ctk.CTkButton(sidebar, text=texto, font=self.fonte_botoes, anchor="w",
                                 height=45, corner_radius=6, fg_color="transparent",
                                 text_color=("gray10", "gray90"), hover_color=("#e2e8f0", "#2d2d3d"),
                                 command=lambda c=chave: self.mudar_tela(c))
            btn.grid(row=idx, column=0, padx=15, pady=6, sticky="ew")
            self.botoes_navegacao[chave] = btn

        # Seletor de Tema no rodapé do menu
        lbl_modo = ctk.CTkLabel(sidebar, text="TEMA DO SISTEMA:", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"))
        lbl_modo.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="w")

        switch_modo = ctk.CTkOptionMenu(sidebar, values=["Dark", "Light"], font=self.fonte_normal,
                                        fg_color=("#cbd5e1", "#2d2d3d"), button_color=("#94a3b8", "#3b82f6"),
                                        text_color=("black", "white"), command=self.atualizar_tema_global)
        switch_modo.grid(row=9, column=0, padx=15, pady=(5, 25), sticky="ew")

    def criar_cabecalho(self):
        header = ctk.CTkFrame(self.lado_direito, height=65, corner_radius=0,
                              fg_color=(self.COR_MENU_CLARO, self.COR_MENU_ESCURO), border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        header.grid(row=0, column=0, sticky="ew")
        header.grid_propagate(False)
        header.grid_columnconfigure(1, weight=1)

        self.lbl_resumo_header = ctk.CTkLabel(header, text="Carregando dados do acervo...",
                                              font=ctk.CTkFont(family="Segoe UI", size=13), text_color=("gray40", "#a6adc8"))
        self.lbl_resumo_header.grid(row=0, column=0, padx=20, pady=18, sticky="w")

        self.lbl_status_node = ctk.CTkLabel(header, text="● SISTEMA ONLINE", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.COR_SUCESSO_VERDE)
        self.lbl_status_node.grid(row=0, column=2, padx=20, pady=18, sticky="e")

    def atualizar_cabecalho(self):
        stats = self.biblioteca.obter_estatisticas_dashboard()
        texto = (f"📚 {stats['total_exemplares']} exemplares  •  "
                 f"👤 {stats['total_usuarios']} usuários  •  "
                 f"🔄 {stats['emprestados']} empréstimos ativos")
        self.lbl_resumo_header.configure(text=texto)

    def atualizar_tema_global(self, modo):
        ctk.set_appearance_mode(modo)
        self.root.update_idletasks()
        self.atualizar_tudo()

    def mudar_tela(self, nome_tela):
        tela_selecionada = self.telas[nome_tela]
        tela_selecionada.lift()

        for nome, btn in self.botoes_navegacao.items():
            if nome == nome_tela:
                btn.configure(fg_color=("#cbd5e1", "#2d2d3d"), text_color=self.COR_DESTAQUE_AZUL)
            else:
                btn.configure(fg_color="transparent", text_color=("gray10", "gray90"))

        # Garante que a tela exibida sempre reflita o estado mais atual dos dados
        if nome_tela == "dashboard":
            self.atualizar_dashboard()
        elif nome_tela == "historico":
            self.atualizar_historico()
        elif nome_tela == "pesquisa":
            self.atualizar_resultados_pesquisa()

    def criar_todas_as_telas(self):
        for nome, criador in [("dashboard", self.criar_tela_dashboard),
                              ("livros", self.criar_tela_livros),
                              ("usuarios", self.criar_tela_usuarios),
                              ("operacoes", self.criar_tela_operacoes),
                              ("pesquisa", self.criar_tela_pesquisa),
                              ("historico", self.criar_tela_historico)]:
            frame_tela = criador()
            frame_tela.grid(row=0, column=0, sticky="nsew")
            self.telas[nome] = frame_tela

    def atualizar_tudo(self):
        """Atualiza absolutamente todas as telas após qualquer alteração nos dados."""
        self.atualizar_tabela_livros()
        self.atualizar_tabela_usuarios()
        self.atualizar_dashboard()
        self.atualizar_historico()
        self.atualizar_resultados_pesquisa()
        self.atualizar_cabecalho()

    # ==================================================================
    # 1. DASHBOARD
    # ==================================================================
    def criar_tela_dashboard(self):
        outer = ctk.CTkScrollableFrame(self.container_conteudo, fg_color="transparent")
        outer.grid_columnconfigure((0, 1, 2), weight=1, uniform="cards")

        ctk.CTkLabel(outer, text="Dashboard — Visão Geral do Sistema", font=self.fonte_secao).grid(
            row=0, column=0, columnspan=3, sticky="w", pady=(0, 15))

        self.dashboard_valores = {}
        cards_info = [
            ("total_titulos", "📚", "Títulos no Acervo", self.COR_DESTAQUE_AZUL),
            ("disponiveis", "✅", "Exemplares Disponíveis", self.COR_SUCESSO_VERDE),
            ("emprestados", "📕", "Exemplares Emprestados", self.COR_ALERTA_VERMELHO),
            ("total_usuarios", "👤", "Usuários Cadastrados", self.COR_ROXO),
            ("total_emprestimos_realizados", "🔄", "Empréstimos Realizados", self.COR_AMBAR),
            ("taxa_ocupacao", "📊", "Taxa de Ocupação do Acervo", self.COR_CIANO),
        ]
        for idx, (chave, icone, titulo_card, cor) in enumerate(cards_info):
            row = 1 + idx // 3
            col = idx % 3
            lbl_valor = self.criar_card_dashboard(outer, row, col, icone, titulo_card, cor)
            self.dashboard_valores[chave] = lbl_valor

        ctk.CTkLabel(outer, text="Estatísticas Visuais", font=self.fonte_secao).grid(
            row=3, column=0, columnspan=3, sticky="w", pady=(25, 15))

        frame_graficos = ctk.CTkFrame(outer, fg_color=("white", "#1e1e2e"), corner_radius=10,
                                      border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        frame_graficos.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=(0, 15))
        self.criar_graficos_dashboard(frame_graficos)

        self.atualizar_dashboard()
        return outer

    def criar_card_dashboard(self, parent, row, col, icone, titulo_card, cor):
        card = ctk.CTkFrame(parent, corner_radius=10, border_width=1, border_color=("#e2e8f0", "#2d2d3d"),
                            fg_color=("white", "#1e1e2e"))
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_columnconfigure(1, weight=1)

        faixa = ctk.CTkFrame(card, width=6, corner_radius=0, fg_color=cor)
        faixa.grid(row=0, column=0, rowspan=2, sticky="ns")

        ctk.CTkLabel(card, text=icone, font=ctk.CTkFont(size=26)).grid(
            row=0, column=1, sticky="w", padx=(15, 5), pady=(15, 0))

        lbl_valor = ctk.CTkLabel(card, text="0", font=ctk.CTkFont(family="Segoe UI", size=25, weight="bold"),
                                 text_color=cor)
        lbl_valor.grid(row=0, column=2, sticky="e", padx=15, pady=(15, 0))

        ctk.CTkLabel(card, text=titulo_card, font=self.fonte_normal, text_color=("gray40", "#a6adc8"),
                    anchor="w").grid(row=1, column=1, columnspan=2, sticky="w", padx=15, pady=(0, 15))
        return lbl_valor

    def criar_graficos_dashboard(self, parent):
        self.fig_dashboard = Figure(figsize=(11, 3.4), dpi=100)
        self.ax_pizza = self.fig_dashboard.add_subplot(131)
        self.ax_usuarios = self.fig_dashboard.add_subplot(132)
        self.ax_top_livros = self.fig_dashboard.add_subplot(133)
        self.fig_dashboard.subplots_adjust(wspace=0.55, left=0.05, right=0.97, top=0.85, bottom=0.15)

        self.canvas_dashboard = FigureCanvasTkAgg(self.fig_dashboard, master=parent)
        self.canvas_dashboard.get_tk_widget().pack(fill="both", expand=True, padx=15, pady=15)

    def atualizar_dashboard(self):
        if not hasattr(self, "dashboard_valores"):
            return
        stats = self.biblioteca.obter_estatisticas_dashboard()
        self.dashboard_valores["total_titulos"].configure(text=str(stats["total_titulos"]))
        self.dashboard_valores["disponiveis"].configure(text=str(stats["disponiveis"]))
        self.dashboard_valores["emprestados"].configure(text=str(stats["emprestados"]))
        self.dashboard_valores["total_usuarios"].configure(text=str(stats["total_usuarios"]))
        self.dashboard_valores["total_emprestimos_realizados"].configure(text=str(stats["total_emprestimos_realizados"]))
        self.dashboard_valores["taxa_ocupacao"].configure(text=f"{stats['taxa_ocupacao']}%")
        self.atualizar_graficos()

    def atualizar_graficos(self):
        if not hasattr(self, "fig_dashboard"):
            return

        escuro = ctk.get_appearance_mode() == "Dark"
        cor_fundo = "#1e1e2e" if escuro else "#ffffff"
        cor_texto = "#e2e8f0" if escuro else "#1e293b"

        stats = self.biblioteca.obter_estatisticas_dashboard()

        for ax in (self.ax_pizza, self.ax_usuarios, self.ax_top_livros):
            ax.clear()
            ax.set_facecolor(cor_fundo)
        self.fig_dashboard.set_facecolor(cor_fundo)

        # --- Gráfico 1: Situação do Acervo (Pizza) ---
        self.ax_pizza.set_title("Situação do Acervo", color=cor_texto, fontsize=10, fontweight="bold")
        candidatos = [
            (stats["disponiveis"], self.COR_SUCESSO_VERDE, "Disponíveis"),
            (stats["emprestados"], self.COR_ALERTA_VERMELHO, "Emprestados"),
        ]
        dados_validos = [(v, c, l) for v, c, l in candidatos if v > 0]
        if dados_validos:
            valores, cores, labels = zip(*dados_validos)
            self.ax_pizza.pie(valores, colors=cores, labels=labels, autopct="%1.0f%%",
                              textprops={"color": cor_texto, "fontsize": 8})
        else:
            self.ax_pizza.text(0.5, 0.5, "Sem exemplares\ncadastrados", ha="center", va="center",
                               color=cor_texto, fontsize=9, transform=self.ax_pizza.transAxes)
            self.ax_pizza.axis("off")

        # --- Gráfico 2: Empréstimos Ativos por Usuário (Barras) ---
        self.ax_usuarios.set_title("Empréstimos Ativos por Usuário", color=cor_texto, fontsize=10, fontweight="bold")
        dados_usuarios = self.biblioteca.obter_emprestimos_por_usuario()
        if dados_usuarios:
            nomes = [n for n, _ in dados_usuarios][::-1]
            qtdes = [q for _, q in dados_usuarios][::-1]
            self.ax_usuarios.barh(nomes, qtdes, color=self.COR_DESTAQUE_AZUL)
            self.ax_usuarios.tick_params(colors=cor_texto, labelsize=8)
            for spine in self.ax_usuarios.spines.values():
                spine.set_color(cor_texto)
            self.ax_usuarios.xaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            self.ax_usuarios.text(0.5, 0.5, "Nenhum empréstimo\nativo no momento", ha="center", va="center",
                                  color=cor_texto, fontsize=9, transform=self.ax_usuarios.transAxes)
            self.ax_usuarios.axis("off")

        # --- Gráfico 3: Livros Mais Emprestados (Barras) ---
        self.ax_top_livros.set_title("Livros Mais Emprestados", color=cor_texto, fontsize=10, fontweight="bold")
        top_livros = self.biblioteca.obter_livros_mais_emprestados()
        if top_livros:
            titulos = [(t[:18] + "…") if len(t) > 18 else t for t, _ in top_livros][::-1]
            qtdes = [q for _, q in top_livros][::-1]
            self.ax_top_livros.barh(titulos, qtdes, color=self.COR_AMBAR)
            self.ax_top_livros.tick_params(colors=cor_texto, labelsize=8)
            for spine in self.ax_top_livros.spines.values():
                spine.set_color(cor_texto)
            self.ax_top_livros.xaxis.set_major_locator(MaxNLocator(integer=True))
        else:
            self.ax_top_livros.text(0.5, 0.5, "Nenhum empréstimo\nregistrado ainda", ha="center", va="center",
                                    color=cor_texto, fontsize=9, transform=self.ax_top_livros.transAxes)
            self.ax_top_livros.axis("off")

        self.canvas_dashboard.draw()

    # ==================================================================
    # 2. ACERVO DE LIVROS
    # ==================================================================
    def criar_tela_livros(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        ctk.CTkLabel(frame, text="Painel do Acervo de Livros", font=self.fonte_secao).pack(anchor="w", pady=(0, 15))

        card_cadastro = ctk.CTkFrame(frame, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        card_cadastro.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card_cadastro, text="Cadastrar Novo Livro no Acervo", font=self.fonte_botoes).grid(
            row=0, column=0, columnspan=4, sticky="w", pady=(15, 15), padx=20)

        self.ent_titulo = ctk.CTkEntry(card_cadastro, placeholder_text="Título do Livro", width=340, height=40, font=self.fonte_normal)
        self.ent_titulo.grid(row=1, column=0, padx=(20, 15), pady=(0, 20))

        self.ent_autor = ctk.CTkEntry(card_cadastro, placeholder_text="Nome do Autor", width=260, height=40, font=self.fonte_normal)
        self.ent_autor.grid(row=1, column=1, padx=(0, 15), pady=(0, 20))

        self.ent_quantidade = ctk.CTkEntry(card_cadastro, placeholder_text="Qtde. Exemplares", width=130, height=40, font=self.fonte_normal)
        self.ent_quantidade.grid(row=1, column=2, padx=(0, 15), pady=(0, 20))

        btn_salvar = ctk.CTkButton(card_cadastro, text="Salvar Livro", height=40, font=self.fonte_botoes,
                                   fg_color=self.COR_DESTAQUE_AZUL, hover_color="#2563eb", command=self.acao_cadastrar_livro)
        btn_salvar.grid(row=1, column=3, padx=(0, 20), pady=(0, 20))

        ctk.CTkLabel(card_cadastro, text="Dica: deixe a quantidade em branco para cadastrar 1 exemplar.",
                    font=ctk.CTkFont(family="Segoe UI", size=11), text_color=("gray40", "#a6adc8")).grid(
            row=2, column=0, columnspan=4, sticky="w", padx=20, pady=(0, 15))

        self.card_lista_livros = ctk.CTkScrollableFrame(frame, label_text="LIVROS CADASTRADOS",
                                                        label_font=self.fonte_botoes, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        self.card_lista_livros.pack(fill="both", expand=True)

        self.atualizar_tabela_livros()
        return frame

    def atualizar_tabela_livros(self):
        for widget in self.card_lista_livros.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.card_lista_livros, fg_color=("#e2e8f0", "#2d2d3d"), corner_radius=4)
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="ID", font=self.fonte_botoes, width=80).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="TÍTULO", font=self.fonte_botoes, width=300, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="AUTOR", font=self.fonte_botoes, width=200, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="STATUS", font=self.fonte_botoes, width=140).pack(side="right", padx=10)

        if not self.biblioteca.livros:
            ctk.CTkLabel(self.card_lista_livros, text="Nenhum livro cadastrado ainda.", font=self.fonte_normal,
                        text_color=("gray40", "#a6adc8")).pack(pady=30)
            return

        for livro in self.biblioteca.livros:
            row = ctk.CTkFrame(self.card_lista_livros, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=str(livro.id_livro), font=self.fonte_normal, width=80).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=livro.titulo, font=self.fonte_normal, width=300, anchor="w",
                        text_color=(self.COR_DESTAQUE_AZUL, "white")).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=livro.autor, font=self.fonte_normal, width=200, anchor="w").pack(side="left", padx=10)

            status_cor = self.COR_SUCESSO_VERDE if livro.disponivel else self.COR_ALERTA_VERMELHO
            status_txt = "Disponível" if livro.disponivel else "Emprestado"
            ctk.CTkLabel(row, text=status_txt, font=self.fonte_botoes, text_color=status_cor, width=140).pack(side="right", padx=10)

    def acao_cadastrar_livro(self):
        titulo = self.ent_titulo.get().strip()
        autor = self.ent_autor.get().strip()
        qtde_texto = self.ent_quantidade.get().strip() or "1"

        if not titulo or not autor:
            messagebox.showwarning("Aviso", "Por favor, preencha título e autor do livro.")
            return

        try:
            quantidade = int(qtde_texto)
            if quantidade < 1:
                raise ValueError
        except ValueError:
            messagebox.showerror("Erro", "A quantidade de exemplares deve ser um número inteiro maior que zero.")
            return

        self.biblioteca.cadastrar_livro(titulo, autor, quantidade)
        self.atualizar_tudo()
        self.ent_titulo.delete(0, tk.END)
        self.ent_autor.delete(0, tk.END)
        self.ent_quantidade.delete(0, tk.END)
        plural = "exemplares" if quantidade > 1 else "exemplar"
        messagebox.showinfo("Sucesso", f"{quantidade} {plural} de '{titulo}' cadastrado(s) com sucesso!")

    # ==================================================================
    # 3. USUÁRIOS
    # ==================================================================
    def criar_tela_usuarios(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        ctk.CTkLabel(frame, text="Gerenciamento de Leitores / Usuários", font=self.fonte_secao).pack(anchor="w", pady=(0, 15))

        card_cadastro = ctk.CTkFrame(frame, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        card_cadastro.pack(fill="x", pady=(0, 20))

        ctk.CTkLabel(card_cadastro, text="Registrar Novo Usuário", font=self.fonte_botoes).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(15, 15), padx=20)

        self.ent_usuario = ctk.CTkEntry(card_cadastro, placeholder_text="Nome Completo do Usuário", width=480, height=40, font=self.fonte_normal)
        self.ent_usuario.grid(row=1, column=0, padx=(20, 15), pady=(0, 20))

        btn_salvar_u = ctk.CTkButton(card_cadastro, text="Registrar", height=40, font=self.fonte_botoes,
                                     fg_color=self.COR_DESTAQUE_AZUL, hover_color="#2563eb", command=self.acao_cadastrar_usuario)
        btn_salvar_u.grid(row=1, column=1, padx=(0, 20), pady=(0, 20))

        self.card_lista_usuarios = ctk.CTkScrollableFrame(frame, label_text="USUÁRIOS ATIVOS",
                                                          label_font=self.fonte_botoes, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        self.card_lista_usuarios.pack(fill="both", expand=True)

        self.atualizar_tabela_usuarios()
        return frame

    def atualizar_tabela_usuarios(self):
        for widget in self.card_lista_usuarios.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.card_lista_usuarios, fg_color=("#e2e8f0", "#2d2d3d"), corner_radius=4)
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="ID USUÁRIO", font=self.fonte_botoes, width=120).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="NOME DO LEITOR", font=self.fonte_botoes, width=330, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="LIVROS EM POSSE", font=self.fonte_botoes, width=330, anchor="w").pack(side="left", padx=10)

        if not self.biblioteca.usuarios:
            ctk.CTkLabel(self.card_lista_usuarios, text="Nenhum usuário cadastrado ainda.", font=self.fonte_normal,
                        text_color=("gray40", "#a6adc8")).pack(pady=30)
            return

        for usuario in self.biblioteca.usuarios:
            row = ctk.CTkFrame(self.card_lista_usuarios, fg_color="transparent")
            row.pack(fill="x", pady=1)

            livros_com_usuario = [l.titulo for l in self.biblioteca.livros if l.id_usuario_atual == usuario.id_usuario]
            livros_texto = ", ".join(livros_com_usuario) if livros_com_usuario else "Nenhum livro retido"
            txt_cor = ("black", "white") if livros_com_usuario else "gray"

            ctk.CTkLabel(row, text=f"#{usuario.id_usuario}", font=self.fonte_normal, width=120).pack(side="left", padx=10)
            ctk.CTkLabel(row, text=usuario.nome, font=self.fonte_normal, width=330, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=livros_texto, font=self.fonte_normal, width=330, anchor="w", text_color=txt_cor).pack(side="left", padx=10)

    def acao_cadastrar_usuario(self):
        nome = self.ent_usuario.get().strip()
        if not nome:
            messagebox.showwarning("Aviso", "O campo de nome do usuário não pode ser vazio.")
            return
        self.biblioteca.cadastrar_usuario(nome)
        self.atualizar_tudo()
        self.ent_usuario.delete(0, tk.END)

    # ==================================================================
    # 4. EMPRÉSTIMOS E DEVOLUÇÕES
    # ==================================================================
    def criar_tela_operacoes(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")

        ctk.CTkLabel(frame, text="Balcão de Atendimento Digital", font=self.fonte_secao).grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # Seção de Empréstimo
        card_emp = ctk.CTkFrame(frame, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        card_emp.grid(row=1, column=0, padx=(0, 10), sticky="nsew")

        ctk.CTkLabel(card_emp, text="Realizar Novo Empréstimo", font=self.fonte_botoes).pack(anchor="w", pady=(15, 15), padx=20)
        ctk.CTkLabel(card_emp, text="ID do Usuário:", font=self.fonte_normal).pack(anchor="w", pady=(5, 5), padx=20)
        self.ent_id_user = ctk.CTkEntry(card_emp, height=40, font=self.fonte_normal, placeholder_text="Ex: 1")
        self.ent_id_user.pack(fill="x", pady=(0, 15), padx=20)

        ctk.CTkLabel(card_emp, text="ID do Livro:", font=self.fonte_normal).pack(anchor="w", pady=(5, 5), padx=20)
        self.ent_id_livro_emp = ctk.CTkEntry(card_emp, height=40, font=self.fonte_normal, placeholder_text="Ex: 101")
        self.ent_id_livro_emp.pack(fill="x", pady=(0, 25), padx=20)

        btn_realizar_emp = ctk.CTkButton(card_emp, text="Confirmar Empréstimo", height=45, font=self.fonte_botoes,
                                         fg_color=self.COR_SUCESSO_VERDE, text_color="white", hover_color="#059669", command=self.acao_registrar_emprestimo)
        btn_realizar_emp.pack(fill="x", padx=20, pady=(0, 20))

        # Seção de Devolução
        card_dev = ctk.CTkFrame(frame, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        card_dev.grid(row=1, column=1, padx=(10, 0), sticky="nsew")

        ctk.CTkLabel(card_dev, text="Registrar Devolução de Item", font=self.fonte_botoes).pack(anchor="w", pady=(15, 15), padx=20)
        ctk.CTkLabel(card_dev, text="ID do Livro Retornado:", font=self.fonte_normal).pack(anchor="w", pady=(5, 5), padx=20)
        self.ent_id_livro_dev = ctk.CTkEntry(card_dev, height=40, font=self.fonte_normal, placeholder_text="Ex: 101")
        self.ent_id_livro_dev.pack(fill="x", pady=(0, 102), padx=20)

        btn_realizar_dev = ctk.CTkButton(card_dev, text="Confirmar Devolução", height=45, font=self.fonte_botoes,
                                         fg_color=self.COR_DESTAQUE_AZUL, text_color="white", hover_color="#2563eb", command=self.acao_registrar_devolucao)
        btn_realizar_dev.pack(fill="x", padx=20, pady=(0, 20))

        return frame

    def acao_registrar_emprestimo(self):
        try:
            id_usuario = int(self.ent_id_user.get())
            id_livro = int(self.ent_id_livro_emp.get())
        except ValueError:
            messagebox.showerror("Erro", "Os IDs informados devem ser numéricos.")
            return

        usuario = next((u for u in self.biblioteca.usuarios if u.id_usuario == id_usuario), None)
        livro = next((l for l in self.biblioteca.livros if l.id_livro == id_livro), None)

        if not usuario or not livro:
            messagebox.showerror("Erro", "Usuário ou Livro não encontrados no banco de dados.")
            return
        if not livro.disponivel:
            messagebox.showerror("Erro", "Este livro já se encontra emprestado.")
            return

        emprestimos_ativos_usuario = sum(1 for e in self.biblioteca.emprestimos if e["id_usuario"] == id_usuario)
        if emprestimos_ativos_usuario >= self.LIMITE_EMPRESTIMOS_POR_USUARIO:
            messagebox.showerror(
                "Limite Atingido",
                f"{usuario.nome} já possui {emprestimos_ativos_usuario} livro(s) emprestado(s).\n"
                f"O limite por usuário é de {self.LIMITE_EMPRESTIMOS_POR_USUARIO} exemplares simultâneos."
            )
            return

        self.biblioteca.registrar_emprestimo(id_usuario, id_livro)
        self.atualizar_tudo()
        self.ent_id_user.delete(0, tk.END)
        self.ent_id_livro_emp.delete(0, tk.END)
        messagebox.showinfo("Sucesso", "Empréstimo efetuado com sucesso!")

    def acao_registrar_devolucao(self):
        try:
            id_livro = int(self.ent_id_livro_dev.get())
        except ValueError:
            messagebox.showerror("Erro", "O ID do livro deve ser numérico.")
            return

        livro = next((l for l in self.biblioteca.livros if l.id_livro == id_livro), None)

        if not livro:
            messagebox.showerror("Erro", "Livro não localizado no acervo.")
            return
        if livro.disponivel:
            messagebox.showwarning("Aviso", "Este livro já consta como disponível no acervo.")
            return

        self.biblioteca.registrar_devolucao(id_livro)
        self.atualizar_tudo()
        self.ent_id_livro_dev.delete(0, tk.END)
        messagebox.showinfo("Sucesso", "Devolução registrada e acervo atualizado.")

    # ==================================================================
    # 5. PESQUISA DE LIVROS
    # ==================================================================
    def criar_tela_pesquisa(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(frame, text="Pesquisa de Livros no Acervo", font=self.fonte_secao).grid(
            row=0, column=0, sticky="w", pady=(0, 15))

        card_busca = ctk.CTkFrame(frame, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        card_busca.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        card_busca.grid_columnconfigure((0, 1), weight=1)

        bloco_titulo = ctk.CTkFrame(card_busca, fg_color="transparent")
        bloco_titulo.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(bloco_titulo, text="🔍 Pesquisar por Título", font=self.fonte_botoes).pack(anchor="w", pady=(0, 10))
        linha_titulo = ctk.CTkFrame(bloco_titulo, fg_color="transparent")
        linha_titulo.pack(fill="x")
        self.ent_pesquisa_titulo = ctk.CTkEntry(linha_titulo, placeholder_text="Digite o título do livro...", height=40, font=self.fonte_normal)
        self.ent_pesquisa_titulo.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_pesquisa_titulo.bind("<Return>", lambda e: self.acao_pesquisar_por_titulo())
        ctk.CTkButton(linha_titulo, text="Buscar", width=100, height=40, font=self.fonte_botoes,
                     fg_color=self.COR_DESTAQUE_AZUL, hover_color="#2563eb", command=self.acao_pesquisar_por_titulo).pack(side="left")

        bloco_autor = ctk.CTkFrame(card_busca, fg_color="transparent")
        bloco_autor.grid(row=0, column=1, sticky="ew", padx=20, pady=20)
        ctk.CTkLabel(bloco_autor, text="🔍 Pesquisar por Autor", font=self.fonte_botoes).pack(anchor="w", pady=(0, 10))
        linha_autor = ctk.CTkFrame(bloco_autor, fg_color="transparent")
        linha_autor.pack(fill="x")
        self.ent_pesquisa_autor = ctk.CTkEntry(linha_autor, placeholder_text="Digite o nome do autor...", height=40, font=self.fonte_normal)
        self.ent_pesquisa_autor.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.ent_pesquisa_autor.bind("<Return>", lambda e: self.acao_pesquisar_por_autor())
        ctk.CTkButton(linha_autor, text="Buscar", width=100, height=40, font=self.fonte_botoes,
                     fg_color=self.COR_DESTAQUE_AZUL, hover_color="#2563eb", command=self.acao_pesquisar_por_autor).pack(side="left")

        btn_limpar = ctk.CTkButton(frame, text="✕ Limpar filtros e exibir todo o acervo", width=260, height=32,
                                   font=ctk.CTkFont(family="Segoe UI", size=12), fg_color="transparent",
                                   text_color=(self.COR_DESTAQUE_AZUL, "#93c5fd"), hover_color=("#e2e8f0", "#2d2d3d"),
                                   command=self.acao_limpar_pesquisa)
        btn_limpar.grid(row=2, column=0, sticky="w", pady=(0, 10))

        self.lbl_pesquisa_status = ctk.CTkLabel(frame, text="Exibindo todo o acervo agrupado por título.",
                                                font=self.fonte_normal, text_color=("gray40", "#a6adc8"))
        self.lbl_pesquisa_status.grid(row=2, column=0, sticky="e", padx=(0, 5))

        self.area_resultados_pesquisa = ctk.CTkScrollableFrame(frame, label_text="RESULTADOS",
                                                                label_font=self.fonte_botoes, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        self.area_resultados_pesquisa.grid(row=3, column=0, sticky="nsew")

        self.atualizar_resultados_pesquisa()
        return frame

    def acao_pesquisar_por_titulo(self):
        termo = self.ent_pesquisa_titulo.get().strip()
        self.ent_pesquisa_autor.delete(0, tk.END)
        self._modo_pesquisa_atual = ("titulo", termo)
        self.atualizar_resultados_pesquisa()

    def acao_pesquisar_por_autor(self):
        termo = self.ent_pesquisa_autor.get().strip()
        self.ent_pesquisa_titulo.delete(0, tk.END)
        self._modo_pesquisa_atual = ("autor", termo)
        self.atualizar_resultados_pesquisa()

    def acao_limpar_pesquisa(self):
        self.ent_pesquisa_titulo.delete(0, tk.END)
        self.ent_pesquisa_autor.delete(0, tk.END)
        self._modo_pesquisa_atual = ("todos", "")
        self.atualizar_resultados_pesquisa()

    def atualizar_resultados_pesquisa(self):
        if not hasattr(self, "area_resultados_pesquisa"):
            return
        for widget in self.area_resultados_pesquisa.winfo_children():
            widget.destroy()

        modo, termo = self._modo_pesquisa_atual

        if modo == "autor" and termo:
            resultados = self.biblioteca.pesquisar_por_autor(termo)
            self.lbl_pesquisa_status.configure(text=f'Resultados para autor: "{termo}"')
            if not resultados:
                self._exibir_mensagem_vazia_pesquisa("Nenhum autor encontrado com esse termo.")
                return
            for autor, grupos in resultados.items():
                ctk.CTkLabel(self.area_resultados_pesquisa, text=f"✍️  {autor}", font=self.fonte_botoes).pack(
                    anchor="w", pady=(12, 5), padx=10)
                for grupo in grupos:
                    self._criar_card_resultado_pesquisa(grupo)
            return

        if modo == "titulo" and termo:
            resultados = self.biblioteca.pesquisar_por_titulo(termo)
            self.lbl_pesquisa_status.configure(text=f'Resultados para título: "{termo}"')
        else:
            resultados = self.biblioteca.obter_titulos_agrupados()
            self.lbl_pesquisa_status.configure(text="Exibindo todo o acervo agrupado por título.")

        if not resultados:
            self._exibir_mensagem_vazia_pesquisa("Nenhum título encontrado com esse termo.")
            return
        for grupo in resultados:
            self._criar_card_resultado_pesquisa(grupo)

    def _exibir_mensagem_vazia_pesquisa(self, texto):
        ctk.CTkLabel(self.area_resultados_pesquisa, text=texto, font=self.fonte_normal,
                    text_color=("gray40", "#a6adc8")).pack(pady=30)

    def _criar_card_resultado_pesquisa(self, grupo):
        card = ctk.CTkFrame(self.area_resultados_pesquisa, fg_color=("#f8fafc", "#181825"), corner_radius=8,
                            border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        card.pack(fill="x", pady=5, padx=5)
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(card, text=grupo["titulo"], font=self.fonte_botoes,
                    text_color=(self.COR_DESTAQUE_AZUL, "white"), anchor="w").grid(
            row=0, column=0, sticky="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(card, text=f"Autor: {grupo['autor']}", font=self.fonte_normal, anchor="w",
                    text_color=("gray40", "#a6adc8")).grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))

        info = f"Exemplares: {grupo['total']}   |   Disponíveis: {grupo['disponiveis']}   |   Emprestados: {grupo['emprestados']}"
        cor_info = self.COR_SUCESSO_VERDE if grupo["disponiveis"] > 0 else self.COR_ALERTA_VERMELHO
        ctk.CTkLabel(card, text=info, font=self.fonte_botoes, text_color=cor_info).grid(
            row=0, column=1, rowspan=2, sticky="e", padx=15)

    # ==================================================================
    # 6. HISTÓRICO DE EMPRÉSTIMOS
    # ==================================================================
    def criar_tela_historico(self):
        frame = ctk.CTkFrame(self.container_conteudo, fg_color="transparent")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(frame, text="Histórico de Empréstimos", font=self.fonte_secao).grid(
            row=0, column=0, sticky="w", pady=(0, 15))

        self.card_lista_historico = ctk.CTkScrollableFrame(frame, label_text="MOVIMENTAÇÕES REGISTRADAS",
                                                            label_font=self.fonte_botoes, border_width=1, border_color=("#e2e8f0", "#2d2d3d"))
        self.card_lista_historico.grid(row=1, column=0, sticky="nsew")

        self.atualizar_historico()
        return frame

    def atualizar_historico(self):
        if not hasattr(self, "card_lista_historico"):
            return
        for widget in self.card_lista_historico.winfo_children():
            widget.destroy()

        header_frame = ctk.CTkFrame(self.card_lista_historico, fg_color=("#e2e8f0", "#2d2d3d"), corner_radius=4)
        header_frame.pack(fill="x", pady=2)
        ctk.CTkLabel(header_frame, text="LIVRO", font=self.fonte_botoes, width=250, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="USUÁRIO", font=self.fonte_botoes, width=190, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="EMPRÉSTIMO", font=self.fonte_botoes, width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="DEVOLUÇÃO", font=self.fonte_botoes, width=150, anchor="w").pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="STATUS", font=self.fonte_botoes, width=120).pack(side="right", padx=10)

        historico_ordenado = sorted(self.biblioteca.historico, key=lambda h: h["id"], reverse=True)

        if not historico_ordenado:
            ctk.CTkLabel(self.card_lista_historico, text="Nenhuma movimentação registrada ainda.",
                        font=self.fonte_normal, text_color=("gray40", "#a6adc8")).pack(pady=30)
            return

        for h in historico_ordenado:
            row = ctk.CTkFrame(self.card_lista_historico, fg_color="transparent")
            row.pack(fill="x", pady=1)

            ctk.CTkLabel(row, text=h["titulo"], font=self.fonte_normal, width=250, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=h["nome_usuario"], font=self.fonte_normal, width=190, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=h["data_emprestimo"], font=self.fonte_normal, width=150, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(row, text=h["data_devolucao"] or "—", font=self.fonte_normal, width=150, anchor="w").pack(side="left", padx=10)

            status_cor = self.COR_ALERTA_VERMELHO if h["status"] == "Emprestado" else self.COR_SUCESSO_VERDE
            ctk.CTkLabel(row, text=h["status"], font=self.fonte_botoes, text_color=status_cor, width=120).pack(side="right", padx=10)


if __name__ == "__main__":
    root = ctk.CTk()
    app = BibliotecaUI(root)
    root.mainloop()
