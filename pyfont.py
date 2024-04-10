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

        self.indexes:dict = {}

class PyFont:
    def __init__(self, window:pg.Surface, path:str, inCurrDirectory:bool=False):
        self.window = window
        
        self.layers:List[
            List[int, int, bool, Tuple[int,int,int], tuple]] = []
        # format:frameidx,frameCount,animated,color,frames

        self.details = Details(0,0)

        self.fontPath:str = path
        self.updatePath(path, inCurrDirectory)
        
        self.ALL:None = None

        self.init(None)

        self.animateList:dict = {} # name, idx = loop(0...end=update)  

    def updatePath(self, path:str, inCurrDirectory:bool=False):
        self.fontPath = path
        if inCurrDirectory:
            self.fontPath = Path(__file__).parent.resolve() / path

    def init(self, path:str|None=None):
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

        self.details.characters.clear()
        self.details.unicodes = ()
        self.details.indexes.clear()

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
            
    def render(self, name:str, text:str, color:Tuple[int,int,int], \
            pos:Tuple[int,int], space:Tuple[int,int]=(7,7), \
            scale:Tuple[int,int]=(7,7), animated:bool=True):
        
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
                    startY += scale[1] + ((scale[1] * height) / 2) + space[1]
                    startX, currY = realX, startY
                    continue
                if unicode == ' ':
                    currX += space[0]
                    continue

                datas = []

            if datas == []:
                frame:List[pg.Rect] = []
                for h in range(height):
                    for w in range(width):
                        frame.append(pg.Rect(currX, currY, *scale))

                        currX += scale[0]

                    currX = startX
                    currY += scale[1]

                layer.append([0, 0, False, color, tuple(frame)])

            elif animated:
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

            startX += scale[0] + ((scale[0] * width) / 2) + space[0]
            currX, currY = startX, startY

        self.layers.append(layer)
        self.details.indexes[name] = len(self.layers) - 1

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

    def animate(self, layer:int|None=None, repeated:bool=True) -> bool:

        finished:bool = True

        if layer != None:
            _layer = self.layers[layer]

            for layer in _layer:
                if not layer[2]: continue
                layer[0] += 1
                if layer[0] == layer[1]:
                    if repeated: layer[0] = 0
                    else: layer[0] -= 1
                else:
                    finished = False
            else:
                finished = False

            return finished
        
        for _layer in self.layers:
            for layer in _layer: 
                if not layer[2]: continue
                layer[0] += 1
                if layer[0] == layer[1]:
                    if repeated: layer[0] = 0
                    else: layer[0] -= 1
                else:
                    finished = False
            else:
                finished = False
        else:
            finished = False

        return finished

    def remove(self, name:str|None=None, endidx:int|str=-1):
        if name is self.ALL:
            self.layers = []
            keys = tuple(self.animateList.keys())
            for key in keys:
                self.animateList.pop(key, None)
            return

        layeridx = self.details.indexes.get(name)

        if layeridx is None:
            print(f"No layer named '{name}' so not removed!")
            return

        length:int = len(self.layers)

        if length < layeridx:
            print(f"{layeridx} amount of layers not exists so not removed!")
            return

        if type(endidx) == str:
            endidx = self.details.indexes.get(endidx)
            
            if endidx is None:
                print(f"No layer named '{name}' so not removed!")
                return

        if endidx != -1:
            if length < endidx:
                print(f"{endidx} amount of layers not exists so not removed!")
                return

            if endidx < layeridx:
                print(f"PyFont.remove: layeridx should be smaller than endidx")
                return

            layeridx -= 1
            endidx += 1

            index:int = 0
            offset:int = 0

            toBeRemoved:List[str] = []

            for key in self.details.indexes.keys():
                if index == endidx: break
                if index < layeridx:
                    index += 1
                    continue

                toBeRemoved.append(key)
                self.layers.pop(index - offset)

                offset += 1
                index += 1

            for key in toBeRemoved:
                self.details.indexes.pop(key, None)
                self.animateList.pop(key, None)

            index = 0

            for key, value in self.details.indexes.items():
                if index == length: break
                if index < layeridx:
                    index += 1
                    continue
                
                self.details.indexes[key] = 0 if value == 0 else value - 1

                index += 1
            
            return
        
        self.layers.pop(layeridx)
        index:int = 0
        layeridx -= 1

        self.details.indexes.pop(name, None)
        self.animateList.pop(name, None)

        for key, value in self.details.indexes.items():
            if index == length: break
            if index < layeridx:
                index += 1
                continue

            self.details.indexes[key] = 0 if value == 0 else value - 1

            index += 1

    def animateEach(self, name:str|List[str]|None=None,
            frameCount:int=100, repeated:bool=False):

        if name is None:
            for key in self.details.indexes:
                self.animateList[key] = [0, frameCount, repeated]
            return
        if type(name) == str:
            self.animateList[name] = [0, frameCount, repeated]
            return
        for key in name:
            self.animateList[key] = [0, frameCount, repeated]

    def update(self):
        value:List[int, int]
        index:int = 0
        toBeRemoved:List[str] = []

        for key in self.animateList:
            value = self.animateList[key]

            if value[0] == value[1]:
                index = self.details.indexes.get(key)
                
                if index is None: continue
                if self.animate(index, value[2]):
                    if not value[2]:
                        toBeRemoved.append(key)

                value[0] = 0
            
            else: value[0] += 1

        if toBeRemoved:
            for key in toBeRemoved:
                self.animateList.pop(key, None)
        
if __name__ == "__main__":
    pg.init()
    window = pg.display.set_mode((727,727))
    pg.display.set_caption("Test 123")

    font = PyFont(window, "Saves/a.afont", True)

    font.render("first", "aa\nAA", (42,42,42), (42,42))
    font.render("second", "AA\naa", (42,42,42), (200,200))

    font.render("third", "aa\nAA", (42,42,42), (42,242))
    font.render("fourth", "AA\naa", (42,42,42), (200,400))

    font.animateEach(("first", "third"), 1000, True)
    font.animateEach(("second", "fourth"), 1000, False)

    running:bool = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT: running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE: running = False
                if event.key == pg.K_RETURN: font.animate(0)
                if event.key == pg.K_r: font.remove("first", "fourth")
                
        window.fill((200,200,200))
        font.display(font.ALL)
        font.update()
        pg.display.update()
