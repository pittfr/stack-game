import pygame
import random

pygame.init()

windowWidth = 750
windowHeight = 1000

windowRes = (windowWidth, windowHeight)
screen = pygame.display.set_mode(windowRes)

pygame.display.set_caption("Stack!")

PHEIGHT = 2.5 #platform height
ISO_MULTIPLIER = 10


class Platform:
    #the height of the cube is always the same, the only thing that changes is the base's dimensions
    def __init__(self, width, depth, rgb, moving): #moving can either be true or false (part of the tower)
        self.moving = moving

        self.width = width
        self.depth = depth
        self.height = PHEIGHT

        self.leaningFactor = 0.9

        self.colors = self.defineColors(rgb)
        self.vertices = self.defineVertices()
        self.edges = self.defineVisibleEdges()
        self.faces = self.defineFaces()

    def defineColors(self, rgb):
        if self.moving:
            def lightenColor(rgb, factor=1.2):
                return tuple(min(255, int(c * factor)) for c in rgb)
            return [lightenColor(rgb, 1.3), lightenColor(rgb, .7), rgb]
        else:
            return rgb

    def defineVertices(self):
        vertices = [(x, y, z)
                    for x in (0, self.width)
                    for y in (0, self.depth)
                    for z in (0, self.height)]
        
        return vertices
    
    '''def defineEdges(self):
        edges = [(i, j) 
            for i, v1 in enumerate(self.vertices) 
            for j, v2 in enumerate(self.vertices) 
            if i < j and sum(a != b for a, b in zip(v1, v2)) == 1]
        
        return edges'''
    
    def defineVisibleEdges(self):
        if(self.moving):
            visible_edges = [
                (1,3),
                (1,5),
                (2,3),
                (2,6),
                (3,7),
                (4,5),
                (4,6),
                (5,7),
                (6,7)
            ]
            return visible_edges
        else:
            return

    def defineFaces(self):
        if self.moving:
            visible_faces = [
                (1,3,7,5), #top face
                (2,3,7,6), #left face
                (4,5,7,6)  #right face
            ]
            return visible_faces
        else:
            return

    def convertToIsometric(self, x, y ,z):
        iso_x = (x - y) * self.leaningFactor
        iso_y = (x + y) / 2 - z
        return iso_x, iso_y
    
    def drawFaces(self):       
        for face, color in zip(self.faces, self.colors):
            #make an array with each faces' vertices
            vertices = [self.vertices[i] for i in face]
            #converting them to isometric projection
            iso_vertices = [self.convertToIsometric(x * ISO_MULTIPLIER, y * ISO_MULTIPLIER, z * ISO_MULTIPLIER) 
                            for x, y, z in vertices]
            #adding some padding so they get centered
            iso_vertices = [(x + windowWidth // 2, y + windowHeight // 2) for x, y in iso_vertices]

            pygame.draw.polygon(screen, color, iso_vertices)

    def drawEdges(self):
        for edge in self.edges:
            #get the 3D coords from 2 vertices
            x1, y1, z1 = self.vertices[edge[0]]
            x2, y2, z2 = self.vertices[edge[1]]
            
            #apply isometric projection to both vertices

            iso_x1, iso_y1 = self.convertToIsometric(x1 * ISO_MULTIPLIER, y1 * ISO_MULTIPLIER, z1 * ISO_MULTIPLIER)
            iso_x2, iso_y2 = self.convertToIsometric(x2 * ISO_MULTIPLIER, y2 * ISO_MULTIPLIER, z2 * ISO_MULTIPLIER)
            
            iso_x1 += windowWidth // 2
            iso_y1 += windowHeight // 2
            iso_x2 += windowWidth // 2
            iso_y2 += windowHeight // 2

            pygame.draw.line(screen, (255, 255, 255), (iso_x1, iso_y1), (iso_x2, iso_y2), 2)

class Tower:
    def __init__(self, num, initialColor): #number of platforms, color of the first platform
        self.platforms = self.definePlatforms(num, initialColor)

    def definePlatforms(self, num, initialColor):
        platforms = []

        def getGradientColor(color, num, index):
            r, g, b = color

            def getRgb(value):
                offset = value / (num + 1)
                return max(0, round(value - (offset * (index + 1))))

            return (getRgb(r), getRgb(g), getRgb(b))

        for i in range(num):
            platform = Platform(10, 10, getGradientColor(initialColor, num, i), False)
            platforms.insert(i, platform)

        return platforms

tower = Tower(3, (100, 50, 150))

clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
