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
                    destinos = func_transicao_n[(sub_estado, simbolo)]
                    if isinstance(destinos, set):
                        novo_estado |= destinos
                    else:
                        novo_estado.add(destinos)
            
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
    alcançaveis = {inicial}
    fila = collections.deque([inicial])
    while fila:
        atual = fila.popleft()
        for simbolo in alfabeto:
            destino = transicoes.get((atual, simbolo))
            if destino is not None and destino not in alcançaveis:
                alcançaveis.add(destino)
                fila.append(destino)
                
    estados = alcançaveis
    finais = finais & alcançaveis
    transicoes_limpas = {k: v for k, v in transicoes.items() if k[0] in alcançaveis}
    
    estados_completos = set(estados)
    transicoes_completas = transicoes_limpas.copy()
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
            
    particao = []
    nao_finais = set(estados_completos) - finais
    if finais: particao.append(finais)
    if nao_finais: particao.append(nao_finais)

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
                    dest = transicoes_completas.get((estado, simbolo))
                    idx_dest = -1
                    for i, g in enumerate(particao):
                        if dest in g:
                            idx_dest = i
                            break
                    assinatura.append(idx_dest)
                chave = tuple(assinatura)
                if chave not in subgrupos: subgrupos[chave] = set()
                subgrupos[chave].add(estado)
            nova_particao.extend(subgrupos.values())
        if len(nova_particao) == len(particao): break
        particao = nova_particao

    est_para_g = {est: i for i, g in enumerate(particao) for est in g}
    estados_min = set(range(len(particao)))
    trans_min = {}
    for i, g in enumerate(particao):
        rep = next(iter(g))
        for s in alfabeto:
            dest_orig = transicoes_completas.get((rep, s))
            trans_min[(i, s)] = est_para_g.get(dest_orig, -1)
            
    return estados_min, trans_min, est_para_g[inicial], {est_para_g[f] for f in finais}, particao

# ================= LÓGICA DE GRAMÁTICA =================
def verificar_tipo_gramatica(variaveis, terminais, producoes):
    for esquerda, regras in producoes.items():
        if esquerda not in variaveis:
            return "Inválida"

        for regra in regras:
            regra = regra.strip()

            # Aceita várias formas de epsilon
            if regra in ["ε", "e", "eps", "epsilon", ""]:
                continue

            # Produção A -> a
            if len(regra) == 1:
                if regra not in terminais:
                    return "GLC"

            # Produção A -> aB
            elif len(regra) == 2:
                if regra[0] not in terminais or regra[1] not in variaveis:
                    return "GLC"

            # Qualquer outra forma já é GLC
            else:
                return "GLC"

    return "GR (Gramática Regular)"

def converter_gr_para_afnd_logica(variaveis, terminais, producoes, inicial):
    estado_final_extra = "QF"
    estados_afnd = list(variaveis) + [estado_final_extra]
    transicoes_n = {}
    finais_n = {estado_final_extra}

    for nt, regras in producoes.items():
        for regra in regras:
            if regra in ["ε", "e", "eps", "epsilon", ""]:
                finais_n.add(nt)
            elif len(regra) == 1 and regra in terminais:
                transicoes_n.setdefault((nt, regra), set()).add(estado_final_extra)
            elif len(regra) == 2 and regra[0] in terminais and regra[1] in variaveis:
                transicoes_n.setdefault((nt, regra[0]), set()).add(regra[1])
    return estados_afnd, list(terminais), transicoes_n, inicial, finais_n

def executar_gramatica():
    print("\n" + "="*40 + "\n        EDITOR DE GRAMÁTICA        \n" + "="*40)
    variaveis = set(input("Informe as variáveis (separadas por espaço): ").split())
    terminais = sorted(list(set(input("Informe os terminais (separados por espaço): ").split())))
    inicial = input("Símbolo inicial: ").strip()
    producoes = {}

    print("\nDefina as produções (ex: S -> aA | b). Digite 'fim' para encerrar.\n")
    while True:
        entrada = input("Produção: ").strip()
        if entrada.lower() == "fim": break
        if "->" not in entrada: continue
        esq, dir_p = entrada.split("->")
        esq = esq.strip()
        alts = [a.strip().replace(" ", "") for a in dir_p.split("|")]
        if esq not in producoes: producoes[esq] = []
        producoes[esq].extend(alts)

    tipo = verificar_tipo_gramatica(variaveis, terminais, producoes)
    print("\nTipo da Gramática:", tipo)

    if tipo == "GR (Gramática Regular)":
        if input("\nDeseja converter para AFD e operar? (s/n): ").lower() == 's':
            # PASSO 1: GR -> AFND
            v_n, t_n, trans_n, ini_n, fin_n = converter_gr_para_afnd_logica(variaveis, terminais, producoes, inicial)
            
            print("\n--- PASSO 1: AFND GERADO (Intermediário) ---")
            # Cabeçalho do AFND
            header = f"{'Estado':<12} | " + "  ".join([f"{s:<10}" for s in t_n])
            print(header)
            print("-" * len(header))
            
            for est in v_n:
                linha = f"{marcar_estado(est, ini_n, fin_n):<12} | "
                for s in t_n:
                    dest = trans_n.get((est, s), set())
                    linha += f"{mostrar_estado(dest):<10}  "
                print(linha)

            # PASSO 2: AFND -> AFD
            print("\n--- PASSO 2: DETERMINIZAÇÃO (AFD FINAL) ---")
            est_a, trans_a, ini_a, fin_a, ordem = converter_afnd_para_afd(v_n, t_n, trans_n, ini_n, fin_n)
            
            # Cabeçalho do AFD
            header_afd = f"{'Estado':<25} | " + "  ".join([f"{s:<15}" for s in t_n])
            print(header_afd)
            print("-" * len(header_afd))
            
            for e in ordem:
                linha = f"{marcar_estado(e, ini_a, fin_a):<25} | "
                for s in t_n:
                    dest = trans_a.get((e, s))
                    linha += f"{mostrar_estado(dest):<15}  "
                print(linha)

            return list(est_a), t_n, trans_a, ini_a, fin_a, '1'
    return None

# ================= MENU PRINCIPAL =================
def executar_sistema():
    while True:
        print("\n" + "="*40 + "\n    EDITOR DE AUTÔMATOS (AFD/AFND)    \n" + "="*40)
        print("1. Criar novo AFD\n2. Criar novo AFND\n3. Criar nova Gramática\n0. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        if opcao == '0': break
        if opcao not in ['1', '2', '3']: continue

        if opcao == '3':
            resultado = executar_gramatica()
            if resultado:
                estados, alfabeto, transicoes, inicial, finais, opcao = resultado
            else: continue
        else:
            estados = input("Informe os estados (separados por espaço): ").split()
            alfabeto = input("Informe o alfabeto (separados por espaço): ").split()
            inicial = input("Estado inicial: ").strip()
            finais = set(input("Estados finais (separados por espaço): ").split())
            transicoes = {}
            print("\nDefina as transições (use '.' para vazio):")
            for e in estados:
                for s in alfabeto:
                    dest = input(f"δ({e}, {s}) -> ").strip()
                    if dest != ".":
                        transicoes[(e, s)] = set(dest.split()) if opcao == '2' else dest

        while True:
            print("\n" + "-"*30 + f"\n OPERAÇÕES DISPONÍVEIS ({'AFD' if opcao == '1' else 'AFND'})\n" + "-"*30)
            print("1. Testar palavra\n2. Converter AFND para AFD" if opcao == '2' else "1. Testar palavra")
            print("3. Minimizar Autômato\n0. Voltar ao Menu Principal")
            
            sub = input("\nEscolha uma operação: ")
            if sub == '0': break
            
            if sub == '1':
                palavra = input("Digite a palavra: ")
                if opcao == '1':
                    atual = inicial
                    valida = True
                    for char in palavra:
                        atual = transicoes.get((atual, char))
                        if atual is None: valida = False; break
                    print(">> RECONHECEU!" if valida and atual in finais else ">> NÃO RECONHECEU!")
                else:
                    atuais = {inicial}
                    for char in palavra:
                        prox = set()
                        for st in atuais:
                            res = transicoes.get((st, char), set())
                            if isinstance(res, set): prox |= res
                            else: prox.add(res)
                        atuais = prox
                    print(">> RECONHECEU!" if atuais & finais else ">> NÃO RECONHECEU!")
            
            elif sub == '2' and opcao == '2':
                est_a, trans_a, ini_a, fin_a, ordem = converter_afnd_para_afd(estados, alfabeto, transicoes, inicial, finais)
                estados, transicoes, inicial, finais, opcao = list(est_a), trans_a, ini_a, fin_a, '1'
                print("\n--- AFD RESULTANTE ---")
                for e in ordem:
                    print(f"{marcar_estado(e, inicial, finais):<20} |", " ".join([f"{s}: {mostrar_estado(trans_a.get((e,s)))}" for s in alfabeto]))

            elif sub == '3':
                est_p, trans_p, ini_p, fin_p = (estados, transicoes, inicial, finais) if opcao == '1' else converter_afnd_para_afd(estados, alfabeto, transicoes, inicial, finais)[:4]
                est_m, trans_m, ini_m, fin_m, particoes = minimizar_afd(est_p, alfabeto, trans_p, ini_p, fin_p)
                print("\n--- AFD MINIMIZADO ---")
                for e in sorted(est_m):
                    print(f"{marcar_estado(e, ini_m, fin_m):<10} |", " ".join([f"{s}: {mostrar_estado(trans_m.get((e,s)))}" for s in alfabeto]))

if __name__ == "__main__":
    executar_sistema()