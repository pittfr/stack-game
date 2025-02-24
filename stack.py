import pygame
import numpy as np
import random
import win32print
import win32gui

def getCurrentMonitorFramerate():
    dc = win32gui.GetDC(0) #get device context
    framerate = win32print.GetDeviceCaps(dc, 116)  # get refresh rate of the monitor
    win32gui.ReleaseDC(0, dc) #release device context
    return framerate

pygame.init()

FRAMERATE = getCurrentMonitorFramerate()
print(FRAMERATE)

windowWidth = 750
windowHeight = 1000

windowRes = (windowWidth, windowHeight)
screen = pygame.display.set_mode(windowRes)

pygame.display.set_caption("Stack!")

SPHEIGHT = 3.5 #starting platform height
PHEIGHT = 2.5 #platform height
NSPLATS = 4 #number of starting platforms
SBASEWIDTH = 12.5 #starting base's width
SBASEDEPTH = 12.5 #starting base's height
MINCVALUE, MAXCVALUE = 50, 205 #MINIMUM AND MAXIMUM COLOR VALUES
STARTVEL = 20 #starting platform velocity
VELMULTIPLIER = 1.02 #velocity multiplier
COLORTHRESHOLD = 80 #color threshold
PLATCENTEROFFSET = 25 #platform center offset
MAXPERFECTOFFSET = 1 #maximum offset for a perfect placement

ISO_MULTIPLIER = 25

platVelocity = STARTVEL
numPlats = NSPLATS

score = numPlats - NSPLATS

nextPlatWidth = SBASEWIDTH
nextPlatDepth = SBASEDEPTH

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
    numSteps = random.randint(10, 20)
    fromIndex = numPlats
    toIndex = numPlats + numSteps

    def colorDistance(color1, color2):
        return ((color1[0] - color2[0]) ** 2 + (color1[1] - color2[1]) ** 2 + (color1[2] - color2[2]) ** 2) ** 0.5


    while True:
        targetColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))
        if colorDistance(startingColor, targetColor) > COLORTHRESHOLD:
            break

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
        
    def setup(self, rgb, lastPlat = None):
        if(self.moving):
            self.direction = self.getDirection()
            self.vertices = self.defineVertices(lastPlat)
        else:
            self.vertices = self.defineVertices()
        self.colors = self.defineColors(rgb)
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

    def defineVertices(self, lastPlat = None):
        #defining the base grid
        x = np.array([0, self.width], dtype=float)
        y = np.array([0, self.depth], dtype=float)
        z = np.array([0, self.height], dtype=float)

        #generating the actual grid
        X, Y, Z = np.meshgrid(x, y, z, indexing="ij")

        vertices = np.column_stack([X.ravel(), Y.ravel(), Z.ravel()]).astype(float)

        if(self.moving and lastPlat != None):
            self.align(lastPlat)

        if(self.direction == 0):
            vertices[:, 0] -= PLATCENTEROFFSET
        elif(self.direction == 1):
            vertices[:, 1] -= PLATCENTEROFFSET

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

    def update(self, delta_time):
        if(self.direction == 1):
            self.vertices[:, 1] += self.velocity * delta_time

            x1, y1, z1 = self.vertices[1]

            if ((y1 > PLATCENTEROFFSET) or (y1 < -PLATCENTEROFFSET)):
                self.velocity *= -1

        elif(self.direction == 0):
            self.vertices[:, 0] += self.velocity * delta_time

            x1, y1, z1 = self.vertices[1]

            if ((x1 > PLATCENTEROFFSET) or (x1 < -PLATCENTEROFFSET)):
                self.velocity *= -1

    def align(self, lastPlat, perfectPlacement = False):
        xOffset = lastPlat.vertices[0][0] - self.vertices[0][0]
        yOffset = lastPlat.vertices[0][1] - self.vertices[0][1]
        self.vertices[:, 0] += xOffset
        self.vertices[:, 1] += yOffset

        if(not perfectPlacement):
            if self.direction == 0:
                self.vertices[:, 0] -= PLATCENTEROFFSET
            elif self.direction == 1:
                self.vertices[:, 1] -= PLATCENTEROFFSET

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
        pass
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

    def getTrimming(self, currentPlat, lastPlat):
        # get the bounding box of the last platform
        last_min_x = min(lastPlat.vertices[:, 0])
        last_max_x = max(lastPlat.vertices[:, 0])
        last_min_y = min(lastPlat.vertices[:, 1])
        last_max_y = max(lastPlat.vertices[:, 1])

        # get the bounding box of the current platform
        curr_min_x = min(currentPlat.vertices[:, 0])
        curr_max_x = max(currentPlat.vertices[:, 0])
        curr_min_y = min(currentPlat.vertices[:, 1])
        curr_max_y = max(currentPlat.vertices[:, 1])

        # calculating the overlap between the two platforms
        overlap_x = max(0, min(last_max_x, curr_max_x) - max(last_min_x, curr_min_x))
        overlap_y = max(0, min(last_max_y, curr_max_y) - max(last_min_y, curr_min_y))
        
        perfect = False

        # trimming the current platform
        if(currentPlat.direction == 0): 
            new_width = overlap_x
            new_depth = currentPlat.depth
            perfect = (currentPlat.width - overlap_x) <= MAXPERFECTOFFSET
        elif(currentPlat.direction == 1):
            new_width = currentPlat.width
            new_depth = overlap_y
            perfect = (currentPlat.depth - overlap_y) <= MAXPERFECTOFFSET

        # check if its a perfect placement
        if(perfect):
            new_width = currentPlat.width
            new_depth = currentPlat.depth
        else:
            new_width = overlap_x
            new_depth = overlap_y

        
        return new_width, new_depth, perfect

    def getLastPlat(self):
        return self.platforms[-1]

    def draw(self):
        self.update()
        for plat in (self.platforms):
            plat.drawFaces()

initialColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))

gradient = newGradient(initialColor)

plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, True)
plat.setup(getGradientColorByGradients(gradients))
tower = Tower(NSPLATS, initialColor)

def drawGame(delta_time):
    screen.fill((0, 0, 0))

    tower.update()
    tower.draw()

    plat.update(delta_time)
    plat.drawFaces()

previous_mouse_state = (0, 0, 0)

clock = pygame.time.Clock()

running = True

def handleEvents():
    global running, previous_mouse_state

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                handlePlatformPlacement()

    current_mouse_state = pygame.mouse.get_pressed()

    if current_mouse_state[0] and not previous_mouse_state[0]:
        handlePlatformPlacement()

    previous_mouse_state = current_mouse_state

def handlePlatformPlacement():
    global plat, numPlats, platVelocity, gradients, score

    lastPlat = tower.getLastPlat()
    nextPlatWidth, nextPlatDepth, perfectPlacement = tower.getTrimming(plat, tower.getLastPlat())

    if(perfectPlacement):
        print("Perfect Placement!")
        plat.width = lastPlat.width
        plat.depth = lastPlat.depth
        plat.align(lastPlat, perfectPlacement)
    else:
        if (nextPlatWidth != plat.width or nextPlatDepth != plat.depth):
            plat.width = nextPlatWidth
            plat.depth = nextPlatDepth

            # align the platform with the last platform
            plat.vertices[:, 0] = np.clip(plat.vertices[:, 0], min(lastPlat.vertices[:, 0]), max(lastPlat.vertices[:, 0]))
            plat.vertices[:, 1] = np.clip(plat.vertices[:, 1], min(lastPlat.vertices[:, 1]), max(lastPlat.vertices[:, 1]))

    tower.add(plat)

    numPlats = tower.getNumPlats()
    score = numPlats - NSPLATS

    platVelocity *= VELMULTIPLIER
    
    lastPlat = tower.getLastPlat()
    
    plat = Platform(nextPlatWidth, nextPlatDepth, PHEIGHT, True)
    plat.setup(getGradientColorByGradients(gradients))
    plat.align(lastPlat)

    print(score)

while running:
    handleEvents()

    delta_time = clock.get_time() / 1000.0

    drawGame(delta_time)

    pygame.display.flip()
    pygame.mouse.set_visible(False)
    clock.tick(FRAMERATE)

pygame.quit()
