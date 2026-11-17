from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from maquina import MaquinaCafe, CARDAPIO

app = FastAPI(title="API Máquina de Café", version="1.0.0")

# Instância única da máquina rodando na memória (para testes)
maquina = MaquinaCafe()

# Modelos de entrada de dados


class CreditoRequest(BaseModel):
    valor: float


class PedidoRequest(BaseModel):
    produtoId: int
    acucar: int


# Mapeamento do Cardápio para os IDs do enunciado
MAPA_PRODUTOS = {
    1: "Café expresso",
    2: "Café longo",
    3: "Café com leite",
    4: "Cappuccino",
    5: "Chocolate quente"
}

# Tratamento global de erros para retornar os códigos HTTP corretos


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    msg = str(exc)
    if "inexistente" in msg:
        status = 404
    elif "Crédito insuficiente" in msg:
        status = 402
    elif "Estoque insuficiente" in msg:
        status = 409
    else:
        status = 400  # Dados inválidos (ex: açúcar fora do limite)
    return JSONResponse(status_code=status, content={"erro": "REGRA_NEGOCIO", "mensagem": msg})


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    msg = str(exc)
    if "preparando outra bebida" in msg:
        return JSONResponse(status_code=409, content={"erro": "MAQUINA_OCUPADA", "mensagem": msg})
    return JSONResponse(status_code=400, content={"erro": "ERRO_REQUISICAO", "mensagem": msg})

# --- Rotas (Endpoints) ---


@app.get("/produtos")
def listar_produtos():
    produtos = []
    for prod_id, nome in MAPA_PRODUTOS.items():
        if nome in CARDAPIO:
            produtos.append({
                "id": prod_id,
                "nome": nome,
                "preco": CARDAPIO[nome]["preco"],
                "tempo_preparo": CARDAPIO[nome]["tempo"],
                "disponivel": True  # O ideal será checar o estoque real futuramente
            })
    return produtos


@app.get("/status")
def consultar_status():
    maquina.estado.atualizar_status()  # Atualiza o relógio dinâmico
    return {
        "estado": type(maquina.estado).__name__.replace("Estado", "").upper(),
        "credito": maquina.credito
    }


@app.post("/credito")
def inserir_credito(req: CreditoRequest):
    maquina.inserir_credito(req.valor)
    return {"credito": maquina.credito}


@app.post("/pedidos", status_code=201)
def criar_pedido(req: PedidoRequest):
    bebida = MAPA_PRODUTOS.get(req.produtoId)
    if not bebida:
        raise ValueError("Bebida inexistente.")

    status = maquina.estado.fazer_pedido(bebida, req.acucar)

    return {
        "produto": bebida,
        "acucar": req.acucar,
        "status": status.upper().replace(" ", "_"),
        "creditoRestante": maquina.credito
    }


@app.post("/troco")
def pedir_troco():
    valor_devolvido = maquina.credito
    maquina.credito = 0.0
    return {"valorDevolvido": valor_devolvido, "credito": 0.0}
