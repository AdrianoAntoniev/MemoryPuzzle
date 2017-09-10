# Memory Puzzle 
#By Al Sweigart al@inventwithpython.com
#http://inventwithpython.com/game
#Released under a "Simplified BSD" license
#copiado por Adriano Rodrigues Vieira para fins educacionais
import random, pygame, sys
from pygame.locals import *

# DEBUG = True
FPS = 30
WINDOWWIDTH = 640
WINDOWHEIGHT = 480

REVEALSPEED = 8 # speed boxes' sliding reveals and covers, used in animations

BOXSIZE = 40 # size of boxes
GAPSIZE = 10 # size of gap between boxes

BOARDWIDTH = 10 # number of columns of icons
BOARDHEIGHT = 7 # number of rows of icons

assert (BOARDWIDTH * BOARDHEIGHT) % 2 == 0, 'Board needs to have and even number of boxes'

XMARGIN = int( (WINDOWWIDTH - BOARDWIDTH * (BOXSIZE + GAPSIZE)) / 2)
YMARGIN = int( (WINDOWHEIGHT - BOARDHEIGHT * (BOXSIZE + GAPSIZE)) / 2)

# Define color schemes
#        R    G    B
GRAY     = (100, 100, 100)
NAVYBLUE = ( 60,  60, 100)
WHITE    = (255, 255, 255)

RED      = (255,   0,   0)
GREEN    = (  0, 255,   0)
BLUE     = (  0,   0, 255)
YELLOW   = (255, 255,   0)
ORANGE   = (255, 128,   0)
PURPLE   = (255,   0, 255)
CYAN     = (  0, 255, 255)

# Environment colors
BGCOLOR = NAVYBLUE
LIGHTBGCOLOR = GRAY
BOXCOLOR = WHITE
HIGHLIGHTCOLOR = BLUE

# Define shapes
DONUT = 'donut'
SQUARE = 'square'
DIAMOND = 'diamond'
LINES = 'lines'
OVAL = 'oval'

ALLCOLORS = (RED, GREEN, BLUE, YELLOW, ORANGE, PURPLE, CYAN)
ALLSHAPES = (DONUT, SQUARE, DIAMOND, LINES, OVAL)

assert len(ALLCOLORS) * len(ALLSHAPES) * 2 >= BOARDHEIGHT * BOARDWIDTH, 'Board is too big'

def main():
	global FPSCLOCK, DISPLAYSURF
	pygame.init()
	FPSCLOCK = pygame.time.Clock()
	DISPLAYSURF = pygame.display.set_mode( (WINDOWWIDTH, WINDOWHEIGHT) )

	# Mouse position
	mouseX = 0
	mouseY = 0

	pygame.display.set_caption('Jogo da memoria!')

	# generate Game board
	mainBoard = getRandomizedBoard()
	"""if DEBUG:
		print 'gennerating mainBoard'"""
	# 	print mainBoard
	revealedBoexes = generateRevealedBoxesData(False)
	firstSelection = None # record the first box clicked
	DISPLAYSURF.fill(BGCOLOR)
	startGameAnimation(mainBoard)

	# main game loop
	while True:
		"""bug fix mouseClick -> mouseClicked"""
		mouseClicked = False

		# draw the game board
		DISPLAYSURF.fill(BGCOLOR)
		drawBoard(mainBoard, revealedBoexes)

		# handle game events
		for event in pygame.event.get():
			if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
				pygame.quit()
				sys.exit()
			elif event.type == MOUSEMOTION:
				mouseX, mouseY =  event.pos
			elif event.type == MOUSEBUTTONUP:
				mouseX, mouseY = event.pos
				mouseClicked = True

		# handle action over a box
		boxX, boxY = getBoxAtPixel(mouseX, mouseY)
		if boxX != None and boxY != None:
			# high light the box under the mouse
			if not revealedBoexes[boxX][boxY]:
				drawHighLightBox(boxX, boxY)

			# reveal the box if clicked
			if not revealedBoexes[boxX][boxY] and mouseClicked:
				revealBoxesAnimation(mainBoard, [(boxX, boxY)])
				revealedBoexes[boxX][boxY] = True
				if firstSelection == None:
					firstSelection = (boxX, boxY)
				# check whether two clicked boxes match
				else:
					icon1Shape, icon1Color = getShapeAndColor(mainBoard, firstSelection[0], firstSelection[1])
					"""bug fix: main -> mainBoard"""
					icon2Shape, icon2Color = getShapeAndColor(mainBoard, boxX, boxY)

					if icon1Shape  != icon2Shape or icon1Color != icon2Color:
						pygame.time.wait(1000) # wait 1000ms
						coverBoxesAnimation(mainBoard, [(firstSelection[0], firstSelection[1]), (boxX, boxY)])
						revealedBoexes[firstSelection[0]][firstSelection[1]] = False
						revealedBoexes[boxX][boxY] = False

					# check whether win the game
					elif hasWon(revealedBoexes):
						gameWonAnimation(mainBoard)
						pygame.time.wait(2000)

						# restart a new game
						mainBoard = getRandomizedBoard()
						revealedBoexes = generateRevealedBoxesData(False)

						# show the revealed game board for one second
						drawBoard(mainBoard, revealedBoexes)
						pygame.display.update()
						pygame.time.wait(1000)
						startGameAnimation(mainBoard)

					firstSelection = None

		# update the game board
		pygame.display.update()
		FPSCLOCK.tick(FPS)

# initialized revealedBoexes
def generateRevealedBoxesData(boolen):
	revealedBoexes = []
	for i in range(BOARDWIDTH):
		revealedBoexes.append([boolen] * BOARDHEIGHT)
	return revealedBoexes

# random generate a game board
def getRandomizedBoard():
	# get all possible combinations of shapes and colors
	icons = []
	for colors in ALLCOLORS:
		for shapes in ALLSHAPES:
			icons.append( (shapes, colors) )

	random.shuffle(icons) # randomize the order of icons
	numOfIconsNeeded = int(BOARDWIDTH * BOARDHEIGHT / 2) # get the number of icons nedded for the game board
	icons = icons[:numOfIconsNeeded] * 2
	random.shuffle(icons)

	# generate the game board
	board = []
	for x in range(BOARDWIDTH):
		column = []
		for y in range(BOARDHEIGHT):
			column.append(icons[0])
			del icons[0]
		board.append(column)
	return board

# split a list into a list of lists, each has size n
def splitList(n, inputList):
	result = []
	for i in range(0, len(inputList), n):
		result.append(inputList[i: i + n])
	return result

# get the left top coordinate of the box[x][y]
def leftTopCoordinate(x, y):
	""" bug fix: * -> +"""
	left = x * (BOXSIZE + GAPSIZE) + XMARGIN
	top = y * (BOXSIZE + GAPSIZE) + YMARGIN
	return (left, top)

# get the box at a certain pixel
def getBoxAtPixel(x, y):
	"""bug fix: BOARDHEIGHT -> BOARDWIDTH"""
	for i in range(BOARDWIDTH):
		for j in range(BOARDHEIGHT):
			left, top = leftTopCoordinate(i, j)
			# search the pixel in the box retangle
			rectangle = pygame.Rect(left, top, BOXSIZE, BOXSIZE)
			if rectangle.collidepoint(x, y):
				return (i, j)
	return (None, None)

def getShapeAndColor(board, boxX, boxY):
	return board[boxX][boxY][0], board[boxX][boxY][1]

def drawIcon(shape, color, boxX, boxY):
	quarterSize = int(BOXSIZE * 0.25)
	halfSize = int(BOXSIZE * 0.5)
	left, top = leftTopCoordinate(boxX, boxY)
	if shape == DONUT:
		pygame.draw.circle(DISPLAYSURF, color, (left + halfSize, top + halfSize), halfSize - 5)
		pygame.draw.circle(DISPLAYSURF, BGCOLOR, (left + halfSize, top + halfSize), quarterSize - 5)
	elif shape == SQUARE:
		pygame.draw.rect(DISPLAYSURF, color, (left + quarterSize, top + quarterSize, BOXSIZE - halfSize, BOXSIZE - halfSize))
	elif shape == DIAMOND:
		pygame.draw.polygon(DISPLAYSURF, color, ((left + halfSize, top), (left + BOXSIZE - 1, top + halfSize), (left + halfSize, top + BOXSIZE - 1), (left, top + halfSize)))
	elif shape == LINES:
		for i in range(0, BOXSIZE, 4):
			pygame.draw.line(DISPLAYSURF, color, (left, top + i), (left + i, top))
			pygame.draw.line(DISPLAYSURF, color, (left + i, top + BOXSIZE - 1), (left + BOXSIZE - 1, top + i))
	elif shape == OVAL:
		pygame.draw.ellipse(DISPLAYSURF, color, (left, top + quarterSize, BOXSIZE, halfSize))

def drawBoxCovers(board, boxes, coverage):
	for box in boxes:
		left, top = leftTopCoordinate(box[0], box[1])
		shape, color = getShapeAndColor(board, box[0], box[1])
		pygame.draw.rect(DISPLAYSURF, BGCOLOR, (left, top, BOXSIZE, BOXSIZE))
		# draw the box icon
		drawIcon(shape, color, box[0], box[1])
		if coverage > 0:
			pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, coverage, BOXSIZE))
		pygame.display.update()
		FPSCLOCK.tick(FPS)

def revealBoxesAnimation(board, box):
	for coverage in range(BOXSIZE, (- REVEALSPEED) - 1, - REVEALSPEED):
		drawBoxCovers(board, box, coverage)

def coverBoxesAnimation(board, box):
	for coverage in range(0, BOXSIZE + REVEALSPEED, REVEALSPEED):
		drawBoxCovers(board, box, coverage)

def drawBoard(board, revealed):
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			left, top = leftTopCoordinate(x, y)
			# if not revealed
			if not revealed[x][y]:
				pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left, top, BOXSIZE, BOXSIZE))
			# if revealed
			else:
				shape, color = getShapeAndColor(board, x, y)
				drawIcon(shape, color, x, y)

def drawHighLightBox(x, y):
	left, top = leftTopCoordinate(x, y)
	pygame.draw.rect(DISPLAYSURF, HIGHLIGHTCOLOR, (left - 5, top - 5, BOXSIZE + 10, BOXSIZE + 10), 4)

def startGameAnimation(board):
	coveredBoxes = generateRevealedBoxesData(False)
	"""if DEBUG:
		print coveredBoxes"""
	boxes = []
	for x in range(BOARDWIDTH):
		for y in range(BOARDHEIGHT):
			boxes.append( (x, y) )
	random.shuffle(boxes)
	"""if DEBUG:
		print boxes"""
	# randomly reveal 8 boxes at a time
	revealList = splitList(8, boxes)
	"""if DEBUG:
		print revealList"""
	drawBoard(board, coveredBoxes)
	for box in revealList:
		revealBoxesAnimation(board, box)
		coverBoxesAnimation(board, box)

def gameWonAnimation(board):
	coveredBoxes = generateRevealedBoxesData(True)
	color1 = LIGHTBGCOLOR
	color2 = BGCOLOR
	for i in range(5):
		color1, color2 = color2, color1
		DISPLAYSURF.fill(color1)
		drawBoard(board, coveredBoxes)
		pygame.display.update()
		pygame.time.wait(300)

def hasWon(revealedBoexes):
	for row in revealedBoexes:
		if False in row:
			return False
	return True

if __name__ == '__main__':
	main()