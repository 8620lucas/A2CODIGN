from dados import locacoes, casas, clientes
from clientes import listar_clientes, buscar_cliente_por_id
from casas import listar_casas, buscar_casa_por_id

# --- Regras de negócio (constantes) ---
LIMITE_LOCACOES_ATIVAS = 3   # máximo de casas alugadas simultaneamente por cliente
PRAZO_MIN_DIAS = 1
PRAZO_MAX_DIAS = 30
DESCONTO_COMBO = 0.15        # desconto se o cliente já tiver outra locação ativa
MULTA_FIXA_POR_DIA = 50.00   # somada à diária, por dia de atraso na saída (checkout)



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


def selecionar_casa():
    listar_casas(apenas_disponiveis=True)
    id_casa = ler_inteiro("\nDigite o ID da Casa desejada: ")
    if id_casa is None:
        return None

    casa = buscar_casa_por_id(id_casa)
    if not casa or casa["unidades_disponiveis"] <= 0:
        print("[ERRO] Casa inexistente ou sem unidades disponíveis no momento.")
        return None
    return casa


def verificar_capacidade(casa, quantidade_hospedes):
    if quantidade_hospedes > casa["capacidade_maxima"]:
        print(
            f"[BLOQUEADO] A casa '{casa['nome']}' comporta no máximo "
            f"{casa['capacidade_maxima']} hóspede(s), mas foram informados {quantidade_hospedes}."
        )
        return False
    return True


def ler_quantidade_hospedes(casa):
    quantidade = ler_inteiro(
        "Quantidade de hóspedes: ",
        "[ERRO] Informe um número válido de hóspedes.",
    )
    if quantidade is None or quantidade < 1:
        print("[ERRO] É necessário informar pelo menos 1 hóspede.")
        return None
    return quantidade


def ler_dias_locacao():
    dias = ler_inteiro(
        f"Quantidade de diárias ({PRAZO_MIN_DIAS} a {PRAZO_MAX_DIAS}): ",
        "[ERRO] Informe um número válido de diárias.",
    )
    if dias is None:
        return None
    if not PRAZO_MIN_DIAS <= dias <= PRAZO_MAX_DIAS:
        print(f"[ERRO] O prazo de locação deve ser entre {PRAZO_MIN_DIAS} e {PRAZO_MAX_DIAS} diárias.")
        return None
    return dias


def registrar_locacao(cliente, casa, quantidade_hospedes, dias, total):
    casa["unidades_disponiveis"] -= 1
    locacao = {
        "id": gerar_id_locacao(),
        "cliente_id": cliente["id"],
        "cliente_nome": cliente["nome"],
        "casa_id": casa["id"],
        "casa_nome": casa["nome"],
        "quantidade_hospedes": quantidade_hospedes,
        "dias": dias,
        "valor_total": total,
        "ativa": True,
    }
    locacoes.append(locacao)
    return locacao


def alugar_casa():
    print("\n--- REGISTRAR NOVA LOCAÇÃO ---")
    if not clientes or not casas:
        print("[ERRO] É necessário ter clientes e casas cadastrados.")
        return

    cliente = selecionar_cliente()
    if not cliente:
        return

    ativas_cliente = locacoes_ativas(cliente["id"])
    if len(ativas_cliente) >= LIMITE_LOCACOES_ATIVAS:
        print(f"[ERRO] Limite atingido! Este cliente já possui {LIMITE_LOCACOES_ATIVAS} casas alugadas simultaneamente.")
        return

    casa = selecionar_casa()
    if not casa:
        return

    quantidade_hospedes = ler_quantidade_hospedes(casa)
    if quantidade_hospedes is None or not verificar_capacidade(casa, quantidade_hospedes):
        return

    dias = ler_dias_locacao()
    if dias is None:
        return

    desconto, total = calcular_valor_locacao(dias, casa["valor_diaria"], bool(ativas_cliente))
    locacao = registrar_locacao(cliente, casa, quantidade_hospedes, dias, total)

    print("\n[SUCESSO] Locação registrada!")
    print(f"Contrato #{locacao['id']} | Cliente: {cliente['nome']} | Casa: {casa['nome']} ({dias} diária(s))")
    if desconto > 0:
        print(f"Desconto Combo ({DESCONTO_COMBO:.0%} por múltiplas locações): -R$ {desconto:.2f}")
    print(f"Valor Total: R$ {total:.2f}")



def devolver_casa():
    print("\n--- ENCERRAMENTO DE LOCAÇÃO (CHECKOUT) ---")
    ativas = locacoes_ativas()
    if not ativas:
        print("Não há locações ativas no momento.")
        return

    for l in ativas:
        print(f"Contrato ID: {l['id']} | Cliente: {l['cliente_nome']} | Casa: {l['casa_nome']} | Prazo: {l['dias']} diária(s)")

    id_loc = ler_inteiro("\nDigite o ID do Contrato para encerrar: ")
    if id_loc is None:
        return

    locacao = next((l for l in ativas if l["id"] == id_loc), None)
    if not locacao:
        print("[ERRO] Contrato ativo não encontrado.")
        return

    casa = buscar_casa_por_id(locacao["casa_id"])

    try:
        dias_atraso = max(0, int(input("Houve dias de atraso na saída (checkout)? (0 se no prazo): ")))
    except ValueError:
        dias_atraso = 0

    if dias_atraso > 0 and casa:
        multa = calcular_multa(dias_atraso, casa["valor_diaria"])
        locacao["valor_total"] += multa
        print(f"[AVISO] Multa por atraso ({dias_atraso} dia(s)): R$ {multa:.2f}")

    locacao["ativa"] = False
    if casa:
        casa["unidades_disponiveis"] += 1

    print(f"[SUCESSO] Casa liberada para nova locação! Valor final acertado: R$ {locacao['valor_total']:.2f}")



def exibir_relatorios():
    print("\n=== RELATÓRIOS GERENCIAIS ===")
    print(f"Clientes Cadastrados          : {len(clientes)}")
    print(f"Casas no Catálogo             : {len(casas)}")
    print(f"Unidades Disponíveis          : {sum(c['unidades_disponiveis'] for c in casas)}")
    print(f"Casas Atualmente Alugadas     : {len(locacoes_ativas())}")
    print(f"Total de Locações Realizadas  : {len(locacoes)}")
    print(f"Faturamento Total Acumulado   : R$ {sum(l['valor_total'] for l in locacoes):.2f}")

    print("\n--- Histórico de Locações ---")
    if not locacoes:
        print("Nenhuma locação registrada ainda.")
        return

    for l in locacoes:
        status = "ALUGADA" if l["ativa"] else "ENCERRADA"
        print(f"#{l['id']} | {l['cliente_nome']} -> '{l['casa_nome']}' | R$ {l['valor_total']:.2f} | [{status}]")



def menu_locacoes():
    acoes = {"1": alugar_casa, "2": devolver_casa}

    while True:
        print("\n=== GERENCIAR LOCAÇÕES ===")
        print("1 - Alugar Casa")
        print("2 - Encerrar Locação (Checkout)")
        print("0 - Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            break
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("[ERRO] Opção inválida!")
