try:
    from tkinter import filedialog
except:
    print("Eu preciso do módulo tkinter para funcionar corretamente, por favor, leia o readme, instale-o e execute-me novamente.")

# Definição de algumas variáveis importantes
TAM = 64 # tamanho em bytes da memória
memory = [] # vetor da memória
free_space = [[0,TAM]] # vetor com os espaços livres no formato {[início_do_espaço,tamanho do espaço]}
process_queue = [] # vetor com a lista de espera dos processos
active_processes = [] # vetor com a lista de processos em execução
realloc_reg = {} # dicionário que salva todas as realocações
algorithm = 'First-Fit' # algoritmo selecionado para execução

def fillMemory():
    ''' 
        Método que enche a memória automaticamente no tamanho inserido com valores Nulos
        Como não existe Null em python, estou utilizando o None, que serve para o mesmo propósito
    '''
    for index in range(0,TAM):
        memory.append(None)

def clear():
    '''Método que limpa todos os registradores e a memória'''
    global free_space, active_processes, process_queue, realloc_reg, memory
    for index in range(0,TAM):
        memory[index] = None
    free_space, active_processes, process_queue, realloc_reg = [[0,TAM]], [], [], {}

def showMemoryMap():
    '''Exibe o mapa da memória'''
    print("Processos são exibidos no formato 'P + número_do_processo' e espaços livres são exibidos como 'None'")
    print("Memória: ", memory)
   
def isThereAProcessWithThis(pid,list):
    '''Verifica se um processo com o ID inserido'''
    pid = "P"+str(pid)
    for process in list:
        if process.pid == pid:
            return True
    return False

def createProcess():
    '''Adiciona manualmente um processo'''
    while True:
        try:
            process_id = int(input("Insira um id (número inteiro positivo) para o processo: "))
            if(isThereAProcessWithThis(process_id,active_processes)):
                print("Já existe um processo com esse id.")
            elif (process_id <= 0):
                print("Insira um id positivo.")
            else:
                break
        except:
            print("Esse id é inválido.")
    while True:
        try:
            process_size = int(input("Insira o tamanho (número inteiro positivo) do processo: "))
            if (process_size <= 0):
                print("Insira um tamanho positivo.")
            else:
                break
        except:
            print("Esse tamanho é inválido.")
    doFitAlgorithm = getFitAlgorithm(algorithm)
    if doFitAlgorithm(Process('P'+str(process_id),process_size,0)):
        print("\nProcesso inserido com sucesso!")
    else:
        print("\nNão há espaço suficiente na memória!")

def removeProcess():
    '''Remove manualmente um processo da execução'''
    while True:
        try:
            process_id = int(input("Insira o id do processo a ser removido (0 para sair): "))
            if(isThereAProcessWithThis(process_id,active_processes)):
                for p in active_processes:
                    if p.pid == 'P'+str(process_id):
                        memDealloc(p)
                        print("Processo removido com sucesso!")
                        break
            elif (process_id < 0):
                print("Insira um id válido.")
            else:
                break
        except:
            print("Esse id é inválido.")

def updateFreeSpaces():
    '''Atualiza o vetor de espaços livres'''
    global free_space
    free_space = []
    free_start = 0
    free_size = 0
    byte = 0
    while byte < TAM:
        if memory[byte] is None:
            free_start = byte
            free_size = 0
            while byte < TAM and memory[byte] is None:
                free_size += 1
                byte += 1
            free_space.append([free_start,free_size])
        else:
            byte += 1

def showFreeSpaces():
    '''Exibe o vetor de espaços livres'''
    for space in free_space:
        print("Início do espaço livre: byte", space[0])
        if space[1] > 1:
            print("Tamanho do espaço livre: %s bytes" % space[1] )
        else:
            print("Tamanho do espaço livre: %s byte" % space[1] )

def showFreeSpacesMin():
    '''Exibe o vetor de espaços livres de uma maneira compacta'''
    text = ""
    for space in free_space:
        text += str(space[0]) + '-' + str(space[0]+space[1]-1) + ', '
    text[:-3]
    return text

def memDefrag():
    '''Compacta a memória, movendo todos os processos em execução para o começo da memória'''
    global realloc_reg, memory
    process_list = []
    # salva todos os processos em execução em uma lista
    for byte in range(0,TAM):
        if memory[byte] is not None and memory[byte] not in process_list:
            firstEntry = True
            for x in range(0, getProcessSize(memory[byte])):
                process_list.append(memory[byte])
                if (firstEntry):
                    realloc_reg[memory[byte]] = [byte,process_list.index(memory[byte])]
                    firstEntry = False
    # reinsere os processos na memória
    for byte in range(0,len(process_list)):
        memory[byte] = process_list[byte]
    for byte in range(len(process_list),TAM):
        memory[byte] = None
    updateFreeSpaces()

def showReallocReg():
    '''Exibe o registrador de realocação'''
    if len(realloc_reg) == 0:
        print("Registrador de Realocação vazio.")
    for key in realloc_reg:
        print("Processo",key ,"-> movido do byte",realloc_reg[key][0] ,"para o byte", realloc_reg[key][1])

def getProcessSize(process_id):
    '''Procura um processo por id na lista de processos ativos'''
    for p in active_processes:
        if p.pid == process_id:
            return p.size
    return None

def memAlloc(position, process):
    '''Método que aloca espaço na memória para um processo'''
    global memory
    for x in range (0,process.size):
        memory[position+x] = process.pid
    active_processes.append(process)
    updateFreeSpaces()

def memDealloc(process):
    '''Método que desaloca espaço na memória'''
    global memory
    for byte in range(0,TAM):
        if memory[byte] is process.pid:
            memory[byte] = None
    active_processes.pop(active_processes.index(process))
    updateFreeSpaces() 

def showFitAlgorithm(fitAlgorithm,file):
    '''Exibe o texto referente ao algoritmo de alocação'''
    file.write("\n******************************************")
    file.write("\n" + showFitAlgotirhmText(fitAlgorithm))
    file.write("\n******************************************\n")

def showFitAlgotirhmText(fitAlgorithm):
    '''Exibe o nome do algoritmo de alocação'''
    if fitAlgorithm is firstFit:
        return "First-fit"
    elif fitAlgorithm is bestFit:
        return "Best-Fit"
    else:
        return "Worst-Fit"

def getFitAlgorithm(fitText):
    '''Retorna o algoritmo de alocação correspondente'''
    if fitText == "First-Fit":
        return firstFit
    elif fitText == "Best-Fit":
        return bestFit
    else:
        return worstFit

def firstFit(process):
    '''Algoritmo de alocação First-fit'''
    position = None
    for space in free_space:
        if space[1] >= process.size:
            position = space[0]
            break
    if position is not None:
        memAlloc(position,process)
        updateFreeSpaces()
        return True
    else:
        return False

def bestFit(process):
    '''Algoritmo de alocação Best-fit'''
    position = None
    best = 0
    for space in free_space:
        if space[1] > best:
            best = space[1]
    for space in free_space:
        if space[1] >= process.size and space[1] <= best:
            best = space[1]
            position = space[0]
    if position is not None:
        memAlloc(position,process)
        updateFreeSpaces()
        return True
    else:
        return False

def worstFit(process):
    '''Algoritmo de alocação Worst-fit'''
    position = None
    worst = free_space[0][1]
    for space in free_space:
        if space[1] >= process.size and space[1] >= worst:
            worst = space[1]
            position = space[0]
    if position is not None:
        memAlloc(position,process)
        updateFreeSpaces()
        return True
    else:
        return False

def killEmAll(time):
    '''Método que mata processos que já terminaram sua execução'''
    for process in active_processes:
        if process.init+process.duration == time:
            memDealloc(process)

def searching(time):
    '''Método que busca um processo para executar no tempo atual'''
    for p in process_queue:
        if p.init == time:
            return p
    return None

def getProcessPosInMemory(process):
    '''Retorna a posição de memória em que o processo se encontra'''
    for byte in range(0,TAM):
        if memory[byte] == process.pid:
            return byte

def simulation(fitAlgorithm, file):
    '''Realiza a simulação automática'''
    mem_fail = 0 # quantidade de falhas de memória
    execution_time = 0 # tempo de execução do programa
    # exibe o algoritmo de alocação
    showFitAlgorithm(fitAlgorithm,file)
    # inicia loop de tempo
    while execution_time < 100 and (len(process_queue) > 0 or len(active_processes) > 0):
        # verifica se algum processo termina sua execução no tempo atual
        killEmAll(execution_time)
        # verifica lista de espera por um processo que execute no tempo atual
        process = searching(execution_time)
        if (process is None):
            execution_time += 1
            continue
        else:
            process_queue.pop(process_queue.index(process))
            file.write('\nT%i: Procurando espaço livre para %s (%i byte(s))\n' % (execution_time, process.pid, process.size))
        # tenta alocar na memória
        if fitAlgorithm(process):
        # se consegue alocar, aloca e segue adiante
            file.write('T%i: Processo %s alocado na posição %i\n' % (execution_time, process.pid, getProcessPosInMemory(process)))
        else:
            # se não consegue alocar, compacta a memória 
            mem_fail += 1
            memDefrag()
            file.write('T%i: Compactando memória...\n' % execution_time)
            # e tenta alocar novamente
            if fitAlgorithm(process):
                # se consegue alocar, aloca e segue adiante
                file.write('T%i: Processo %s alocado na posição %i\n' % (execution_time, process.pid, getProcessPosInMemory(process)))
            else:
                # se não consegue alocar novamente, mata o processo
                mem_fail += 1
                file.write('T%i: Não foi encontrado espaço suficiente para a alocação do processo %s.\n' % (execution_time, process.pid))
        # exibe lista dos espaços vazios
        file.write('T%i: Lista de espaços vazios: %s\n' % (execution_time, showFreeSpacesMin()))
        # passagem do tempo
        execution_time += 1
    # Exibe o tempo total de execução
    file.write("\nTempo total de execução: %i u.t.\n" % execution_time)
    # Exibe o número de falhas de memória
    file.write("Total de falhas de memória: %i\n" % mem_fail)

def loadFromFile():
    '''Carrega uma sequência de programas de um arquivo e executa os 3 algoritmos de alocação'''
    try:
        file = open(filedialog.askopenfilename(title="Arquivo com os processos"), 'r')
    except:
        print("Erro na abertura do arquivo.")
        return
    global process_queue
    process_list = file.readlines()
    index = 0
    # extraindo os processos do arquivo
    while index < len(process_list):
        process_queue.append(Process(process_list[index][:-1],int(process_list[index+1]),int(process_list[index+2]),int(process_list[index+3])))
        index += 4
    file.close()
    # cria o arquivo de log
    file = open('log.txt','w')
    process_list = process_queue.copy()
    print("Executando a simulação, dependendo do tamanho da memória e da quantidade de processos")
    print("pode demorar de alguns segundos até alguns minutos, por favor, aguarda até que a operação termine!\n")
    alg_list = [firstFit,bestFit,worstFit]
    for fit_alg in alg_list:
        print("Executando o algoritmo %s ..." %  showFitAlgotirhmText(fit_alg))
        simulation(fit_alg,file)
        process_queue = process_list.copy()
        clear()
    file.close()
    print("\nFoi salvo um registro das operações no arquivo log.txt")

class Process(object):
    '''Classe referente a Processo, contendo o ID, tamanho, tempo inicial e duração de execução'''
    def __init__(self,pid,size=1,init=0,duration=10):
        self.pid = pid
        self.size = size
        self.init = init
        self.duration = duration
    def __repr__(self):
        return '[ '+ self.pid+', '+str(self.size)+', '+str(self.init)+', '+str(self.duration)+' ]'

if __name__ == "__main__":
    '''Loop principal do programa, execução do menu'''
    fillMemory()
    while True:
        print("\n########################################")
        print("#                                      #")
        print("#         SIMULADOR DE MEMÓRIA         #")
        print("#                                      #")
        print("########################################")
        print("\n0. Encerrar o programa")
        print("1. Alterar algoritmo de alocação: %s " % algorithm)
        print("2. Adicionar um processo para execução")
        print("3. Remover um processo da execução")
        print("4. Exibir a lista de espaços livres")
        print("5. Exibir o registrador de realocação")
        print("6. Exibir do mapa de utilização de memória")
        print("7. Compactar a memória")
        print("8. Carregar processos de um arquivo e iniciar simulação")
        value = int(input("\nOpção escolhida: "))
        while value > 8 or value < 0:
            value = int(input("Opção Inválida, escolha novamente: "))
        print('')
        if value == 0:
            exit(0)
        elif value == 1:
            print("\nEscolha o algoritmo.\n")
            print("1. First-Fit")
            print("2. Best-Fit")
            print("3. Worst-Fit")
            value = int(input("\nAlgoritmo Escolhido: "))
            while value > 3 or value < 1:
                value = int(input("Opção Inválida, escolha novamente: "))
            if value == 1:
                algorithm = "First-Fit"
            elif value == 2:
                algorithm = "Best-Fit"
            else:
                algorithm = "Worst-Fit"
        elif value == 2:
            createProcess()
        elif value == 3:
            removeProcess()
        elif value == 4:
            showFreeSpaces()
        elif value == 5:
            showReallocReg()
        elif value == 6:
            showMemoryMap()
        elif value == 7:
            print("Compactando a memória...")
            memDefrag()
            print("Memória compatada com sucesso!")
        else:
            loadFromFile()
            clear()
        input("\nPressione enter para continuar...")