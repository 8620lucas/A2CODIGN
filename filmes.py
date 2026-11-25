from dados import filmes


CLASSIFICACOES_VALIDAS = (0, 10, 12, 14, 16, 18)
GENERO_PADRAO = "Geral"



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


def gerar_id_filme():
    return max((f["id"] for f in filmes), default=0) + 1


def buscar_filme_por_id(id_filme):
    return next((f for f in filmes if f["id"] == id_filme), None)


def titulo_ja_cadastrado(titulo):
    return any(f["titulo"].lower() == titulo.lower() for f in filmes)


def formatar_classificacao(classificacao):
    return "Livre" if classificacao == 0 else f"+{classificacao} anos"


def selecionar_filme(acao):
    """Lista o catálogo e pede o ID do filme a ser alterado/excluído."""
    listar_filmes()
    if not filmes:
        return None

    id_busca = ler_inteiro(f"\nDigite o ID do filme que deseja {acao}: ")
    if id_busca is None:
        return None

    filme = buscar_filme_por_id(id_busca)
    if not filme:
        print("[ERRO] Filme não encontrado.")
    return filme



def ler_dados_numericos():
    """Lê e valida classificação, diária e cópias. Retorna uma tupla ou None."""
    try:
        classificacao = int(input("Classificação indicativa (0 para Livre, 10, 12, 14, 16 ou 18): "))
        if classificacao not in CLASSIFICACOES_VALIDAS:
            print("[ERRO] Classificação inválida! Use 0 (Livre), 10, 12, 14, 16 ou 18.")
            return None

        valor_diaria = converter_decimal(input("Valor da diária (R$): "))
        if valor_diaria <= 0:
            print("[ERRO] O valor da diária deve ser maior que zero.")
            return None

        copias = int(input("Quantidade de cópias em estoque: "))
        if copias < 1:
            print("[ERRO] É necessário cadastrar pelo menos 1 cópia.")
            return None
    except ValueError:
        print("[ERRO] Classificação, diária e cópias devem ser números válidos.")
        return None

    return classificacao, valor_diaria, copias


def cadastrar_filme():
    print("\n--- CADASTRAR NOVO FILME ---")
    titulo = input("Título do filme: ").strip()
    if not titulo:
        print("[ERRO] O título não pode ficar em branco.")
        return

    if titulo_ja_cadastrado(titulo):
        print("[ERRO] Este filme já está cadastrado no catálogo.")
        return

    genero = input("Gênero (ex: Ação, Comédia, Drama, Animação): ").strip() or GENERO_PADRAO

    dados = ler_dados_numericos()
    if dados is None:
        return
    classificacao, valor_diaria, copias = dados

    novo_filme = {
        "id": gerar_id_filme(),
        "titulo": titulo,
        "genero": genero,
        "classificacao": classificacao,
        "valor_diaria": valor_diaria,
        "copias_disponiveis": copias,
    }
    filmes.append(novo_filme)
    print(f"[SUCESSO] Filme '{titulo}' cadastrado com ID {novo_filme['id']}!")



def listar_filmes(apenas_disponiveis=False):
    titulo_lista = "FILMES DISPONÍVEIS PARA LOCAÇÃO" if apenas_disponiveis else "CATÁLOGO COMPLETO DE FILMES"
    print(f"\n--- {titulo_lista} ---")

    exibidos = [f for f in filmes if not apenas_disponiveis or f["copias_disponiveis"] > 0]
    if not exibidos:
        print("Nenhum filme encontrado.")
        return

    for f in exibidos:
        print(
            f"ID: {f['id']} | {f['titulo']} [{f['genero']}] | "
            f"Classif.: {formatar_classificacao(f['classificacao'])} | "
            f"Diária: R$ {f['valor_diaria']:.2f} | Disponíveis: {f['copias_disponiveis']}"
        )



def atualizar_diaria(filme, texto):
    try:
        valor = converter_decimal(texto)
        if valor > 0:
            filme["valor_diaria"] = valor
    except ValueError:
        print("[AVISO] Diária inválida, mantido valor anterior.")


def atualizar_copias(filme, texto):
    try:
        qtd = int(texto)
        if qtd >= 0:
            filme["copias_disponiveis"] = qtd
    except ValueError:
        print("[AVISO] Quantidade inválida, mantido valor anterior.")


def alterar_filme():
    filme = selecionar_filme("alterar")
    if not filme:
        return

    print(f"Editando: {filme['titulo']} (ENTER para manter o valor atual)")
    novo_titulo = input(f"Novo título [{filme['titulo']}]: ").strip()
    nova_diaria = input(f"Nova diária R$ [{filme['valor_diaria']:.2f}]: ").strip()
    novas_copias = input(f"Nova qtd de cópias [{filme['copias_disponiveis']}]: ").strip()

    if novo_titulo:
        filme["titulo"] = novo_titulo
    if nova_diaria:
        atualizar_diaria(filme, nova_diaria)
    if novas_copias:
        atualizar_copias(filme, novas_copias)

    print("[SUCESSO] Dados do filme atualizados!")



def filme_esta_alugado(id_filme, locacoes):
    return any(loc["filme_id"] == id_filme and loc["ativa"] for loc in locacoes)


def excluir_filme(locacoes):
    filme = selecionar_filme("excluir")
    if not filme:
        return

    # Regra de negócio: impedir exclusão se houver cópia alugada no momento
    if filme_esta_alugado(filme["id"], locacoes):
        print("[ERRO] Não é possível excluir este filme pois há cópias alugadas no momento.")
        return

    filmes.remove(filme)
    print(f"[SUCESSO] Filme '{filme['titulo']}' removido do catálogo.")



def menu_filmes(locacoes):
    acoes = {
        "1": cadastrar_filme,
        "2": listar_filmes,
        "3": alterar_filme,
        "4": lambda: excluir_filme(locacoes),
    }

    while True:
        print("\n=== GERENCIAR FILMES ===")
        print("1 - Cadastrar Filme")
        print("2 - Consultar Catálogo")
        print("3 - Alterar Filme")
        print("4 - Excluir Filme")
        print("0 - Voltar ao Menu Principal")
        opcao = input("Escolha uma opção: ").strip()

        if opcao == "0":
            break
        acao = acoes.get(opcao)
        if acao:
            acao()
        else:
            print("[ERRO] Opção inválida!")