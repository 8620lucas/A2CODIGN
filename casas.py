from dados import casas


CAPACIDADE_MINIMA = 1
LOCALIZACAO_PADRAO = "A definir"



def ler_inteiro(prompt, mensagem_erro="[ERRO] Digite um ID numérico válido."):
    """Lê um inteiro do usuário. Retorna None (e avisa) se a entrada for inválida."""
    try:
        return int(input(prompt))
    except ValueError:
        print(mensagem_erro)
        return None


def converter_decimal(texto):
    """Converte texto em float aceitando vírgula como separador decimal."""
    return float(texto.strip().replace(",", "."))


def gerar_id_casa():
    return max((c["id"] for c in casas), default=0) + 1


def buscar_casa_por_id(id_casa):
    return next((c for c in casas if c["id"] == id_casa), None)


def nome_ja_cadastrado(nome):
    return any(c["nome"].lower() == nome.lower() for c in casas)


def selecionar_casa(acao):
    """Lista o catálogo e pede o ID da casa a ser alterada/excluída."""
    listar_casas()
    if not casas:
        return None

    id_busca = ler_inteiro(f"\nDigite o ID da casa que deseja {acao}: ")
    if id_busca is None:
        return None

    casa = buscar_casa_por_id(id_busca)
    if not casa:
        print("[ERRO] Casa não encontrada.")
    return casa



def ler_dados_numericos():
    """Lê e valida capacidade máxima, diária e unidades disponíveis. Retorna uma tupla ou None."""
    try:
        capacidade_maxima = int(input("Capacidade máxima de hóspedes: "))
        if capacidade_maxima < CAPACIDADE_MINIMA:
            print(f"[ERRO] A capacidade máxima deve ser de pelo menos {CAPACIDADE_MINIMA} hóspede(s).")
            return None

        valor_diaria = converter_decimal(input("Valor da diária (R$): "))
        if valor_diaria <= 0:
            print("[ERRO] O valor da diária deve ser maior que zero.")
            return None

        unidades = int(input("Quantidade de unidades disponíveis para locação: "))
        if unidades < 1:
            print("[ERRO] É necessário cadastrar pelo menos 1 unidade.")
            return None
    except ValueError:
        print("[ERRO] Capacidade, diária e unidades devem ser números válidos.")
        return None

    return capacidade_maxima, valor_diaria, unidades


def cadastrar_casa():
    print("\n--- CADASTRAR NOVA CASA ---")
    nome = input("Nome da casa/imóvel: ").strip()
    if not nome:
        print("[ERRO] O nome não pode ficar em branco.")
        return

    if nome_ja_cadastrado(nome):
        print("[ERRO] Esta casa já está cadastrada no catálogo.")
        return

    localizacao = input("Localização (ex: Praia do Forte - BA, Monte Verde - MG): ").strip() or LOCALIZACAO_PADRAO

    dados = ler_dados_numericos()
    if dados is None:
        return
    capacidade_maxima, valor_diaria, unidades = dados

    nova_casa = {
        "id": gerar_id_casa(),
        "nome": nome,
        "localizacao": localizacao,
        "capacidade_maxima": capacidade_maxima,
        "valor_diaria": valor_diaria,
        "unidades_disponiveis": unidades,
    }
    casas.append(nova_casa)
    print(f"[SUCESSO] Casa '{nome}' cadastrada com ID {nova_casa['id']}!")



def listar_casas(apenas_disponiveis=False):
    titulo_lista = "CASAS DISPONÍVEIS PARA LOCAÇÃO" if apenas_disponiveis else "CATÁLOGO COMPLETO DE CASAS"
    print(f"\n--- {titulo_lista} ---")

    exibidas = [c for c in casas if not apenas_disponiveis or c["unidades_disponiveis"] > 0]
    if not exibidas:
        print("Nenhuma casa encontrada.")
        return

    for c in exibidas:
        print(
            f"ID: {c['id']} | {c['nome']} [{c['localizacao']}] | "
            f"Capacidade: até {c['capacidade_maxima']} hóspede(s) | "
            f"Diária: R$ {c['valor_diaria']:.2f} | Disponíveis: {c['unidades_disponiveis']}"
        )



def atualizar_diaria(casa, texto):
    try:
        valor = converter_decimal(texto)
        if valor > 0:
            casa["valor_diaria"] = valor
    except ValueError:
        print("[AVISO] Diária inválida, mantido valor anterior.")


def atualizar_unidades(casa, texto):
    try:
        qtd = int(texto)
        if qtd >= 0:
            casa["unidades_disponiveis"] = qtd
    except ValueError:
        print("[AVISO] Quantidade inválida, mantido valor anterior.")


def alterar_casa():
    casa = selecionar_casa("alterar")
    if not casa:
        return

    print(f"Editando: {casa['nome']} (ENTER para manter o valor atual)")
    novo_nome = input(f"Novo nome [{casa['nome']}]: ").strip()
    nova_diaria = input(f"Nova diária R$ [{casa['valor_diaria']:.2f}]: ").strip()
    novas_unidades = input(f"Nova qtd de unidades [{casa['unidades_disponiveis']}]: ").strip()

    if novo_nome:
        casa["nome"] = novo_nome
    if nova_diaria:
        atualizar_diaria(casa, nova_diaria)
    if novas_unidades:
        atualizar_unidades(casa, novas_unidades)

    print("[SUCESSO] Dados da casa atualizados!")



def casa_esta_alugada(id_casa, locacoes):
    return any(loc["casa_id"] == id_casa and loc["ativa"] for loc in locacoes)


def excluir_casa(locacoes):
    casa = selecionar_casa("excluir")
    if not casa:
        return

    # Regra de negócio: impedir exclusão se houver unidade alugada no momento
    if casa_esta_alugada(casa["id"], locacoes):
        print("[ERRO] Não é possível excluir esta casa pois há unidades alugadas no momento.")
        return

    casas.remove(casa)
    print(f"[SUCESSO] Casa '{casa['nome']}' removida do catálogo.")



def menu_casas(locacoes):
    acoes = {
        "1": cadastrar_casa,
        "2": listar_casas,
        "3": alterar_casa,
        "4": lambda: excluir_casa(locacoes),
    }

    while True:
        print("\n=== GERENCIAR CASAS ===")
        print("1 - Cadastrar Casa")
        print("2 - Consultar Catálogo")
        print("3 - Alterar Casa")
        print("4 - Excluir Casa")
        print("0 - Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            break
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("[ERRO] Opção inválida!")
