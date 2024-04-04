import pygame as pg
from typing import List, Tuple
from pathlib import Path, PurePath

class Char:
    # format: [[[bool, ...], ...], ...]
    pixels:List[List]
    unicode:str 
    frameCount:int
    currentFrame:int

    def __init__(self, unicode:str):
        self.unicode = unicode
        self.pixels = list()
        self.pixels = [[],]
        self.frameCount = 0
        self.currentFrame = 0

class Details:
    def __init__(self, width:int, height:int):
        self.width = width
        self.height = height

        self.characters:dict = {}
        self.unicodes:tuple = ()

class PyFont:
    def __init__(self, window:pg.Surface, path:str, inCurrDirectory:bool=False):
        self.window = window
        
        self.layers:List[
            List[int, int, bool, Tuple[int,int,int], tuple]] = []

        self.details = Details(0,0)

        self.fontDatas:List[list] = []
        self.fontPath:str = path
        self.updateFont(path, inCurrDirectory)
        
        self.ALL:None = None

        self.initFont(None)

    def updateFont(self, path:str, inCurrDirectory:bool=False):
        self.fontPath = path
        if inCurrDirectory:
            self.fontPath = Path(__file__).parent.resolve() / path

    def initFont(self, path:str|None=None):
        if path is None: path = self.fontPath
        path = Path(path)
        
        if not path.exists(): raise FileNotFoundError(f"path: {path}")
        if path.is_dir(): raise ValueError(f"path: {path}")

        path = PurePath(path)
        for index, suffix in enumerate(path.suffixes):
            if index != 0: continue
            if suffix == ".afont": break
        else:
            raise ValueError(f"file type should be '.afont' path: {path}")

        row:List = []
        gettingUnicode:bool = False

        height:int = 0

        self.details.characters = dict()
        self.details.characters = {}
        self.details.unicodes = ()

        gettingWidth:bool = True
        gettingHeight:bool = True
    
        unicodes:List = []
        currCharacter:Char = None

        with open(path, "rb") as file:
            for byte in file.read():
                if gettingUnicode:

                    if currCharacter:
                        empty:bool = True
                        for row in currCharacter.pixels:
                            for active in row:
                                if active:
                                    empty = False
                                    break

                        if empty:
                            self.characters[unicodes[-1]] = None
                            unicodes.pop()
                            
                    byte = chr(byte) 
                    self.details.characters[byte] = Char(byte)
                    unicodes.append(byte)
                    gettingUnicode = False
                    currCharacter = self.details.characters[byte]
                    row = []
                    continue

                match byte:
                    case 2:
                        if gettingWidth:
                            self.details.width = len(row) 
                            gettingWidth = False
                        if gettingHeight: height += 1
                        currCharacter.pixels[-1].append(tuple(row))
                        row = []

                    case 3:
                        if gettingHeight:
                            self.details.height = height
                            gettingHeight = False
                        currCharacter.frameCount += 1
                        currCharacter.pixels.append([])
                    
                    case 4:
                        if currCharacter: currCharacter.pixels.pop()
                        gettingUnicode = True

                    case _: row.append(byte)

            if currCharacter.pixels[-1] == []:
                currCharacter.pixels.pop()

            self.details.unicodes = tuple(unicodes)
            
    def render(self, text:str, color:Tuple[int,int,int], \
            pos:Tuple[int,int], space:Tuple[int,int]=(7,7), \
            scale:Tuple[int,int]=(7,7), animated:bool=True) -> list|None:
        
        currX:int = pos[0]
        currY:int = pos[1]

        startX:int = currX
        realX:int = pos[0]
        startY:int = currY

        width:int = self.details.width
        height:int = self.details.height

        datas:List[list] = []
        layer:List[List[int, int, bool, Tuple[int,int,int], tuple]] = []

        for unicode in text:
            if unicode in self.details.unicodes:
                datas = self.details.characters[unicode]
            else:
                if unicode == '\n':
                    startY += (scale[1] * height) + space[1]
                    startX, currY = realX, startY
                    continue
                if unicode == ' ':
                    currX += scale[0] + space[0]
                    continue

                datas = [ # cube if unicode is not available yet
                    [1 for _ in range(width)]
                    for _ in range(height)]

            if animated:
                frames:List[Tuple[pg.Rect]] = []
                currFrame:List[pg.Rect] = []

                for frame in range(datas.frameCount):
                    currFrame = []
                    currY = startY
                    for h in range(height):
                        for w in range(width):
                            if datas.pixels[frame][h][w]:
                                currFrame.append(pg.Rect(
                                    currX, currY, *scale))

                            currX += scale[0]

                        currX = startX
                        currY += scale[1]

                    frames.append(tuple(currFrame))    

                layer.append([0, datas.frameCount, True, color, tuple(frames)])
            
            else:
                frame:List[pg.Rect] = []
                for h in range(height):
                    for w in range(width):
                        if datas.pixels[0][h][w]:
                            frame.append(pg.Rect(
                                currX, currY, *scale))

                        currX += scale[0]

                    currX = startX
                    currY += scale[1]
                
                layer.append([0, datas.frameCount, False, color, tuple(frame)])

            startX += (scale[0] * width) + space[0]
            currX, currY = startX, startY

        self.layers.append(layer)

    def display(self, layer:int|None=None):

        if layer != None:
            _layer = self.layers[layer]
            for layer in _layer:
                if not layer[2]: # animated
                    for rect in layer[4]:
                        pg.draw.rect(self.window, layer[3], rect)

                    continue

                for rect in layer[4][layer[0]]:
                    pg.draw.rect(self.window, layer[3], rect)  

            return

        for _layer in self.layers:
            for layer in _layer:
                if not layer[2]: # animated
                    for rect in layer[4]:
                        pg.draw.rect(self.window, layer[3], rect)

                    continue

                for rect in layer[4][layer[0]]:
                    pg.draw.rect(self.window, layer[3], rect)               

    def animate(self, layer:int|None=None):

        if layer != None:
            _layer = self.layers[layer]

            for layer in _layer:
                if not layer[2]: continue
                layer[0] += 1
                if layer[0] == layer[1]:
                    layer[0] = 0

            return
        
        for _layer in self.layers:
            for layer in _layer: 
                if not layer[2]: continue
                layer[0] += 1
                if layer[0] == layer[1]:
                    layer[0] = 0

if __name__ == "__main__":
    pg.init()
    window = pg.display.set_mode((727,727))
    pg.display.set_caption("Test 123")

    font = PyFont(window, "Saves/q.afont", True)
    font.render("aa\nbb", (42,42,42), (42,42))
    font.render("cc\ndd", (42,42,42), (200,200))

    running:bool = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT: running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE: running = False
                if event.key == pg.K_RETURN: font.animate(font.ALL)
                
        window.fill((200,200,200))
        font.display(font.ALL)
        pg.display.update()
