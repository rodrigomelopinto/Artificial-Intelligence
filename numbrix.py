# numbrix.py: Template para implementação do projeto de Inteligência Artificial 2021/2022.
# Devem alterar as classes e funções neste ficheiro de acordo com as instruções do enunciado.
# Além das funções e classes já definidas, podem acrescentar outras que considerem pertinentes.

# Grupo 12:
# 95569 Eduardo Miranda
# 95666 Rodrigo Pinto

import numbers
import queue
import sys
import copy
from search import InstrumentedProblem, Problem, Node, astar_search, breadth_first_tree_search, depth_first_tree_search, greedy_search, recursive_best_first_search
import time
import collections

from utils import manhattan_distance

class NumbrixState:
    state_id = 0

    def __init__(self, board):
        self.board = board
        self.id = NumbrixState.state_id
        NumbrixState.state_id += 1

    def __lt__(self, other):
        return self.id < other.id


class Board:
    """ Representação interna de um tabuleiro de Numbrix. """

    def __init__(self, n, matrix):
        self.matrix = matrix
        self.n = n

    def to_string(self):
        board_str = ''
        for i in range(0,self.n):
            for j in range(0,self.n):
                if j == self.n-1:
                    board_str += str(self.matrix[i][j]) + '\n'
                else:
                    board_str += str(self.matrix[i][j]) + '\t'
        return board_str[:-1]
                
    
    def get_number(self, row: int, col: int) -> int:
        """ Devolve o valor na respetiva posição do tabuleiro. """
        return self.matrix[row][col]
        pass
    
    def adjacent_vertical_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente abaixo e acima, 
        respectivamente. """
        if row == 0:
            return (self.matrix[row+1][col], None)
        if row == self.n - 1:
            return (None, self.matrix[row-1][col])
        return (self.matrix[row+1][col], self.matrix[row-1][col])
        pass
    
    def adjacent_horizontal_numbers(self, row: int, col: int) -> (int, int):
        """ Devolve os valores imediatamente à esquerda e à direita, 
        respectivamente. """
        if col == 0:
            return (None, self.matrix[row][col+1])
        if col == self.n - 1:
            return (self.matrix[row][col-1], None)
        return (self.matrix[row][col-1], self.matrix[row][col+1])
        pass
    
    @staticmethod    
    def parse_instance(filename: str):
        """ Lê o ficheiro cujo caminho é passado como argumento e retorna
        uma instância da classe Board. """
        f = open(filename, "r")
        line = f.readline()
       
        n = int(line[:-1])
        matrix = [[None for j in range(n)] for i in range(n)]
        row = 0
        col = 0
        i = 0
        number = ''
        line = f.readline()
        while(row < n):
            while(line[i]!='\t' and line[i]!='\n'):
                number += line[i]
                i = i + 1
            matrix[row][col] = int(number)
            number =''
            if col == n - 1:
                i = 0
                col = 0
                row = row + 1
                line = f.readline()
                continue
            col  = col + 1
            i = i + 1
            
        f.close()
        board = Board(n,matrix)
        return board
        pass


class Numbrix(Problem):
    def __init__(self, board: Board):
        """ O construtor especifica o estado inicial. """
        self.initial = NumbrixState(board)
        super().__init__(self.initial)
        pass

    def actions(self, state: NumbrixState):
        """ Retorna uma lista de ações que podem ser executadas a
        partir do estado passado como argumento. """
        actions = []
        numbers = []
        val = state.board.n*state.board.n
        min = state.board.n*state.board.n
        
        for i in range(0,state.board.n):
            for j in range(0, state.board.n):
                if state.board.matrix[i][j] != 0:
                    numbers.append(state.board.matrix[i][j])
                    
                    if(state.board.matrix[i][j]==1 and (state.board.matrix[i][j] + 1 not in state.board.adjacent_horizontal_numbers(i,j) and 
                            state.board.matrix[i][j] + 1 not in state.board.adjacent_vertical_numbers(i,j))):
                        val = 1
                        continue

                    if(min > state.board.matrix[i][j]):
                        min = state.board.matrix[i][j]
                        
                    if(state.board.matrix[i][j] != 1 and val > state.board.matrix[i][j] and (state.board.matrix[i][j] + 1 not in state.board.adjacent_horizontal_numbers(i,j) and 
                            state.board.matrix[i][j] + 1 not in state.board.adjacent_vertical_numbers(i,j)
                            or( state.board.matrix[i][j] - 1 not in state.board.adjacent_horizontal_numbers(i,j) and 
                            state.board.matrix[i][j] - 1 not in state.board.adjacent_vertical_numbers(i,j)))):# and state.board.matrix[i][j] != 1):
                        val = state.board.matrix[i][j]
                       
        for a in range(0,state.board.n):
            for b in range(0, state.board.n):
                if state.board.matrix[a][b] == val:
                    if(val + 1 not in numbers and val != state.board.n*state.board.n):
                        if(state.board.adjacent_horizontal_numbers(a,b)[0] == 0):
                            actions.append((a,b-1,val+1))
                        if(state.board.adjacent_horizontal_numbers(a,b)[1] == 0):
                            actions.append((a,b+1,val+1))
                        if(state.board.adjacent_vertical_numbers(a,b)[0] == 0):
                            actions.append((a+1,b,val+1))
                        if(state.board.adjacent_vertical_numbers(a,b)[1] == 0):
                            actions.append((a-1,b,val+1))
                    if(val == min and val != 1 and min + 1 in numbers):
                        if(val - 1 not in numbers):
                            if(state.board.adjacent_vertical_numbers(a,b)[0] == 0):
                                actions.append((a+1,b,val-1))
                            if(state.board.adjacent_horizontal_numbers(a,b)[1] == 0):
                                actions.append((a,b+1,val-1))
                            if(state.board.adjacent_horizontal_numbers(a,b)[0] == 0):
                                actions.append((a,b-1,val-1))
                            if(state.board.adjacent_vertical_numbers(a,b)[1] == 0):
                                actions.append((a-1,b,val-1))

        return actions
        pass

    def result(self, state: NumbrixState, action):
        """ Retorna o estado resultante de executar a 'action' sobre
        'state' passado como argumento. A ação a executar deve ser uma
        das presentes na lista obtida pela execução de 
        self.actions(state). """
        state2 = copy.deepcopy(state)
        if(action in self.actions(state2)):
            state2.board.matrix[action[0]][action[1]] = action[2]
        return state2
        pass

    def goal_test(self, state: NumbrixState):
        """ Retorna True se e só se o estado passado como argumento é
        um estado objetivo. Deve verificar se todas as posições do tabuleiro 
        estão preenchidas com uma sequência de números adjacentes. """
        for i in range(0,state.board.n):
            for j in range(0,state.board.n):
                if(state.board.matrix[i][j] == state.board.n * state.board.n):
                    if(state.board.matrix[i][j] - 1 in state.board.adjacent_vertical_numbers(i, j) or  state.board.matrix[i][j] - 1 in state.board.adjacent_horizontal_numbers(i, j)):
                        continue
                    else:
                        return False
                if (state.board.matrix[i][j] + 1 in state.board.adjacent_vertical_numbers(i, j) or  state.board.matrix[i][j] + 1 in state.board.adjacent_horizontal_numbers(i, j)):
                    continue
                else:
                    return False
        return True

        pass

    def h(self, node: Node):
        """ Função heuristica utilizada para a procura A*. """
        board = node.state.board
        num = 0
        max = board.n*board.n
        k=1
        numbers = {}
        border = []
        path = []
        zeromatrix = [[None for j in range(board.n)] for i in range(board.n)]
        inf = float("inf")
            
        for a in range(0,board.n):
            for b in range(0,board.n):
                if(board.matrix[a][b] != 0):
                    numbers[board.matrix[a][b]] = (a,b)
                else:
                    zeromatrix[a][b] = False
    
        for i in range(0,board.n):
            for j in range(0,board.n):
                if(board.matrix[i][j] == 0):
                    continue

                if(board.matrix[i][j] != max):
                    while(numbers.get(board.matrix[i][j] + k) == None and board.matrix[i][j] + k != max):
                        k +=1
                    if(numbers.get(board.matrix[i][j] + k) != None):
                        if(manhattan_distance((i,j),numbers.get(board.matrix[i][j] + k)) > k):
                            return inf
                        elif(k != 1 and 0 not in board.adjacent_vertical_numbers(i,j) and 0 not in board.adjacent_horizontal_numbers(i,j)):
                            return inf

                        path = checkPath(board,board.matrix[i][j],board.matrix[i][j] + k,i,j)
                        if(path == None):
                            return inf
                        if(len(path) > k + 1):
                            return inf
                        num += abs(k-manhattan_distance((i,j),numbers.get(board.matrix[i][j] + k)))
                    k=1
        
        for i in range(0,board.n):
            for j in range(0,board.n):
                if(zeromatrix[i][j] == True or zeromatrix[i][j] == None):
                    continue
                else:
                    border = getborder(board,i,j,zeromatrix)
                    if(checkBubbles(board,border,numbers) == True):
                        return inf
        
        return num


def checkBubbles(board : Board,border, numbers):
    max = board.n*board.n
    aux = 0
    k = 1

    for num in border:
        if(num[0] == 1):
            if(num[0] + 1 in numbers):
                continue
            else:
                return False

        if(num[0] == max):
            if(num[0] - 1 in numbers):
                continue
            else:
                return False

        if(num[0] + 1 in numbers and num[0] - 1 in numbers):
            continue
        else:
            aux += 1
            val = num

    if(aux == 1):
        while(numbers.get(val[0] + k) == None and val[0] + k <= max):
            k +=1

        if(val[0] + k <= max):
            return True
        else:
            return False
    elif(aux > 1):
        return False

    return True
    

def getborder(board, sr, sc,zeromatrix):
    rq = collections.deque([])
    cq = collections.deque([])
    border = []

    dr = [-1, +1, 0, 0]
    dc = [0, 0, +1, -1]

    rq.append(sr)
    cq.append(sc)
    zeromatrix[sr][sc] = True

    def get_neighbors(r, c):
        for i in range(0,4):
            rr = r + dr[i]
            cc = c + dc[i]
            
            if rr < 0 or cc < 0:
                continue
            if rr >= board.n or cc >= board.n:
                continue
            
            if zeromatrix[rr][cc] == True:
                continue
            if board.matrix[rr][cc] != 0:
                border.append([board.matrix[rr][cc],(rr,cc)])
                continue
            
            rq.append(rr)
            cq.append(cc)
            zeromatrix[rr][cc] = True
    
    while len(rq) > 0:
        r = rq.pop()
        c = cq.pop()
    
        get_neighbors(r, c)

    return border

def checkPath(board : Board,src,end,sr,sc):
    queue = [([src,(sr,sc)], [])]
    visited = [[None for j in range(board.n)] for i in range(board.n)]

    def get_neighbors(node, board):
        node_left = [board.adjacent_horizontal_numbers(node[1][0],node[1][1])[0],(node[1][0], node[1][1] - 1)]
        node_right = [board.adjacent_horizontal_numbers(node[1][0],node[1][1])[1],(node[1][0], node[1][1] + 1)]
        node_down = [board.adjacent_vertical_numbers(node[1][0],node[1][1])[0],(node[1][0] + 1, node[1][1])]
        node_up = [board.adjacent_vertical_numbers(node[1][0],node[1][1])[1],(node[1][0] - 1, node[1][1])]
        neighbors = [node_left, node_right, node_down, node_up]
        return neighbors

    while len(queue) > 0:
        node, path = queue.pop(0)
        path.append(node[0])
        visited[node[1][0]][node[1][1]] = True

        if node[0] == end:
            return path

        adj_nodes = get_neighbors(node, board)
        for item in adj_nodes:
            if item[0] != None:
                if visited[item[1][0]][item[1][1]] != True and board.matrix[item[1][0]][item[1][1]] == 0 or board.matrix[item[1][0]][item[1][1]] == end:
                    queue.append((item, path[:]))

    return None

if __name__ == "__main__":
    board = Board.parse_instance(sys.argv[1])
    problem = Numbrix(board)
   
    goal_node = greedy_search(problem)

    print(goal_node.state.board.to_string(), sep="")
    
    pass
