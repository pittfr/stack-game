import pygame
import numpy as np

from constants import *
from utils import lightenColor

from classes.tower import Tower

class Platform:
    def __init__(self, width, depth, height, platVelocity, numPlats, moving, z_offset = PHEIGHT): #moving can either be true or false (false means the platform is a part of the tower)
        self.moving = moving
        self.direction = self.getDirection(numPlats) if moving else -1 # this will be either 0 or 1; 0 (moving right to left) and 1 (moving left to right); -1 means no movement
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
        self.vertices = self.defineVertices(lastPlat)
        self.colors = self.defineColors(rgb)
        self.edges = self.defineVisibleEdges()
        self.faces = self.defineFaces()

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

            pygame.draw.polygon(screen, color, iso_vertices)

    def drawEdges(self, screen):
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

            if (y1 > PLATCENTEROFFSET):
                y1 = PLATCENTEROFFSET
                self.velocity *= -1
            if (y1 < -PLATCENTEROFFSET):
                y1 = -PLATCENTEROFFSET
                self.velocity *= -1

        elif(self.direction == 0):
            self.vertices[:, 0] += self.velocity * delta_time

            x1, y1, z1 = self.vertices[1]

            if (x1 > PLATCENTEROFFSET):
                x1 = PLATCENTEROFFSET
                self.velocity *= -1
            if (x1 < -PLATCENTEROFFSET):
                x1 = -PLATCENTEROFFSET
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