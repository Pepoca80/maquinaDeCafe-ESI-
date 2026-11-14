import time
from abc import ABC, abstractmethod

# Dicionário centralizando as receitas, preços e tempos (Padrão Strategy/Factory simplificado)
CARDAPIO = {
    "Café expresso": {"agua": 40, "cafe": 8, "leite": 0, "chocolate": 0, "tempo": 5, "preco": 4.00},
    "Café longo": {"agua": 120, "cafe": 8, "leite": 0, "chocolate": 0, "tempo": 8, "preco": 4.50},
    "Café com leite": {"agua": 40, "cafe": 8, "leite": 150, "chocolate": 0, "tempo": 10, "preco": 6.00},
    "Cappuccino": {"agua": 40, "cafe": 8, "leite": 100, "chocolate": 5, "tempo": 12, "preco": 6.50},
    "Chocolate quente": {"agua": 50, "cafe": 0, "leite": 120, "chocolate": 30, "tempo": 12, "preco": 7.00}
}


class MaquinaCafe:
    def __init__(self):
        self.estado = EstadoPronta(self)
        self.credito = 0.0
        self.previsao_termino = None
        self.estoque = {
            "agua": 2000,
            "cafe": 500,
            "leite": 1000,
            "chocolate": 400,
            "acucar": 300,
            "copos": 50
        }

    def mudar_estado(self, novo_estado):
        self.estado = novo_estado

    def inserir_credito(self, valor):
        valores_aceitos = [0.50, 1.00, 2.00, 5.00, 10.00, 20.00]
        if valor not in valores_aceitos:
            raise ValueError("Valor não aceito.")
        if self.credito + valor > 50.00:
            raise ValueError("Crédito limite excedido.")
        self.credito += valor


class EstadoMaquina(ABC):
    def __init__(self, maquina: MaquinaCafe):
        self.maquina = maquina

    @abstractmethod
    def fazer_pedido(self, bebida, acucar): pass

    @abstractmethod
    def cancelar_pedido(self): pass

    @abstractmethod
    def atualizar_status(self): pass


class EstadoPronta(EstadoMaquina):
    def fazer_pedido(self, bebida, acucar):
        if acucar < 0 or acucar > 3:
            raise ValueError("Açúcar deve ser de 0 a 3 porções.")

        if bebida not in CARDAPIO:
            raise ValueError("Bebida inexistente.")

        receita = CARDAPIO[bebida]

        if self.maquina.credito < receita["preco"]:
            raise ValueError("Crédito insuficiente.")

        necessidade_acucar = acucar * 5

        # Validação do estoque (RN02)
        if (self.maquina.estoque["agua"] < receita["agua"] or
            self.maquina.estoque["cafe"] < receita["cafe"] or
            self.maquina.estoque["leite"] < receita["leite"] or
            self.maquina.estoque["chocolate"] < receita["chocolate"] or
            self.maquina.estoque["acucar"] < necessidade_acucar or
                self.maquina.estoque["copos"] < 1):
            raise ValueError("Estoque insuficiente.")

        # Débito de ingredientes e crédito (RN03)
        self.maquina.estoque["agua"] -= receita["agua"]
        self.maquina.estoque["cafe"] -= receita["cafe"]
        self.maquina.estoque["leite"] -= receita["leite"]
        self.maquina.estoque["chocolate"] -= receita["chocolate"]
        self.maquina.estoque["acucar"] -= necessidade_acucar
        self.maquina.estoque["copos"] -= 1

        self.maquina.credito -= receita["preco"]
        self.maquina.previsao_termino = time.time() + receita["tempo"]
        self.maquina.mudar_estado(EstadoPreparando(self.maquina))
        return "Pedido em preparo"

    def cancelar_pedido(self):
        raise Exception("Nenhum pedido em preparo para cancelar.")

    def atualizar_status(self):
        pass  # Não faz nada se a máquina já está pronta


class EstadoPreparando(EstadoMaquina):
    def atualizar_status(self):
        # Verifica dinamicamente se o tempo já passou
        if self.maquina.previsao_termino and time.time() >= self.maquina.previsao_termino:
            self.maquina.previsao_termino = None
            self.maquina.mudar_estado(EstadoPronta(self.maquina))

    def fazer_pedido(self, bebida, acucar):
        self.atualizar_status()  # Dá um "refresh" antes de bloquear
        if type(self.maquina.estado).__name__ == "EstadoPronta":
            return self.maquina.estado.fazer_pedido(bebida, acucar)
        raise Exception("A máquina está preparando outra bebida.")

    def cancelar_pedido(self):
        self.maquina.previsao_termino = None
        self.maquina.mudar_estado(EstadoPronta(self.maquina))
        return "Pedido cancelado"
