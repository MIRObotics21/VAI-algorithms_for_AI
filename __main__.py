import os
import sys
import pygame
import random

#vitejte ve hre Maze escape!
#pointou je vytvorit nahodne generovane bludiste, jehoz resitelnost bude kontrolovana:
#1)bud neinformovanou metodou Djikstra
#2)nebo informovanou A*
#dalsi featura je dynamicka napoveda cesty pomoci A*

#nutne knihovny jsou:
#1)pygame - kvuli graficke vizualizaci
#2)random - kvuli nahodnemu generovani hraciho pole

#kazde pole je instance tridy Node
#obsahuje informaci o jeho poloze v prostoru, typu ('wall', 'path', 'player', 'finish' a 'help'),
#pointery na okolni 4 instance
#a udaje pro algoritmy umele inteligence - naklady na cestu, heuristiku a pointer na nejlepsi sousedni
class Node:
    def __init__(self):
        self.pos_x, self.pos_y = None, None
        self.type = 'wall'
        self.up, self.down, self.left, self.right = None, None, None, None
        self.bestPrev = None
        self.cost = None
        self.heuristic = None

#samotny Maze je graf, kde kazdy vrchol je propojen s jeho sousedy nahore, dole, vpravo, vlevo
#v teto tride se nachazi globalni promenne NodePointers (list pointeru na nody) a NodeTypes (list typu nodu s odpovidajicimi indexi)
#v idealnim pripade by tyto listy nahrazeny prohledavacimi algorytmy, slouzi jenom k ulehceni vyhledavani urcitych instanci
class Maze:
    def __init__(self, screen_width, screen_height):
        self.running = True

        self.scrn_w, self.scrn_h = screen_width, screen_height
        self.Nodesize = None

        self.NodePointers = []
        self.NodeTypes = []

        self.StartNode = None
        self.EndNode = None

    #metoda build_maze stavi bludiste o velikosti size*size
    def build_maze(self, size, start_id, end_id):
        #nasledujici promenne stanovuji dynamicky velikost a pozici pole vuci velikosti obrazovky
        NodeSize = (self.scrn_h/size)/1.3
        self.Nodesize = NodeSize
        NodeSpaceBetween = NodeSize/10
        NullPosY = (self.scrn_h/2)-((size/2)*NodeSize)-((size/2)*NodeSpaceBetween)
        NullPosX = (self.scrn_w/2)-((size/2)*NodeSize)-((size/2)*NodeSpaceBetween)
        PosX = NullPosX
        PosY = NullPosY

        #nulta instance tridy Node
        prev_Node = None

        #pri generovani se vzdy vyplni promenne pozice x a y, typ a pointery na vedlejsi instance
        #generace spodni rady - vsechny instance budou typu 'wall'
        for i in range(size):
            new_node = Node()
            self.NodePointers.append(new_node)
            self.NodeTypes.append(new_node.type)
            new_node.pos_x = PosX
            PosX = PosX + NodeSize + NodeSpaceBetween
            new_node.pos_y = PosY
            if i >=1:
                new_node.left = prev_Node
                prev_Node.right = new_node
            prev_Node = new_node

        prev_Node = None
        for j in range(size-2):
            PosX = NullPosX
            PosY = PosY + NodeSize + NodeSpaceBetween
            for k in range(size):
                #prvni a posledni budou vzdy typu 'wall'
                if k == 0 or k == size-1:
                    new_node = Node()
                    self.NodePointers.append(new_node)
                    self.NodeTypes.append(new_node.type)
                    new_node.pos_x = PosX
                    PosX = PosX + NodeSize + NodeSpaceBetween
                    new_node.pos_y = PosY
                    if k >= 1:
                        new_node.left = prev_Node
                        prev_Node.right = new_node
                    prev_Node = new_node
                    down_Node = self.NodePointers[self.NodePointers.index(new_node)-size]
                    down_Node.up = new_node
                    new_node.down = down_Node
                #instance Nodu ve stredu bludiste budou mit nahodne typy 'wall' nebo 'path'
                else:
                    new_node = Node()
                    new_node_type = random.choice(['wall','path'])
                    new_node.type = new_node_type
                    self.NodePointers.append(new_node)
                    self.NodeTypes.append(new_node.type)
                    new_node.pos_x = PosX
                    PosX = PosX + NodeSize + NodeSpaceBetween
                    new_node.pos_y = PosY
                    if k >= 1:
                        new_node.left = prev_Node
                        prev_Node.right = new_node
                    prev_Node = new_node
                    down_Node = self.NodePointers[self.NodePointers.index(new_node)-size]
                    down_Node.up = new_node
                    new_node.down = down_Node

        prev_Node = None
        #horni rada, cela typu 'wall', stejne jako prvni
        PosX = NullPosX
        PosY = PosY + NodeSize + NodeSpaceBetween
        for l in range(size):
            new_node = Node()
            self.NodePointers.append(new_node)
            self.NodeTypes.append(new_node.type)
            new_node.pos_x = PosX
            PosX = PosX + NodeSize + NodeSpaceBetween
            new_node.pos_y = PosY
            if l >= 1:
                new_node.left = prev_Node
                prev_Node.right = new_node
            prev_Node = new_node
            down_Node = self.NodePointers[self.NodePointers.index(new_node) - size]
            down_Node.up = new_node
            new_node.down = down_Node

        #jako posledni priradime ponter StartNode a EndNode, podle pozadovanych id ze vstupu
        #jejich typ jsou 'player' a 'finish'
        self.StartNode = self.NodePointers[start_id]
        self.StartNode.cost = 0
        self.StartNode.type = 'player'
        self.NodeTypes[start_id] = 'player'
        self.EndNode = self.NodePointers[end_id]
        self.EndNode.type = 'finish'
        self.NodeTypes[end_id] = 'finish'

    #metoda pro vypocet euklidovske vzdalenosti na zaklade parametru x a y
    #nepotrebujeme odmocnovat vysledek
    def Euklid(self, start):
        start_x = start.pos_x
        start_y = start.pos_y
        end_x = self.EndNode.pos_x
        end_y = self.EndNode.pos_y
        distance = (start_x - end_x)**2 + (start_y - end_y)**2
        return distance

    #metoda pro nelezeni nejkratsi cesty pomoci A*
    def Astar(self):
        #nejsprve jsou resetovany vsechny naklady a nejlepsi predchozi, dulezite pro dynamickou napovedu
        for i in self.NodePointers:
            i.cost = None
            i.bestPrev = None

        #klasicka preparace na A*
        self.StartNode.heuristic = self.Euklid(self.StartNode)
        self.StartNode.cost = 0
        open = [self.StartNode]
        closed = []
        path = []
        expand = None
        fmin = None

        #nalezeni nejlevnejsi instance z open podle f = g+h = naklady+heuristika
        while open:
            for i in range(len(open)):
                current = open[i]
                f = current.cost + current.heuristic
                if fmin == None or f < fmin:
                    fmin = f
                    expand = open[i]
            fmin = None

            #prohledavan nejlevnejsi - jde do closed
            open.remove(expand)
            closed.append(expand)

            #nejprve se kontroluje jestli soused je vubec expandovatelny, musi byt jineho typu nez 'wall' a nesmi byt v closed
            if expand.up.type != 'wall' and expand.up not in closed:
                #pokud jeste nebyl nalezen tak je pridan do open
                #bestPrev je nastaven prohledavany
                if expand.up not in open:
                    open.append(expand.up)
                    expand.up.cost = expand.cost+1
                    expand.up.heuristic = self.Euklid(expand.up)
                    expand.up.bestPrev = expand
                #pokud uz je v open, je zkontrolovano, jestli nema levnejsi naklady
                #pokud ano, je prepsan naklad a bestPrev
                if expand.up in open:
                    if expand.up.cost > expand.cost + 1:
                        expand.up.cost = expand.cost + 1
                        expand.up.bestPrev = expand
            #opakuje se 4x pro 'up', 'down', 'left', 'right'
            if expand.down.type != 'wall' and expand.down not in closed:
                if expand.down not in open:
                    open.append(expand.down)
                    expand.down.cost = expand.cost+1
                    expand.down.heuristic = self.Euklid(expand.down)
                    expand.down.bestPrev = expand
                if expand.down in open:
                    if expand.down.cost > expand.cost + 1:
                        expand.down.cost = expand.cost + 1
                        expand.down.bestPrev = expand
            if expand.left.type != 'wall' and expand.left not in closed:
                if expand.left not in open:
                    open.append(expand.left)
                    expand.left.cost = expand.cost + 1
                    expand.left.heuristic = self.Euklid(expand.left)
                    expand.left.bestPrev = expand
                if expand.left in open:
                    if expand.left.cost > expand.cost + 1:
                        expand.left.cost = expand.cost + 1
                        expand.left.bestPrev = expand
            if expand.right.type != 'wall' and expand.right not in closed:
                if expand.right not in open:
                    open.append(expand.right)
                    expand.right.cost = expand.cost+1
                    expand.right.heuristic = self.Euklid(expand.right)
                    expand.right.bestPrev = expand
                if expand.right in open:
                    if expand.right.cost > expand.cost + 1:
                        expand.right.cost = expand.cost + 1
                        expand.right.bestPrev = expand

            #backtracking po nalezeni nejlepsi cesty
            if self.EndNode in closed and open == []:
                current = self.EndNode
                while current.bestPrev != None:
                    path.append(current)
                    current = current.bestPrev
                return path

        #pokud cyklus while skoncil s prazdnym open a nebyla nalezena cesta, tak metoda vraci false
        if path == []:
            return False

    #metoda pro kontrolu neinformovanym prohledavanim pomoci Djikstry
    def Djikstra(self):
        #opet reset
        for i in self.NodePointers:
            i.cost = None
            i.bestPrev = None

        #priprava
        self.StartNode.cost = 0
        open = [self.StartNode]
        closed = []
        path = []
        expand = None

        #tentokrat vyber nezavisly na heuristice a nakladum
        while open:
            expand = open[0]

            open.remove(expand)
            closed.append(expand)

            #obdobne reseni jako u A*, nevyzaduje vypocet heuristik
            if expand.up.type != 'wall' and expand.up not in closed:
                if expand.up not in open:
                    open.append(expand.up)
                    expand.up.cost = expand.cost + 1
                    expand.up.bestPrev = expand
                if expand.up in open:
                    if expand.up.cost > expand.cost + 1:
                        expand.up.cost = expand.cost + 1
                        expand.up.bestPrev = expand
            if expand.down.type != 'wall' and expand.down not in closed:
                if expand.down not in open:
                    open.append(expand.down)
                    expand.down.cost = expand.cost + 1
                    expand.down.bestPrev = expand
                if expand.down in open:
                    if expand.down.cost > expand.cost + 1:
                        expand.down.cost = expand.cost + 1
                        expand.down.bestPrev = expand
            if expand.left.type != 'wall' and expand.left not in closed:
                if expand.left not in open:
                    open.append(expand.left)
                    expand.left.cost = expand.cost + 1
                    expand.left.bestPrev = expand
                if expand.left in open:
                    if expand.left.cost > expand.cost + 1:
                        expand.left.cost = expand.cost + 1
                        expand.left.bestPrev = expand
            if expand.right.type != 'wall' and expand.right not in closed:
                if expand.right not in open:
                    open.append(expand.right)
                    expand.right.cost = expand.cost + 1
                    expand.right.bestPrev = expand
                if expand.right in open:
                    if expand.right.cost > expand.cost + 1:
                        expand.right.cost = expand.cost + 1
                        expand.right.bestPrev = expand

            #backtracking stejny
            if self.EndNode in closed:
                current = self.EndNode
                while current.bestPrev != None:
                    path.append(current)
                    current = current.bestPrev
                return path

        #neuspech stejny
        if path == []:
            return False

    #metoda pro pohyb hrace v bludisti
    def move(self, direction):
        #v zavislosti na stlacene klavese vybira souseda
        if direction == 'up':
            new_player_pos = self.StartNode.up
        if direction == 'down':
            new_player_pos = self.StartNode.down
        if direction == 'left':
            new_player_pos = self.StartNode.left
        if direction == 'right':
            new_player_pos = self.StartNode.right

        #pokud se muze na nove pole pohnout (neni 'wall')
        #prepisuji se udaje o StartNode
        if new_player_pos.type == 'path' or new_player_pos.type == 'finish':
            self.StartNode.type = 'path'
            new_player_pos.type = 'player'
            id_old = self.NodePointers.index(self.StartNode)
            id_new = self.NodePointers.index(new_player_pos)
            self.NodeTypes[id_old] = 'path'
            self.NodeTypes[id_new] = 'player'
            self.StartNode = new_player_pos

    #pygame graficka vizualizace pomoci metody run
    def run(self):
        #inicializace pygamu
        pygame.init()
        self.screen = pygame.display.set_mode((self.scrn_w, self.scrn_h))
        pygame.display.set_caption('Maze')
        clock = pygame.time.Clock()

        while self.running:
            #kontroly vstupu a reakce na ne
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                #reakce na 'w','s','a','d'
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.move('up')
                    if event.key == pygame.K_w:
                        self.move('down')
                    if event.key == pygame.K_a:
                        self.move('left')
                    if event.key == pygame.K_d:
                        self.move('right')
                #reakce na stlaceni M1 - zobrazeni napovedy pomoci A*
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        A = self.Astar()
                        if A != False:
                            for i in A:
                                if i.type == 'path':
                                   i.type = 'help'
                #reakce na konec stlaceni M1 - skryti napovedy
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        if A != False:
                            for i in A:
                                if i.type == 'help':
                                    i.type = 'path'

            #vykresleni hraci plochy
            #pozadi bile
            self.screen.fill((255, 255, 255))

            #pro kazdou instanci se vykresluje ctverec s prislusnou barvou
            for i in range(len(self.NodePointers)):
                current_node = self.NodePointers[i]
                if current_node.type == 'wall':
                    pygame.draw.rect(self.screen, (0, 0, 0), (current_node.pos_x, current_node.pos_y, self.Nodesize, self.Nodesize))
                if current_node.type == 'path':
                    pygame.draw.rect(self.screen, (0, 255, 0), (current_node.pos_x, current_node.pos_y, self.Nodesize, self.Nodesize))
                if current_node.type == 'player':
                    pygame.draw.rect(self.screen, (255, 0, 0), (current_node.pos_x, current_node.pos_y, self.Nodesize, self.Nodesize))
                if current_node.type == 'finish':
                    pygame.draw.rect(self.screen, (0, 0, 255), (current_node.pos_x, current_node.pos_y, self.Nodesize, self.Nodesize))
                if current_node.type == 'help':
                    pygame.draw.rect(self.screen, (255, 165, 0), (current_node.pos_x, current_node.pos_y, self.Nodesize, self.Nodesize))

            #ukonceni programu pokud hrac dojde na konecne pole
            if 'finish' not in self.NodeTypes:
                self.running = False
                print('CG, you are winner!')

            #refresh rate okna
            pygame.display.flip()
            clock.tick(30)

        pygame.quit()

#main ma za ukol
#1)generovat nahodne bludiste
#2)pocitat jak dlouho trvaji kontroly pomoci A* a Djikstra
#3)inicializovat hru pokud dojde k nalezeni resitelneho bludiste
if __name__ == '__main__':
    solvable_found = False
    i=0

    pygame.init()
    start_time = pygame.time.get_ticks()
    totalDjikstra = 0
    totalAstar = 0

    while solvable_found == False:
        bludiste = Maze(1920, 1020)
        bludiste.build_maze(20, 21, 378)
        i = i+1

        startDjikstra = pygame.time.get_ticks()
        bludiste.Djikstra()
        endDjikstra = pygame.time.get_ticks()
        totalDjikstra = totalDjikstra + endDjikstra - startDjikstra

        startAstar = pygame.time.get_ticks()
        bludiste.Astar()
        endAstar = pygame.time.get_ticks()
        totalAstar = totalAstar + endAstar - startAstar

        if bludiste.Astar() != False:
            solvable_found = True

    elapsed_time = pygame.time.get_ticks() - start_time
    print(f"Elapsed time to find solvable Maze: {elapsed_time / 1000:.2f} seconds")
    print(f'Number of possible Mazes generated:',i)
    print(f"Elapsed time to find solvable using Djikstra: {totalDjikstra / 1000:.2f} seconds")
    print(f"Elapsed time to find solvable using A*: {totalAstar / 1000:.2f} seconds")
    pygame.quit()

    bludiste.run()