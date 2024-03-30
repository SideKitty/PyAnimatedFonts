from pathlib import Path

class FontDetails:
    width, height = 1, 1 

    # format: [[[bool, ...], ...], ...]
    pixelDatas = [[[],],]
    frameCount = 1

    def clearDatas(self):
        self.pixelDatas = [
            [[0 for _ in range(self.width)]
            for _ in range(self.height)]
            for _ in range(self.frameCount)]

    def growBy(self, count:int):
        if count < 1: return
        self.frameCount += count

        if count == 1:
            self.pixelDatas.append([
                [0 for _ in range(self.width)]
                for _ in range(self.height)])
            return
        
        for _ in range(count):
            self.pixelDatas.append([
                [0 for _ in range(self.width)]
                for _ in range(self.height)])

    def removeLast(self, count:int):
        if count < 1: return
        self.frameCount -= count
        for _ in range(count):
            self.pixelDatas.pop()

    def setResolution(self, w:int, h:int, clear:bool=False):
        isXGrowing:bool = self.width < w
        isYGrowing:bool = self.height < h
        
        newXDifference:int = abs(w - self.width)
        newYDifference:int = abs(h - self.height)

        if w < 1 or h < 1: w, h = 1, 1
        self.width, self.height = w, h

        if clear:
            self.clearDatas()
            return

        if isYGrowing:
            for frame in self.pixelDatas:
                for _ in range(newYDifference):
                    frame.append([
                        [0 for _ in range(w)]
                        for _ in range(h)])
        else:
            for frame in self.pixelDatas:
                for _ in range(newYDifference):
                    frame.pop()
                    
        if isXGrowing:
            for frame in self.pixelDatas:
                for row in frame:
                    for _ in range(newXDifference):
                        row.append(0)
        else:
            for frame in self.pixelDatas:
                for row in frame:
                    for _ in range(newXDifference):
                        row.pop()

class Font:
    def __init__(self, details:FontDetails):
        self.details:FontDetails 
        self.error:bool = False
        self.path:str = ""

        try: _ = details.pixelDatas
        except NameError:
            print("Font.init: given details is wrong type")
            self.error = True
            return

        self.details = details
        self.details.clearDatas()
        self.pixelSize:tuple

    def updatePixelSize(self, winSizeX:int, winSizeY:int):
        self.pixelSize = (
            winSizeX / self.details.width,
            winSizeY / self.details.height)

    def saveTo(self, path:str, inCurrDirectory:bool=True):
        self.path = path
        if inCurrDirectory:
            self.path = Path(__file__).parent.resolve() / path

        with open(self.path, "wb") as file:
            for frame in self.details.pixelDatas:
                for row in frame:
                    file.write(bytearray(row))
                    file.write(b'42')
                file.write(b'84')

    def open(self, path:str, inCurrDirectory:bool=True):
        self.path = path
        if inCurrDirectory:
            self.path = Path(__file__).parent.resolve() / path

        with open(self.path, "rb") as file:
            self.details.frameCount = 0
            self.details.pixelDatas = [[],]

            row = []

            gettingWidth:bool = True
            gettingHeight:bool = True
            height:int = 0

            for byte in file.read():
                match byte:
                    case 50:
                        if gettingWidth:
                            self.details.width = len(row) 
                            gettingWidth = False
                        if gettingHeight: height += 1
                        self.details.pixelDatas[-1].append(row)
                        row = []

                    case 52: continue
                    case 56:
                        if gettingHeight:
                            self.details.height = height
                            gettingHeight = False
                        self.details.frameCount += 1
                        self.details.pixelDatas.append([])
                    
                    case _: row.append(byte)
            
            if self.details.pixelDatas[-1] == []:
                self.details.pixelDatas.pop()
