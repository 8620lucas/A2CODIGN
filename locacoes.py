from dados import locacoes, filmes, clientes
from clientes import listar_clientes, buscar_cliente_por_id
from filmes import listar_filmes, buscar_filme_por_id

# --- Regras de negócio (constantes) ---
LIMITE_LOCACOES_ATIVAS = 3   # máximo de filmes alugados simultaneamente por cliente
PRAZO_MIN_DIAS = 1
PRAZO_MAX_DIAS = 7
DESCONTO_COMBO = 0.15        # desconto se o cliente já tiver outra locação ativa
MULTA_FIXA_POR_DIA = 5.00    # somada à diária, por dia de atraso



def ler_inteiro(prompt, mensagem_erro="[ERRO] ID inválido."):
    """Lê um inteiro do usuário. Retorna None (e avisa) se a entrada for inválida."""
    try:
        return int(input(prompt))
    except ValueError:
        print(mensagem_erro)
        return None


def gerar_id_locacao():
    return max((l["id"] for l in locacoes), default=0) + 1


def locacoes_ativas(cliente_id=None):
    """Retorna locações ativas, opcionalmente filtradas por cliente."""
    return [
        l for l in locacoes
        if l["ativa"] and (cliente_id is None or l["cliente_id"] == cliente_id)
    ]


# --- Cálculos ---
def calcular_valor_locacao(dias, valor_diaria, possui_locacao_ativa):
    """Retorna (desconto, total) de uma locação."""
    subtotal = dias * valor_diaria
    desconto = subtotal * DESCONTO_COMBO if possui_locacao_ativa else 0.0
    return desconto, subtotal - desconto


def calcular_multa(dias_atraso, valor_diaria):
    return dias_atraso * (valor_diaria + MULTA_FIXA_POR_DIA)



def selecionar_cliente():
    listar_clientes()
    id_cliente = ler_inteiro("\nDigite o ID do Cliente: ")
    if id_cliente is None:
        return None

    cliente = buscar_cliente_por_id(id_cliente)
    if not cliente:
        print("[ERRO] Cliente não encontrado.")
    return cliente


def selecionar_filme():
    listar_filmes(apenas_disponiveis=True)
    id_filme = ler_inteiro("\nDigite o ID do Filme desejado: ")
    if id_filme is None:
        return None

    filme = buscar_filme_por_id(id_filme)
    if not filme or filme["copias_disponiveis"] <= 0:
        print("[ERRO] Filme inexistente ou sem cópias disponíveis em estoque.")
        return None
    return filme


def cliente_pode_assistir(cliente, filme):
    if cliente["idade"] < filme["classificacao"]:
        print(
            f"[BLOQUEADO] O cliente tem {cliente['idade']} anos e o filme "
            f"'{filme['titulo']}' tem classificação +{filme['classificacao']} anos."
        )
        return False
    return True


def ler_dias_locacao():
    dias = ler_inteiro(
        f"Quantidade de dias de locação ({PRAZO_MIN_DIAS} a {PRAZO_MAX_DIAS}): ",
        "[ERRO] Informe um número válido de dias.",
    )
    if dias is None:
        return None
    if not PRAZO_MIN_DIAS <= dias <= PRAZO_MAX_DIAS:
        print(f"[ERRO] O prazo de locação deve ser entre {PRAZO_MIN_DIAS} e {PRAZO_MAX_DIAS} dias.")
        return None
    return dias


def registrar_locacao(cliente, filme, dias, total):
    filme["copias_disponiveis"] -= 1
    locacao = {
        "id": gerar_id_locacao(),
        "cliente_id": cliente["id"],
        "cliente_nome": cliente["nome"],
        "filme_id": filme["id"],
        "filme_titulo": filme["titulo"],
        "dias": dias,
        "valor_total": total,
        "ativa": True,
    }
    locacoes.append(locacao)
    return locacao


def alugar_filme():
    print("\n--- REGISTRAR NOVA LOCAÇÃO ---")
    if not clientes or not filmes:
        print("[ERRO] É necessário ter clientes e filmes cadastrados.")
        return

    cliente = selecionar_cliente()
    if not cliente:
        return

    ativas_cliente = locacoes_ativas(cliente["id"])
    if len(ativas_cliente) >= LIMITE_LOCACOES_ATIVAS:
        print(f"[ERRO] Limite atingido! Este cliente já possui {LIMITE_LOCACOES_ATIVAS} filmes alugados simultaneamente.")
        return

    filme = selecionar_filme()
    if not filme or not cliente_pode_assistir(cliente, filme):
        return

    dias = ler_dias_locacao()
    if dias is None:
        return

    desconto, total = calcular_valor_locacao(dias, filme["valor_diaria"], bool(ativas_cliente))
    locacao = registrar_locacao(cliente, filme, dias, total)

    print("\n[SUCESSO] Locação registrada!")
    print(f"Contrato #{locacao['id']} | Cliente: {cliente['nome']} | Filme: {filme['titulo']} ({dias} dia(s))")
    if desconto > 0:
        print(f"Desconto Combo ({DESCONTO_COMBO:.0%} por múltiplas locações): -R$ {desconto:.2f}")
    print(f"Valor Total: R$ {total:.2f}")



def devolver_filme():
    print("\n--- DEVOLUÇÃO DE FILME ---")
    ativas = locacoes_ativas()
    if not ativas:
        print("Não há locações ativas no momento.")
        return

    for l in ativas:
        print(f"Contrato ID: {l['id']} | Cliente: {l['cliente_nome']} | Filme: {l['filme_titulo']} | Prazo: {l['dias']} dia(s)")

    id_loc = ler_inteiro("\nDigite o ID do Contrato para devolução: ")
    if id_loc is None:
        return

    locacao = next((l for l in ativas if l["id"] == id_loc), None)
    if not locacao:
        print("[ERRO] Contrato ativo não encontrado.")
        return

    filme = buscar_filme_por_id(locacao["filme_id"])

    try:
        dias_atraso = max(0, int(input("Houve dias de atraso na entrega? (0 se no prazo): ")))
    except ValueError:
        dias_atraso = 0

    if dias_atraso > 0 and filme:
        multa = calcular_multa(dias_atraso, filme["valor_diaria"])
        locacao["valor_total"] += multa
        print(f"[AVISO] Multa por atraso ({dias_atraso} dia(s)): R$ {multa:.2f}")

    locacao["ativa"] = False
    if filme:
        filme["copias_disponiveis"] += 1

    print(f"[SUCESSO] Filme devolvido ao estoque! Valor final acertado: R$ {locacao['valor_total']:.2f}")



def exibir_relatorios():
    print("\n=== RELATÓRIOS GERENCIAIS ===")
    print(f"Clientes Cadastrados          : {len(clientes)}")
    print(f"Títulos no Catálogo           : {len(filmes)}")
    print(f"Cópias Disponíveis na Loja    : {sum(f['copias_disponiveis'] for f in filmes)}")
    print(f"Filmes Atualmente Alugados    : {len(locacoes_ativas())}")
    print(f"Total de Locações Realizadas  : {len(locacoes)}")
    print(f"Faturamento Total Acumulado   : R$ {sum(l['valor_total'] for l in locacoes):.2f}")

    print("\n--- Histórico de Locações ---")
    if not locacoes:
        print("Nenhuma locação registrada ainda.")
        return

    for l in locacoes:
        status = "ALUGADO" if l["ativa"] else "DEVOLVIDO"
        print(f"#{l['id']} | {l['cliente_nome']} -> '{l['filme_titulo']}' | R$ {l['valor_total']:.2f} | [{status}]")



def menu_locacoes():
    acoes = {"1": alugar_filme, "2": devolver_filme}

    while True:
        print("\n=== GERENCIAR LOCAÇÕES ===")
        print("1 - Alugar Filme")
        print("2 - Devolver Filme")
        print("0 - Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            break
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("[ERRO] Opção inválida!")