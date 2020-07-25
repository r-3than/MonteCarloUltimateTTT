import pygame
import numpy as np
import copy , random
import threading , time
from math import sqrt




class tttGame:
    def __init__(self,amtrow,amtcol,height,width,margin,playcolour,player1Col,player2Col):
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GREEN = (0, 255, 0)
        self.RED = (255, 0, 0)
        self.BLUE = (0,0,255)
        self.amtrow = amtrow
        self.amtcol = amtcol
        self.height = height
        self.width = width
        self.margin = margin
        self.playcolour = playcolour
        self.Player1 = player1Col
        self.Player2 = player2Col
        self.MovesPlayed = []
        self.grid = []
        self.TotalGrid = []
        ##TF
        self.env = Game()

        self.MC = MonteCarlo(self.env)
        self.MC.getChildren()
        self.MCThread = threading.Thread(target=self.simThread)
        #self.MCThread.start()
        #self.model =load_model("./1kRun.h5")
        #self.model.summary()
        ##TF

        for row in range(3):
            self.TotalGrid.append([])
            for column in range(3):
                self.TotalGrid[row].append(0)
        for row in range(amtrow):
            self.grid.append([])
            for column in range(amtcol):
                self.grid[row].append(0)

        self.totxsize = ((width + margin) * amtrow)+5*margin
        self.totysize = ((height + self.margin) * amtcol)+5*self.margin


        self.allowedx = -1
        self.allowedy = -1
        self.playablex = self.margin
        self.playabley = self.margin
        self.playsizex = (3*self.width + 4*self.margin)*3
        self.playsizey = (3*self.height + 4*self.margin)*3
        self.playrect = [self.playablex,self.playabley,self.playsizex,self.playsizex]
        self.playwidth = int(self.width//20)
        if self.playwidth == 0:
            self.playwidth = 1
        self.done = False
        self.redPlaying = True

        self.tot3by3 = (3*self.width+self.margin)

        self.Main()

    def Main(self):
        time.sleep(1)
        self.newAiCalc()
        WINDOW_SIZE = [self.totxsize, self.totysize]
        self.screen = pygame.display.set_mode(WINDOW_SIZE)

        pygame.display.set_caption("Ulimate Tic tac toe what evers")
        self.clock = pygame.time.Clock()
        while not self.done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.done = True
                elif event.type == pygame.K_q:
                    print ("quit")
                    self.done = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.pos = pygame.mouse.get_pos()
                    pos = self.pos
                    self.xcord = ((pos[0] - ((pos[0]//self.tot3by3)-1)*self.margin) - 2*self.margin) // (self.margin+self.width)
                    self.ycord = ((pos[1] - ((pos[1]//self.tot3by3)-1)*self.margin) - 2*self.margin)// (self.margin+self.height)
                    print("Click ", pos, "Grid coordinates: ", self.xcord, self.ycord , "Inner cords",self.xcord%3,self.ycord%3)
                    if self.xcord /8 <= 1 and self.ycord /8 <= 1:
                        if self.grid[self.xcord][self.ycord] == 0:
                            if (self.allowedx == -1 and self.allowedy == -1) or (self.allowedx <= self.xcord <= self.allowedx+2 and self.allowedy <= self.ycord <= self.allowedy+2): #move anywhere
                                if self.redPlaying == True:
                                    self.grid[self.xcord][self.ycord] = 1
                                    self.redPlaying = False
                                    self.playcolour = self.Player2
                                else:
                                    self.grid[self.xcord][self.ycord] = 2
                                    self.redPlaying = True
                                    self.playcolour = self.Player1
                                #self.MovesPlayed.append(str(self.xcord)+","+str(self.ycord))

                                self.winCalc()
                                self.allowedx ,self.allowedy = self.NextBox()
                                self.ResizePlayBox()
                                action = (self.xcord*9) +self.ycord
                                self.MC.parse(action)
                                self.MC.env.step(action)



                                self.newAiCalc()

            self.screen.fill(self.BLACK)
            extramarginx = 0
            extramarginy = 0
            for row in range(amtrow):
                if row%3 == 0:
                    extramarginy = extramarginy +self.margin
                for column in range(amtcol):
                    color = self.WHITE
                    if column%3 == 0:
                        extramarginx = extramarginx + self.margin
                    if self.grid[column][row] == 1:
                        color = self.Player1
                    if self.grid[column][row] == 2:
                        color = self.Player2
                    pygame.draw.rect(self.screen,
                                     color,
                                     [((self.margin + self.width) * column) + self.margin + extramarginx,
                                      ((self.margin + self.height) * row) + self.margin+ extramarginy,
                                      self.width,
                                      self.height])

                    pygame.draw.rect(self.screen, self.playcolour, self.playrect,self.playwidth)
                extramarginx =0

            self.clock.tick(60)

            pygame.display.flip()

        pygame.quit()
    def simThread(self):
        self.calcing = True
        while self.calcing == True:
            if self.MC.maxPlayouts > self.MC.currentplayouts:
                self.MC.singleSim()
                print("RUNNING!")
    def newAiCalc(self):
        ##HERE!
        #self.calcing = False
        #while self.MCThread.is_alive():
        #    time.sleep(0.1)
        self.MC.sim()
        action=self.MC.bestMove()
        self.MC.parse(action)
        self.MC.env.step(action)
        x = action // 9
        y = action % 9
        self.xcord = x
        self.ycord = y
        if self.redPlaying == True:
            self.grid[self.xcord][self.ycord] = 1
            self.redPlaying = False
            self.playcolour = self.Player2
        else:
            self.grid[self.xcord][self.ycord] = 2
            self.redPlaying = True
            self.playcolour = self.Player1
        self.winCalc()
        self.allowedx ,self.allowedy = self.NextBox()
        self.ResizePlayBox()
        #self.MCThread.start()

    def ChooseBest(self):
        PossibleMoves = self.PlayableSq()
        highestPercent = 0
        drawhighpercent =0
        bestmove = [PossibleMoves[0][0],PossibleMoves[0][1]]
        for move in PossibleMoves:
            tempGrid = copy.deepcopy(self.grid)
            if self.redPlaying:
                tempGrid[move[0]][move[1]] = 1
            else:
                tempGrid[move[0]][move[1]] = 2
            Grid = tempGrid
            npGrid = [0 for i in range(81)]
            for xCord in range(0,len(Grid)-1):
                    for yCord in range(0,len(Grid[xCord])-1):
                        if Grid[xCord][yCord] != 0:
                            npGrid[(xCord+(yCord*9))] = ((float(Grid[xCord][yCord]) -1)) - 0.25
            #print(npGrid)
            npGrid = np.array(npGrid)
            #print(npGrid,npGrid.shape)
            npGrid=npGrid.reshape(1,-1)
        #print(npGrid,npGrid.shape,npGrid.ndim)
            #print(move)
            vals=self.model.predict(npGrid,batch_size=1)
            #print(round(vals[0][0],2),"Draw percent")
            if vals[0] > highestPercent:
                highestPercent = vals[0]
                drawhighpercent = vals[0][0]
                bestmove[0] = move[0]
                bestmove[1] = move[1]

            #print(round(vals[0][2],2),"Blue (Player 1) win percent")

        print("Orange:",bestmove)
        #time.sleep(1)
        if self.redPlaying == True:
            self.grid[bestmove[0]][bestmove[1]] = 1
            self.redPlaying = False
            self.playcolour = self.Player2
        else:
            self.grid[bestmove[0]][bestmove[1]] = 2
            self.redPlaying = True
            self.playcolour = self.Player1
        #self.MovesPlayed.append(str(self.xcord)+","+str(self.ycord))
        self.xcord =  bestmove[0]
        self.ycord =  bestmove[1]
        self.winCalc()
        self.allowedx ,self.allowedy = self.NextBox()
        self.ResizePlayBox()
        #self.ChooseBest()

    def PlayableSq(self):
        playableSquares = []
        for x in range(0,8):
            for y in range(0,8):
                if self.grid[x][y] == 0:
                    if (self.allowedx == -1 and self.allowedy == -1) or (self.allowedx <= x <= self.allowedx+2 and self.allowedy <= y <= self.allowedy+2):
                        playableSquares.append((x,y))
        return playableSquares
    def NextBox(self):
        if self.TotalGrid[self.xcord%3][self.ycord%3] != 0:
            return (-1,-1)
        else:
            return((self.xcord%3)*3,(self.ycord%3)*3)

    def SetWin(self,Team):
        for x in range(self.amtrow):
            for y in range(self.amtcol):
                self.grid[x][y] = Team
        for x in self.TotalGrid:
            for y in x:
                y = Team

    def winSetter(self,Team):
        self.TotalGrid[self.xcord//3][self.ycord//3] = Team
        for x in range((self.xcord//3) * 3,(self.xcord//3) *3 + 3):
            for y in range((self.ycord//3) * 3,(self.ycord//3) *3 + 3):
                self.grid[x][y] = Team
        for x in range(0,3):
            if self.TotalGrid[x][0] == Team and self.TotalGrid[x][1] == Team and self.TotalGrid[x][2] == Team:
                print("Win detected on",x)
                self.SetWin(Team)
        for y in range(0,3):
            if self.TotalGrid[0][y] == Team and self.TotalGrid[1][y] == Team and self.TotalGrid[2][y] == Team:
                print("Win detected on ",y)
                self.SetWin(Team)
        if (self.TotalGrid[0][0] ==Team and self.TotalGrid[1][1] == Team and self.TotalGrid[2][2] == Team) or (self.TotalGrid[2][0] == Team and self.TotalGrid[1][1] == Team and self.TotalGrid[0][2] == Team ):
            print("Win here detected")
            self.SetWin(Team)
        print(self.TotalGrid)


    def ResizePlayBox(self):
        if self.allowedx == -1 and self.allowedy == -1:
            self.playrect[0] = self.margin
            self.playrect[1] = self.margin
            self.playrect[2] = (3*self.width + 4*self.margin)*3
            self.playrect[3] = (3*self.height + 4*self.margin)*3
        else:

            self.playrect[1]=self.allowedy*(self.margin+self.height) + 2*self.margin + ((self.allowedy//3 -1)*self.margin)
            self.playrect[0]=self.allowedx*(self.margin+self.width) + 2*self.margin + ((self.allowedx//3 -1) *self.margin)
            self.playrect[2]=(self.margin+self.width)*3 + self.margin
            self.playrect[3]=(self.margin+self.height)*3 + self.margin

    def winCalc(self):
        OC = [self.xcord,self.ycord]
        IC = (self.xcord%3,self.ycord%3)
        thisTileTeam = self.grid[self.xcord][self.ycord]
        Team = thisTileTeam
        if thisTileTeam == 0:
            return "Invaild Team"
        if IC == (0,0):

            if self.grid[self.xcord+1][self.ycord] == thisTileTeam and self.grid[self.xcord+2][self.ycord] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord][self.ycord+1] == thisTileTeam and self.grid[self.xcord][self.ycord+2] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord+1][self.ycord+1] == thisTileTeam and self.grid[self.xcord+2][self.ycord+2] == thisTileTeam:
                self.winSetter(Team)
        elif IC == (1,0):
            if self.grid[self.xcord+1][self.ycord] == thisTileTeam and self.grid[self.xcord-1][self.ycord] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord][self.ycord+1] == thisTileTeam and self.grid[self.xcord][self.ycord+2] == thisTileTeam:
                self.winSetter(Team)
        elif IC == (2,0):
            if self.grid[self.xcord-1][self.ycord] == thisTileTeam and self.grid[self.xcord-2][self.ycord] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord][self.ycord+1] == thisTileTeam and self.grid[self.xcord][self.ycord+2] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord-1][self.ycord+1] == thisTileTeam and self.grid[self.xcord-2][self.ycord+2] == thisTileTeam:
                self.winSetter(Team)
        elif IC == (0,1):
            if self.grid[self.xcord][self.ycord+1] == thisTileTeam and self.grid[self.xcord][self.ycord-1] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord+1][self.ycord] == thisTileTeam and self.grid[self.xcord+2][self.ycord] == thisTileTeam:
                self.winSetter(Team)
        elif IC == (1,1):
            if self.grid[self.xcord][self.ycord+1] == thisTileTeam and self.grid[self.xcord][self.ycord-1] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord+1][self.ycord] == thisTileTeam and self.grid[self.xcord-1][self.ycord] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord-1][self.ycord-1] == thisTileTeam and self.grid[self.xcord+1][self.ycord+1] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord-1][self.ycord+1] == thisTileTeam and self.grid[self.xcord+1][self.ycord-1] == thisTileTeam:
                self.winSetter(Team)

        elif IC == (2,1):
            if self.grid[self.xcord][self.ycord+1] == thisTileTeam and self.grid[self.xcord][self.ycord-1] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord-1][self.ycord] == thisTileTeam and self.grid[self.xcord-2][self.ycord] == thisTileTeam:
                self.winSetter(Team)

        elif IC == (0,2):
            if self.grid[self.xcord+1][self.ycord] == thisTileTeam and self.grid[self.xcord+2][self.ycord] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord][self.ycord-1] == thisTileTeam and self.grid[self.xcord][self.ycord-2] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord+1][self.ycord-1] == thisTileTeam and self.grid[self.xcord+2][self.ycord-2] == thisTileTeam:
                self.winSetter(Team)
        elif IC == (1,2):
            if self.grid[self.xcord+1][self.ycord] == thisTileTeam and self.grid[self.xcord-1][self.ycord] == thisTileTeam:
                self.winSetter(Team)
            elif self.grid[self.xcord][self.ycord-1] == thisTileTeam and self.grid[self.xcord][self.ycord-2] == thisTileTeam:
                self.winSetter(Team)

        elif IC == (2,2):
            if (self.grid[self.xcord][self.ycord-1] == thisTileTeam and self.grid[self.xcord][self.ycord-2] == thisTileTeam) :
                self.winSetter(Team)
            elif (self.grid[self.xcord-1][self.ycord] == thisTileTeam and self.grid[self.xcord-2][self.ycord] == thisTileTeam):
                self.winSetter(Team)
            elif self.grid[self.xcord-1][self.ycord-1] == thisTileTeam and self.grid[self.xcord-2][self.ycord-2] == thisTileTeam:
                self.winSetter(Team)
        amtused = 0
        #print(self.xcord,IC[0],self.ycord,IC[1])
        for x in range(self.xcord-IC[0],self.xcord-IC[0]+3):
            for y in range(self.ycord-IC[1],self.ycord-IC[1]+3):
                if self.grid[x][y] != 0:
                    amtused = amtused + 1
        if amtused == 9:
            if self.TotalGrid[self.xcord//3][self.ycord//3] == 0:
                self.TotalGrid[self.xcord//3][self.ycord//3] = -1
                print("Box tied!!")

amtrow =9
amtcol =9
 # HEIGHT AND WIDTH NEED TO BE LARGER THAN MARGIN !!!
HEIGHT = 90
WIDTH = 90
MARGIN = 15
playcolour = [25, 250, 100]



import numpy as np
import copy , random

class box:
    def __init__(self):
        self.Tiles = [[0,0,0],[0,0,0],[0,0,0]]
        self.full = False
        self.OwnedBy = 0
    def tryPlay(self,x,y,team):
        if self.Tiles[x][y] == 0:
            self.Tiles[x][y] = team
            tempReward = int(self.checkWin(team))
            return tempReward
        return -1
    def checkWin(self,team):
        r = 0
        for x in range(0,3):
            if self.Tiles[x][0] == team and self.Tiles[x][1] == team and self.Tiles[x][2] == team:
                ##print("Win")
                r=self.fillBox(team)
            if self.Tiles[0][x] == team and self.Tiles[1][x] == team and self.Tiles[2][x] == team:
                ##print("Win")
                r=self.fillBox(team)
        if self.Tiles[0][0] == team and self.Tiles[1][1] == team and self.Tiles[2][2] == team:
            ##print("Win")
            r=self.fillBox(team)
        if self.Tiles[2][0] == team and self.Tiles[1][1] == team and self.Tiles[0][2] == team:
            ##print("Win")
            r=self.fillBox(team)

        count = 0
        for j in self.Tiles:
            for i in j:
                if i != 0:
                    count = count + 1
        if count == 9:
            self.full = True
        return r

    def fillBox(self,team):
        ##print("Filling")
        for x in range(0,3):
            for y in range(0,3):
                self.Tiles[x][y] = team
        self.full = True
        self.OwnedBy = team
        return 1

class Game:
    def __init__(self):
        self.Player = 1
        self.boxes = [[],[],[]]
        self.done = True
        self.hasWon = False
        self.reset()

    def amtbox(self):
        temp = 0
        for i in self.boxes:
            for j in i:
                if j.OwnedBy != 0:
                    temp = temp+1
        if temp >= 4:
            return True
        else:
            return False

    def reset(self):
        self.lastreward = 0
        self.hasWon = False
        self.hasFailed = False
        self.allowedX = -1
        self.allowedY = -1
        self.boxes = [[],[],[]]
        for i in range(3):
            for j in range(3):
                self.boxes[i].append(box())
        ##print(self.boxes)
        ##print("Finished")

        return self.getState()

    def getState(self):
        action = 0
        tempList = []
        for action in range(0,81):
            ###print(action)
            x = action // 9
            y = action % 9
            indexX = x//3
            indexY = y //3
            tempList.append(self.boxes[indexX][indexY].Tiles[x%3][y%3])

        return tempList

    def step(self,action):
        reward = 0.01
        tempReward = 0
        x = action // 9
        y = action % 9
        indexX = x//3
        indexY = y //3
        ##print(self.allowedX,self.allowedY , indexX , indexY)
        ##print(x,y,x%3,y%3)

        if self.allowedX == -1 and self.allowedY == -1:
            tempReward = self.boxes[indexX][indexY].tryPlay(x%3,y%3,self.Player)
            if tempReward >=0 :
                #print("Move is good")
                self.allowedX , self.allowedY = x%3 , y%3
                if self.boxes[self.allowedX][self.allowedY].full:
                    self.allowedX,self.allowedY = -1 , -1
                reward = reward*2
            else:
                reward = -5
                #self.hasFailed = True
        elif self.allowedX == indexX and self.allowedY ==indexY:
            tempReward = self.boxes[indexX][indexY].tryPlay(x%3,y%3,self.Player)
            if tempReward >=0 :
                ##print("Move is good")
                self.allowedX , self.allowedY = x%3 , y%3
                if self.boxes[self.allowedX][self.allowedY].full:
                    self.allowedX,self.allowedY = -1 , -1
                reward = reward*2
            else:
                reward = -5
                #self.hasFailed = True
        else:
            ##print(self.boxes[indexX][indexY].Tiles)
            ##print("sel is wrong")
            reward = -5
            #self.hasFailed = True

        if self.hasWon:
            reward = -5
            return (self.Player,0)
        if self.checkWin(self.Player) == "WIN":
            return (self.Player,1)
            self.fillBoard()
            reward = 5
            self.hasWon = True
        if self.isFull() == True:
            return (self.Player,2)
            self.hasWon = True
            reward = -3

        state = self.getState()
        self.Player = -self.Player

        reward = reward - self.lastreward + tempReward
        self.lastreward = tempReward

        done = self.hasWon or self.hasFailed
        return None
    def fillBoard(self):
        for action in range(0,81):
            ##print(action)
            x = action // 9
            y = action % 9
            indexX = x//3
            indexY = y //3
            self.boxes[indexX][indexY].Tiles[x%3][y%3] = self.Player

    def getMoves(self):
        moves = []
        for action in range(0,81):
            ##print(action)
            x = action // 9
            y = action % 9
            indexX = x//3
            indexY = y //3
            if self.allowedX == -1 and self.allowedY == -1:
                #print("playanywher")
                if self.boxes[indexX][indexY].Tiles[x%3][y%3] == 0:
                    moves.append(action)
            elif self.allowedX == indexX and self.allowedY ==indexY:
                if self.boxes[indexX][indexY].Tiles[x%3][y%3] == 0:
                    moves.append(action)
        ##print(moves)
        return moves
    def checkWin(self,team):
        for x in range(0,3):
            if self.boxes[x][0].OwnedBy == team and self.boxes[x][1].OwnedBy == team and self.boxes[x][2].OwnedBy == team:
                ##print("Win")
                return "WIN"
            if self.boxes[0][x].OwnedBy == team and self.boxes[1][x].OwnedBy == team and self.boxes[2][x].OwnedBy == team:
                ##print("Win")
                return "WIN"
        if self.boxes[0][0].OwnedBy == team and self.boxes[1][1].OwnedBy == team and self.boxes[2][2].OwnedBy == team:
            ##print("Win")
            return "WIN"
        if self.boxes[2][0].OwnedBy == team and self.boxes[1][1].OwnedBy == team and self.boxes[0][2].OwnedBy == team:
            ##print("Win")
            return "WIN"

    def isFull(self):
        x = 0
        for j in self.boxes:
            for i in j:
                if i.full:
                    x = x+1
        if x== 9:
            return True
        else:
            return False
    def copy(self,envObj):
        envObj.Player = self.Player
        envObj.boxes = copy.deepcopy(self.boxes)
        envObj.allowedX , envObj.allowedY = self.allowedX , self.allowedY

    def render(self):
        tempList = []
        for action in range(0,81):

            ###print(action)
            if action % 9 == 0:
                print(tempList)
                tempList = []

            x = action // 9
            y = action % 9
            indexX = x//3
            indexY = y //3
            tempList.append(self.boxes[indexX][indexY].Tiles[x%3][y%3])
        print(tempList)

class Node:
    def __init__(self,parent,move,env,r):
        self.parent = parent
        self.move = move
        self.currentEnv = env
        self.r = r
        self.playouts = 1
        self.winningAmongChildren = 0
        self.lossAmongChildren = 0
        self.children = None
        self.prob = 0
        self.UCT = 0
    def getChildren(self):
        if self.children == None:
            self.children = []
            for item in self.currentEnv.getMoves():
                newEnv = Game()
                self.currentEnv.copy(newEnv)
                r=newEnv.step(item)
                newNode = Node(self,item,newEnv,r)
                self.children.append(newNode)
        else:
            for child in self.children:
                child.getChildren()
    def eval(self):
        if self.parent != None:

            try:
                self.UCT = self.winningAmongChildren/self.playouts + sqrt(2)*sqrt(np.log(self.parent.playouts)/self.playouts)
            except:
                print(np.log(self.parent.playouts),self.playouts)

            #print(self.UCT)
    def highestChildUCT(self):
        highestUCT = 0
        tempChild = None
        if self.children != None:
            for child in self.children:
                if child.UCT >= highestUCT:
                    highestUCT = child.UCT
                    tempChild = child
        return tempChild
    def printChildren(self):
        if self.children != None:
            for child in self.children:
                child.printChildren()
        else:
            self.currentEnv.render()
    def playout(self,useUCT=True):
        self.playouts = self.playouts + 1
        found = False
        nextPlay = None
        move = None
        moves = self.currentEnv.getMoves()
        if self.r == (1,1) or self.r == (-1,0):
            self.winningAmongChildren = self.winningAmongChildren + 1
            self.prob = 999
            return "WIN"
        if self.r == (1,0) or self.r == (-1,1):
            self.lossAmongChildren = self.lossAmongChildren + 1
            self.prob = -999
            return "fLOSS"
        if self.r == (1,2) or self.r == (-1,2):
            return "DRAW"
        if len(moves) != 0:
            move = moves[random.randint(0,len(moves)-1)]
            if self.currentEnv.amtbox():
                for mov in moves:
                    tempEnv = Game()
                    self.currentEnv.copy(tempEnv)
                    r = tempEnv.step(mov)
                    if r == (-1,1):
                        move = mov
                    if r ==(1,1):
                        move = mov
        if self.children != None:
            for child in self.children:
                if child.move == move:
                    found=True
                    nextPlay = child
                    break
        else:
            self.children = []
        if found == False and move != None:
            newEnv = Game()
            self.currentEnv.copy(newEnv)
            r=newEnv.step(move)
            newNode = Node(self,move,newEnv,r)
            self.children.append(newNode)
            nextPlay = newNode
        if random.randint(0,10) > 2 and useUCT:
            this = self.highestChildUCT()
            if this != None:
                nextPlay = this
        #if self.lossAmongChildren > self.winningAmongChildren * 5:
        #    return "END"
        self.eval()
        if nextPlay != None:
            isWon = nextPlay.playout(useUCT)
            if isWon == "WIN":
                #print("WINNNERRR!")
                self.winningAmongChildren = self.winningAmongChildren + 1
                self.prob = round(self.winningAmongChildren/self.playouts,5)
                return "WIN"
            if isWon == "fLOSS":
                self.winningAmongChildren = 0
                self.prob = -999
                self.lossAmongChildren = self.lossAmongChildren + 1
                return "LOSS"
            if isWon == "LOSS":
                self.lossAmongChildren = self.lossAmongChildren + 1
                return "LOSS"
            if isWon == "DRAW":
                self.winningAmongChildren = self.winningAmongChildren + 0.5
                self.prob = round(self.winningAmongChildren/self.playouts,5)
                return "DRAW"

    def handover(self):
        for item in self.currentEnv.getMoves():
            found = False
            if self.children != None:
                for child in self.children:
                    if child.move == item:
                        found = True
                        break
            else:
                self.children = []
            if found == False:
                newEnv = Game()
                self.currentEnv.copy(newEnv)
                r=newEnv.step(item)
                newNode = Node(self,item,newEnv,r)
                self.children.append(newNode)
        return self.children

class MonteThread:
    def __init__(self,threadObj):
        self.isDone = False
        self.threadObj = threadObj
        self.threadObj.start()
    def checkisDone(self):
        self.isDone = self.threadObj.is_alive()
        return self.isDone

class MonteCarlo:
    def __init__(self,env):
        self.playouts = 50
        self.currentplayouts = 0
        self.maxPlayouts = 1000
        self.env = env
        self.threads = []
        self.children = []
    def getChildren(self):
        self.children = []
        for item in self.env.getMoves():
            newEnv = Game()
            self.env.copy(newEnv)
            r=newEnv.step(item)
            newNode = Node(None,item,newEnv,r)
            self.children.append(newNode)
    def generateNextLayer(self):
        for child in self.children:
            child.getChildren()
    def printChildren(self):
        for child in self.children:
            child.printChildren()
    def sim(self):
        self.currentplayouts = self.currentplayouts + self.playouts
        for y in range(0,self.playouts):

            for child in self.children:
                newThread = threading.Thread(target=child.playout)
                aMontThread = MonteThread(newThread)
                self.threads.append(aMontThread)

    def singleSim(self):
        for child in self.children:
            newThread = threading.Thread(target=child.playout,args=(False,))
            aMontThread = MonteThread(newThread)
            self.threads.append(aMontThread)
    def printProb(self):
        for child in self.children:
            print((child.prob,child.move))

    def getProb(self):
        probsList = []
        for child in self.children:
            probsList.append((child.prob,child.move))
        return probsList
    def bestMove(self):
        """threadFinished = False
        while not threadFinished:
            time.sleep(1)
            for th in self.threads:
                if th.checkisDone():
                    self.threads.remove(th)
                if len(self.threads) == 0:
                    threadFinished = True"""
        Probs = self.getProb()
        #print(Probs)
        max = Probs[0][0]
        move = Probs[0][1]
        for prob in Probs:
            if prob[0] >= max:
                max = prob[0]
                move = prob[1]
        print("I think I have a ,", max,"% chance of winning!")
        return move
    def parse(self,move):
        self.currentplayouts = 0
        for child in self.children:
            if child.move == move:
                self.children = child.handover()





amtrow =9
amtcol =9
 # HEIGHT AND WIDTH NEED TO BE LARGER THAN MARGIN !!!
height = 90
width = 90
margin = 15
playcolour = [25, 250, 100]
player1Col,player2Col = [200,10,10] , [10,10,200]

theGame = tttGame(amtrow,amtcol,height,width,margin,playcolour,player1Col,player2Col)
"""
env = Game()
MC = MonteCarlo(env)
MC.getChildren()
while True:

    #MC.generateNextLayer()
    #MC.printChildren()
    MC.sim()
    MC.printProb()
    i = int(input("Machine :"))
    MC.parse(i)
    MC.env.step(i)
    MC.env.render()
    print(MC.env.getMoves())
    i = int(input("Human :"))
    MC.parse(i)
    MC.env.step(i)
    MC.env.render()"""
