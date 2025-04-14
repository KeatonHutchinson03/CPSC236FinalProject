# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, pygame, sys
from pygame.locals import *

EASY_FPS = 7
MEDIUM_FPS = 12
HARD_FPS = 18

WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE     = (255, 255, 255)
BLACK     = (  0,   0,   0)
RED       = (255,   0,   0)
GREEN     = (  0, 255,   0)
DARKGREEN = (  0, 155,   0)
DARKGRAY  = ( 40,  40,  40)
YELLOW    = (255, 255,   0)
BGCOLOR = BLACK

#New colors introduced to have the worm spawn in a different color everytime. 
WORM_COLORS = [
    (255, 0, 0),     # RED
    (0, 255, 0),     # GREEN
    (0, 155, 0),     # DARKGREEN
    (0, 0, 255),     # BLUE
    (255, 255, 0),   # YELLOW
    (255, 165, 0),   # ORANGE
    (128, 0, 128),   # PURPLE
    (0, 255, 255),   # CYAN
    (255, 192, 203), # PINK
    (160, 82, 45),   # BROWN
]

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0 # syntactic sugar: index of the worm's head
def selectDifficulty():
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        titleFont = pygame.font.Font('freesansbold.ttf', 40)

        easyText = titleFont.render('1 - Easy', True, GREEN)
        medText = titleFont.render('2 - Medium', True, YELLOW)
        hardText = titleFont.render('3 - Hard', True, RED)

        easyRect = easyText.get_rect(center=(WINDOWWIDTH // 2, 200))
        medRect = medText.get_rect(center=(WINDOWWIDTH // 2, 260))
        hardRect = hardText.get_rect(center=(WINDOWWIDTH // 2, 320))

        DISPLAYSURF.blit(easyText, easyRect)
        DISPLAYSURF.blit(medText, medRect)
        DISPLAYSURF.blit(hardText, hardRect)

        drawPressKeyMsg()
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == KEYDOWN:
                if event.key == K_1:
                    return EASY_FPS
                elif event.key == K_2:
                    return MEDIUM_FPS
                elif event.key == K_3:
                    return HARD_FPS
                elif event.key == K_ESCAPE:
                    terminate()

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, FPS

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    #New Feature added: Difficulty Setting Selection before game is played.
    # The user can select between Easy, Medium and Hard.
    # The FPS will be set according to the difficulty selected.
    FPS = selectDifficulty() 
    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()



def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    #New Feature added: Enemy worm. 
    enemyStartX = CELLWIDTH - startx - 1
    enemyStartY = CELLHEIGHT - starty - 1
    enemyCoords = [{'x': enemyStartX, 'y': enemyStartY},
                   {'x': enemyStartX - 1, 'y': enemyStartY},
                   {'x': enemyStartX - 2, 'y': enemyStartY}]
    direction = RIGHT
    #Delay for enemy
    enemyMoveCounter = 0
    enemyMoveDelay = 2  # Enemy moves every 3 frames
    # Start the apple in a random place.
    apple = getRandomLocation()

    while True: # main game loop
        for event in pygame.event.get(): # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return # game over

        # check if worm has eaten an apple
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation() # set a new apple somewhere
        else:
            del wormCoords[-1] # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)
        
        playerHead = wormCoords[0]
    
        # Enemy movement logic (every few frames)
        enemyMoveCounter += 1
        #Enemy is set to a slower speed then user, so it can be avoided. 
        if enemyMoveCounter >= enemyMoveDelay:
            enemyMoveCounter = 0  # Reset counter

        # Enemy worm movement code here
            enemyHead = enemyCoords[0]
            playerHead = wormCoords[0]

            dx = playerHead['x'] - enemyHead['x']
            dy = playerHead['y'] - enemyHead['y']

            if abs(dx) > abs(dy):
                move_x = 1 if dx > 0 else -1
                move_y = 0
            else:
                move_y = 1 if dy > 0 else -1
                move_x = 0

            newEnemyHead = {'x': enemyHead['x'] + move_x, 'y': enemyHead['y'] + move_y}
            enemyCoords.insert(0, newEnemyHead)
            del enemyCoords[-1]  # Keep enemy worm same length

        for enemy in enemyCoords:
            if enemy['x'] == wormCoords[HEAD]['x'] and enemy['y'] == wormCoords[HEAD]['y']:
                return  # game over
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        drawWorm(wormCoords)
        drawEnemy(enemyCoords)
        drawApple(apple)
        drawScore(len(wormCoords) - 3)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3 # rotate by 3 degrees each frame
        degrees2 += 7 # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)

    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    drawPressKeyMsg()
    pygame.display.update()
    pygame.time.wait(500)
    checkForKeyPress() # clear out any key presses in the event queue

    while True:
        if checkForKeyPress():
            pygame.event.get() # clear event queue
            return

def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

#new function for drawing the enemy worm.
def drawEnemy(enemyCoords):
    outerColor = (200, 0, 0)  # dark red
    innerColor = (255, 50, 50)  # bright red

    for coord in enemyCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE

        enemySegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, outerColor, enemySegmentRect)

        enemyInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, innerColor, enemyInnerSegmentRect)

def drawWorm(wormCoords):
    # Pick a random pair of outer and inner colors for the worm
    outerColor = random.choice(WORM_COLORS)
    
    # Optionally define inner color as a brighter version (or fixed, like white/green)
    def brighten(color, amount=100):
        return tuple(min(255, c + amount) for c in color)

    innerColor = brighten(outerColor)
    
    #Colors will mix and match to give a random effect for the worm.
    
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE

        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, outerColor, wormSegmentRect)

        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, innerColor, wormInnerSegmentRect)



def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE): # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE): # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
