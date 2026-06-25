import json
import os
from datetime import datetime
from collections import defaultdict

from livro import Livro
from usuario import Usuario


class GerenciadorBiblioteca:


    FORMATO_DATA = "%d/%m/%Y %H:%M"

    def __init__(self, arquivo_dados="dados.json"):
        self.arquivo_dados = arquivo_dados
        self.livros = []
        self.usuarios = []
        self.emprestimos = []   # Empréstimos ATIVOS (ainda não devolvidos)
        self.historico = []     # Histórico COMPLETO (ativos + já devolvidos)
        self.carregar_dados()

    # ------------------------------------------------------------------
    # CADASTROS
    # ------------------------------------------------------------------
    def _proximo_id_livro(self):
        return max((l.id_livro for l in self.livros), default=0) + 1

    def _proximo_id_usuario(self):
        return max((u.id_usuario for u in self.usuarios), default=0) + 1

    def _proximo_id_historico(self):
        return max((h["id"] for h in self.historico), default=0) + 1

    def cadastrar_livro(self, titulo, autor, quantidade=1):
        """
        Cadastra `quantidade` exemplares para o mesmo título/autor.
        Cada exemplar recebe um ID próprio, mas todos compartilham
        título e autor (permitindo agrupamento na pesquisa).
        """
        titulo = titulo.strip()
        autor = autor.strip()
        quantidade = max(1, int(quantidade))

        agora = datetime.now().strftime(self.FORMATO_DATA)
        novos_ids = []
        for _ in range(quantidade):
            id_livro = self._proximo_id_livro()
            novo_livro = Livro(id_livro, titulo, autor, disponivel=True,
                                id_usuario_atual=None, data_cadastro=agora)
            self.livros.append(novo_livro)
            novos_ids.append(id_livro)

        self.salvar_dados()
        print(f"{quantidade} exemplar(es) de '{titulo}' cadastrado(s)! IDs: {novos_ids}")
        return novos_ids

    def cadastrar_usuario(self, nome):
        nome = nome.strip()
        id_usuario = self._proximo_id_usuario()
        agora = datetime.now().strftime(self.FORMATO_DATA)
        novo_usuario = Usuario(id_usuario, nome, data_cadastro=agora)
        self.usuarios.append(novo_usuario)
        self.salvar_dados()
        print(f"Usuário '{nome}' cadastrado com sucesso! ID: {id_usuario}")
        return id_usuario

    # ------------------------------------------------------------------
    # EMPRÉSTIMOS / DEVOLUÇÕES
    # ------------------------------------------------------------------
    def registrar_emprestimo(self, id_usuario, id_livro):
        usuario = next((u for u in self.usuarios if u.id_usuario == id_usuario), None)
        livro = next((l for l in self.livros if l.id_livro == id_livro), None)

        if not usuario:
            print("Erro: Usuário não encontrado!")
            return False
        if not livro:
            print("Erro: Livro não encontrado!")
            return False
        if not livro.disponivel:
            print("Erro: Este livro já está emprestado!")
            return False

        agora = datetime.now().strftime(self.FORMATO_DATA)

        livro.disponivel = False
        livro.id_usuario_atual = id_usuario

        self.emprestimos.append({
            "id_usuario": id_usuario,
            "id_livro": id_livro,
            "data_emprestimo": agora,
        })

        self.historico.append({
            "id": self._proximo_id_historico(),
            "id_livro": id_livro,
            "titulo": livro.titulo,
            "autor": livro.autor,
            "id_usuario": id_usuario,
            "nome_usuario": usuario.nome,
            "data_emprestimo": agora,
            "data_devolucao": None,
            "status": "Emprestado",
        })

        self.salvar_dados()
        print(f"Sucesso: Livro '{livro.titulo}' emprestado para {usuario.nome}!")
        return True

    def registrar_devolucao(self, id_livro):
        livro = next((l for l in self.livros if l.id_livro == id_livro), None)

        if not livro:
            print("Erro: Livro não encontrado!")
            return False
        if livro.disponivel:
            print("Aviso: Este livro já consta como disponível na biblioteca.")
            return False

        agora = datetime.now().strftime(self.FORMATO_DATA)

        livro.disponivel = True
        livro.id_usuario_atual = None

        self.emprestimos = [e for e in self.emprestimos if e["id_livro"] != id_livro]

        # Atualiza o registro de histórico em aberto mais recente deste livro
        registro_aberto = next(
            (h for h in reversed(self.historico)
             if h["id_livro"] == id_livro and h["status"] == "Emprestado"),
            None
        )
        if registro_aberto:
            registro_aberto["data_devolucao"] = agora
            registro_aberto["status"] = "Devolvido"

        self.salvar_dados()
        print(f"Sucesso: Livro '{livro.titulo}' devolvido com sucesso!")
        return True

    def listar_livros_disponiveis(self):
        disponiveis = [l for l in self.livros if l.disponivel]
        if not disponiveis:
            print("\nNão há livros disponíveis no momento.")
            return
        print("\n=== LIVROS DISPONÍVEIS ===")
        for l in disponiveis:
            print(f"[{l.id_livro}] {l.titulo} - Autor: {l.autor}")

    # ------------------------------------------------------------------
    # ESTATÍSTICAS (DASHBOARD)
    # ------------------------------------------------------------------
    def obter_estatisticas_dashboard(self):
        total_exemplares = len(self.livros)
        disponiveis = sum(1 for l in self.livros if l.disponivel)
        emprestados = total_exemplares - disponiveis

        titulos_distintos = {(l.titulo.strip().lower(), l.autor.strip().lower())
                              for l in self.livros}

        taxa_ocupacao = (emprestados / total_exemplares * 100) if total_exemplares else 0.0

        return {
            "total_titulos": len(titulos_distintos),
            "total_exemplares": total_exemplares,
            "disponiveis": disponiveis,
            "emprestados": emprestados,
            "total_usuarios": len(self.usuarios),
            "total_emprestimos_realizados": len(self.historico),
            "taxa_ocupacao": round(taxa_ocupacao, 1),
        }

    def obter_emprestimos_por_usuario(self, limite=8):
        """Retorna [(nome_usuario, qtde_emprestimos_ativos), ...] ordenado desc."""
        contagem = defaultdict(int)
        for e in self.emprestimos:
            usuario = next((u for u in self.usuarios if u.id_usuario == e["id_usuario"]), None)
            nome = usuario.nome if usuario else f"Usuário #{e['id_usuario']}"
            contagem[nome] += 1

        resultado = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        return resultado[:limite]

    def obter_livros_mais_emprestados(self, limite=8):
        """Retorna [(titulo, qtde_total_de_emprestimos), ...] ordenado desc."""
        contagem = defaultdict(int)
        for h in self.historico:
            contagem[h["titulo"]] += 1

        resultado = sorted(contagem.items(), key=lambda x: x[1], reverse=True)
        return resultado[:limite]

    # ------------------------------------------------------------------
    # PESQUISA AGRUPADA DE EXEMPLARES
    # ------------------------------------------------------------------
    def _agrupar_livros(self, lista_livros):
        """Agrupa uma lista de exemplares (Livro) por título+autor."""
        grupos = {}
        for livro in lista_livros:
            chave = (livro.titulo.strip().lower(), livro.autor.strip().lower())
            if chave not in grupos:
                grupos[chave] = {
                    "titulo": livro.titulo,
                    "autor": livro.autor,
                    "ids": [],
                    "total": 0,
                    "disponiveis": 0,
                    "emprestados": 0,
                }
            grupo = grupos[chave]
            grupo["ids"].append(livro.id_livro)
            grupo["total"] += 1
            if livro.disponivel:
                grupo["disponiveis"] += 1
            else:
                grupo["emprestados"] += 1
        return sorted(grupos.values(), key=lambda g: g["titulo"].lower())

    def obter_titulos_agrupados(self):
        """Agrupamento de TODO o acervo (usado para listagens gerais)."""
        return self._agrupar_livros(self.livros)

    def pesquisar_por_titulo(self, termo):
        termo = termo.strip().lower()
        if not termo:
            return self.obter_titulos_agrupados()
        encontrados = [l for l in self.livros if termo in l.titulo.lower()]
        return self._agrupar_livros(encontrados)

    def pesquisar_por_autor(self, termo):
        termo = termo.strip().lower()
        if not termo:
            return {}
        encontrados = [l for l in self.livros if termo in l.autor.lower()]
        grupos = self._agrupar_livros(encontrados)

        # Reorganiza por autor (pode haver mais de um autor batendo com o termo)
        por_autor = defaultdict(list)
        for g in grupos:
            por_autor[g["autor"]].append(g)
        return dict(por_autor)

    # ------------------------------------------------------------------
    # PERSISTÊNCIA
    # ------------------------------------------------------------------
    def salvar_dados(self):
        dados = {
            "livros": [l.to_dict() for l in self.livros],
            "usuarios": [u.to_dict() for u in self.usuarios],
            "emprestimos": self.emprestimos,
            "historico": self.historico,
        }
        with open(self.arquivo_dados, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

    def carregar_dados(self):
        if not os.path.exists(self.arquivo_dados):
            return

        try:
            with open(self.arquivo_dados, 'r', encoding='utf-8') as f:
                dados = json.load(f)

                self.livros = [
                    Livro(
                        id_livro=l["id_livro"],
                        titulo=l["titulo"],
                        autor=l["autor"],
                        disponivel=l.get("disponivel", True),
                        id_usuario_atual=l.get("id_usuario_atual"),
                        data_cadastro=l.get("data_cadastro"),
                    )
                    for l in dados.get("livros", [])
                ]
                self.usuarios = [
                    Usuario(
                        id_usuario=u["id_usuario"],
                        nome=u["nome"],
                        data_cadastro=u.get("data_cadastro"),
                    )
                    for u in dados.get("usuarios", [])
                ]
                self.emprestimos = dados.get("emprestimos", [])
                self.historico = dados.get("historico", [])

            self._migrar_dados_legados()
        except Exception as exc:
            print(f"Aviso: Erro ao ler o arquivo de dados ({exc}). Iniciando sistema vazio.")

    def _migrar_dados_legados(self):
        """
        Garante compatibilidade com arquivos dados.json gerados pela versão
        anterior do sistema (sem id_usuario_atual, sem histórico, sem datas).
        """
        alterado = False

        # 1) Garante id_usuario_atual e datas de empréstimo coerentes
        for emp in self.emprestimos:
            emp.setdefault("data_emprestimo", "Não informado")

            livro = next((l for l in self.livros if l.id_livro == emp["id_livro"]), None)
            if livro and livro.id_usuario_atual is None:
                livro.id_usuario_atual = emp["id_usuario"]
                alterado = True


        ids_no_historico_aberto = {
            (h["id_livro"], h["status"]) for h in self.historico
        }
        for emp in self.emprestimos:
            chave = (emp["id_livro"], "Emprestado")
            if chave not in ids_no_historico_aberto:
                livro = next((l for l in self.livros if l.id_livro == emp["id_livro"]), None)
                usuario = next((u for u in self.usuarios if u.id_usuario == emp["id_usuario"]), None)
                if livro and usuario:
                    self.historico.append({
                        "id": self._proximo_id_historico(),
                        "id_livro": livro.id_livro,
                        "titulo": livro.titulo,
                        "autor": livro.autor,
                        "id_usuario": usuario.id_usuario,
                        "nome_usuario": usuario.nome,
                        "data_emprestimo": emp.get("data_emprestimo", "Não informado"),
                        "data_devolucao": None,
                        "status": "Emprestado",
                    })
                    alterado = True

        if alterado:
            self.salvar_dados()
