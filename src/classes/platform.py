import pygame
import numpy as np

from constants import *
from utils.utils import lightenColor, ease_in_out

class Platform:
    def __init__(self, width, depth, height, platVelocity, numPlats, moving, z_offset = PHEIGHT): #moving can either be true or false (false means the platform is a part of the tower)
        self.moving = moving
        self.expanding = False
        self.direction = self.getDirection(numPlats) if moving else -1 # this will be either 0 or 1; 0 (moving right to left) and 1 (moving left to right); -1 means no movement
        self.velocity = platVelocity

        self.width = width
        self.depth = depth
        self.height = height
        self.z_offset = z_offset
        self.initial_vertices = None
        self.final_vertices = None
        self.targetDepth = self.depth

        self.expand_duration = .5 # seconds
        self.expand_timer = 0 # current time for the expansion animation
        self.expand_progress = 0 # progress from 0 to 1

        self.colors = None
        self.vertices = None
        self.edges = None
        self.faces = None
        
    def setup(self, rbg, lastPlat = None):
        """
        sets up the platform with the given color and aligns it with the last platform if provided
        
        rgb: tuple of (r, g, b) values for the platform color
        lastPlat: the last platform object to align with
        """
        self.vertices = self.getVertices(lastPlat)
        self.initial_vertices = self.vertices.copy()
        self.final_vertices = self.vertices.copy()
        self.colors = self.getColors(rbg)
        self.edges = self.getEdges()
        self.faces = self.getVisibleFaces()

    def getDirection(self, numPlats):
        """
        determines the direction of the platform's movement
        
        returns a direction value (0 for right to left, 1 for left to right, -1 for no movement)
        """

        currentPlat = numPlats - NSPLATS

        if(self.moving):
            if(currentPlat % 2 == 1):
                return 0
            else:
                return 1
        else:
            return -1

    def getColors(self, rgb):
        """
        defines the colors for the platform's faces
        
        rgb: tuple of (r, g, b) values for the base color
        returns a list of colors for the platform's faces
        """
        return [lightenColor(rgb, 1.4), lightenColor(rgb, .6), rgb]

    def getVertices(self, lastPlat = None):
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

        if(self.direction == 0):
            vertices[:, 0] -= PLATCENTEROFFSET
        elif(self.direction == 1):
            vertices[:, 1] -= PLATCENTEROFFSET

        if(not self.moving):
            vertices[:, 2] -= self.z_offset

        return vertices

    def getEdges(self):
        """
        defines the edges of the platform
        
        returns a list of edges for the platform
        """
        edges = [
            (0,1),
            (0,2),
            (0,4),
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
        return edges

    def getVisibleEdges(self):
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

    def getFaces(self):
        """
        defines the faces of the platform
        
        returns a list of faces for the platform
        """
        faces = [
            (0,1,3,2), # not visible left face
            (0,1,5,4), # not visible right face
            (0,2,6,4), # bottom face
            (1,3,7,5), # top face
            (2,3,7,6), # visible left face
            (4,5,7,6)  # visible right face
        ]

        return faces

    def getVisibleFaces(self):
        """
        defines the visible faces of the platform
        
        returns a list of the visible faces for the platform
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

    def drawFaces(self, screen):       
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

            # draw the face if it's visible
            if any(0 <= x < WINDOW_WIDTH and 0 <= y < WINDOW_HEIGHT for x, y in iso_vertices):
                pygame.draw.polygon(screen, color, iso_vertices)

    def drawTargetEdges(self, screen):
        """
        draws the edges of the platform
        """
        for edge in self.edges:
            # get the 3D coords from 2 vertices
            x1, y1, z1 = self.final_vertices[edge[0]]
            x2, y2, z2 = self.final_vertices[edge[1]]
            
            # apply isometric projection to both vertices

            iso_x1, iso_y1 = self.convertToIsometric(x1 * ISO_MULTIPLIER, y1 * ISO_MULTIPLIER, z1 * ISO_MULTIPLIER)
            iso_x2, iso_y2 = self.convertToIsometric(x2 * ISO_MULTIPLIER, y2 * ISO_MULTIPLIER, z2 * ISO_MULTIPLIER)
            
            iso_x1 += WINDOW_WIDTH // 2
            iso_y1 += WINDOW_HEIGHT // 2
            iso_x2 += WINDOW_WIDTH // 2
            iso_y2 += WINDOW_HEIGHT // 2

            pygame.draw.line(screen, (255, 255, 255), (iso_x1, iso_y1), (iso_x2, iso_y2), 2)

    def align(self, lastPlat):
        """
        aligns the platform with the last platform
        
        lastPlat: the last platform object to align with
        perfectPlacement: boolean indicating if the placement is perfect
        refPointIndex: the index of the reference point for alignment
        """

        refPoint = self.final_vertices[DEFAULTALIGNINDEX]

        targetPoint = lastPlat.final_vertices[DEFAULTALIGNINDEX]

        # calculate offsets to align bottom-left corners
        xOffset = targetPoint[0] - refPoint[0]
        yOffset = targetPoint[1] - refPoint[1]

        # apply the offset to all vertices
        self.vertices[:, 0] += xOffset
        self.vertices[:, 1] += yOffset

        # only apply the PLATCENTEROFFSET for moving platforms
        if(self.moving):
            if self.direction == 0:
                self.vertices[:, 0] -= PLATCENTEROFFSET
            elif self.direction == 1:
                self.vertices[:, 1] -= PLATCENTEROFFSET

        self.final_vertices = self.vertices.copy()

    def perfectAlign(self, lastPlat):
        """
        aligns the platform perfectly with the last platform
        
        lastPlat: the last platform object to align with
        """

        # stop the moving animation if it's in progress
        self.moving = False

        # 
        refPoint = self.final_vertices[DEFAULTALIGNINDEX]
        targetPoint = lastPlat.final_vertices[DEFAULTALIGNINDEX]

        # calculate offsets to align bottom-left corners
        xOffset = targetPoint[0] - refPoint[0]
        yOffset = targetPoint[1] - refPoint[1]

        # apply the offset to all vertices
        self.vertices[:, 0] += xOffset
        self.vertices[:, 1] += yOffset

        self.final_vertices = self.vertices.copy()

    def update(self, delta_time):
        """
        updates the platform's position based on its velocity and direction
        
        delta_time: time elapsed since the last update
        """
        if(self.moving):
            if(self.direction == 1):
                self.vertices[:, 1] += self.velocity * delta_time

                x1, y1, z1 = self.vertices[1]

                if (y1 > PLATCENTEROFFSET):
                    # reset position to boundary and reverse direction
                    offset = y1 - PLATCENTEROFFSET
                    self.vertices[:, 1] -= offset
                    self.velocity *= -1
                elif (y1 < -PLATCENTEROFFSET):
                    # reset position to boundary and reverse direction
                    offset = -PLATCENTEROFFSET - y1
                    self.vertices[:, 1] += offset
                    self.velocity *= -1

            elif(self.direction == 0):
                self.vertices[:, 0] += self.velocity * delta_time

                x1, y1, z1 = self.vertices[1]

                if (x1 > PLATCENTEROFFSET):
                    # reset position to boundary and reverse direction
                    offset = x1 - PLATCENTEROFFSET
                    self.vertices[:, 0] -= offset
                    self.velocity *= -1
                elif (x1 < -PLATCENTEROFFSET):
                    # reset position to boundary and reverse direction
                    offset = -PLATCENTEROFFSET - x1
                    self.vertices[:, 0] += offset
                    self.velocity *= -1

            self.final_vertices = self.vertices.copy()

        if(self.expanding):
            if self.expand_progress < 1.0:
                self.expand_timer += delta_time
                self.expand_progress = min(1.0, self.expand_timer / self.expand_duration)
                
                # use the existing ease_in_out function from utils.py
                smooth_t = ease_in_out(self.expand_progress)

                # instead of animating all vertices, only animate the face that's expanding
                if self.direction == 0:  # expanding width (right face)
                    if(self.expandDirection == 1): # expanding visible face
                        right_face = self.getFaces()[5] # visible right face

                        for i in right_face:
                            # only animate the x coordinate
                            self.vertices[i, 0] = self.initial_vertices[i, 0] + (self.final_vertices[i, 0] - self.initial_vertices[i, 0]) * smooth_t
                    elif(self.expandDirection == -1): # expanding non visible face
                        left_face = self.getFaces()[0] # not visible left face

                        for i in left_face:
                            # only animate the x coordinate
                            self.vertices[i, 0] = self.initial_vertices[i, 0] + (self.final_vertices[i, 0] - self.initial_vertices[i, 0]) * smooth_t

                elif self.direction == 1:  # expanding depth (left face) 
                    if(self.expandDirection == 1): # expanding visible face
                        left_face = self.getFaces()[4] # visible left face

                        for i in left_face:
                            # only animate the y coordinate
                            self.vertices[i, 1] = self.initial_vertices[i, 1] + (self.final_vertices[i, 1] - self.initial_vertices[i, 1]) * smooth_t
                    elif(self.expandDirection == -1): # expanding non visible face
                        right_face = self.getFaces()[1] # not visible right face

                        for i in right_face:
                            # only animate the y coordinate
                            self.vertices[i, 1] = self.initial_vertices[i, 1] + (self.final_vertices[i, 1] - self.initial_vertices[i, 1]) * smooth_t
                    
            else:
                # when animation completes, make sure we're exactly at final positions
                if self.direction == 0:  # width expansion
                    right_face = self.getFaces()[5] # visible right face
                    for i in right_face:
                        self.vertices[i, 0] = self.final_vertices[i, 0]
                elif self.direction == 1:  # depth expansion  
                    left_face = self.getFaces()[4] # visible left face
                    for i in left_face:
                        self.vertices[i, 1] = self.final_vertices[i, 1]
                
                self.expanding = False
                self.expand_timer = 0
                self.expand_progress = 0

    def draw(self, screen):
        self.drawFaces(screen)
        #self.drawTargetEdges(screen)

    @staticmethod
    def calculateDimensions(plat):
        """
        calculates the dimensions of the platform

        plat: the platform object
        returns a tuple of the platform's width, height, and depth
        """
        
        x0, y0, z0 = plat.final_vertices[0]
        
        # for width calculation
        x4 = plat.final_vertices[4][0]
        
        # for height calculation
        z1 = plat.final_vertices[1][2]
        
        # for depth calculation
        y2 = plat.final_vertices[2][1]

        width = abs(x4 - x0)

        height = abs(z1 - z0)

        depth = abs(y2 - y0)

        return round(width, DECIMALPLACES), round(height, DECIMALPLACES), round(depth, DECIMALPLACES)

    def expand(self):
        """
        expands one face of the platform at a time while ensuring
        the platform stays within the maximum allowed bounds
        """

        # round all vertices to the specified number of decimal places
        self.vertices = np.round(self.vertices, DECIMALPLACES)

        # calculate current dimensions
        current_width, _, current_depth = self.calculateDimensions(self)

        # set up expansion variables
        self.initial_vertices = self.vertices.copy()
        self.final_vertices = self.vertices.copy()

        self.expandDirection = 0 # 0 means no expansion, 1 means expanding a visible face, -1 means expanding an non visible face
                
        # define faces for expansion
        if self.direction == 0:  # width expansion (X axis)
            # check if it's already at maximum width
            if current_width >= MAXBASESIDE:
                self.expanding = False
                self.expandDirection = 0
                return self.width, self.depth, self.expanding
                    
            right_face = self.getFaces()[5] # visible right face
            left_face = self.getFaces()[0] # not visible left face
                        
            # check if expanding would push any vertex beyond max bounds
            proposed_expansion = self.final_vertices.copy()
            
            # try to expand the visible face first
            right_expansion_safe = True

            for index in right_face:
                if(proposed_expansion[index, 0] >= MAXBASESIDE):
                    right_expansion_safe = False
                    break
            
            if right_expansion_safe: # if expanding right face is safe, then expand it
                self.expandDirection = 1
                # apply the expansion
                for i in right_face:
                    expandAmount = self.final_vertices[i, 0] + EXPANDAMOUNT

                    if(expandAmount + EXPAND_MARGIN >= MAXBASESIDE): # if expanding would exceed bounds, then set it to the maximum
                        self.final_vertices[i, 0] = MAXBASESIDE
                    else: # otherwise, expand it
                        self.final_vertices[i, 0] = round(expandAmount, DECIMALPLACES)

            else: # if expanding right face would exceed bounds, try left face
                proposed_expansion = self.final_vertices.copy()

                left_expansion_safe = True

                for index in left_face:
                    if(proposed_expansion[index, 0] <= 0):
                        left_expansion_safe = False
                        break

                if left_expansion_safe: # if expanding left face is safe, then expand it
                    self.expandDirection = -1

                    for i in left_face:
                        expandAmount = self.final_vertices[i, 0] - EXPANDAMOUNT

                        if(expandAmount - EXPAND_MARGIN <= 0): # if expanding would exceed bounds, then set it to the minimum
                            self.final_vertices[i, 0] = 0
                        else: # otherwise, expand it
                            self.final_vertices[i, 0] = round(expandAmount, DECIMALPLACES)

                else: # if expanding right and left face would exceed bounds, then dont expand it
                    self.expanding = False
                    return self.width, self.depth, self.expanding
        
        else:  # depth expansion (Y axis)

            # check if already at maximum depth
            if current_depth >= MAXBASESIDE:
                self.expanding = False
                self.expandDirection = 0
                return self.width, self.depth, self.expanding
                
            left_face = self.getFaces()[4] # visible left face
            right_face = self.getFaces()[1] # not visible right face
                        
            # check if expanding would push any vertex beyond max bounds
            proposed_expansion = self.final_vertices.copy()

            # try to expand the visible face first
            left_expansion_safe = True

            for index in left_face:
                if(proposed_expansion[index, 1] >= MAXBASESIDE):
                    left_expansion_safe = False
                    break
            
            if left_expansion_safe: # if expanding the left face is safe, then expand it
                self.expandDirection = 1
                
                # apply the expansion
                for i in left_face:
                    expandAmount = self.final_vertices[i, 1] + EXPANDAMOUNT

                    if(expandAmount + EXPAND_MARGIN >= MAXBASESIDE): # if expanding would exceed bounds, then set it to the maximum
                        self.final_vertices[i, 1] = MAXBASESIDE
                    else: # otherwise, expand it
                        self.final_vertices[i, 1] = round(expandAmount, DECIMALPLACES)

            else: # if expanding the left face would exceed bounds, try right face

                proposed_expansion = self.final_vertices.copy()

                right_expansion_safe = True

                for index in right_face:
                    if(proposed_expansion[index, 1] <= 0):
                        right_expansion_safe = False
                        break

                if right_expansion_safe: # if expanding right face is safe, then expand it
                    self.expandDirection = -1
                    
                    # apply the expansion
                    for i in right_face:
                        expandAmount = self.final_vertices[i, 1] - EXPANDAMOUNT

                        if(expandAmount - EXPAND_MARGIN <= 0): # if expanding would exceed bounds, then set it to the minimum
                            self.final_vertices[i, 1] = 0
                        else: # otherwise, expand it
                            self.final_vertices[i, 1] = round(expandAmount, DECIMALPLACES)

                else: # if expanding right face would exceed bounds, then dont expand it
                    self.expanding = False
                    self.expandDirection = 0
                    return self.width, self.depth, self.expanding
        
        self.expanding = True
        self.expand_timer = 0
        self.expand_progress = 0
        
        # round all final vertices to the specified number of decimal places
        self.final_vertices = np.round(self.final_vertices, DECIMALPLACES)

        self.width, self.height, self.depth = self.calculateDimensions(self)
        return self.width, self.depth, self.expandDirection
