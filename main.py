import pygame as pg
from pathlib import Path, PurePath
from file_manager import FontDetails, Font

pg.init()
winSize = (800, 800)
window = pg.display.set_mode(winSize)
title:str = "Untitled"
pg.display.set_caption(f"Font-Maker {title} a[0]")

clock = pg.time.Clock() 
FPS = 30 

whiteMode = True
fontPath = "test.afont"
fontPath = Path(__file__).parent.resolve() / "Saves" / fontPath
fontPath = PurePath(fontPath)

class appColors:
    def __init__(self):
        self.background :tuple
        self.fontPixel  :tuple
        self.activePixel:tuple
        self.gridLines  :tuple
        self.topBarBG   :tuple
        self.topBarTexts:tuple
        self.topBarActive:tuple
        self.topBarClick:tuple

    def whiteMode(self):
        self.background = (255,255,255)
        self.fontPixel = (0,0,0)
        self.activePixel = (55,55,55)
        self.gridLines = (200,200,200)
        self.topBarBG = (200,200,200)
        self.topBarTexts = (0,0,0)
        self.topBarActive = (150,150,150)
        self.topBarClick = (255,255,255)

    def darkMode(self):
        self.background = (0,0,0)
        self.fontPixel = (255,255,255)
        self.activePixel = (200,200,200)
        self.gridLines = (55,55,55)
        self.topBarBG = (55,55,55)
        self.topBarTexts = (255,255,255)
        self.topBarActive = (105,105,105)
        self.topBarClick = (55,55,55)

activeGridIndex = (0,0)
currentFrameIndex = 0

previewing:bool = False
previewidx:int = 0
pvPosX:int = 0
pvPosY:int = 0
previewFrame:int = 0
previewLatency:bool = 10

def display(font:Font, colors:appColors):
    window.fill(colors.background)
    
    global previewing, previewidx
    global pvPosX, pvPosY, previewlen
    global previewFrame, previewLatency

    if previewing:
        pvPosX, pvPosY = 0, 0
        for row in font.details.currCharacter.pixels[previewidx]:
            for active in row:
                if active:
                    pg.draw.rect(window, colors.activePixel,
                        pg.Rect(pvPosX, pvPosY,
                            font.pixelSize[0],
                            font.pixelSize[1]))

                pvPosX += font.pixelSize[0]

            pvPosX = 0
            pvPosY += font.pixelSize[1]

        previewFrame += 1
        if previewFrame == previewLatency:
            previewFrame = 0
            previewidx += 1
            length = font.details.currCharacter.frameCount
            if previewidx == length:
                previewidx = 0
                previewing = False
        
        pg.display.update()
        return

    currX:int = 0
    currY:int = 0

    for y in font.details.currCharacter.pixels[currentFrameIndex]:
        for active in y:
            if active:
                pg.draw.rect(window,
                    colors.fontPixel,
                    pg.Rect(currX, currY,
                        font.pixelSize[0],
                        font.pixelSize[1]))
            
            pg.draw.line(window, colors.gridLines,
                (currX, currY),
                (currX, currY + font.pixelSize[1]))

            pg.draw.line(window, colors.gridLines,
                (currX, currY),
                (currX + font.pixelSize[0], currY))

            currX += font.pixelSize[0]

        currX = 0
        currY += font.pixelSize[1]

    pg.display.update()

holdingButton:int = 0
holdingKey:int = 0

gettingUnicode:bool = False

forSaving:bool = False
forOpening:bool = False

def userInputs(font:Font) -> bool:
    global holdingKey, holdingButton, title
    global currentFrameIndex, previewing
    global forSaving, forOpening, gettingUnicode

    for event in pg.event.get():

        if event.type == pg.QUIT:
            return False

        if event.type == pg.KEYDOWN:
            holdingKey = event.key
            
            if previewing:
                previewing = False
                return True

            if event.mod == pg.KMOD_RSHIFT:
                gettingUnicode = True
                continue

            if gettingUnicode:
                if forSaving:
                    fontPath = Path(__file__).parent.resolve() \
                        / "Saves" / f"{event.unicode}.afont"

                    title = fontPath.relative_to(fontPath.parents[1])
                    
                    font.saveTo(fontPath)

                    pg.display.set_caption(f"Font-Maker {title} \
{event.unicode}[{currentFrameIndex}]")

                    gettingUnicode = False
                    forSaving = False
                    return True

                if forOpening:
                    fontPath = Path(__file__).parent.resolve() \
                        / "Saves" / f"{event.unicode}.afont"

                    if not fontPath.exists() or fontPath.is_dir():
                        return True

                    font.open(fontPath)
                    currentFrameIndex = 0

                    title = fontPath.relative_to(fontPath.parents[1])
                    pg.display.set_caption(
                        f"Font-Maker {title} {event.unicode}[0]")
                    
                    forOpening = False
                    gettingUnicode = False
                    return True

                currentFrameIndex = 0
                previewidx = 0
                font.details.changeCharacter(event.unicode)
                gettingUnicode = False
                pg.display.set_caption(
                    f"Font-Maker {title} {event.unicode}[0]")
                return True

            match event.key:
                case pg.K_ESCAPE:
                    return False

                case pg.K_p:
                    previewing = True

                case pg.K_r:
                    font.details.fillDatas(0)

                case pg.K_f:
                    font.details.fillDatas(1)

                case pg.K_e:
                    length = font.details.currCharacter.frameCount
                    currentFrameIndex += 1
                    if currentFrameIndex == length:
                        if event.mod and pg.KMOD_LSHIFT:
                            font.details.growBy(1)
                        else:
                            currentFrameIndex = 0 

                    pg.display.set_caption(f"Font-Maker {title} \
{font.details.currCharacter.unicode}[{currentFrameIndex}]")

                case pg.K_q:
                    length = font.details.currCharacter.frameCount - 1
                    if currentFrameIndex == 0:
                        currentFrameIndex = length
                    else:
                        currentFrameIndex -= 1
                    pg.display.set_caption(f"Font-Maker {title} \
{font.details.currCharacter.unicode}[{currentFrameIndex}]")

                case pg.K_s:
                    if event.mod and pg.KMOD_CTRL:
                        if pg.KMOD_SHIFT:
                            forSaving = True
                            gettingUnicode = True
                            continue

                        prePath:str = fontPath
                        font.saveTo(fontPath)
                        if fontPath != prePath:
                            title = fontPath.relative_to(fontPath.parents[1])

                case pg.K_o:
                    if event.mod and pg.KMOD_CTRL:
                        if pg.KMOD_SHIFT:
                            forOpening = True
                            gettingUnicode = True
                            return True

                        font.open(fontPath)
                        font.updatePixelSize(winSize[0], winSize[1])
                        title = fontPath.relative_to(fontPath.parents[1])
                    pg.display.set_caption(f"Font-Maker {title} \
{font.details.currCharacter.unicode}[{currentFrameIndex}]")

            return True

        if event.type == pg.KEYUP:
            holdingKey = 0
            return True

        global activeGridIndex
        if event.type == pg.MOUSEBUTTONDOWN:

            if previewing:
                previewing = False
                return True

            holdingButton = event.button
            activeGridIndex = (-1,-1)
            return True

        if event.type == pg.MOUSEBUTTONUP:
            holdingButton = 0
            return True

        if event.type == pg.MOUSEMOTION:
            x, y = pg.mouse.get_pos()
            gridIndex:tuple = (
                int(x / font.pixelSize[0]),
                int(y / font.pixelSize[1]))
            if gridIndex == activeGridIndex: continue
            activeGridIndex = gridIndex

        if holdingButton:
            frame = font.details.currCharacter.pixels[currentFrameIndex]
            frame[activeGridIndex[1]][activeGridIndex[0]] = \
                True if holdingButton == 1 else False

    return True

if __name__ == "__main__":
    details = FontDetails()
    details.setResolution(8,10,True)

    font = Font(details)
    font.updatePixelSize(winSize[0], winSize[1])
    
    colors = appColors()
    
    if whiteMode:
        colors.whiteMode()
    else:
        colors.darkMode()
    
    while userInputs(font):
        display(font, colors)
        clock.tick(FPS)

    pg.quit()
