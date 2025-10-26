# FlexOrder-DesignPatterns

A arquitetura é orientada a objetos e utiliza padrões como Strategy, Decorator e Facade para organizar o sistema de checkout.
Pagamentos e fretes são implementados como estratégias que sobrassaem uma sobre a outra, descontos e taxas usam decoradores para adicionar regras sem alterar o código original, e o CheckoutFacade centraliza o processo de compra, integrando cálculo, pagamento e emissão de nota fiscal.

1.Construir calculador base e aplicar decorators de desconto conforme necessário(Aplicar prioridade de desconto: PIX primeiro)
2. Calcular valor após desconto (usado para cálculo de frete)
3. Calcular frete via estratégia (baseado no valor após desconto)
4. Compor decorator de embalagem (se houver) sobre o calculador de desconto
5. Valor final = valor (com desconto e possivelmente taxa de embalagem) + frete
6. Processar pagamento via estratégia
7. Orquestra subsistemas em caso de sucesso

