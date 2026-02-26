Editor de Autômatos e Gramáticas
Este projeto é um sistema interativo em Python para a criação, manipulação e conversão de Autômatos Finitos (Determinísticos e Não-Determinísticos) e Gramáticas Regulares.

👥 Autores
Este projeto foi desenvolvido por:

Enzo Silva dos Santos Silva

Caetano Otávio Garcia de Oliveira

Henrique Costa Fernandes

🚀 Funcionalidades
O sistema oferece um conjunto completo de ferramentas para o estudo de Teoria da Computação:

1. Manipulação de Autômatos (AFD e AFND)
Criação Personalizada: Definição de estados, alfabeto, transições e estados finais.

Simulação: Teste de palavras para verificar se são reconhecidas pelo autômato configurado.

Determinística (NFA -> DFA): Algoritmo de conversão automática de Autômatos Finitos Não-Determinísticos para Determinísticos utilizando a construção de subconjuntos.

2. Minimização de AFD
Implementação do algoritmo de partição para redução do número de estados, garantindo que o autômato seja o mais eficiente possível (autômato mínimo).

Remoção automática de estados inalcançáveis e criação de "estado morto", se necessário.

3. Processamento de Gramáticas
Editor de Gramática: Interface para entrada de produções no formato S -> aA | b.

Classificação: Identifica se a gramática informada é Regular (GR) ou Livre de Contexto (GLC).

Conversão GR -> AFD: Transforma gramáticas regulares em autômatos equivalentes para processamento de strings.

🛠️ Como Executar
Certifique-se de ter o Python 3.x instalado.

Clone este repositório ou baixe o arquivo .py.

Execute o script principal:

python main.py


Estrutura do Código
converter_afnd_para_afd: Implementa a lógica de construção de subconjuntos (frozensets).

minimizar_afd: Realiza a partição de estados equivalentes e limpeza de estados inalcançáveis.

verificar_tipo_gramatica: Analisa a estrutura das produções para classificar a gramática.

mostrar_estado: Função auxiliar para formatação visual (ex: exibe conjuntos como {q0,q1}).