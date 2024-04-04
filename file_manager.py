from pathlib import Path
from typing import List
from os import remove as deleteFile

class Char:
    # format: [[[bool, ...], ...], ...]
    pixels:List[List]
    unicode:str 
    frameCount:int

    def __init__(self, unicode:str):
        self.unicode = unicode
        self.pixels = list()
        self.pixels = [[],]
        self.frameCount = 1

class FontDetails:
    width, height = 1, 1 

    characters = {"a": Char("a")}
    unicodes = ["a"]
    currCharacter = characters["a"]

    def changeCharacter(self, unicode:str):
        fillAfter:bool = False
        if not unicode in self.unicodes:
            self.unicodes.append(unicode)
            self.characters[unicode] = Char(unicode)
            fillAfter = True
        self.currCharacter = self.characters[unicode]
        if fillAfter: self.fillDatas(0)

    def fillDatas(self, value:bool):
        self.currCharacter.pixels = [
            [[value for _ in range(self.width)]
            for _ in range(self.height)]
            for _ in range(self.currCharacter.frameCount)]

    def growBy(self, count:int):
        if count < 1: return
        self.currCharacter.frameCount += count

        if count == 1:
            self.currCharacter.pixels.append([
                [0 for _ in range(self.width)]
                for _ in range(self.height)])
            return
        
        for _ in range(count):
            self.currCharacter.pixels.append([
                [0 for _ in range(self.width)]
                for _ in range(self.height)])

    def removeLast(self, count:int):
        if count < 1: return
        self.currCharacter.frameCount -= count
        for _ in range(count):
            self.currCharacter.pixels.pop()

    def setResolution(self, w:int, h:int, clear:bool=False):
        isXGrowing:bool = self.width < w
        isYGrowing:bool = self.height < h
        
        newXDifference:int = abs(w - self.width)
        newYDifference:int = abs(h - self.height)

        if w < 1 or h < 1: w, h = 1, 1
        self.width, self.height = w, h

        if clear:
            self.fillDatas(0)
            return

        if isYGrowing:
            for frame in self.currCharacter.pixels:
                for _ in range(newYDifference):
                    frame.append([
                        [0 for _ in range(w)]
                        for _ in range(h)])
        else:
            for frame in self.currCharacter.pixels:
                for _ in range(newYDifference):
                    frame.pop()
                    
        if isXGrowing:
            for frame in self.currCharacter.pixels:
                for row in frame:
                    for _ in range(newXDifference):
                        row.append(0)
        else:
            for frame in self.currCharacter.pixels:
                for row in frame:
                    for _ in range(newXDifference):
                        row.pop()

class Font:
    def __init__(self, details:FontDetails):
        self.details:FontDetails 
        self.path:str = "Untitled"

        self.error:bool = False

        try: _ = details.currCharacter.pixels
        except NameError:
            print("Font.init: given details is wrong type")
            self.error = True
            return

        details.fillDatas(0)
        self.details = details
        self.pixelSize:tuple

    def updatePixelSize(self, winSizeX:int, winSizeY:int):
        self.pixelSize = (
            winSizeX / self.details.width,
            winSizeY / self.details.height)

    def saveTo(self, path:str|Path, inCurrDirectory:bool=True):
        self.path = path
        if inCurrDirectory:
            self.path = Path(__file__).parent.resolve() / path
       
        if Path(self.path).is_dir():
            print("Cannot save because current path is directory")
            return

        if self.path.exists():
            deleteFile(self.path)

        with open(self.path, "wb") as file:
            for unicode in self.details.unicodes:
                file.write(b'\4')
                file.write(unicode.encode("utf-8"))
                for frame in self.details.characters[unicode].pixels:
                    for row in frame:
                        file.write(bytearray(row))
                        file.write(b'\2')
                    file.write(b'\3')

    def open(self, path:str|Path, inCurrDirectory:bool=True):
        self.path = path
        if inCurrDirectory:
            self.path = Path(__file__).parent.resolve() / path

        with open(self.path, "rb") as file:
            self.details.currCharacter.frameCount = 0
            self.details.currCharacter.pixels = [[],]

            row = []

            gettingWidth:bool = True
            gettingHeight:bool = True
            height:int = 0
            gettingUnicode:bool = False

            self.details.unicodes = []
            self.details.characters = tuple()
            self.details.characters = {}
            self.details.currCharacter = None

            for byte in file.read():
                if gettingUnicode:
                    byte = chr(byte)
                    self.details.characters[byte] = Char(byte)
                    self.details.unicodes.append(byte)
                    gettingUnicode = False
                    self.details.currCharacter = self.details.characters[byte]
                    continue

                match byte:
                    case 2:
                        if gettingWidth:
                            self.details.width = len(row) 
                            gettingWidth = False
                        if gettingHeight: height += 1
                        self.details.currCharacter.pixels[-1].append(row)
                        row = []

                    case 3:
                        if gettingHeight:
                            self.details.height = height
                            gettingHeight = False
                        self.details.currCharacter.frameCount += 1
                        self.details.currCharacter.pixels.append([])
                    
                    case 4:
                        if self.details.currCharacter:
                            self.details.currCharacter.pixels.pop()
                            self.details.currCharacter.frameCount -= 1
                        gettingUnicode = True

                    case _: row.append(byte)

            self.details.currCharacter.pixels.pop()
            self.details.currCharacter.frameCount -= 1

            self.details.currCharacter = self.details.characters["a"]
