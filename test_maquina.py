import pytest
from maquina import MaquinaCafe
from unittest.mock import patch


def test_maquina_inicia_pronta():
    maquina = MaquinaCafe()
    assert type(maquina.estado).__name__ == "EstadoPronta"


def test_cancelar_pedido_maquina_pronta_falha():
    maquina = MaquinaCafe()
    # RN05: Cancelamento só é permitido no estado EM_PREPARO
    with pytest.raises(Exception, match="Nenhum pedido em preparo"):
        maquina.estado.cancelar_pedido()


def test_fazer_pedido_muda_para_preparando():
    maquina = MaquinaCafe()
    # Inserindo crédito para cobrir o expresso (R$ 4,00)
    maquina.inserir_credito(5.00)
    # RN04: Ao receber pedido, a máquina passa a PREPARANDO
    resultado = maquina.estado.fazer_pedido("Café expresso", 2)
    assert resultado == "Pedido em preparo"
    assert type(maquina.estado).__name__ == "EstadoPreparando"


def test_inserir_credito_valido():
    maquina = MaquinaCafe()
    maquina.inserir_credito(5.00)
    assert maquina.credito == 5.00


def test_inserir_credito_invalido_falha():
    maquina = MaquinaCafe()
    # RN01: Apenas 0.50, 1.00, 2.00, 5.00, 10.00, 20.00
    with pytest.raises(ValueError, match="Valor não aceito"):
        maquina.inserir_credito(3.00)


def test_pedido_sem_credito_falha():
    maquina = MaquinaCafe()
    # A máquina inicia com 0.00 de crédito
    with pytest.raises(ValueError, match="Crédito insuficiente"):
        maquina.estado.fazer_pedido("Café expresso", 2)


def test_estoque_inicial_completo():
    maquina = MaquinaCafe()
    assert maquina.estoque["agua"] == 2000
    assert maquina.estoque["cafe"] == 500
    assert maquina.estoque["copos"] == 50


def test_pedido_invalido_acucar_falha():
    maquina = MaquinaCafe()
    maquina.inserir_credito(10.00)
    # RN02: Açúcar deve ser de 0 a 3 porções
    with pytest.raises(ValueError, match="Açúcar deve ser de 0 a 3 porções"):
        maquina.estado.fazer_pedido("Café expresso", 4)


def test_pedido_sem_estoque_falha():
    maquina = MaquinaCafe()
    maquina.inserir_credito(10.00)
    # Simulando falta de água (expresso exige 40ml)
    maquina.estoque["agua"] = 20

    with pytest.raises(ValueError, match="Estoque insuficiente"):
        maquina.estado.fazer_pedido("Café expresso", 0)


def test_pedido_sucesso_desconta_estoque_e_credito():
    maquina = MaquinaCafe()
    maquina.inserir_credito(10.00)

    # Pedido: Cappuccino (R$ 6.50) com 2 porções de açúcar (10g)
    # Receita: 40ml água, 8g café, 100ml leite, 5g chocolate, 1 copo
    maquina.estado.fazer_pedido("Cappuccino", 2)

    assert maquina.estoque["agua"] == 1960
    assert maquina.estoque["cafe"] == 492
    assert maquina.estoque["leite"] == 900
    assert maquina.estoque["chocolate"] == 395
    assert maquina.estoque["acucar"] == 290
    assert maquina.estoque["copos"] == 49

    # Crédito restante deve ser 10.00 - 6.50
    assert maquina.credito == 3.50
    assert type(maquina.estado).__name__ == "EstadoPreparando"


def test_verificar_status_conclui_preparo_automaticamente():
    maquina = MaquinaCafe()
    maquina.inserir_credito(5.00)

    with patch('time.time') as mock_time:
        # Fixamos o relógio inicial
        mock_time.return_value = 100.0

        # Pede um Expresso (tempo de preparo: 5 segundos)
        maquina.estado.fazer_pedido("Café expresso", 0)
        assert type(maquina.estado).__name__ == "EstadoPreparando"

        # Avançamos o relógio em 3 segundos (ainda não terminou)
        mock_time.return_value = 103.0
        maquina.estado.atualizar_status()
        assert type(maquina.estado).__name__ == "EstadoPreparando"

        # Avançamos o relógio para 6 segundos (já terminou)
        mock_time.return_value = 106.0
        maquina.estado.atualizar_status()

        # Deve ter voltado para o estado PRONTA automaticamente
        assert type(maquina.estado).__name__ == "EstadoPronta"
