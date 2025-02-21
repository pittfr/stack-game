import pygame
import numpy as np
import random

pygame.init()

windowWidth = 750
windowHeight = 1000

windowRes = (windowWidth, windowHeight)
screen = pygame.display.set_mode(windowRes)

pygame.display.set_caption("Stack!")

FRAMERATE = 60
SPHEIGHT = 3.5 #starting platform height
PHEIGHT = 2.75 #platform height
NSPLATS = 4 #number of starting platforms
SBASEWIDTH = 12.5 #starting base's width
SBASEDEPTH = 12.5 #starting base's height
MINCVALUE, MAXCVALUE = 50, 205 #MINIMUM AND MAXIMUM COLOR VALUES
STARTVEL = .3 #starting platform velocity

ISO_MULTIPLIER = 25

platVelocity = STARTVEL
numPlats = NSPLATS

gradients = []

def getGradientColor(startingColor, targetColor, numSteps, index):
    #s stands for "starting"; t stands for "target"
    sr, sg, sb = startingColor
    tr, tg, tb = targetColor

    def getRgb(svalue, tvalue):
        diff = tvalue - svalue
        offset = diff / (numSteps)
        value = svalue + (offset * (index + 1))
        value = max(0, min(255, int(value)))
        return value
    
    return (getRgb(sr, tr), getRgb(sg, tg), getRgb(sb, tb))

def getGradientColorByGradients(gradients):
    global numPlats

    if not gradients:
        startingColor = (random.randint(MINCVALUE, MAXCVALUE), 
                         random.randint(MINCVALUE, MAXCVALUE), 
                         random.randint(MINCVALUE, MAXCVALUE))
        #gradients.append(newGradient(startingColor))

    currentGradient = gradients[-1]
    startIndex, endIndex = currentGradient[0]
    startColor, targetColor = currentGradient[1]
    numSteps = currentGradient[2]

    if numPlats > endIndex:
        newStartColor = targetColor
        newGradientObj = newGradient(newStartColor)
        gradients.append(newGradientObj)
        return newGradientObj[1][0]

    index = numPlats - startIndex
    return getGradientColor(startColor, targetColor, numSteps, index)

def newGradient(startingColor):
    global numPlats
    numSteps = random.randint(7, 15)
    fromIndex = numPlats
    toIndex = numPlats + numSteps
    targetColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))

    color = ((fromIndex, toIndex), (startingColor, targetColor), numSteps)

    global gradients
    gradients.append(color)

    return color

class Platform:
    #the height of the cube is always the same, the only thing that changes is the base's dimensions
    def __init__(self, width, depth, height, moving, z_offset = PHEIGHT): #moving can either be true or false (false means the platform is a part of the tower)
        self.moving = moving
        self.direction = None #this will be either 0 or 1; 0 (moving right to left) and 1 (moving left to right)
        global platVelocity
        self.velocity = platVelocity

        self.width = width
        self.depth = depth
        self.height = height
        self.z_offset = z_offset

        self.leaningFactor = 0.65

        self.colors = None
        self.vertices = None
        self.edges = None
        self.faces = None
        
    def setup(self, rgb):
        if(self.moving):
            self.direction = self.getDirection()
        self.colors = self.defineColors(rgb)
        self.vertices = self.defineVertices()
        self.edges = self.defineVisibleEdges()
        self.faces = self.defineFaces()
    
    def lightenColor(self, rgb, factor=1.2):
        return tuple(max(0, min(255, int(c * factor))) for c in rgb)

    def getDirection(self):
        global numPlats

        currentPlat = numPlats - NSPLATS

        if(self.moving and currentPlat % 2 == 1):
            return 0
        elif(self.moving and currentPlat % 2 == 0):
            return 1
        
        if not self.moving:
            return -1

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

        if(self.direction == 0):
            vertices[:, 0] -= 25
        elif(self.direction == 1):
            vertices[:, 1] -= 25

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
        if(self.direction == 1):
            self.vertices[:, 1] += self.velocity

            x1, y1, z1 = self.vertices[1]

            if ((y1 > 25) or (y1 < -25)):
                self.velocity *= -1

        elif(self.direction == 0):
            self.vertices[:, 0] += self.velocity

            x1, y1, z1 = self.vertices[1]

            if ((x1 > 25) or (x1 < -25)):
                self.velocity *= -1

class Tower:
    def __init__(self, num, initialColor): #number of platforms, color of the first platform
        self.numStartingPlats = num
        self.initialColor = initialColor
        self.platforms = self.setupStartingPlatforms()
        self.t = -1 #time factor (-1 (when the animation is not supposed to play) or 0 to 1) used to make smooth animations when a platform is added to the tower
        self.animationTime = .1

        self.initial_z_positions = []
        self.final_z_positions = []

    def setupStartingPlatforms(self): #setup the tower
        platforms = []
        
        for i in range(self.numStartingPlats):
            z_offset = self.numStartingPlats * SPHEIGHT - (i) * SPHEIGHT
            platform = Platform(SBASEWIDTH, SBASEDEPTH, SPHEIGHT, False, z_offset)
            platform.setup(getGradientColor((0, 0, 0), self.initialColor, self.numStartingPlats, i))
            platforms.append(platform)
        
        return platforms

    def ease_in_out(self, t): #returns eased time
        return 1 - (1 - t)**3

    def add(self, plat): #called when the user presses the mouse button
        plat.moving = False
        self.platforms.append(plat)

        for platform in self.platforms:
            platform.vertices[:, 2] -= plat.height
        '''if(self.t == -1):
            self.t = 0

            self.initial_z_positions = [platform.vertices[:, 2].copy() for platform in self.platforms]
            
            self.final_z_positions = [
                (platform.vertices[:, 2] - platform.height).copy() for platform in self.platforms
            ]

        #self.t = -1'''
    
    def getNumPlats(self): #returns the amount of platforms that are in the tower (including the starting ones)
        return len(self.platforms)

    def getTowers(self): #returns the array of objects
        return self.platforms

    def update(self):
        #animation
        '''if(self.t != -1):
            global FRAMERATE
            self.t += 1 / (20) #calculate the interpolation factor (1 / the amount of frames the animation takes)

            if(self.t > 1): #if the animation is over make it -1 again
                for i, platform in enumerate(self.platforms):
                    platform.vertices[:, 2] = self.final_z_positions[i]
                self.t = -1


            eased_t = self.ease_in_out(self.t)

            for i, platform in enumerate(self.platforms):
                platform.vertices[:, 2] = self.initial_z_positions[i] + (self.final_z_positions[i] - self.initial_z_positions[i]) * eased_t'''

        #tower go down
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

gradient = newGradient(initialColor)

plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, True)
plat.setup(getGradientColorByGradients(gradients))
tower = Tower(NSPLATS, initialColor)

def drawGame():
    screen.fill((0, 0, 0))

    tower.update()
    tower.draw()

    plat.update()
    plat.drawFaces()

previous_mouse_state = (0, 0, 0)

clock = pygame.time.Clock()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    current_mouse_state = pygame.mouse.get_pressed()

    if current_mouse_state[0] and not previous_mouse_state[0]:
        #mouse clicked
        tower.add(plat)
        numPlats = tower.getNumPlats()
        plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, True)
        plat.setup(getGradientColorByGradients(gradients))

    previous_mouse_state = current_mouse_state

    '''if(numPlats == NSPLATS):
        newColor()'''

    drawGame()

    pygame.display.flip()
    pygame.mouse.set_visible(False)
    clock.tick(FRAMERATE)

pygame.quit()
