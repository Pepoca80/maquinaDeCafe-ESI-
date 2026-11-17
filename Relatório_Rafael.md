Relatório de Decisões de Projeto

Projeto: API REST de Máquina de Café

1. Visão Geral  
Este documento registra as definições iniciais de arquitetura e tecnologia para o desenvolvimento da API REST que simula o back-end de uma máquina de café automática. O objetivo principal do projeto é garantir um código limpo, testável e com clara separação de responsabilidades.

2. Decisões Tecnológicas  
Linguagem de Programação: Python  
Optamos pelo uso de Python. A linguagem permite focar de maneira direta e objetiva na lógica de negócio e oferece um rico ecossistema de bibliotecas e frameworks (como FastAPI ou Flask) que facilitam a criação da API REST, bem como a geração automática da documentação (Swagger). O ecossistema de testes (ex: Pytest) fornecerá o ferramental adequado para atingir a meta de 75% de cobertura de código exigida no escopo.

3. Arquitetura e Padrões de Projeto  
Padrão Adotado: State (Estado)  
Problema Identificado: O comportamento da máquina de café muda drasticamente de acordo com o seu contexto atual. Existem quatro estados principais: PRONTA, PREPARANDO, AGUARDANDO_LIMPEZA e MANUTENCAO. 

Operações como "fazer um pedido", "entrar em manutenção" ou "cancelar pedido" têm regras de validação distintas dependendo do momento.

Implementar isso com estruturas condicionais tradicionais (if/else) nos serviços geraria um  
código complexo, frágil e difícil de testar e escalar.

Solução: A aplicação do padrão State. Foi criada uma interface base (EstadoMaquina) que  
define os comportamentos esperados, e classes concretas (como EstadoPronta) que  
encapsulam as regras específicas do respectivo contexto.

Benefícios:  
Isolamento de Responsabilidades (Single Responsibility Principle): Cada estado gerencia  
apenas as suas próprias transições.  
Manutenibilidade: A inclusão de novas regras de bloqueio (ex: recusar pedidos durante a  
limpeza) afetará apenas a classe correspondente.  
Testabilidade: Fica mais simples escrever testes unitários independentes para cada fase  
operacional da máquina.

4. Próximos Passos (Back-log Imediato)

* Definir o framework Web (FastAPI ou Flask) para orquestrar os endpoints HTTP.  
* Configurar o banco de dados (SQLite ou PostgreSQL via SQLAlchemy) para persistir o estoque, o saldo e o estado da máquina entre as reinicializações.  
* Implementar e documentar os demais estados concretos (EstadoPreparando, EstadoAguardandoLimpeza e EstadoManutencao).

5. Metodologia de Desenvolvimento (TDD)  
Test-Driven Development (Desenvolvimento Orientado a Testes)  
Para garantir o cumprimento do requisito de 75% de cobertura de código e a correta aplicação das regras de negócio (RNs) sem acoplamento, optou-se pela adoção do TDD. O ciclo consiste em escrever o teste antes da funcionalidade, garantindo que o código de produção seja concebido estritamente para satisfazer os requisitos do domínio.

Exemplo Prático: Transições de Estado  
O primeiro ciclo TDD validou o estado inicial da máquina e o bloqueio de cancelamentos indevidos (RN04 e RN05). Abaixo, os testes propostos e a implementação mínima para satisfazê-los.

* Casos de Teste (test\_maquina.py):

import pytest  
from maquina import MaquinaCafe

def test_maquina_inicia_pronta():  
    maquina = MaquinaCafe()  
    assert type(maquina.estado).__name__ == "EstadoPronta"

def test_cancelar_pedido_maquina_pronta_falha():  
    maquina = MaquinaCafe()  
    # RN05: Cancelamento só é permitido no estado EM\_PREPARO  
    with pytest.raises(Exception, match="Nenhum pedido em preparo"):  
        maquina.estado.cancelar_pedido()

def test_fazer_pedido_muda_para_preparando():  
    maquina = MaquinaCafe()  
    # RN04: Ao receber pedido, a máquina passa a PREPARANDO  
    resultado = maquina.estado.fazer_pedido("Café expresso", 2)  
    assert resultado == "Pedido em preparo"  
    assert type(maquina.estado).__name__ == "EstadoPreparando"

* Implementação Mínima (maquina.py):

from abc import ABC, abstractmethod

class MaquinaCafe:  
    def __init__(self):  
        self.estado = EstadoPronta(self)

    def mudar_estado(self, novo_estado):  
        self.estado = novo_estado

class EstadoMaquina(ABC):  
    def __init__(self, maquina: MaquinaCafe):  
        self.maquina = maquina

    @abstractmethod  
    def fazer_pedido(self, bebida, acucar): pass

    @abstractmethod  
    def cancelar_pedido(self): pass

class EstadoPronta(EstadoMaquina):  
    def fazer_pedido(self, bebida, acucar):  
        self.maquina.mudar_estado(EstadoPreparando(self.maquina))  
        return "Pedido em preparo"

    def cancelar_pedido(self):  
        raise Exception("Nenhum pedido em preparo para cancelar.")

class EstadoPreparando(EstadoMaquina):  
    def fazer_pedido(self, bebida, acucar):  
        raise Exception("A máquina está preparando outra bebida.")

    def cancelar_pedido(self):  
        self.maquina.mudar_estado(EstadoPronta(self.maquina))  
        return "Pedido cancelado"

5.1. Evolução do TDD: Identificação e Correção de Regressões  
Durante a implementação do controle de saldo (RN01 e RN02), o método TDD demonstrou sua eficácia na prevenção de regressões. Ao introduzir a trava de segurança que bloqueia pedidos sem saldo suficiente, o teste original que validava a mudança para o estado `PREPARANDO\` (`test_fazer_pedido_muda_para_preparando`) falhou com a exceção `ValueError: Crédito insuficiente`.

Como o teste instanciava a máquina com o saldo inicial zerado, a nova regra de negócio agiu corretamente ao barrar a operação. Essa falha imediata serviu como validação de que o sistema protege suas próprias regras. Para adequar a suíte de testes à nova realidade do domínio, o teste foi refatorado inserindo o crédito necessário antes do pedido:

def test_fazer_pedido_muda_para_preparando():  
    maquina \= MaquinaCafe()  
    # Pré-condição atualizada (RN01): Inserção de crédito para cobrir a bebida  
    maquina.inserir_credito(5.00)   
      
    \# RN04: Ao receber pedido, a máquina passa a PREPARANDO  
    resultado = maquina.estado.fazer_pedido("Café expresso", 2)  
      
    assert resultado == "Pedido em preparo"  
    assert type(maquina.estado).__name__ == "EstadoPreparando"

Essa dinâmica comprova a maturidade da arquitetura, onde a adição de novas restrições de negócio alerta imediatamente os desenvolvedores sobre a necessidade de atualizar os fluxos e as pré-condições do sistema.

6. Modelagem de Domínio: Cardápio e Estoque  
6.1. Estratégia de Testes (TDD)  
A segunda fase de implementação focou na parametrização das receitas e no controle de capacidade dos reservatórios, garantindo o cumprimento da RN02 (validação de ingredientes) e RN03 (débito em estoque e crédito).

Os testes foram desenhados para cobrir os cenários de limite máximo e mínimo exigidos pelo escopo, mapeando comportamentos críticos:

* Validação do estoque inicial com capacidade máxima (ex: 2000ml de água, 500g de café, 50 copos).  
* Bloqueio de pedidos com parâmetros inválidos (ex: açúcar fora do limite de 0 a 3 porções).  
* Bloqueio de pedidos por falta de insumos (simulando falha ao pedir um expresso com apenas 20ml de água no reservatório).  
* Efetivação do pedido com sucesso, verificando o débito exato dos ingredientes, desconto no crédito e transição para o estado de preparo.

6.2. Implementação e Padrões Aplicados  
Para satisfazer os testes, o domínio foi atualizado adotando uma variação simplificada do padrão Strategy/Factory através de um dicionário estático (CARDAPIO).

* Encapsulamento de Receitas: O dicionário centraliza as necessidades de água, café, leite, chocolate, tempo de preparo e preço de cada uma das 5 bebidas. Isso eliminou a necessidade de múltiplas condicionais.  
* Validação Transacional: No método fazer_pedido da classe EstadoPronta, a validação de crédito e estoque ocorre em bloco antes de qualquer alteração de estado. Se qualquer insumo faltar, uma exceção ValueError é lançada.  
* Débito Integrado: Após a aprovação das regras de negócio, os ingredientes consumidos e o valor da bebida são subtraídos atomicamente, seguidos pela transição da máquina para o EstadoPreparando.

7. Controle de Tempo e Concorrência (RN04)

* Problema: A especificação exige que a máquina fique no estado `PREPARANDO` durante o tempo da receita, recusando novos pedidos. O uso de funções de pausa como `time.sleep()` bloquearia a *thread* principal do servidor web, impedindo que outras requisições (como a consulta de status) fossem processadas.
* Solução: Foi implementado um cálculo dinâmico de tempo. Ao iniciar o preparo, a máquina registra o *timestamp* atual somado ao tempo da receita (`previsao_termino = time.time() + receita["tempo"]`). O método `atualizar_status()` foi adicionado à interface do padrão State. Quando o estado atual é `EstadoPreparando`, esse método verifica se o relógio do sistema já ultrapassou a previsão. Se sim, ele devolve a máquina automaticamente para `EstadoPronta`.
* TDD: A funcionalidade foi validada utilizando o módulo `unittest.mock.patch` para simular (falsificar) o avanço do relógio do sistema durante o teste, garantindo a cobertura da mudança automática de estado sem atrasar a execução da suíte de testes.

8. Camada de API (HTTP) e Documentação Automática

* Framework e Roteamento: A camada web foi construída utilizando **FastAPI**, integrando a classe de domínio `MaquinaCafe` aos endpoints REST exigidos (`/produtos`, `/status`, `/credito`, `/pedidos`, `/troco`). A escolha desse *framework* cumpriu instantaneamente o requisito de documentação da API, gerando a interface interativa Swagger UI nativamente na rota `/docs`.
* Tratamento Global de Exceções: Para manter o princípio de separação de responsabilidades, as regras de negócio não conhecem códigos HTTP. Em vez disso, foram implementados *Exception Handlers* globais no FastAPI. Exceções puras de Python (`ValueError` e `Exception`) lançadas pelo domínio são interceptadas pelo controlador e convertidas nas respostas mapeadas na especificação:
* 400 (Bad Request): Dados inválidos (ex: açúcar fora do limite).
* 402 (Payment Required): Crédito insuficiente.
* 404 (Not Found): Bebida inexistente no cardápio.
* 409 (Conflict): Falta de estoque de insumos ou máquina já ocupada em preparo.



9. Expansão do Padrão State (Limpeza e Manutenção)

Seguindo o ciclo TDD de falha e correção, a arquitetura baseada em estados foi expandida para contemplar a RN07 (Limpeza Obrigatória a cada 30 preparos) e a RN08 (Manutenção).

* A interface `EstadoMaquina` foi enriquecida com os métodos `entrar_manutencao`, `sair_manutencao` e `registrar_limpeza`.
* As novas classes `EstadoAguardandoLimpeza` e `EstadoManutencao` foram criadas. Ambas bloqueiam a função `fazer_pedido`. A primeira restringe o uso até que um operador realize a limpeza, e a segunda permite o reabastecimento.
* Benefício Comprovado: A adição dessas duas novas fases operacionais complexas foi feita sem quebrar ou alterar a lógica interna das classes `EstadoPronta` e `EstadoPreparando`, comprovando a eficácia e a escalabilidade do padrão de projeto escolhido.

10. Próximos Passos (Back-log Atualizado)

* Rotas do Operador e Autenticação (RN11): Criar os endpoints administrativos (`/operador/*`) com exigência de token (configurado via variáveis de ambiente) para alterar preços, repor estoque e acionar as recém-criadas funções de manutenção e limpeza.
* Camada de Persistência (Repository): Substituir o dicionário de estoque e a variável de crédito salvos na memória RAM por um banco de dados relacional (SQLite/PostgreSQL) gerenciado pelo SQLAlchemy, garantindo que a máquina sobreviva a reinicializações.
* Módulo de Relatórios (RN12): Utilizar o histórico de pedidos persistido no banco para construir a consulta de faturamento e vendas por período, finalizando os endpoints da API.

11. Implementação da Limpeza Obrigatória (RN07) e Manutenção (RN08)
Para concluir as transições do padrão State, foram incorporados o contador de preparos e as regras restritas ao operador.

* Controle de Ciclo de Vida: A classe MaquinaCafe recebeu a propriedade contador_preparos. A cada bebida concluída, o contador é incrementado. O método atualizar_status() do EstadoPreparando foi refatorado: ao atingir 30 preparos no término do tempo da receita, a máquina transita autonomamente para EstadoAguardandoLimpeza em vez de retornar para EstadoPronta.

* Regras de Reabastecimento (RN09): Foi implementado o método reabastecer(), que valida a capacidade máxima de cada reservatório. A operação só é permitida se a máquina estiver no EstadoManutencao, garantindo o bloqueio de acessos indevidos.

11.1. Evolução do TDD: Isolamento de Estado e Ciclo de Vida Interno
Durante a validação do bloqueio por necessidade de limpeza (RN07), o ciclo TDD evidenciou falhas na construção do cenário de teste que desrespeitavam o encapsulamento do domínio.

* Interferência de Regras Externas (ValueError: Valor não aceito): A primeira versão do teste falhou ao tentar inserir R$ 50.00 de crédito em uma única operação. A trava de segurança da RN01 bloqueou a ação. Para isolar o teste (que deveria focar apenas na limpeza), o estado inicial foi injetado diretamente na memória da instância (maquina.credito = 150.00), desvinculando o teste da RN07 das restrições da RN01.

* Quebra da Máquina de Estados (Failed: DID NOT RAISE Exception): A segunda versão do teste iterou 30 pedidos forçando a mudança de estado de fora para dentro (maquina.mudar_estado(EstadoPronta(maquina))). Isso burlou o ciclo de vida interno, ignorando a verificação embutida no método atualizar_status() e impedindo a transição correta para a limpeza.

Solução Arquitetural no Teste: O cenário foi refatorado para respeitar o encapsulamento do padrão State. Simulou-se o 30º preparo instanciando a máquina diretamente no EstadoPreparando, manipulando o tempo artificialmente (previsao_termino = time.time() - 1) e acionando o método interno atualizar_status(). A transição correta para EstadoAguardandoLimpeza ocorreu naturalmente, provando que as regras de negócio estão íntegras, blindadas e não dependem de orquestração externa.

12. Próximos Passos (Back-log Atualizado)

* Rotas do Operador e Autenticação (RN11): Implementar os endpoints administrativos no FastAPI (/operador/estoque, /operador/manutencao, /operador/limpeza) protegidos por autenticação via token (configurado em variável de ambiente).

* Camada de Persistência (Repository): Configurar o SQLAlchemy em banco de dados relacional para persistir o nível de estoque, o saldo e o estado, garantindo sobrevivência a reinicializações.

* Módulo de Relatórios (RN12): Estruturar a modelagem de dados dos pedidos consolidados para viabilizar a consulta gerencial de faturamento e vendas por período.