
import subprocess
import pygame
import time
import math
import os


white = (255, 255, 255)
black = (0, 0, 0)
pink = (255, 182, 193)
blue = (173, 216, 230)

class onScreenTile():
    def __init__(self, aRect, aPos):
        self.rect = aRect
        self.pos = aPos

class gameScreen():
    def __init__(self):
        pygame.init()
        self.allsprites = pygame.sprite.Group()
        self.specialsprites = pygame.sprite.Group()
        self.specialpieces = []
        self.font = pygame.font.SysFont("Arial", 42)
        self.tiles = []
        self.sur = ""
        self.game = ""

    def addSprite(self, aSprite):
        self.allsprites.add(aSprite)

    def drawSquares(self, positions, color):
        for tile in positions:
            i = tile[0]
            j = tile[1]
            x = 100 + 75/2 + i * 75
            y = 50 + 75/2 + ((7-j) * 75)
            
            pygame.draw.circle(self.sur, color, (x, y), 30)

    def drawBoard(self):
        dw = True
        
        pygame.draw.rect(self.sur, black, pygame.Rect(99, 49, 602, 602), width=2)
        for i in range(8):
            row = []
            for j in range(8):
                rect = pygame.Rect(100+j*75, 50+i*75, 75, 75)
                tile = onScreenTile(rect, (j, 7-i))
                row.append(tile)
                if dw:
                    
                    pygame.draw.rect(self.sur, blue, rect)
                    pygame.draw.rect(self.sur, black, rect, width=2)
                else:
                    pygame.draw.rect(self.sur, pink, rect)
                    pygame.draw.rect(self.sur, black, rect, width=2)
                if j != 7:
                    dw = not dw
                else:
                    letter = self.font.render(str(8 - i), True, black)
                    self.sur.blit(letter, ((125+8*75), 60 + (i * 75)))
            self.tiles.append(row)
        thing = "ABCDEFGH"
        for i in range(8):
            letter = self.font.render(thing[i], True, black)
            self.sur.blit(letter, ((125 + i * 75), 60 + 8* 75))

    def updateScreen(self):
        self.sur.fill(white)
        self.drawBoard()
        if self.game.checkers != "": self.drawSquares(self.game.checkers, (255, 0, 0))
        if self.game.botChoice != "": self.drawSquares(self.game.botChoice, (0, 100, 0))
        
        
        self.drawSprites()
        pygame.display.update()

    def drawPromotion(self):
        
        self.specialpieces.append(dumbQueen(9, 7, self.game.activePlayer))
        self.specialpieces.append(dumbRook(9, 5, self.game.activePlayer))
        self.specialpieces.append(dumbBishop(9, 3, self.game.activePlayer))
        self.specialpieces.append(dumbKnight(9, 1, self.game.activePlayer))
        for item in self.specialpieces: self.specialsprites.add(item)
        self.updateScreen()
        running = True
        while running:
            selection = ""
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    for item in self.specialpieces:
                        if item.rect.collidepoint(event.pos):
                            match item.name():
                                case "queen":
                                    
                                    selection = "q"
                                case "rook":

                                    selection = "r"
                                case "knight":
                                    selection = "n"
                                case "bishop":
                                    selection = "b"
                            
                            for item in self.specialsprites:
                                item.kill()
                            return selection
                elif event.type == pygame.MOUSEMOTION:
                    set = False
                    for item in self.specialpieces:
                        if item.rect.collidepoint(event.pos):
                            pygame.mouse.set_cursor(pygame.cursors.ball)
                            set = True
                    if not set:
                        pygame.mouse.set_cursor(pygame.cursors.arrow)
                        

        
    def drawSprites(self):
        self.allsprites.draw(self.sur)
        self.specialsprites.draw(self.sur)

    def startScreen(self):
        start = pygame.display.set_mode((800, 400))
        start.fill((255, 0, 255))
        noBot = self.font.render("No Bots", True, black)
        rect = pygame.Rect(50, 100, 200, 100)
        botrect = pygame.Rect(350, 100, 200, 100)
        bot = self.font.render("Bots", True, black)
        text_rect2 = bot.get_rect(center=botrect.center)
        text_rect = noBot.get_rect(center=rect.center)

        pygame.draw.rect(start, white, rect)
        pygame.draw.rect(start, white, botrect)
        start.blit(noBot, text_rect)
        start.blit(bot, text_rect2)
        pygame.display.update()
        running = True
        self.game = game(self)
        gameStarted = False
        count = 0
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONUP:
                    if rect.collidepoint(event.pos):
                        self.game.startGame(False, 0, False, 0)
                        gameStarted = True
                    elif botrect.collidepoint(event.pos):
                        self.game.startGame(True, 5, True, 10)
                        gameStarted = True
                
            if gameStarted:
                if not self.game.gameStopped():
                    if not self.game.step():
                        running = False
                else:
                    gameStarted = False
                    count = 1
            if count != 0:
                count += 1
            if count > 10000:
                self.allsprites.empty()
                self.startScreen()

    def makeMainScreen(self):
        self.sur = pygame.display.set_mode((1000, 900))


class botHandler():
    def __init__(self):
        self.process = ""
    
    def readLine(self):
        return self.process.stdout.readline().strip()
    
    def botCommand(self, aCommand):
        self.process.stdin.write(aCommand+"\n")
        self.process.stdin.flush()

    def startBot(self):
        try:
            self.process = subprocess.Popen("./stockfish/stockfish-windows-x86-64-avx2.exe", stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,text=True)
        except:
            return False
        self.botCommand("uci")
        self.botCommand("ucinewgame")
        line = self.process.stdout.readline()
        while line != "uciok\n":
            line = self.process.stdout.readline()
        return True
    
    
    
    def getBotInput(self, movesString, aDifficulty):
        if movesString != "":
            self.botCommand("position startpos moves " + movesString)
        else:
            self.botCommand("position startpos")
        self.botCommand("go depth " + str(aDifficulty))
        aBotInput = self.readLine()
        while len(aBotInput) < 13 or aBotInput[:8] != "bestmove":
            aBotInput = self.readLine()
            
        
        aScreen.game.botString = aBotInput[9:14]
        return aBotInput


class game():
    def __init__(self, aScreen):
        
        self.board = ""
        self.player1 = ""
        self.player2 = ""
        self.activePlayer = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""
        self.enPassantTile = ""
        self.checkers = ""
        self.myScreen = aScreen
        self.myBotHandler = botHandler()
        self.botChoice = ""
        self.promotionSquares = ""
        
        self.botStarted = self.myBotHandler.startBot()

    def getBotInput(self, aDifficulty):
        return self.myBotHandler.getBotInput(self.movesString, aDifficulty)
    
    def drawSquares(self, aList, Color):
        self.myScreen.drawSquares(aList, Color)

    def startGame(self, player1bot, player1dif, player2bot, player2dif):
        self.board = board()
        self.player1 = ""
        self.player2 = ""
        self.turns = 0
        self.movesString = ""
        self.botString = ""
        self.myScreen.makeMainScreen()
        if not self.botStarted:
            print("Sorry bot is sleepy")
            self.player1 = humanPlayer(True, self)
            self.player2 = humanPlayer(False, self)
        else:
            if player1bot:
                self.player1 = botPlayer(True, player1dif, self)
            else:
                self.player1 = humanPlayer(True, self)
            if player2bot:
                self.player2 = botPlayer(False, player2dif, self)
            else:
                self.player2 = humanPlayer(False, self)
        
        self.player1.start()
        self.player2.start()
        self.activePlayer = self.player1
        self.myScreen.updateScreen()

        
    def step(self):
        if not self.activePlayer.takeTurn():
            return False
        self.drawCheck()
        return True

    def drawBot(self):
        anArray = self.parseThings(self.botString[0], self.botString[1], self.botString[2], self.botString[3])
        squares = []
        squares.append((anArray[0], anArray[1]))
        squares.append((anArray[2], anArray[3]))
        
        self.botChoice = squares
        

    

    def drawCheck(self):
        if self.inCheck(self.activePlayer.getColor()):
            daKing = self.activePlayer.king
            self.checkers = self.getNonActivePlayer().getCheckers(daKing)
            
            self.checkers.append((daKing.x, daKing.y))
            
            self.myScreen.updateScreen()
            
        else:
            self.checkers = ""
                
    def hasPiece(self, col, row):
        return self.activePlayer.hasPiece(col, row)
    
    def gameStopped(self):
        if len(self.player1.pieces) == 1 and len(self.player2.pieces) == 1:
            print("The game was a stalemate")
            return True
        if self.activePlayer.hasMove():
            return False
        if self.inCheck(self.color()):
            self.winner()
        else:
            print("The game was a stalemate")
        return True
    
    def parseThings(self, a, b, c, d):
        row = int(b) - 1
        col = ord(a) - ord('a')
        newRow = int(d) - 1
        newCol = ord(c) - ord('a')
        return [col, row, newCol, newRow]
    
    def botInput(self, aString):
        promote = False
        if len(aString) > 13:
            promote = aString[13]
        array = self.parseThings(aString[9], aString[10], aString[11], aString[12])
        
        if len(aString) > 13:
            self.movesString += aString[9:14] + " "
            self.botString = aString[9:14]
        else:
            self.movesString += aString[9:13] + " "
            self.botString = aString[9:13]
        array.append(promote)
        return array

    def getNonActivePlayer(self):
        if self.p1act():
            return self.player2
        return self.player1
    
    def p1act(self):
        return self.activePlayer == self.player1
    
    def winner(self):
        print(self.getNonActivePlayer().name() + "won!")

    def inCheck(self, aColor):
        if aColor == self.player1.color:
            return self.player2.isChecking(self.player1.king)
        
        return self.player1.isChecking(self.player2.king)
    
    def color(self):
        return self.activePlayer.getColor()

    def switchPlayer(self):
        if self.p1act():
            self.activePlayer = self.player2
        else:
            self.activePlayer = self.player1
            self.turns += 1

    def activePlayerPrompt(self, aString):
        return self.activePlayer.name() + aString
    
    def getTile(self, x, y):
        return self.board.getTile(x, y)

    def movePiece(self, aPiece, col, row, enPassantTile, castle, promotion):
        
        destTile = self.getTile(col, row)
        eatenPiece = destTile.piece
        
        if aPiece.name() == "pawn":
            if row == self.getNonActivePlayer().row:
                aPiece.remove()
                match promotion:
                    case "q":
                        aPiece = queen(-2, -2, self.activePlayer)
                    case "n":
                        aPiece = knight(-2, -2, self.activePlayer)
                    case "r":
                        aPiece = rook(-2, -2, self.activePlayer)
                    case "b":
                        aPiece = bishop(-2, -2, self.activePlayer)
                self.activePlayer.addPiece(aPiece)

        
        if eatenPiece != "EMPTY":
            eatenPiece.remove()
        elif aPiece.name() == "pawn" and self.enPassantTile == destTile:
            magicNum = 0
            if self.p1act():
                magicNum = 4
            destTile.getNeighbor(2+magicNum).piece.remove()
        if enPassantTile:
            self.enPassantTile = enPassantTile
        else:
            self.enPassantTile = ""
        if castle:
            magicNum = 0
            if castle[0] == 7:
                magicNum = 2
            self.movePiece(self.board.getTile(castle[0], self.activePlayer.row).getPiece(), 3+magicNum, self.activePlayer.row, False, False, False)
            self.switchPlayer()

        destTile.setPiece(aPiece)
        aPiece.tile.empty()
        aPiece.setHasMoved(True)
        aPiece.move(col, row)
        self.switchPlayer()
        self.myScreen.updateScreen()
        



class board():
        
    def __init__(self):
        self.columns = []

        for i in range(8):
            self.columns.append(column(i))

        for i in range(8):
            leftNeighbor = nullColumn.getSingleInstance()
            rightNeighbor = nullColumn.getSingleInstance()
            if i != 0:
                leftNeighbor = self.columns[i-1]
            if i != 7:
                rightNeighbor = self.columns[i+1]
            self.columns[i].setNeighbors(leftNeighbor, rightNeighbor)
        for item in self.columns:
            item.setTileNeighbors()
        for item in self.columns:
            item.setRookTileNeighbors()
    
    def getTile(self, col, row):
        return self.columns[col].getTile(row)

class nullColumn():
    singleInstance = ""
    
    @classmethod
    def getSingleInstance(cls):
        if cls.singleInstance == "":
            cls.singleInstance = cls()
        return cls.singleInstance
    
    def getTile(self, i):
        return nullTile.getSingleInstance()

class column():
    
    def __init__(self, i):
        self.tiles = []
        self.neighbors = []
        for j in range(8):
            self.tiles.append(tile(i, j))
        for _ in range(2):
            self.neighbors.append(nullColumn.getSingleInstance())
        for i in range(8):
            if i != 0:
                self.tiles[i].setNeighbor(6, self.tiles[i-1])
            if i != 7:
                self.tiles[i].setNeighbor(2, self.tiles[i+1])

    def setNeighbors(self, left, right):
        self.neighbors[0] = left
        self.neighbors[1] = right

    def setTileNeighbors(self):
        for i in range(8):
            rightNeighbor = self.neighbors[1].getTile(i)
            leftNeighbor = self.neighbors[0].getTile(i)

            self.tiles[i].setNeighbor(0, rightNeighbor)
            self.tiles[i].setNeighbor(1, rightNeighbor.getNeighbor(2))
            self.tiles[i].setNeighbor(7, rightNeighbor.getNeighbor(6))
            
            self.tiles[i].setNeighbor(4, leftNeighbor)
            self.tiles[i].setNeighbor(3, leftNeighbor.getNeighbor(2))
            self.tiles[i].setNeighbor(5, leftNeighbor.getNeighbor(6))

    def setRookTileNeighbors(self):
        for i in range(8):
            rightNeighbor = self.neighbors[1].getTile(i)
            leftNeighbor = self.neighbors[0].getTile(i)
            rrightNeighbor = rightNeighbor.getNeighbor(0)
            lleftNeighbor = leftNeighbor.getNeighbor(4)
            uupNeighbor = self.tiles[i].neighbors[2].getNeighbor(2)
            ddownNeighbor = self.tiles[i].neighbors[6].getNeighbor(6)
            self.tiles[i].setRookNeighbor(0, rrightNeighbor.getNeighbor(2))
            self.tiles[i].setRookNeighbor(1, uupNeighbor.getNeighbor(0))
            self.tiles[i].setRookNeighbor(2, uupNeighbor.getNeighbor(4))
            self.tiles[i].setRookNeighbor(3, lleftNeighbor.getNeighbor(2))
            self.tiles[i].setRookNeighbor(4, lleftNeighbor.getNeighbor(6))
            self.tiles[i].setRookNeighbor(5, ddownNeighbor.getNeighbor(4))
            self.tiles[i].setRookNeighbor(6, ddownNeighbor.getNeighbor(0))            
            self.tiles[i].setRookNeighbor(7, rrightNeighbor.getNeighbor(6))

    def getTile(self, i):
        return self.tiles[i]

class nullTile():
    singleInstance = ""
    
    @classmethod
    def getSingleInstance(cls):
        if cls.singleInstance == "":
            cls.singleInstance = cls()
        return cls.singleInstance
    
    def getNeighbor(self, i):
        return self
    
    def getRookNeighbor(self, i):
        return self
    
    def slide(self, dir, i):
        return False

    def hasMoved(self):
        return True
    
    def isNullTile(self):
        return True
    
class tile():
    def empty(self):
        self.piece = "EMPTY"

    def isNullTile(self):
        return False

    def isEmpty(self):
        return self.piece == "EMPTY"
    
    def getPlayer(self):
        
        if self.isEmpty():
            return "null"
        return self.piece.player
    
    def hasMoved(self):
        if self.isEmpty():
            return True
        else:
            return self.piece.getHasMoved()

    def __init__(self, i, j):
        self.piece = "EMPTY"
        self.neighbors = []
        self.rookNeighbors = []
        self.x = i
        self.y = j
        for _ in range(8):
            self.neighbors.append(nullTile.getSingleInstance())
            self.rookNeighbors.append(nullTile.getSingleInstance())

    def getPos(self):
        return (self.x, self.y)
    
    def slide(self, dir, i):
        if i == 0:
            return self
        if not self.isEmpty():
            return False
        return self.getNeighbor(dir).slide(dir, i - 1)
    
    def setNeighbor(self, i, aTile):
        self.neighbors[i] = aTile

    def setRookNeighbor(self, i, aTile):
        self.rookNeighbors[i] = aTile

    def getNeighbor(self, i):
        return self.neighbors[i]
    
    def getRookNeighbor(self, i):
        return self.rookNeighbors[i]
    
    def getPiece(self):
        return self.piece
    
    def setPiece(self, aPiece):
        self.piece = aPiece

class player():
  
    
    def hasMove(self):
        for item in self.pieces:
            if len(item.findMoves()) > 0:
                return True
        return False
    
    def start(self):
        self.pieces.append(knight(1, self.row, self))
        self.pieces.append(knight(6, self.row, self))
        self.king = king(4, self.row, self)
        self.pieces.append(self.king)
        self.pieces.append(queen(3, self.row, self))
        self.pieces.append(rook(0, self.row, self))
        self.pieces.append(rook(7, self.row, self))
        self.pieces.append(bishop(2, self.row, self))
        self.pieces.append(bishop(5, self.row, self))
        for i in range(8):
            self.pieces.append(pawn(i, self.pawnsRow, self))

    def getCheckers(self, aKing):
        checkers = []
        for item in self.pieces:
            if item.canMove(aKing.x, aKing.y):
                checkers.append((item.x, item.y))
        return checkers
    
    def isChecking(self, aKing):
        checkers = self.getCheckers(aKing)
        return len(checkers) > 0

    def addPiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.append(aPiece)

    def removePiece(self, aPiece):
        if aPiece != "EMPTY":
            self.pieces.remove(aPiece)
          

    def __init__(self, player1, aGame):
        self.king = "EMPTY"
        self.tempMoveString = ""
        self.pieces = []
        self.myGame = aGame
        if player1:
            self.color = "white"
            self.row = 0
            self.pawnsRow = 1
            self.pname = "Player 1:  "
        else:
            self.color = "black"
            self.row = 7
            self.pawnsRow = 6
            self.pname = "Player 2:  "

    def hasPiece(self, col, row):
        aPiece = self.myGame.board.getTile(col, row).getPiece()
       
        if aPiece == "EMPTY":
            return False
        if aPiece.getColor() == self.color:
            return aPiece
        
        return False
    
    def getColor(self):
        return self.color
    
    def name(self):
        return self.pname

    
class humanPlayer(player):

    def checkSelection(self, validPiece, pos):
        thing = "abcdefgh"
        if not validPiece: return False
        for row in aScreen.tiles:
            for tile in row:
                if tile.rect.collidepoint(pos):
                    col = tile.pos[0]
                    row = tile.pos[1]
                    if validPiece.cCanMove(col, row):
                        
                        startX = thing[validPiece.x]
                        startY = str(validPiece.y+1)
                        endX = thing[col]
                        endY = str(row+1)
                        promotion = " "
                        if validPiece.name() == "pawn":
                            if row == self.myGame.getNonActivePlayer().row:
                                
                                promotion = self.myGame.myScreen.drawPromotion()
                        self.tempMoveString = startX + startY + endX + endY + promotion
                        if self.tempMoveString != self.myGame.botString:
                            self.myGame.drawBot()
                            print("The bot thought about this move:  " + self.myGame.botString)
                        else:
                            self.myGame.botChoice = ""
                            print("youre so smart")
                        self.myGame.movesString += self.tempMoveString + " "
                        if promotion == " ": anArray = validPiece.canMove(col, row)
                        else: anArray = [None, False, False]
                        self.myGame.movePiece(validPiece, col, row, anArray[1], anArray[2], promotion)
                        return True
        return False
    
    def drawPosibilities(self, validPiece):
        aScreen.sur.fill((255, 255, 255))
        aScreen.drawBoard()
        moves = validPiece.findMoves()
        self.myGame.drawSquares(moves, (255, 150, 0))
        if self.myGame.checkers != "": self.myGame.drawSquares(self.myGame.checkers, (255, 0, 0))
        aScreen.drawSprites()

        pygame.display.update()

    def findPosibilities(self, aPos):
        for piece in self.pieces:
            if piece.rect.collidepoint(aPos):
                self.drawPosibilities(piece)
                pygame.mouse.set_cursor(pygame.cursors.diamond)
                return piece
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        return False
    def takeTurn(self):
        
        self.myGame.getBotInput(10)
        running = True
        
        validPiece = False
        dragging = False
        mouseDown = False
        validPieceOgPos = ""
        originalMousePos = ""
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                   
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if not validPiece:
                        for piece in self.pieces:
                            if piece.rect.collidepoint(event.pos):
                                validPiece = piece
                                validPieceOgPos = (100 + piece.x * 75 + 75/2, 50 + (7-piece.y) * 75 + 75/2)
                                dragging = False
                                mouseDown = True
                                originalMousePos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    wasClick = True
                    if dragging:
                        dragging = False
                        wasClick = False
                    else:
                        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
                    
                    mouseDown = False
                    if not wasClick:
                        if self.checkSelection(validPiece, event.pos):
                            
                            running = False
                            
                        if running:
                            if validPiece: validPiece.setPos(validPieceOgPos)
                            aScreen.updateScreen()
                            validPiece = False
                    else:
                        if validPiece and not validPiece.rect.collidepoint(event.pos):
                            if self.checkSelection(validPiece, event.pos):
                                running = False
                                
                            if running:
                                aScreen.updateScreen()
                                validPiece = False
                            
                elif event.type == pygame.MOUSEMOTION:
                    if mouseDown:
                        
                        if compareTuple(event.pos, originalMousePos):

                            dragging = True
                    
                    if not validPiece and not self.findPosibilities(event.pos):
                        aScreen.updateScreen()
                    elif validPiece and dragging:
                        validPiece.setPos(event.pos)
                        self.drawPosibilities(validPiece)
        return True
def compareTuple(t1, t2):
    x = t1[0] - t2[0]
    y = t1[1] - t2[1]
    return math.sqrt(x * x + y * y) > 5

class botPlayer(player):
    def __init__(self, player1, difficulty, aGame):
        super().__init__(player1, aGame)
        self.difficulty = difficulty

    def takeTurn(self):
        
        botString = self.myGame.getBotInput(self.difficulty)

        botString = self.myGame.botInput(botString)
        
        self.myGame.drawBot()
        validPiece = self.hasPiece(botString[0], botString[1]) 
        col = botString[2]
        row = botString[3]
        anArray = validPiece.canMove(col, row)
        print("Turn " + str(self.myGame.turns) + ": The bot choose:  " + self.myGame.botString)
        self.myGame.movePiece(validPiece, col, row, anArray[1], anArray[2], botString[4])
        time.sleep(0.25)
        return True

class dumbPiece(pygame.sprite.Sprite):
    def __init__(self, anX, aY, aPlayer):
        super().__init__()
        self.x = anX
        self.y = aY
        self.coords = ""
        self.color = aPlayer.getColor()
        self.player = aPlayer
        self.myGame = aPlayer.myGame
        self.image = False
        self.move(anX, aY)

    def move(self, anX, aY):
        if not self.image:
            anImage = "./" + self.color + "/" + self.name() + ".png"
            self.image = pygame.image.load(anImage).convert_alpha()
        self.x = anX
        self.y = aY
        self.coords = (100 + (75*anX), 50 + (75*(7-aY)))
        self.rect = self.image.get_rect(topleft = self.coords)
        self.draw()

    def draw(self):
        self.myGame.myScreen.addSprite(self)

class piece(dumbPiece):
    
    def getColor(self):
        return self.color

    def getX(self):
        return self.x

    def getY(self):
        return self.y
    
    def getHasMoved(self):
        return self.hasMoved
    
    def setHasMoved(self, aBool):
        self.hasMoved = aBool
    
    def setCoords(self, anX, aY):
        self.x = anX
        self.y = aY

    def __init__(self, anX, aY, aPlayer):
        super().__init__(anX, aY, aPlayer)
        
        
        self.hasMoved = False
        aTile = self.myGame.getTile(anX, aY)
        self.tile = aTile
        aTile.setPiece(self)
        self.move(anX, aY)

    def move(self, anX, aY):
        super().move(anX, aY)
        self.tile = self.myGame.getTile(anX, aY)

    def setPos(self, aPos):
        self.coords = (aPos[0], aPos[1])
        self.rect = self.image.get_rect(center = self.coords)
    
    def remove(self):
        self.kill()
        self.player.removePiece(self)
        self.tile.empty()

    def getTile(self):
        return self.tile
    
    def cCanMove(self, anX, aY):
        oldX = self.x
        oldY = self.y
        if anX == oldX and oldY == aY:
            return False
        anArray = self.canMove(anX, aY)
        if not anArray:
            return False
        newTile = anArray[0]
        oldPiece = newTile.getPiece()
        oldTile = self.tile
        oldTile.empty()
        
        bad = False
        try: self.myGame.getNonActivePlayer().removePiece(oldPiece)
        except: bad = True
        newTile.setPiece(self)
        self.setCoords(anX, aY)
        if self.myGame.inCheck(self.color):
            anArray = False
        oldTile.setPiece(self)
        if not bad: self.myGame.getNonActivePlayer().addPiece(oldPiece)
        newTile.setPiece(oldPiece)
        self.setCoords(oldX, oldY)
        return anArray
    
    def isValidMove(self, tile):
        if not tile:
            return False
        if not tile.isNullTile() and (tile.isEmpty() or tile.getPlayer() != self.player):
            return True
        return False
        
    def isSuperValidMove(self, aPos):
        return self.cCanMove(aPos[0], aPos[1])
    
    def checkValidity(self, aTile, moves):
        if self.isValidMove(aTile):
            tPos = aTile.getPos()
            if self.isSuperValidMove(tPos):
                moves.append(tPos)
        return moves
        

class dumbKnight(dumbPiece):
    def name(self):
        return "knight"
        
class knight(piece):

    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for tile in self.tile.rookNeighbors:
            if tile == destTile:
                return default(destTile)
        return False
    
    def findMoves(self):
        moves = []
        for tile in self.tile.rookNeighbors:
            moves = self.checkValidity(tile, moves)
        return moves
    
    def name(self):
        return "knight"
    
class dumbRook(dumbPiece):
    def name(self):
        return "rook"
    
class rook(piece):

    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for i in range(8):
            if i % 2 == 1:
                continue
            else:
                for j in range(8):
                    if self.tile.getNeighbor(i).slide(i, j) == destTile:
                        return default(destTile)
        return False 
    
    def findMoves(self):
        moves = []
        for i in range(8):
            if i % 2 == 1:
                continue
            else:
                for j in range(8):
                    tile = self.tile.getNeighbor(i).slide(i, j)
                    moves = self.checkValidity(tile, moves)
                    if not tile or not tile.isEmpty():
                        break
                   
        return moves
    
    def name(self):
        return "rook"

class pawn(piece):

    def name(self):
        return "pawn"
    
    def canMove(self, col, row):
        magicNum = 4
        if self.player == self.myGame.player1:
            magicNum = 0
        destTile = self.myGame.getTile(col, row)
        myTile = self.getTile()
        front = myTile.getNeighbor(2+magicNum)
        if destTile == myTile.getNeighbor(1+magicNum) or destTile == myTile.getNeighbor(3+magicNum):
            
            if self.myGame.enPassantTile == destTile:
                return default(destTile)
            
            if destTile.isEmpty() or destTile.getPlayer() == self.player:
                
                return False
            else:
                return default(destTile)
            
        
        elif destTile == front.getNeighbor(2+magicNum):
        
            if self.getHasMoved() or not front.isEmpty() or not destTile.isEmpty():
                return False
            else:
                return [destTile, front, False]
        elif destTile == front:
            if not destTile.isEmpty():
                return False
            else:
                return default(destTile)
        return False
    
    def checkDiag(self, aTile):
        if aTile.isNullTile():
            return False
        if not aTile.isEmpty() and aTile.getPlayer() != self.player:
            return True
        if aTile == self.myGame.enPassantTile:
            return True
        return False
    
    def findMoves(self):
        magicNum = 4
        if self.player == self.myGame.player1:
            magicNum = 0
        myTile = self.getTile()
        front = myTile.getNeighbor(2+magicNum)
        diag1 = myTile.getNeighbor(1+magicNum)
        diag2 = myTile.getNeighbor(3+magicNum)
        moves = []
        
        
        if self.checkDiag(diag1):
            diag1pos = diag1.getPos()
            if self.isSuperValidMove(diag1pos): moves.append(diag1pos)
        if self.checkDiag(diag2): 
            diag2pos = diag2.getPos()
            if self.isSuperValidMove(diag2pos): moves.append(diag2pos)
        if front.isEmpty(): 
            fPos = front.getPos()
            if self.isSuperValidMove(fPos):
                moves.append(fPos)
            if not self.getHasMoved():
                ffront = front.getNeighbor(2+magicNum)
                ffPos = ffront.getPos()
                if ffront.isEmpty():
                    if self.isSuperValidMove(ffPos):
                        moves.append(ffPos)
        return moves
        

        
class dumbBishop(dumbPiece):
    def name(self):
        return "bishop"    

class bishop(piece):
    

    def name(self):
        return "bishop"

    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for i in range(8):
            if i % 2 == 0:
                continue
            else:
                for j in range(8):
                    if self.tile.getNeighbor(i).slide(i, j) == destTile:
                        return default(destTile)
        return False
    
    def findMoves(self):
        moves = []
        for i in range(8):
            if i % 2 == 0:
                continue
            else:
                for j in range(8):
                    posibileTile = self.tile.getNeighbor(i).slide(i, j)
                    moves = self.checkValidity(posibileTile, moves)
                   
                    if not posibileTile or not posibileTile.isEmpty():
                        break
                    
        return moves


        
class king(piece):

    def name(self):
        return "king"
    
    def canMove(self, anX, aY, ):
        destTile = self.myGame.getTile(anX, aY)
        answer = default(destTile)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            answer = False
        for i in range(8):
            if self.tile.getNeighbor(i) == destTile and answer:
                return answer
        rightCastle = self.tile.getNeighbor(0).getNeighbor(0)
        leftCastle = self.tile.getNeighbor(4).getNeighbor(4)
        if not self.hasMoved and rightCastle == destTile:
            if self.myGame.inCheck(self.color) or rightCastle.getNeighbor(0).hasMoved():
                return False
            if not rightCastle.getNeighbor(4).isEmpty() or not rightCastle.isEmpty():
                return False
            self.setCoords(anX-1, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX-2, aY)
                return False
            self.setCoords(anX, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX-2, aY)
                return False
            self.setCoords(anX-2, aY)
            return [destTile, False, [7]]
        if not self.hasMoved and leftCastle == destTile:
            if self.myGame.inCheck(self.color) or leftCastle.getNeighbor(4).getNeighbor(4).hasMoved():
                return False
            if not leftCastle.getNeighbor(4).isEmpty() or not leftCastle.isEmpty() or not leftCastle.getNeighbor(0).isEmpty():
                return False
            self.setCoords(anX+1, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX+2, aY)
                return False
            self.setCoords(anX, aY)
            if self.myGame.inCheck(self.color):
                self.setCoords(anX+2, aY)
                return False
            self.setCoords(anX+2, aY)
            return [destTile, False, [0]]
        
    def findMoves(self):
        moves = []
        myTile = self.getTile()
        for i in range(8):
            tile = self.tile.getNeighbor(i)
            moves = self.checkValidity(tile, moves)
        rightCastle = self.tile.getNeighbor(0).getNeighbor(0)
        leftCastle = self.tile.getNeighbor(4).getNeighbor(4)
        
        if not self.hasMoved and not self.myGame.inCheck(self.color):
            if not rightCastle.getNeighbor(0).hasMoved():
                
                rCpos = rightCastle.getPos()
                anX = rCpos[0]
                aY = rCpos[1]
                if rightCastle.isEmpty() and rightCastle.getNeighbor(4).isEmpty():
                    self.setCoords(anX-1, aY)
                    if not self.myGame.inCheck(self.color):
                        self.setCoords(anX, aY)
                        if not self.myGame.inCheck(self.color):
                            moves.append(rCpos)
                
            if not leftCastle.getNeighbor(4).getNeighbor(4).hasMoved():
                lCpos = leftCastle.getPos()
                anX = lCpos[0]
                aY = lCpos[1]
                if leftCastle.isEmpty() and leftCastle.getNeighbor(0).isEmpty() and leftCastle.getNeighbor(4).isEmpty():
                    self.setCoords(anX+1, aY)
                    if not self.myGame.inCheck(self.color):
                        self.setCoords(anX, aY)
                        if not self.myGame.inCheck(self.color):
                            
                            moves.append(lCpos)

        self.setCoords(myTile.getPos()[0], myTile.getPos()[1])
        return moves
                    
class dumbQueen(dumbPiece):
    def name(self):
        return "queen"

class queen(piece):

    def name(self):
        return "queen"
    
    def canMove(self, anX, aY):
        destTile = self.myGame.getTile(anX, aY)
        if not destTile.isEmpty() and destTile.getPlayer() == self.player:
            return False
        for i in range(8):
            for j in range(8):
                if self.tile.getNeighbor(i).slide(i, j) == destTile:
                    return default(destTile)
        return False
    
    def findMoves(self):
        moves = []
        for i in range(8):
            for j in range(8):
                tile = self.tile.getNeighbor(i).slide(i, j)
                moves = self.checkValidity(tile, moves)
                if not tile or not tile.isEmpty():
                    break

        return moves

def default(aTile):
    return [aTile, False, False] 

aScreen = gameScreen()
aScreen.startScreen()