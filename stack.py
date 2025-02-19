import pygame
import numpy as np
import random

pygame.init()

windowWidth = 750
windowHeight = 1000

windowRes = (windowWidth, windowHeight)
screen = pygame.display.set_mode(windowRes)

pygame.display.set_caption("Stack!")

SPHEIGHT = 3.5 #starting platform height
PHEIGHT = 3 #platform height
NSPLATS = 4 #number of starting platforms
SBASEWIDTH = 12.5
SBASEDEPTH = 12.5
MINCVALUE, MAXCVALUE = 100, 220 #MINIMUM AND MAXIMUM COLOR VALUES

ISO_MULTIPLIER = 25

def getGradientColor(startingColor, targetColor, numSteps, index):
    #s stands for "starting"; t stands for "target"
    r, g, b = startingColor
    tr, tg, tb = targetColor

    def getRgb(svalue, tvalue):
        diff = tvalue - svalue
        offset = diff / (numSteps + 1)
        value = svalue + (offset * (index + 1))
        value = max(0, min(255, int(value)))
        return value

        '''offset = value / (numSteps + 1)
        value = max(0, int((offset * (index + 1)))) #make it so the value cant be less than 0
        return min(255, value) #value cant be more than 255'''
    
    return (getRgb(r, tr), getRgb(g, tg), getRgb(b, tb))

class Platform:
    #the height of the cube is always the same, the only thing that changes is the base's dimensions
    def __init__(self, width, depth, height, moving, z_offset = PHEIGHT): #moving can either be true or false (false means the platform is a part of the tower)
        self.moving = moving

        self.width = width
        self.depth = depth
        self.height = height
        self.z_offset = z_offset

        self.leaningFactor = 0.7

        self.colors = None
        self.vertices = None
        self.edges = None
        self.faces = None
        
    def setup(self, rgb):
        self.colors = self.defineColors(rgb)
        self.vertices = self.defineVertices()
        self.edges = self.defineVisibleEdges()
        self.faces = self.defineFaces()
    
    def lightenColor(self, rgb, factor=1.2):
        return tuple(max(0, min(255, int(c * factor))) for c in rgb)

    def defineColors(self, rgb):
        return [self.lightenColor(rgb, 1.4), self.lightenColor(rgb, .6), rgb]

    def defineVertices(self):
        #defining the base grid
        x = np.array([0, self.width])
        y = np.array([0, self.depth])
        z = np.array([0, self.height])

        #generating the actual grid
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

        vertices = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()]).astype(float)

        if(not self.moving):
            vertices[:, 2] -= self.z_offset

        return vertices
        '''if(self.moving):
            vertices = [[x, y, z]
                        for x in (0, self.width)
                        for y in (0, self.depth)
                        for z in (0, self.height)]
            return vertices
        else:
            vertices = [[x, y, z + self.z_offset]
                        for x in (0, self.width)
                        for y in (0, self.depth)
                        for z in (0, self.height)]
            return vertices'''
    
    '''def defineEdges(self):
        edges = [(i, j) 
            for i, v1 in enumerate(self.vertices) 
            for j, v2 in enumerate(self.vertices) 
            if i < j and sum(a != b for a, b in zip(v1, v2)) == 1]
        
        return edges'''
    
    def defineVisibleEdges(self):
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

    def defineFaces(self):
        visible_faces = [
            (1,3,7,5), #top face
            (2,3,7,6), #left face
            (4,5,7,6)  #right face
        ]
        return visible_faces

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

    def update(self):
        for i in range(len(self.vertices)):
            self.vertices[i][1] += .1

class Tower:
    def __init__(self, num, initialColor): #number of platforms, color of the first platform
        self.numPlats = num
        self.initialColor = initialColor
        self.platforms = self.setupStartingPlatforms()
        
    def setupStartingPlatforms(self):
        platforms = []
        
        for i in range(self.numPlats):
            z_offset = self.numPlats * SPHEIGHT - (i) * SPHEIGHT
            platform = Platform(SBASEWIDTH, SBASEDEPTH, SPHEIGHT, False, z_offset)
            platform.setup(getGradientColor((0, 0, 0), self.initialColor, self.numPlats, i))
            platforms.append(platform)
        
        return platforms
    
    def getNumPlats(self):
        return self.numPlats

    def getTowers(self):
        return self.platforms

    def update(self):
        pass
        '''for plat in (self.platforms):
            for i in range(len(plat.vertices)):  
                plat.vertices[i][2] -= 0.1
            plat.defineVisibleEdges()
            plat.defineFaces()'''

    def draw(self):
        self.update()
        for plat in (self.platforms):
            plat.drawFaces()

initialColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))

colors = []
colors.append(initialColor)

plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, True)
plat.setup((200,100,255))
tower = Tower(NSPLATS, initialColor)

clock = pygame.time.Clock()
running = True

tower.update()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    tower.draw()

    #plat.update()
    plat.drawEdges()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
