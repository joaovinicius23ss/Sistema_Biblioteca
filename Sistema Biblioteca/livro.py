class Livro:
    """
    Representa um exemplar físico de um livro no acervo.

    Vários exemplares podem compartilhar o mesmo título/autor (quando o
    bibliotecário cadastra "Quantidade de Exemplares" > 1). Cada exemplar
    possui seu próprio ID e seu próprio status de disponibilidade.
    """

    def __init__(self, id_livro, titulo, autor, disponivel=True,
                 id_usuario_atual=None, data_cadastro=None):
        self.id_livro = id_livro
        self.titulo = titulo
        self.autor = autor
        self.disponivel = disponivel
        # ID do usuário que está com o exemplar emprestado (None se disponível)
        self.id_usuario_atual = id_usuario_atual
        # Data em que o exemplar foi cadastrado no acervo
        self.data_cadastro = data_cadastro

    def to_dict(self):
        return {
            "id_livro": self.id_livro,
            "titulo": self.titulo,
            "autor": self.autor,
            "disponivel": self.disponivel,
            "id_usuario_atual": self.id_usuario_atual,
            "data_cadastro": self.data_cadastro,
        }

    def __repr__(self):
        status = "Disponível" if self.disponivel else "Emprestado"
        return f"<Livro #{self.id_livro} '{self.titulo}' ({status})>"
