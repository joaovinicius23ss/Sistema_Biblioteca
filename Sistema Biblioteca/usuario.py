class Usuario:

    def __init__(self, id_usuario, nome, data_cadastro=None):
        self.id_usuario = id_usuario
        self.nome = nome
        self.data_cadastro = data_cadastro

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nome": self.nome,
            "data_cadastro": self.data_cadastro,
        }

    def __repr__(self):
        return f"<Usuario #{self.id_usuario} '{self.nome}'>"
