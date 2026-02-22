import collections

# ================= FUNÇÕES DE FORMATAÇÃO E EXIBIÇÃO =================
def mostrar_estado(estado):
    """Formata a visualização de estados (simples, conjuntos ou grupos)."""
    if estado is None or estado == -1 or (isinstance(estado, (set, frozenset)) and not estado):
        return "∅"
    if isinstance(estado, int):
        return f"G{estado}"
    if isinstance(estado, (frozenset, set)):
        return "{" + ",".join(sorted(list(map(str, estado)))) + "}"
    return str(estado)

def marcar_estado(e, estado_inicial, estados_finais):
    """Adiciona prefixos de inicial (->) e final (*)."""
    prefixo = ""
    if e == estado_inicial:
        prefixo += "->"
    if e in estados_finais:
        prefixo += "*"
    return f"{prefixo}{mostrar_estado(e)}"

# ================= LÓGICA DE CONVERSÃO AFND -> AFD =================
def converter_afnd_para_afd(estados_n, alfabeto, func_transicao_n, inicial_n, finais_n):
    estado_inicial_afd = frozenset([inicial_n])
    fila = collections.deque([estado_inicial_afd])
    estados_afd = {estado_inicial_afd}
    func_transicao_afd = {}
    ordem_descoberta = [estado_inicial_afd]

    while fila:
        atual = fila.popleft()
        for simbolo in alfabeto:
            novo_estado = set()
            for sub_estado in atual:
                if (sub_estado, simbolo) in func_transicao_n:
                    novo_estado |= func_transicao_n[(sub_estado, simbolo)]
            
            novo_estado_froz = frozenset(novo_estado)
            func_transicao_afd[(atual, simbolo)] = novo_estado_froz
            
            if novo_estado_froz not in estados_afd:
                estados_afd.add(novo_estado_froz)
                fila.append(novo_estado_froz)
                ordem_descoberta.append(novo_estado_froz)

    finais_afd = {e for e in estados_afd if e & finais_n}
    return estados_afd, func_transicao_afd, estado_inicial_afd, finais_afd, ordem_descoberta

# ================= LÓGICA DE MINIMIZAÇÃO =================
def minimizar_afd(estados, alfabeto, transicoes, inicial, finais):
    # -1. Remover Estados Inalcançáveis (Busca em Largura - BFS)
    alcançaveis = {inicial}
    fila = collections.deque([inicial])
    
    while fila:
        atual = fila.popleft()
        for simbolo in alfabeto:
            destino = transicoes.get((atual, simbolo))
            # Se a transição existe e o destino ainda não foi visitado
            if destino is not None and destino not in alcançaveis:
                alcançaveis.add(destino)
                fila.append(destino)
                
    # Filtra as variáveis originais para manter apenas o que é alcançável
    estados = alcançaveis
    finais = finais & alcançaveis
    transicoes_limpas = {}
    for (origem, simb), dest in transicoes.items():
        if origem in alcançaveis:
            transicoes_limpas[(origem, simb)] = dest
    transicoes = transicoes_limpas

    # 0. Preencher a tabela com Estado Morto (Tornar o AFD Completo)
    estados_completos = set(estados)
    transicoes_completas = transicoes.copy()
    estado_morto = "Morto"
    precisa_morto = False

    for estado in estados:
        for simbolo in alfabeto:
            if transicoes_completas.get((estado, simbolo)) is None:
                transicoes_completas[(estado, simbolo)] = estado_morto
                precisa_morto = True
    
    if precisa_morto:
        estados_completos.add(estado_morto)
        for simbolo in alfabeto:
            transicoes_completas[(estado_morto, simbolo)] = estado_morto
            
    estados = estados_completos
    transicoes = transicoes_completas

    # 1. Divisão inicial: Finais e Não-Finais
    particao = []
    nao_finais = set(estados) - finais
    if finais: particao.append(finais)
    if nao_finais: particao.append(nao_finais)

    # 2. Refinamento de partições (Algoritmo de Moore)
    while True:
        nova_particao = []
        for grupo in particao:
            if len(grupo) <= 1:
                nova_particao.append(grupo)
                continue
            
            subgrupos = {}
            for estado in grupo:
                assinatura = []
                for simbolo in alfabeto:
                    dest = transicoes.get((estado, simbolo), None)
                    idx_dest = -1
                    for i, g in enumerate(particao):
                        if dest in g:
                            idx_dest = i
                            break
                    assinatura.append(idx_dest)
                
                chave = tuple(assinatura)
                if chave not in subgrupos:
                    subgrupos[chave] = set()
                subgrupos[chave].add(estado)
            
            nova_particao.extend(subgrupos.values())
        
        if len(nova_particao) == len(particao):
            break
        particao = nova_particao

    # 3. Construção do autômato minimizado
    est_para_g = {est: i for i, g in enumerate(particao) for est in g}
    estados_min = set(range(len(particao)))
    trans_min = {}
    
    for i, g in enumerate(particao):
        representante = next(iter(g))
        for s in alfabeto:
            dest_orig = transicoes.get((representante, s), None)
            trans_min[(i, s)] = est_para_g.get(dest_orig, -1)
            
    ini_min = est_para_g[inicial]
    fin_min = {est_para_g[f] for f in finais}
    
    return estados_min, trans_min, ini_min, fin_min, particao

# ================= MENU PRINCIPAL E INTERAÇÃO =================
def executar_sistema():
    while True:
        print("\n" + "="*40)
        print("      EDITOR DE AUTÔMATOS (AFD/AFND)      ")
        print("="*40)
        print("1. Criar novo AFD")
        print("2. Criar novo AFND")
        print("0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == '0':
            print("Encerrando...")
            break
        
        if opcao not in ['1', '2']:
            print("Opção inválida!")
            continue

        # --- Entrada de Dados ---
        estados = input("Informe os estados (separados por espaço): ").split()
        alfabeto = input("Informe o alfabeto (separados por espaço): ").split()
        inicial = input("Estado inicial: ").strip()
        finais = set(input("Estados finais (separados por espaço): ").split())
        
        transicoes = {}
        print("\nDefina as transições (use '.' para transição vazia):")
        for e in estados:
            for s in alfabeto:
                if opcao == '1': # AFD
                    destino = input(f"δ({e}, {s}) -> ").strip()
                    transicoes[(e, s)] = None if destino == "." else destino
                else: # AFND
                    destinos = input(f"δ({e}, {s}) -> (estados separados por espaço): ").strip()
                    transicoes[(e, s)] = set() if destinos == "." else set(destinos.split())

        # --- Sub-menu de Operações ---
        while True:
            print("\n" + "-"*30)
            tipo_nome = "AFD" if opcao == '1' else "AFND"
            print(f" OPERAÇÕES DISPONÍVEIS ({tipo_nome})")
            print("-"*30)
            print("1. Testar palavra")
            if opcao == '2':
                print("2. Converter AFND para AFD")
            print("3. Minimizar Autômato")
            print("0. Voltar ao Menu Principal")
            
            sub_opt = input("\nEscolha uma operação: ")
            
            if sub_opt == '0':
                break
            
            elif sub_opt == '1':
                palavra = input("Digite a palavra para teste: ")
                if opcao == '1': # Validar AFD
                    atual = inicial
                    valida = True
                    for char in palavra:
                        atual = transicoes.get((atual, char))
                        if atual is None:
                            valida = False
                            break
                    if valida and atual in finais:
                        print(">> RECONHECEU!")
                    else:
                        print(">> NÃO RECONHECEU!")
                else: # Validar AFND
                    atuais = {inicial}
                    for char in palavra:
                        proximos = set()
                        for st in atuais:
                            proximos |= transicoes.get((st, char), set())
                        atuais = proximos
                    if atuais & finais:
                        print(">> RECONHECEU!")
                    else:
                        print(">> NÃO RECONHECEU!")

            elif sub_opt == '2' and opcao == '2':
                est_a, trans_a, ini_a, fin_a, ordem = converter_afnd_para_afd(estados, alfabeto, transicoes, inicial, finais)
                print("\n--- AFD RESULTANTE DA CONVERSÃO ---")
                for e in ordem:
                    status = marcar_estado(e, ini_a, fin_a)
                    print(f"{status:<20}", end=" | ")
                    for s in alfabeto:
                        dest = trans_a.get((e, s))
                        print(f"{s}: {mostrar_estado(dest)}", end="  ")
                    print()
                
                if input("\nDeseja continuar as operações usando este AFD convertido? (s/n): ").lower() == 's':
                    estados, transicoes, inicial, finais, opcao = list(est_a), trans_a, ini_a, fin_a, '1'

            elif sub_opt == '3':
                # Se for AFND, converte antes de minimizar
                if opcao == '2':
                    print("\n[Aviso] AFND detectado. Convertendo para AFD primeiro...")
                    estados_p, trans_p, ini_p, fin_p, _ = converter_afnd_para_afd(estados, alfabeto, transicoes, inicial, finais)
                else:
                    estados_p, trans_p, ini_p, fin_p = estados, transicoes, inicial, finais
                
                est_m, trans_m, ini_m, fin_m, particoes = minimizar_afd(estados_p, alfabeto, trans_p, ini_p, fin_p)
                
                print("\n--- GRUPOS DE EQUIVALÊNCIA ---")
                for i, g in enumerate(particoes):
                    print(f"G{i}: {[mostrar_estado(item) for item in g]}")
                
                print("\n--- TABELA DO AFD MINIMIZADO ---")
                for e in sorted(est_m):
                    status = marcar_estado(e, ini_m, fin_m)
                    print(f"{status:<10}", end=" | ")
                    for s in alfabeto:
                        dest = trans_m.get((e, s))
                        print(f"{s}: {mostrar_estado(dest)}", end="  ")
                    print()

if __name__ == "__main__":
    executar_sistema()