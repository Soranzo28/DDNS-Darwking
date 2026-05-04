# Agente baseado em Objetivo com Troca de Estados

# Estados implementados:

# - fugir: se afasta de zonas de perigo 
# - coletar_tesouro: monta um plano para pegar um tesouro próximo
# - coletar_municao: monta um plano para pegar uma municao proxima
# - coletar_caixa: explode caixas de madeira
# - explorar: faz um movimento aleatório levando em consideração zonas de perigo 

import random

from collections import deque


class Agent:
    # Construtor da classe: serve para inicializar variáveis de estado interno
    def __init__(self):
        self.estado = "explorar"  # Armazena o estado inicial de ação do agente
        self.zona_perigo = set()
        self.bombas_anteriores = set()
        self.fumaca = {}

    # Função booleana auxiliar para verificar se uma posição p está bloqueada.
    # Retorna True se p está fora do mapa ou se estiver ocupada por parede/bomba/agente
    def tem_bloqueio(self, game_state, p):
        return not game_state.is_in_bounds(p) or game_state.entity_at(p) in [
            "sb",
            "ib",
            "ob",
            "b",
            0,
            1,
        ]

    # Retorna a distância de Manhattan entre os pontos p1 e p2.
    def distancia(self, p1, p2):
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    # Retorna uma tupla (d,tx,ty) sendo a distancia do tesouro mais próximo e suas coordenadas.
    # Retorna 1000 na distância caso não existam tesouros.
    def tesouro_proximo(self, ax, ay, game_state, player_state):
        d = 1000  # começa com um valor "infinito"
        tx = -1
        ty = -1

        for tesouro_x, tesouro_y in game_state.treasure:
            # distancia do tesouro até o agente
            dist = self.distancia((ax, ay), (tesouro_x, tesouro_y))
            if dist < d:
                rota = self.busca_largura(ax,ay, tesouro_x, tesouro_y, game_state, player_state)
                if rota:
                    d = dist
                    tx = tesouro_x
                    ty = tesouro_y

        return d, tx, ty

    # Retorna uma tupla (d,mx,my) sendo a distancia da municao mais próxima e suas coordenadas.
    # Retorna 1000 na distância caso não existam munições.
    def municao_proxima(self, ax, ay, game_state, player_state):
        d = 1000  # começa com um valor "infinito"
        mx = -1
        my = -1

        for municao_x, municao_y in game_state.ammo:
            # distancia da municao até o agente
            dist = self.distancia((ax, ay), (municao_x, municao_y))
            if dist < d:
                rota = self.busca_largura(ax,ay, municao_x, municao_y, game_state, player_state)
                if rota:
                    d = dist
                    mx = municao_x
                    my = municao_y

        return d, mx, my

    # Retorna uma tupla (d,tx,ty) sendo a distancia da bomba mais próxima e suas posição.
    # Retorna 1000 na distância caso não existam bombas.
    def bomba_proxima(self, ax, ay, game_state):
        d = 1000  # começa com um valor "infinito"
        bx = -1
        by = -1

        for bomba_x, bomba_y in game_state.bombs:
            # distancia da bomba até o agente
            dist = self.distancia((ax, ay), (bomba_x, bomba_y))
            if dist < d:
                d = dist
                bx = bomba_x
                by = bomba_y

        return d, bx, by

    def caixa_madeira_proxima(self, ax, ay, game_state):
        posicoes = [(ax, ay), (ax, ay + 1), (ax + 1, ay), (ax, ay - 1), (ax - 1, ay)]

        for p in posicoes:
            if game_state.entity_at(p) == "sb":
                return p

        return ()

    # Reconstrói uma rota até o ponto (mx,my) a partir de um dicionário
    # "visitados" que foi preenchido em um algoritmo de busca
    def reconstroi(self, mx, my, visitados):
        rota = [(mx, my)]
        x, y = (mx, my)

        while visitados[(x, y)] is not None:
            x, y = visitados[(x, y)]
            if visitados[(x, y)] is not None:
                rota.append((x, y))

        return rota[::-1]  # Inverte a lista

    # Retorna a ação que um agente no ponto a precisar realizar para se aproximar/afastar do ponto b
    # Recebe game_state
    # Recebe a: ponto (x,y) considerado como o agente que irá se mover
    # Recebe b: ponto (x,y) que é o ponto de referência
    # Recebe aproximar: se True o objetivo é se aproximar, caso contrário vai tentar afastar.
    # Retorna uma ação que mais aproxima ou afasta a de b.
    def mover(self, game_state, a, b, aproximar=True):

        dist_ab = self.distancia(a, b)

        actions = []
        adjacentes = {
            "u": (a[0], a[1] + 1),
            "r": (a[0] + 1, a[1]),
            "d": (a[0], a[1] - 1),
            "l": (a[0] - 1, a[1]),
        }
        for action, p in adjacentes.items():
            if not self.tem_bloqueio(game_state, p):
                dist_pb = self.distancia(p, b)
                if (dist_pb > dist_ab and not aproximar) or (
                    dist_pb < dist_ab and aproximar
                ):
                    actions.append(action)

        # Se tem alguma ação escolhe uma aleatoriamente
        if len(actions) > 0:
            return random.choice(actions)

        # Senão retorna vazio
        return ""

    # Retorna verdadeiro se o ponto (x,y) é uma posição livre no mapa.
    # Para ser considerada livre a posição deve estar dentro dos limites
    # do mapa e não deve conter nenhum objeto indicado na lista "ocupados"
    # Por padrão, ocupados são apenas blocos de madeira, minério e indestrutível
    def posicao_livre(self, x, y, game_state, ocupados=["sb", "ob", "ib", "b"]):
        b = game_state.is_in_bounds((x, y))
        e = game_state.entity_at((x, y))
        return b and e not in ocupados

    # Retorna uma lista com as posicões livres adjacentes a (ex,ey)
    def vizinhanca_livre(
        self, ex, ey, game_state, ocupados=["sb", "ob", "ib", "b"], evitar_perigo=set()
    ):
        vizinhos = []
        # Coordenadas de   cima,      baixo,   esquerda,   direita
        posicoes = [(ex, ey - 1), (ex, ey + 1), (ex - 1, ey), (ex + 1, ey)]
        for px, py in posicoes:
            if (
                self.posicao_livre(px, py, game_state, ocupados) and (px, py) not in evitar_perigo
            ):
                vizinhos.append((px, py))
        return vizinhos

    # Calcula uma rota da origem (ox,oy) até uma meta (mx,my).
    # A rota é uma lista de coordenadas ou uma lista vazia caso não exista uma rota
    # O motivo mais comum de uma rota não existir é a existência de obstaculos.
    # Como essa função usa a função vizinhanca_livre, a opção padrão do parâmetro
    # `ocupados` determina o que será considerado um obstáculo.
    def busca_largura(
        self, ox, oy, mx, my, game_state, player_state, evitar_perigo=set()
    ):
        visitados = {}
        visitados[(ox, oy)] = None
        fila = deque([(ox, oy)])  # criando a fila com a pos inicial

        while fila:  # enquanto tiver elementos na fila
            ex, ey = fila.popleft()  # retiramos elemento da esq. da fila
            if ex == mx and ey == my:  # verifica se atingiu a meta
                return self.reconstroi(mx, my, visitados)

            for x, y in self.vizinhanca_livre(
                ex, ey, game_state, evitar_perigo=evitar_perigo
            ):
                if (x, y) not in visitados:
                    visitados[(x, y)] = (ex, ey)
                    fila.append((x, y))
        return []  # Retorna uma rota vazia caso não encontre a meta

    def atualizar_mapa_perigo(self, game_state):
        bombas_atuais = set(game_state.bombs)

        # Detecta explosao
        explodiram = self.bombas_anteriores - bombas_atuais
        for bx, by in explodiram:
            self.fumaca[(bx, by)] = 2

        # Atualiza memoria
        self.bombas_anteriores = bombas_atuais

        # "Esfria" o rastro da bomba
        for pos in list(self.fumaca.keys()):
            self.fumaca[pos] -= 1
            if self.fumaca[pos] <= 0:
                del self.fumaca[pos]

        # Novo mapa de perigo
        nova_zona = set()

        # Junta tudo que representa perigo (bombas ainda ativas + rastros das bombas)
        todas_ameacas = list(bombas_atuais) + list(self.fumaca.keys())

        for bx, by in todas_ameacas:
            nova_zona.add((bx, by))  # centro da bomba
            for i in range(1, 4):  # os "braços" da explosao
                nova_zona.update(
                    [(bx + i, by), (bx - i, by), (bx, by + i), (bx, by - i)]
                )

        self.zona_perigo = nova_zona

    def rota_de_fuga(self, ax, ay, game_state):
        visitados = {}
        visitados[(ax, ay)] = None
        fila = deque([(ax, ay)])

        while fila:
            ex, ey = fila.popleft()

            if (ex, ey) not in self.zona_perigo:
                return self.reconstroi(ex, ey, visitados)

            for x, y in self.vizinhanca_livre(ex, ey, game_state):
                if (x, y) not in visitados:
                    visitados[(x, y)] = (ex, ey)
                    fila.append((x, y))
        return []

    # Função principal do jogo: deve retornar uma das ações abaixo:
    # 'u' = Andar para cima
    # 'r' = Andar para direita
    # 'd' = Andar para baixo
    # 'l' = Andar para esquerda
    # 'p' = Jogar bomba
    # ''  = Ficar parado

    def next_move(self, game_state, player_state):

        # SENSORES ========================================================

        self.atualizar_mapa_perigo(game_state)

        ax, ay = player_state.location

        distancia_tesouro, tx, ty = self.tesouro_proximo(ax, ay, game_state, player_state)
        distancia_municao, mx, my = self.municao_proxima(ax, ay, game_state, player_state)
        caixa_proxima = self.caixa_madeira_proxima(ax, ay, game_state)

        # TRANSIÇÃO DE ESTADOS ============================================

        if (ax, ay) in self.zona_perigo:
            self.estado = "fugir"
        elif distancia_municao <= 30 and player_state.ammo <= 1:
            self.estado = "coletar_municao"
        elif caixa_proxima and player_state.ammo > 0:
            self.estado = "coletar_caixa"
        elif distancia_tesouro <= 20:
            self.estado = "coletar_tesouro"
        else:
            self.estado = "explorar"

        print("Estado atual:", self.estado)

        # EXECUÇÃO DE AÇÕES ===============================================

        if self.estado == "fugir":
            rota = self.rota_de_fuga(ax, ay, game_state)
            if rota and rota[0] != (ax, ay):
                return self.mover(game_state, (ax, ay), rota[0])
            return random.choice(["u", "d", "l", "r"])

        if self.estado == "coletar_tesouro":
            rota = self.busca_largura(
                ax, ay, tx, ty, game_state, player_state, evitar_perigo=self.zona_perigo
            )
            if rota:
                return self.mover(game_state, (ax, ay), rota[0])

        if self.estado == "coletar_caixa":
            return "p"

        if self.estado == "coletar_municao":
            rota = self.busca_largura(
                ax, ay, mx, my, game_state, player_state, evitar_perigo=self.zona_perigo
            )
            if rota:
                return self.mover(game_state, (ax, ay), rota[0])

        if self.estado == "explorar":
            vizinhos_seguros = self.vizinhanca_livre(
                ax, ay, game_state, evitar_perigo=self.zona_perigo
            )
            if vizinhos_seguros:
                destino = random.choice(vizinhos_seguros)
                return self.mover(game_state, (ax, ay), destino)
            return ""

        return ""  # Caso nenhuma ação seja possível fica parado por padrão.
