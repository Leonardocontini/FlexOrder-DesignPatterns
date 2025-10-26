from abc import ABC, abstractmethod


class EstrategiaPagamento(ABC):
    @abstractmethod
    def processar_pagamento(self, valor: float) -> bool:
       
        pass

class PagamentoPix(EstrategiaPagamento):
    def processar_pagamento(self, valor: float) -> bool:
        print(f"Processando R${valor:.2f} via PIX...")
        print("   -> Pagamento com PIX APROVADO (QR Code gerado).")
        return True

class PagamentoCredito(EstrategiaPagamento):
    def processar_pagamento(self, valor: float) -> bool:
        print(f"Processando R${valor:.2f} via Cartão de Crédito...")
        if valor < 1000:
            print("   -> Pagamento com Credito APROVADO.")
            return True
        else:
            print("   -> Pagamento com Credito REJEITADO (limite excedido).")
            return False

class PagamentoEstrategia(EstrategiaPagamento):
    def processar_pagamento(self, valor: float) -> bool:
        print(f"Processando R${valor:.2f} via Transferência...")
        print("   -> Pagamento via transferencia APROVADO (requer 10 segundos de espera).")
        return True


class EstrategiaFrete(ABC):
    @abstractmethod
    def calcular(self, valor_com_desconto: float) -> float:

        pass

class FreteNormal(EstrategiaFrete):
    def calcular(self, valor_com_desconto: float) -> float:
        custo_frete = valor_com_desconto * 0.05
        print(f"Frete Normal: R${custo_frete:.2f}")
        return custo_frete

class FreteExpresso(EstrategiaFrete):
    def calcular(self, valor_com_desconto: float) -> float:
        custo_frete = valor_com_desconto * 0.10 + 15.00
        print(f"Frete Expresso (com taxa): R${custo_frete:.2f}")
        return custo_frete

class FreteTeletransporte(EstrategiaFrete):
    def calcular(self, valor_com_desconto: float) -> float:
        custo_frete = 50.00
        print(f"Frete Teletransporte: R${custo_frete:.2f}")
        return custo_frete


class CalculadorValor(ABC):
    @abstractmethod
    def calcular(self) -> float:
        
        pass

class CalculadorBasePedido(CalculadorValor):
    def __init__(self, pedido: "Pedido"):
        self.pedido = pedido

    def calcular(self) -> float:
        return self.pedido.valor_base

class CalculadorDecorador(CalculadorValor):
    def __init__(self, componente: CalculadorValor):
        self._componente = componente

    def calcular(self) -> float:
        return self._componente.calcular()


class DescontoPix(CalculadorDecorador):

    def __init__(self, componente: CalculadorValor, pedido: "Pedido"):
        super().__init__(componente)
        self.pedido = pedido

    def calcular(self) -> float:
        base = self._componente.calcular()
        if isinstance(self.pedido.pagamento, PagamentoPix):
            print("Aplicando 5% de desconto PIX.")
            return base * 0.95
        return base

class DescontoPedidoGrande(CalculadorDecorador):
    def __init__(self, componente: CalculadorValor, pedido: "Pedido"):
        super().__init__(componente)
        self.pedido = pedido

    def calcular(self) -> float:
        base = self._componente.calcular()
        if not isinstance(self.pedido.pagamento, PagamentoPix) and self.pedido.valor_base > 500:
            print("Aplicando 10% de desconto para pedidos grandes .")
            return base * 0.90
        return base

class TaxaEmbalagemPresente(CalculadorDecorador):
    def __init__(self, componente: CalculadorValor, pedido: "Pedido", taxa: float = 5.0):
        super().__init__(componente)
        self.pedido = pedido
        self.taxa = taxa

    def calcular(self) -> float:
        valor = self._componente.calcular()
        if self.pedido.tem_embalagem_presente:
            print(f"Adicionando R${self.taxa:.2f} de Embalagem de Presente.")
            return valor + self.taxa
        return valor


class SistemaEstoque:
    def registrar_pedido(self, pedido: "Pedido"):
  
        print("SistemaEstoque: Registrando itens no estoque .")

class GeradorNotaFiscal:
    def gerar(self, pedido: "Pedido", valor: float):
    
        print(f"GeradorNotaFiscal: Nota fiscal gerada para valor R${valor:.2f}.")


class CheckoutFacade:
    def __init__(self):
        self.estoque = SistemaEstoque()
        self.gerador_nf = GeradorNotaFiscal()

    def concluir_transacao(self, pedido: "Pedido") -> bool:
        print("=========================================")
        print("Iniciando processo de checkout...")
        print("=========================================")

        calculador_base = CalculadorBasePedido(pedido)
        calculador_desconto = calculador_base
        if isinstance(pedido.pagamento, PagamentoPix):
            calculador_desconto = DescontoPix(calculador_desconto, pedido=pedido)
        elif pedido.valor_base > 500:
            calculador_desconto = DescontoPedidoGrande(calculador_desconto, pedido=pedido)

        valor_apos_desconto = calculador_desconto.calcular()

        custo_frete = pedido.frete.calcular(valor_apos_desconto)

        calculador_completo = calculador_desconto
        if pedido.tem_embalagem_presente:
            calculador_completo = TaxaEmbalagemPresente(calculador_completo, pedido=pedido)

        valor_final = calculador_completo.calcular() + custo_frete

        print(f"\nValor a Pagar: R${valor_final:.2f}")


        if pedido.pagamento.processar_pagamento(valor_final):

            self.estoque.registrar_pedido(pedido)
            self.gerador_nf.gerar(pedido, valor_final)
            print("\nSUCESSO: Pedido finalizado e registrado no estoque.")
            return True
        else:
            print("\nFALHA: Transação abortada.")
            return False


class Pedido:
    def __init__(
        self,
        itens: list,
        estrategia_pagamento: EstrategiaPagamento,
        estrategia_frete: EstrategiaFrete,
        tem_embalagem_presente: bool = False
    ):
        self.itens = itens
        self.pagamento = estrategia_pagamento
        self.frete = estrategia_frete
        self.valor_base = sum(item['valor'] for item in itens)
        self.tem_embalagem_presente = tem_embalagem_presente

    
    def set_pagamento(self, nova_estrategia: EstrategiaPagamento):
        self.pagamento = nova_estrategia

    def set_frete(self, nova_estrategia: EstrategiaFrete):
        self.frete = nova_estrategia


    def finalizar_compra(self) -> bool:
        facade = CheckoutFacade()
        return facade.concluir_transacao(self)


if __name__ == "__main__":
    itens_p1 = [
        {'nome': 'Capa da Invisibilidade', 'valor': 150.0},
        {'nome': 'Poção de Voo', 'valor': 80.0}
    ]
    pedido1 = Pedido(
        itens_p1,
        estrategia_pagamento=PagamentoPix(),
        estrategia_frete=FreteNormal(),
        tem_embalagem_presente=False
    )
    pedido1.finalizar_compra()

    print("\n--- Próximo Pedido ---\n")

    itens_p2 = [
        {'nome': 'Cristal Mágico', 'valor': 600.0}
    ]
    pedido2 = Pedido(
        itens_p2,
        estrategia_pagamento=PagamentoCredito(),
        estrategia_frete=FreteExpresso(),
        tem_embalagem_presente=True
    )
    pedido2.finalizar_compra()

    print("\n--- Exemplo de troca de estratégia em tempo de execução ---\n")
    pedido2.set_frete(FreteTeletransporte())
    pedido2.set_pagamento(PagamentoEstrategia())
    pedido2.finalizar_compra()

#A arquitetura é orientada a objetos e utiliza padrões como Strategy, Decorator e Facade para organizar o sistema de checkout.
#Pagamentos e fretes são implementados como estratégias que sobrassaem uma sobre a outra, descontos e taxas usam decoradores para adicionar regras sem alterar o código original, e o CheckoutFacade centraliza o processo de compra, integrando cálculo, pagamento e emissão de nota fiscal.

    
#1.Construir calculador base e aplicar decorators de desconto conforme necessário(Aplicar prioridade de desconto: PIX primeiro)
#2. Calcular valor após desconto (usado para cálculo de frete)
#3. Calcular frete via estratégia (baseado no valor após desconto)
#4. Compor decorator de embalagem (se houver) sobre o calculador de desconto
#5. Valor final = valor (com desconto e possivelmente taxa de embalagem) + frete
#6. Processar pagamento via estratégia
#7. Orquestra subsistemas em caso de sucesso

