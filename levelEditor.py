import sys, random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from levelLoader import Tile, LevelLoader
from toolbox import minmax


WINDOW_SIZE_X = 1200
WINDOW_SIZE_Y = 1000
NUMBER_OF_TILES = 100
TILE_SIZE = 10

class LevelEditor(QWidget):

    def __init__(self):
        super().__init__()

        self.mouse_x = 0
        self.mouse_y = 0
        self.brushShape = "rect"
        self.brushSize = 3
        self.selected_tile = Tile.grass
        self.density = 1

        self.levelMatrix = []
        self.levelMatrixPrevious = []
        for y in range(NUMBER_OF_TILES):
            self.levelMatrix.append([])
            self.levelMatrixPrevious.append([])
            for x in range(NUMBER_OF_TILES):
                self.levelMatrix[y].append(Tile.grass)
                self.levelMatrixPrevious[y].append(Tile.grass)

        self.tileTextures = {tileEnum : QPixmap('textures/' + tileName + '.png') for tileName, tileEnum in Tile.__members__.items()}

        self.setTileFunctions = {
            tileName : (lambda x : (lambda : self.setTile(x)))(tileEnum) for tileName, tileEnum in Tile.__members__.items()
        }

        self.initUI()
        self.setMouseTracking(True)

    def copyToBackup(self):
        for y in range(NUMBER_OF_TILES):
            for x in range(NUMBER_OF_TILES):
                self.levelMatrixPrevious[y][x] = self.levelMatrix[y][x]

    def copyFromBackup(self):
        for y in range(NUMBER_OF_TILES):
            for x in range(NUMBER_OF_TILES):
                self.levelMatrix[y][x] = self.levelMatrixPrevious[y][x]

    def initUI(self):
        self.setGeometry(100, 100, WINDOW_SIZE_X, WINDOW_SIZE_Y)
        self.setWindowTitle("Level Editor")
        self.show()

        loadButton = QPushButton("Load", self)
        loadButton.setGeometry(1000, 50, 100, 40)
        loadButton.show()
        loadButton.clicked.connect(self.loadFile)

        saveButton = QPushButton("Save", self)
        saveButton.setGeometry(1100, 50, 100, 40)
        saveButton.show()
        saveButton.clicked.connect(self.saveFile)

        chooseTileButton = QPushButton("Choose Tile", self)
        chooseTileButton.setGeometry(1030, 150, 140, 40)
        chooseTileButton.show()

        tileMenu = QMenu(self)
        for tileName, tileEnum in Tile.__members__.items():
            action = QAction(tileName, self)
            action.setIcon(QIcon("textures/" + tileName + ".png"))
            action.triggered.connect(self.setTileFunctions[tileName])
            tileMenu.addAction(action)

        chooseTileButton.setMenu(tileMenu)

        chooseShapeButton = QPushButton("Choose shape", self)
        chooseShapeButton.setGeometry(1030, 200, 140, 40)
        chooseShapeButton.show()

        shapeMenu = QMenu(self)
        rectAction = QAction('rectangle', self)
        rectAction.triggered.connect(lambda : self.setShape('rect'))
        shapeMenu.addAction(rectAction)
        circleAction = QAction('circle', self)
        circleAction.triggered.connect(lambda : self.setShape('circle'))
        shapeMenu.addAction(circleAction)
        bucketAction = QAction('bucket [BETA]', self)
        bucketAction.triggered.connect(lambda : self.setShape('bucket'))
        shapeMenu.addAction(bucketAction)
        chooseShapeButton.setMenu(shapeMenu)

        densitySlider = QSlider(Qt.Horizontal, self)
        densitySlider.setGeometry(1030, 250, 140, 20)
        densitySlider.show()
        densitySlider.setMinimum(0)
        densitySlider.setMaximum(100)
        densitySlider.setValue(100)
        densitySlider.valueChanged.connect(self.setDensity)


    def setTile(self, tile):
        self.selected_tile = tile

    def setShape(self, shape):
        self.brushShape = shape

    def setDensity(self, density):
        self.density = density / 100

    def loadFile(self):
        url = QFileDialog.getOpenFileUrl(self, "Save File", QDir.currentPath(), "TXT files (*.txt)")
        filePath = url[0].toLocalFile()
        self.levelMatrix, _ = LevelLoader.loadLevel(filePath)
        self.levelMatrixPrevious = self.levelMatrix.copy()

    def saveFile(self):
        url = QFileDialog.getSaveFileUrl(self, "Save File", QDir.currentPath(), "TXT files (*.txt)")
        filePath = url[0].toLocalFile()
        file = open(filePath, "w+")
        for row in self.levelMatrix:
            for tile in row:
                file.write(str(tile.value))
            file.write('\n')
        file.close()

    def fillBrush(self):

        print('changed')
        self.copyToBackup()

        rect = self.mouseRect()
        worldRect = QRectF(rect.x() * TILE_SIZE, rect.y() * TILE_SIZE, rect.width() * TILE_SIZE, rect.height() * TILE_SIZE)

        if self.brushShape == 'rect':
            for x in range(rect.x(), rect.x() + self.brushSize):
                for y in range(rect.y(), rect.y() + self.brushSize):
                    if random.random() < self.density:
                        self.levelMatrix[y][x] = self.selected_tile
        elif self.brushShape == 'circle':
            shape = QPainterPath()
            shape.addEllipse(worldRect)
            for x in range(rect.x(), rect.x() + self.brushSize):
                for y in range(rect.y(), rect.y() + self.brushSize):
                    center = QPointF(x * TILE_SIZE + TILE_SIZE / 2, y * TILE_SIZE + TILE_SIZE / 2)
                    if shape.contains(center):
                        if random.random() < self.density:
                            self.levelMatrix[y][x] = self.selected_tile
        elif self.brushShape == 'bucket':
            tile_x = int(self.mouse_x // 10)
            tile_y = int(self.mouse_y // 10)
            openList = [(tile_x, tile_y)]
            tile = self.levelMatrix[tile_y][tile_x]
            closedList = []
            while len(openList) != 0:
                x, y = openList[0]
                closedList.append((x, y))
                neighbors1 = [(x-1,y-1),(x-1,y),(x-1,y+1),(x,y-1),(x,y+1),(x+1,y-1),(x+1,y),(x+1,y+1)]
                neighbors2 = list(filter(lambda p : p not in closedList and p not in openList, neighbors1))
                neighbors3 = list(filter(lambda p : 0 <= p[0] < 100 and 0 <= p[1] < 100, neighbors2))
                neighbors4 = list(filter(lambda p : self.levelMatrix[p[1]][p[0]] == tile, neighbors3))
                openList.remove((x,y))
                openList.extend(neighbors4)

            for x,y in closedList:
                if random.random() < self.density:
                    self.levelMatrix[y][x] = self.selected_tile

        print(self.levelMatrix[0])
        print(self.levelMatrixPrevious[0])

    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)

        self.drawTiles(qp)

        qp.setPen(Qt.blue)

        rect = self.mouseRect()
        worldRect = QRectF(rect.x() * TILE_SIZE, rect.y() * TILE_SIZE, rect.width() * TILE_SIZE, rect.height() * TILE_SIZE)
        if self.brushShape == 'rect':
            qp.drawRect(worldRect)
        elif self.brushShape == 'circle':
            qp.drawEllipse(worldRect)

        qp.end()

    def drawTiles(self, qp):

        qp.setPen(Qt.NoPen)
        for row in range(NUMBER_OF_TILES):
            for column in range(NUMBER_OF_TILES):
                tile = self.levelMatrix[row][column]
                texture = self.tileTextures[tile]
                qp.drawPixmap(column*TILE_SIZE, row*TILE_SIZE, texture)


    def mouseMoveEvent(self, event):
        # check bounds
        minVal = self.brushSize * TILE_SIZE / 2
        maxVal = NUMBER_OF_TILES * TILE_SIZE - minVal
        self.mouse_x = minmax(event.x(), minVal, maxVal)
        self.mouse_y = minmax(event.y(), minVal, maxVal)

        if event.buttons() == Qt.LeftButton:
            self.fillBrush()

        self.update()

    def mousePressEvent(self, event):
        self.fillBrush()
        self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Z:
            print('now')
            self.copyFromBackup()

    def wheelEvent(self, event):
        THRESHOLD = 60
        delta_y = event.angleDelta().y() # should be 120 or -120 for a normal mouse
        if delta_y > THRESHOLD:
            self.brushSize += 1
        elif delta_y < -THRESHOLD:
            self.brushSize -= 1
            if self.brushSize < 0:
                self.brushSize = 0

        self.update()

    def mouseRect(self):
        # This is ugly and i dont understand it
        self.x = self.mouse_x + TILE_SIZE / 2
        self.y = self.mouse_y + TILE_SIZE / 2
        topLeft_x = (self.x - self.brushSize * TILE_SIZE / 2) // 10
        topLeft_y = (self.y - self.brushSize * TILE_SIZE / 2) // 10

        return QRect(topLeft_x, topLeft_y, self.brushSize, self.brushSize)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    game = LevelEditor()
    sys.exit(app.exec_())
