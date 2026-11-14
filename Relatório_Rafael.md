Relatório de Decisões de Projeto

Projeto: API REST de Máquina de Café

1\. Visão Geral  
Este documento registra as definições iniciais de arquitetura e tecnologia para o desenvolvimento da API REST que simula o back-end de uma máquina de café automática. O objetivo principal do projeto é garantir um código limpo, testável e com clara separação de responsabilidades.

2\. Decisões Tecnológicas  
Linguagem de Programação: Python  
Optamos pelo uso de Python. A linguagem permite focar de maneira direta e objetiva na lógica de negócio e oferece um rico ecossistema de bibliotecas e frameworks (como FastAPI ou Flask) que facilitam a criação da API REST, bem como a geração automática da documentação (Swagger). O ecossistema de testes (ex: Pytest) fornecerá o ferramental adequado para atingir a meta de 75% de cobertura de código exigida no escopo.

3\. Arquitetura e Padrões de Projeto  
Padrão Adotado: State (Estado)  
Problema Identificado: O comportamento da máquina de café muda drasticamente de acordo com o seu contexto atual. Existem quatro estados principais: PRONTA, PREPARANDO, AGUARDANDO\_LIMPEZA e MANUTENCAO. 

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

4\. Próximos Passos (Back-log Imediato)

* Definir o framework Web (FastAPI ou Flask) para orquestrar os endpoints HTTP.  
* Configurar o banco de dados (SQLite ou PostgreSQL via SQLAlchemy) para persistir o estoque, o saldo e o estado da máquina entre as reinicializações.  
* Implementar e documentar os demais estados concretos (EstadoPreparando, EstadoAguardandoLimpeza e EstadoManutencao).

5\. Metodologia de Desenvolvimento (TDD)  
Test-Driven Development (Desenvolvimento Orientado a Testes)  
Para garantir o cumprimento do requisito de 75% de cobertura de código e a correta aplicação das regras de negócio (RNs) sem acoplamento, optou-se pela adoção do TDD. O ciclo consiste em escrever o teste antes da funcionalidade, garantindo que o código de produção seja concebido estritamente para satisfazer os requisitos do domínio.

Exemplo Prático: Transições de Estado  
O primeiro ciclo TDD validou o estado inicial da máquina e o bloqueio de cancelamentos indevidos (RN04 e RN05). Abaixo, os testes propostos e a implementação mínima para satisfazê-los.

* Casos de Teste (test\_maquina.py):

import pytest  
from maquina import MaquinaCafe

def test\_maquina\_inicia\_pronta():  
    maquina \= MaquinaCafe()  
    assert type(maquina.estado).\_\_name\_\_ \== "EstadoPronta"

def test\_cancelar\_pedido\_maquina\_pronta\_falha():  
    maquina \= MaquinaCafe()  
    \# RN05: Cancelamento só é permitido no estado EM\_PREPARO  
    with pytest.raises(Exception, match="Nenhum pedido em preparo"):  
        maquina.estado.cancelar\_pedido()

def test\_fazer\_pedido\_muda\_para\_preparando():  
    maquina \= MaquinaCafe()  
    \# RN04: Ao receber pedido, a máquina passa a PREPARANDO  
    resultado \= maquina.estado.fazer\_pedido("Café expresso", 2\)  
    assert resultado \== "Pedido em preparo"  
    assert type(maquina.estado).\_\_name\_\_ \== "EstadoPreparando"

* Implementação Mínima (maquina.py):

from abc import ABC, abstractmethod

class MaquinaCafe:  
    def \_\_init\_\_(self):  
        self.estado \= EstadoPronta(self)

    def mudar\_estado(self, novo\_estado):  
        self.estado \= novo\_estado

class EstadoMaquina(ABC):  
    def \_\_init\_\_(self, maquina: MaquinaCafe):  
        self.maquina \= maquina

    @abstractmethod  
    def fazer\_pedido(self, bebida, acucar): pass

    @abstractmethod  
    def cancelar\_pedido(self): pass

class EstadoPronta(EstadoMaquina):  
    def fazer\_pedido(self, bebida, acucar):  
        self.maquina.mudar\_estado(EstadoPreparando(self.maquina))  
        return "Pedido em preparo"

    def cancelar\_pedido(self):  
        raise Exception("Nenhum pedido em preparo para cancelar.")

class EstadoPreparando(EstadoMaquina):  
    def fazer\_pedido(self, bebida, acucar):  
        raise Exception("A máquina está preparando outra bebida.")

    def cancelar\_pedido(self):  
        self.maquina.mudar\_estado(EstadoPronta(self.maquina))  
        return "Pedido cancelado"

5.1. Evolução do TDD: Identificação e Correção de Regressões  
Durante a implementação do controle de saldo (RN01 e RN02), o método TDD demonstrou sua eficácia na prevenção de regressões. Ao introduzir a trava de segurança que bloqueia pedidos sem saldo suficiente, o teste original que validava a mudança para o estado \`PREPARANDO\` (\`test\_fazer\_pedido\_muda\_para\_preparando\`) falhou com a exceção \`ValueError: Crédito insuficiente\`.

Como o teste instanciava a máquina com o saldo inicial zerado, a nova regra de negócio agiu corretamente ao barrar a operação. Essa falha imediata serviu como validação de que o sistema protege suas próprias regras. Para adequar a suíte de testes à nova realidade do domínio, o teste foi refatorado inserindo o crédito necessário antes do pedido:

def test\_fazer\_pedido\_muda\_para\_preparando():  
    maquina \= MaquinaCafe()  
    \# Pré-condição atualizada (RN01): Inserção de crédito para cobrir a bebida  
    maquina.inserir\_credito(5.00)   
      
    \# RN04: Ao receber pedido, a máquina passa a PREPARANDO  
    resultado \= maquina.estado.fazer\_pedido("Café expresso", 2\)  
      
    assert resultado \== "Pedido em preparo"  
    assert type(maquina.estado).\_\_name\_\_ \== "EstadoPreparando"

Essa dinâmica comprova a maturidade da arquitetura, onde a adição de novas restrições de negócio alerta imediatamente os desenvolvedores sobre a necessidade de atualizar os fluxos e as pré-condições do sistema.

6\. Modelagem de Domínio: Cardápio e Estoque  
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
* Validação Transacional: No método fazer\_pedido da classe EstadoPronta, a validação de crédito e estoque ocorre em bloco antes de qualquer alteração de estado. Se qualquer insumo faltar, uma exceção ValueError é lançada.  
* Débito Integrado: Após a aprovação das regras de negócio, os ingredientes consumidos e o valor da bebida são subtraídos atomicamente, seguidos pela transição da máquina para o EstadoPreparando.

7\. Próximos Passos (Back-log Atualizado)

* Controle de Tempo e Concorrência (RN04): Implementar o registro de timestamp ao entrar no estado PREPARANDO, permitindo calcular dinamicamente o fim do preparo nas consultas de status, sem bloquear a thread da API com timers.  
* Camada HTTP (FastAPI): Iniciar o roteamento da API, acoplando a classe MaquinaCafe aos controladores web e mapeando as exceções de domínio para os códigos HTTP adequados (400, 402, 409).  
* Persistência (Repository): Configurar o banco de dados via SQLAlchemy para persistir o estado dos reservatórios e registrar o histórico de vendas.

8\. Próximos Passos: Persistência de Dados  
Para atender ao requisito de sobrevivência de dados após reinicializações, será implementada a camada de banco de dados.

* Padrão Repository: Todo acesso a dados será encapsulado em classes de repositório, garantindo a separação de responsabilidades. Os controladores não terão contato direto com o banco, e as entidades de negócio não farão queries.  
* Implementação: Utilização do ORM SQLAlchemy com SQLite (ou PostgreSQL). A persistência do histórico de pedidos finalizados será a base para o desenvolvimento do endpoint de relatórios gerenciais, que totalizará faturamento e consumo por período.

