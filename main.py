# M = {Q, Σ, δ, q0, F}

# Q = {q0, q1}
# Σ = {a, b}

# δ = {
#       δ: (q0, a) -> q1,   
#       δ: (q0, b) -> q1,
#       δ: (q1, a) -> q1,
#       δ: (q1, b) -> q1
#     }

# q0 = q0 
# F = {q1}



# =========== AFD E VALIDAÇÃO =============

# definindo as estruturas 
estados = []
alfabeto  = []
func_transicao = {}
estado_inicial = ""
estados_finais = []

# recebendo dados do automato
print("Informe o conjunto de estados: ", end ="")
estados = input().split()
print(estados)

print("Informe o alfabeto de entrada: ", end="")
alfabeto = input().split()

print("Informe o estado inicial: ", end="")
estado_inicial = input()

print("Informe os estados finais: ", end="")
estados_finais = input().split()

print("Defina as funções de transição: ")
for estado in estados: 
    for simbolo in alfabeto: 
        print(f"\t {simbolo}")
        print(f"{estado}\t--->\t", end="")
        proximo_estado = input().strip()

        if " " in proximo_estado: #Verificação se o usuário tentou colocar mais de um estado
            print("ERRO: AFD não permite múltiplos estados para uma mesma transição.")
            print(f"Você tentou definir: δ({estado}, {simbolo}) -> {proximo_estado}")
            break
        if proximo_estado != "." and proximo_estado not in estados:
            print("ERRO: Estado inválido. Não pertence ao conjunto de estados Q.")
            print(f"Estado informado: {proximo_estado}")
            break
        if proximo_estado == ".":
            func_transicao [(estado, simbolo)] = None
        else:   
            func_transicao [(estado, simbolo)] = proximo_estado

# reconhecendo linguagens

print("Informe a palavra a ser reconhecida: ", end="")
entrada = input()

estado_atual = estado_inicial

for simbolo in entrada:
    print(f"Estado atual: {estado_atual}")
    print(f"Entrada atual: {simbolo}")

    print(f"Proximo estado: {func_transicao[(estado_atual, simbolo)]}")

    estado_atual = func_transicao[(estado_atual, simbolo)]
    
    if estado_atual == None: 
        print("O automato não reconhceu a linguagem")
        break
if estado_atual in estados_finais:
    print("Reconheceu")
else:
    print("Não reconheceu")


# ================= AFN ===================

print("Informe o conjunto de estados do AFND: ", end="")
estados = input().split()

print("Informe o alfabeto: ", end="")
alfabeto = input().split()

print("Defina o estado inicial do AFND: ", end="")
estado_inicial = input().strip()

print("Informe os estados finais: ", end="")
estados_finais = set(input().split())

print("Defina a função de transição")
print("Use '.' para nenhuma transição ou estados separados por espaço (ex: q1 q2)")

for estado in estados:
    for simbolo in alfabeto:
        print(f"{estado} --{simbolo}--> ", end="")
        entrada = input().strip()

        if entrada == ".":
            func_transicao[(estado, simbolo)] = set()
        else:
            proximos = set(entrada.split())

            if not proximos.issubset(estados):
                print("ERRO: Estado inválido informado.")
                exit()

            func_transicao[(estado, simbolo)] = proximos


# ========== Reconhecimento da linguagem ==========

print("Informe a palavra a ser reconhecida: ", end="")
entrada = input().strip()

estados_atuais = {estado_inicial}

for simbolo in entrada:
    novos_estados = set()

    for estado in estados_atuais:
        novos_estados |= func_transicao.get((estado, simbolo), set())

    estados_atuais = novos_estados
    print(f"Após '{simbolo}': {estados_atuais}")

if estados_atuais & estados_finais:
    print("Reconheceu")
else:
    print("Não reconheceu")
