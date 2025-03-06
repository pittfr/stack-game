import pygame
import numpy as np
import random
import win32print
import win32gui
import os

# constants
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 1000

SPHEIGHT = 5  # starting platform height
PHEIGHT = 2  # platform height
NSPLATS = 3  # number of starting platforms
SBASEWIDTH = 12.5  # starting base's width
SBASEDEPTH = 12.5  # starting base's height
PLATCENTEROFFSET = 25  # platform center offset
MAXPERFECTOFFSETPERCENTAGE = 0.12  # maximum offset for a perfect placement
MINVALIDSIDE = 0.15  # minimum valid side length for a platform

COLORTHRESHOLD = 75  # color distance threshold for the gradients
BACKGROUNDDESATURATION = 0.4  # background desaturation factor
MINCVALUE, MAXCVALUE = 25, 205  # MINIMUM AND MAXIMUM COLOR VALUES
MINNSTEPS, MAXNSTEPS = 7, 15  # MINIMUM AND MAXIMUM NUMBER OF STEPS FOR THE GRADIENT

STARTVEL = 25  # starting platform velocity
VELINCREMENT = 0.10  # velocity increment

ISO_MULTIPLIER = 25

def getCurrentMonitorFramerate():
    """
    gets the current monitor's refresh rate
    """
    dc = win32gui.GetDC(0)  # get device context
    framerate = win32print.GetDeviceCaps(dc, 116)  # get refresh rate of the monitor
    win32gui.ReleaseDC(0, dc)  # release device context
    return framerate

# initialize Pygame
try:
    pygame.init()
except pygame.error as e:
    print(f"Failed to initialize Pygame: {e}")
    exit(1)

FRAMERATE = getCurrentMonitorFramerate()
print(FRAMERATE)

windowRes = (WINDOW_WIDTH, WINDOW_HEIGHT)
screen = pygame.display.set_mode(windowRes)
pygame.display.set_caption("Stack!")

# initialize game variables
platVelocity = STARTVEL
numPlats = NSPLATS
score = numPlats - NSPLATS
perfectStackCounter = 0
gameover = False
nextPlatWidth = SBASEWIDTH
nextPlatDepth = SBASEDEPTH
gradients = []

# load sound effects
stackingSFXs = []
perfectStackingSFXs = []

for i in range(1, 3):
    try:
        stackingSFXs.append(pygame.mixer.Sound(f"assets/SFX/normalStack/stack{i}.wav"))
    except pygame.error as e:
        print(f"Error loading normalStack/{i}.wav: {e}")

for i in range(1, 21):
    try:
        perfectStackingSFXs.append(pygame.mixer.Sound(f"assets/SFX/perfectStack/perfect{i}.wav"))
    except pygame.error as e:
        print(f"Error loading perfectStack/{i}.wav: {e}")

# colors
def lightenColor(rgb, factor=1.2):
    """
    lightens the given RGB color by a specified factor
    
    rgb: tuple of (r, g, b) values
    factor: lightening factor
    returns a tuple of lightened (r, g, b) values
    """
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)

def desaturateColor(rgb, factor=0.5):
    """
    desaturates the given RGB color by blending it with its grayscale equivalent
    
    rgb: tuple of (r, g, b) values
    factor: desaturation factor (0.0 = fully saturated, 1.0 = fully desaturated)
    returns a tuple of desaturated (R, G, B) values
    """
    r, g, b = rgb
    gray = int(0.3 * r + 0.59 * g + 0.11 * b)  # convert to grayscale using luminance formula
    desaturated = (
        int(r + (gray - r) * factor),
        int(g + (gray - g) * factor),
        int(b + (gray - b) * factor)
    )
    return desaturated

def newGradient(startingColor):
    """
    creates a new gradient with the given starting color and adds it to the list of gradients
    """
    global gradients, gradient
    gradient = Gradient(startingColor)
    gradients.append(gradient)
    return gradient

def drawBackground(screen, gradients):
    """
    draws the gradient background on the screen.
    """
    if not gradients:
        return

    currentGradient = gradients[-1]
    startColor = currentGradient.startingColor
    targetColor = currentGradient.targetColor

    for i in range(WINDOW_HEIGHT):
        color = desaturateColor(
                lightenColor(
                    Gradient.getGradientColorFrom(startColor, targetColor, WINDOW_HEIGHT, WINDOW_HEIGHT - i - 1)
                ), 
                BACKGROUNDDESATURATION
            )
        pygame.draw.line(screen, color, (0, i), (WINDOW_WIDTH, i))

# classes

class Gradient:
    def __init__(self, startingColor):
        self.startingColor = startingColor
        self.targetColor = self.generateTargetColor()
        self.numSteps = random.randint(MINNSTEPS, MAXNSTEPS)
        self.fromIndex = numPlats
        self.toIndex = numPlats + self.numSteps

    def generateTargetColor(self):
        while True:
            targetColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))
            if self.colorDistance(self.startingColor, targetColor) > COLORTHRESHOLD:
                if gradients:
                    last_startingColor = gradients[-1].startingColor
                    if self.colorDistance(last_startingColor, self.startingColor) > COLORTHRESHOLD:
                        return targetColor
                else:
                    return targetColor

    @staticmethod
    def colorDistance(color1, color2):
        return ((color1[0] - color2[0]) ** 2 + (color1[1] - color2[1]) ** 2 + (color1[2] - color2[2]) ** 2) ** 0.5

    def getGradientColor(self, index):
        sr, sg, sb = self.startingColor
        tr, tg, tb = self.targetColor

        def getRgb(svalue, tvalue):
            diff = tvalue - svalue
            offset = diff / self.numSteps
            value = svalue + (offset * (index + 1))
            return max(0, min(255, int(value)))

        return (getRgb(sr, tr), getRgb(sg, tg), getRgb(sb, tb))
    
    @staticmethod
    def getGradientColorFrom(startingColor, targetColor, numSteps, index):
        sr, sg, sb = startingColor
        tr, tg, tb = targetColor

        def getRgb(svalue, tvalue):
            diff = tvalue - svalue
            offset = diff / numSteps
            value = svalue + (offset * (index + 1))
            return max(0, min(255, int(value)))

        return (getRgb(sr, tr), getRgb(sg, tg), getRgb(sb, tb))

    def getCurrentColor(self):
        global numPlats
        if numPlats > self.toIndex:
            newStartColor = self.targetColor
            newGradientObj = newGradient(newStartColor)
            return newGradientObj.startingColor

        index = numPlats - self.fromIndex
        return self.getGradientColor(index)

class Platform:
    def __init__(self, width, depth, height, moving, z_offset = PHEIGHT): #moving can either be true or false (false means the platform is a part of the tower)
        self.moving = moving
        self.direction = None # this will be either 0 or 1; 0 (moving right to left) and 1 (moving left to right)
        global platVelocity
        self.velocity = platVelocity

        self.width = width
        self.depth = depth
        self.height = height
        self.z_offset = z_offset

        self.colors = None
        self.vertices = None
        self.edges = None
        self.faces = None
        
    def setup(self, rgb, lastPlat = None):
        """
        sets up the platform with the given color and aligns it with the last platform if provided
        
        rgb: tuple of (r, g, b) values for the platform color
        lastPlat: the last platform object to align with
        """
        if(self.moving):
            self.direction = self.getDirection()
            self.vertices = self.defineVertices(lastPlat)
        else:
            self.vertices = self.defineVertices()
        self.colors = self.defineColors(rgb)
        self.edges = self.defineVisibleEdges()
        self.faces = self.defineFaces()

    def getDirection(self):
        """
        determines the direction of the platform's movement
        
        returns a direction value (0 for right to left, 1 for left to right, -1 for no movement)
        """
        global numPlats

        currentPlat = numPlats - NSPLATS

        if(self.moving and currentPlat % 2 == 1):
            return 0
        elif(self.moving and currentPlat % 2 == 0):
            return 1
        
        if not self.moving:
            return -1

    def defineColors(self, rgb):
        """
        defines the colors for the platform's faces
        
        rgb: tuple of (r, g, b) values for the base color
        returns a list of colors for the platform's faces
        """
        return [lightenColor(rgb, 1.4), lightenColor(rgb, .6), rgb]

    def defineVertices(self, lastPlat = None):
        """
        defines the vertices of the platform
        
        lastPlat: the last platform object to align with
        returns an array of vertices for the platform
        """
        # defining the base grid
        x = np.array([0, self.width], dtype=float)
        y = np.array([0, self.depth], dtype=float)
        z = np.array([0, self.height], dtype=float)

        # generating the actual grid
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
    
    def defineVisibleEdges(self):
        """
        defines the visible edges of the platform
        
        returns a list of visible edges for the platform
        """
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
        """
        defines the visible faces of the platform
        
        returns a list of visible faces for the platform
        """
        visible_faces = [
            (1,3,7,5), # top face
            (2,3,7,6), # left face
            (4,5,7,6)  # right face
        ]
        return visible_faces

    def convertToIsometric(self, x, y ,z):
        """
        converts 3D coordinates to isometric projection
        
        x: X coordinate
        y: Y coordinate
        z: Z coordinate
        returns a tuple of isometric (x, y) coordinates
        """
        leaningFactor = 0.65
        iso_x = (x - y) * leaningFactor
        iso_y = (x + y) / 2 - z
        return iso_x, iso_y
    
    def drawFaces(self):       
        """
        draws the faces of the platform
        """
        for face, color in zip(self.faces, self.colors):
            # make an array with each faces' vertices
            vertices = [self.vertices[i] for i in face]
            # converting them to isometric projection
            iso_vertices = [self.convertToIsometric(x * ISO_MULTIPLIER, y * ISO_MULTIPLIER, z * ISO_MULTIPLIER) 
                            for x, y, z in vertices]
            # adding some padding so they get centered
            iso_vertices = [(x + WINDOW_WIDTH // 2, y + WINDOW_HEIGHT // 2) for x, y in iso_vertices]

            pygame.draw.polygon(screen, color, iso_vertices)

    def drawEdges(self):
        """
        draws the edges of the platform
        """
        for edge in self.edges:
            # get the 3D coords from 2 vertices
            x1, y1, z1 = self.vertices[edge[0]]
            x2, y2, z2 = self.vertices[edge[1]]
            
            # apply isometric projection to both vertices

            iso_x1, iso_y1 = self.convertToIsometric(x1 * ISO_MULTIPLIER, y1 * ISO_MULTIPLIER, z1 * ISO_MULTIPLIER)
            iso_x2, iso_y2 = self.convertToIsometric(x2 * ISO_MULTIPLIER, y2 * ISO_MULTIPLIER, z2 * ISO_MULTIPLIER)
            
            iso_x1 += WINDOW_WIDTH // 2
            iso_y1 += WINDOW_HEIGHT // 2
            iso_x2 += WINDOW_WIDTH // 2
            iso_y2 += WINDOW_HEIGHT // 2

            pygame.draw.line(screen, (255, 255, 255), (iso_x1, iso_y1), (iso_x2, iso_y2), 2)

    def update(self, delta_time):
        """
        updates the platform's position based on its velocity and direction
        
        delta_time: time elapsed since the last update
        """
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
        """
        aligns the platform with the last platform
        
        lastPlat: the last platform object to align with
        perfectPlacement: boolean indicating if the placement is perfect
        """
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
    def __init__(self, num, initialColor): # number of platforms, color of the first platform
        self.numStartingPlats = num
        self.initialColor = initialColor
        self.platforms = self.setupStartingPlatforms()
        self.t = -1 # time variable for the animation (-1 means the animation is not running, 0 to 1 means the animation is running)
        self.animationTime = 0.4 # time it takes for the animation to complete

        self.initial_z_positions = []
        self.final_z_positions = []

    def setupStartingPlatforms(self): # setup the tower
        """
        sets up the starting platforms for the tower
        
        returns a list of starting platform objects
        """
        platforms = []
        
        for i in range(self.numStartingPlats):
            z_offset = self.numStartingPlats * SPHEIGHT - (i) * SPHEIGHT # z offset for the starting platforms
            platform = Platform(SBASEWIDTH, SBASEDEPTH, SPHEIGHT, False, z_offset)
            platform.setup(Gradient.getGradientColorFrom((0, 0, 0), self.initialColor, self.numStartingPlats, i))
            platforms.append(platform)
        
        return platforms

    def ease_in_out(self, t): # easing function for the animation (t is the time variable)
        """
        easing function for the animation
        
        t: time variable
        returns eased time value
        """
        return 1 - (1 - t)**3

    def add(self, plat): # called when the user presses the mouse button
        """
        adds a new platform to the tower and starts the animation
        
        plat: the new platform object to add
        """
        plat.moving = False # the platform is no longer moving
        self.platforms.append(plat) # add the platform to the tower

        shift_amount = plat.height # the amount the platform will be shifted down

        self.initial_z_positions = [platform.vertices[:, 2].copy() for platform in self.platforms] # copy the z positions of the platforms
        self.final_z_positions = [platform.vertices[:, 2].copy() - shift_amount for platform in self.platforms] # copy the shifted z positions of the platforms

        self.t = 0 # starts the animation 
    
    def getNumPlats(self): # returns the amount of platforms that are in the tower (including the starting ones)
        return len(self.platforms)

    def getTowers(self): # returns the array of objects
        return self.platforms

    def update(self):
        if self.t != -1: # if the animation is running
            self.t += 1 / (FRAMERATE * self.animationTime) #increment the time variable

            if self.t >= 1: # if the animation is finished
                self.t = -1 # stop the animation
                for i, platform in enumerate(self.platforms): # set the z positions of the platforms to the final z positions (to avoid floating point errors)
                    platform.vertices[:, 2] = self.final_z_positions[i]
            else: # if the animation is still running
                eased_t = self.ease_in_out(self.t) # get the eased time

                for i, platform in enumerate(self.platforms): # update the z positions of the platforms
                    platform.vertices[:, 2] = self.initial_z_positions[i] + (self.final_z_positions[i] - self.initial_z_positions[i]) * eased_t

    def getTrimming(self, currentPlat, lastPlat): # trim the current platform to fit the last platform
        def dynamicPerfectOffset(size):
            base_offset = size * MAXPERFECTOFFSETPERCENTAGE

            # exponential decay factor (prevents large offsets for big platforms)
            scaling_factor = 1 - np.exp(-size / SBASEWIDTH)  

            adjusted_offset = base_offset * scaling_factor

            return max(0.15, adjusted_offset)  # ensure a reasonable minimum

        if currentPlat.direction == 0:
            MAXPERFECTOFFSET = dynamicPerfectOffset(currentPlat.width)
        else:
            MAXPERFECTOFFSET = dynamicPerfectOffset(currentPlat.depth)

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

    def getLastPlat(self): # returns the last platform in the tower
        return self.platforms[-1]

    def draw(self):
        self.update()
        for plat in (self.platforms):
            plat.drawFaces()

#game functions

def setupGame():
    global initialColor, gradient, plat, tower, previous_mouse_state, clock, running, gameover, score, platVelocity, numPlats, gradients, perfectStackCounter
    
    gradients = []
    numPlats = NSPLATS
    
    initialColor = (random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE), random.randint(MINCVALUE, MAXCVALUE))
    newGradient(initialColor)

    plat = Platform(SBASEWIDTH, SBASEDEPTH, PHEIGHT, True)
    plat.setup(gradient.getCurrentColor())
    tower = Tower(NSPLATS, initialColor)

    previous_mouse_state = (0, 0, 0)
    clock = pygame.time.Clock()
    running = True
    gameover = False
    score = numPlats - NSPLATS
    perfectStackCounter = 0
    platVelocity = STARTVEL

def handleEvents():
    global running, previous_mouse_state, gameover

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if(not gameover):
                    handlePlatformPlacement()
            elif event.key == pygame.K_r:
                gameover = True

    current_mouse_state = pygame.mouse.get_pressed()

    if current_mouse_state[0] and not previous_mouse_state[0]:
        if(not gameover):
            handlePlatformPlacement()

    previous_mouse_state = current_mouse_state

def handlePlatformPlacement():
    global plat, numPlats, platVelocity, gradients, score, gameover, perfectStackCounter

    lastPlat = tower.getLastPlat()
    nextPlatWidth, nextPlatDepth, perfectPlacement = tower.getTrimming(plat, tower.getLastPlat())

    if(perfectPlacement):
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

    platVelocity += VELINCREMENT
    
    if(nextPlatWidth <= MINVALIDSIDE or nextPlatDepth <= MINVALIDSIDE):
        gameover = True
    else:
        score = numPlats - NSPLATS + 1
        tower.add(plat)

        numPlats = tower.getNumPlats()

        lastPlat = tower.getLastPlat()
        plat = Platform(nextPlatWidth, nextPlatDepth, PHEIGHT, True)
        plat.setup(gradients[-1].getCurrentColor())
        plat.align(lastPlat)

        if(perfectPlacement):
            perfectStackCounter += 1
            perfectStackingSFXs[(perfectStackCounter % len(perfectStackingSFXs)) - 1].play()
        else:
            random.choice(stackingSFXs).play()
            perfectStackCounter = 0
        print(score)

def drawGame(delta_time):
    global gameover
    screen.fill((0, 0, 0))

    drawBackground(screen, gradients)

    tower.update()
    tower.draw()

    if(not gameover):
        plat.update(delta_time)
        plat.drawFaces()

# main game loop
setupGame()

while running:
    delta_time = clock.tick(FRAMERATE) / 1000.0  # delta_time is the time it takes to render one frame

    handleEvents()

    if gameover:
        setupGame()
        os.system('cls')  # this line is for debug only

    drawGame(delta_time)
    pygame.display.flip()

pygame.quit()
