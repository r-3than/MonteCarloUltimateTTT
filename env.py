import numpy as np
import copy , random , threading

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
    MC.env.render()
