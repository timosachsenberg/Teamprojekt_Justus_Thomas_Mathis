from PyQt5.QtCore import QRectF
from enum import Enum

class Tile(Enum):
    floor = 0
    wall = 1
    sand = 2

class LevelLoader:

    LEVEL_SIZE = 100
    TILE_SIZE = 10

    # Reads a txt file and creates an 2 dimensional array representing a level
    # A '0' represents free space, a '1' represents a wall
    @staticmethod
    def loadLevel(filePath):
        levelMatrix = []
        rects = []

        f = open(filePath, "r")
        for i in range(LevelLoader.LEVEL_SIZE):
            line = f.readline()
            row = []
            for c in line:
                if c == '0':
                    row.append(Tile.floor)
                elif c == '1':
                    row.append(Tile.wall)
                elif c == '2':
                    row.append(Tile.sand)
                elif c == '\n':
                    pass
                else:
                    raise Exception('Unknown symbol: "' + c + '" in level "' + filePath + '"')
            levelMatrix.append(row)

        for i in range(LevelLoader.LEVEL_SIZE):
            for j in range(LevelLoader.LEVEL_SIZE):
                if levelMatrix[i][j] == Tile.wall:
                    new_rect = QRectF(j * LevelLoader.TILE_SIZE, i * LevelLoader.TILE_SIZE,
                                    LevelLoader.TILE_SIZE, LevelLoader.TILE_SIZE)

                    # Check if the rect would already be covered by one of our rects
                    if any(rect.contains(new_rect) for rect in rects):
                        continue

                    # Explore right and down to cover more walls in one square
                    n=0
                    while all(all(x == Tile.wall for x in column[j:j+n]) for column in levelMatrix[i:i+n]):
                        n += 1

                    rects.append(QRectF(j * LevelLoader.TILE_SIZE, i * LevelLoader.TILE_SIZE,
                                        (n-1) * LevelLoader.TILE_SIZE, (n-1) * LevelLoader.TILE_SIZE))

        return levelMatrix, rects
