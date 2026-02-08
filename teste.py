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