from dados import locacoes
from clientes import menu_clientes
from casas import menu_casas
from locacoes import menu_locacoes, exibir_relatorios

def menu_principal():
    while True:
        print("\n========================================")
        print(   "           Casa da Sogra Locações     ")
        print("porque ninguém aguenta ficar muito tempo com a sogra")
        print("========================================")
        print("MENU PRINCIPAL")
        print("1 - Gerenciar Clientes")
        print("2 - Gerenciar Casas")
        print("3 - Locações (Alugar / Encerrar)")
        print("4 - Relatórios")
        print("0 - Sair do Sistema")
        print("========================================")

        opcao = input("Digite a opção desejada: ").strip()

        if opcao == "1":
            menu_clientes(locacoes)
        elif opcao == "2":
            menu_casas(locacoes)
        elif opcao == "3":
            menu_locacoes()
        elif opcao == "4":
            exibir_relatorios()
        elif opcao == "0":
            print("\nEncerrando o sistema. Obrigado por utilizar a Casa da Sogra Locações!")
            break
        else:
            print("\n[ERRO] Opção inválida! Tente novamente.")

if __name__ == "__main__":
    menu_principal()
