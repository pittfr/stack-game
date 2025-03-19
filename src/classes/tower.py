import numpy as np

from constants import *
from utils.utils import ease_in_out

from classes.gradient import Gradient
from classes.platform import Platform

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
            platform = Platform(SBASEWIDTH, SBASEDEPTH, SPHEIGHT, 0, i, False, z_offset)
            
            platform.setup(Gradient.getGradientColorFrom((0, 0, 0), self.initialColor, self.numStartingPlats, i))
            platforms.append(platform)
        
        return platforms

    def add(self, plat): # called when the user presses the mouse button
        """
        adds a new platform to the tower and starts the animation
        
        plat: the new platform object to add
        """
        
        plat.moving = False # the platform is no longer moving
        if(not plat.expanding):
            plat.final_vertices = plat.vertices.copy()
        self.platforms.append(plat) # add the platform to the tower

        shift_amount = plat.height # the amount the platform will be shifted down

        self.initial_z_positions = [platform.vertices[:, 2].copy() for platform in self.platforms] # copy the z positions of the platforms
        self.final_z_positions = [platform.vertices[:, 2].copy() - shift_amount for platform in self.platforms] # copy the shifted z positions of the platforms

        self.t = 0 # starts the animation

    def getNumPlats(self): # returns the amount of platforms that are in the tower (including the starting ones)
        return len(self.platforms)

    def getTowers(self): # returns the array of objects
        return self.platforms

    def update(self, framerate, delta_time):
        for plat in (self.platforms):
            plat.update(delta_time)
            
        if self.t != -1: # if the animation is running
            self.t += 1 / (framerate * self.animationTime) #increment the time variable

            if self.t >= 1: # if the animation is finished
                self.t = -1 # stop the animation
                for i, platform in enumerate(self.platforms): # set the z positions of the platforms to the final z positions (to avoid floating point errors)
                    platform.vertices[:, 2] = self.final_z_positions[i]
            else: # if the animation is still running
                eased_t = ease_in_out(self.t) # get the eased time

                for i, platform in enumerate(self.platforms): # update the z positions of the platforms
                    platform.vertices[:, 2] = self.initial_z_positions[i] + (self.final_z_positions[i] - self.initial_z_positions[i]) * eased_t

            for plat in self.platforms:
                plat.final_vertices[:, 2] = plat.vertices.copy()[:, 2]

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

    def draw(self, screen):
        for plat in (self.platforms):
            plat.draw(screen)