import random

from constants import *

class Gradient:
    def __init__(self, startingColor, gradients, fromIndex):
        self.startingColor = startingColor
        self.targetColor = self.generateTargetColor(gradients)
        self.numSteps = random.randint(MINNSTEPS, MAXNSTEPS)
        self.fromIndex = fromIndex
        self.toIndex = fromIndex + self.numSteps

    def generateTargetColor(self, gradients):
        attempts = 0
        max_attempts = 1000  # prevent an infinite loop
        while attempts < max_attempts:
            targetColor = (
                random.randint(MINCVALUE, MAXCVALUE),
                random.randint(MINCVALUE, MAXCVALUE),
                random.randint(MINCVALUE, MAXCVALUE)
            )
            if self.colorDistance(self.startingColor, targetColor) > COLORTHRESHOLD:
                if gradients:
                    last_startingColor = gradients[-1].startingColor
                    if self.colorDistance(last_startingColor, self.startingColor) > COLORTHRESHOLD:
                        return targetColor
                else:
                    return targetColor
            attempts += 1
        
        return (random.randint(MINCVALUE, MAXCVALUE),
                random.randint(MINCVALUE, MAXCVALUE),
                random.randint(MINCVALUE, MAXCVALUE))  # random fallback color
    
    @staticmethod
    def colorDistance(color1, color2):
        """
        calculates the Euclidean distance between two RGB colors
        """
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
        """
        gets the gradient color at the given index between the starting and target colors with the given number of steps
        """
        sr, sg, sb = startingColor
        tr, tg, tb = targetColor

        def getRgb(svalue, tvalue):
            diff = tvalue - svalue
            offset = diff / numSteps
            value = svalue + (offset * (index + 1))
            return max(0, min(255, int(value)))

        return (getRgb(sr, tr), getRgb(sg, tg), getRgb(sb, tb))
        
    @staticmethod
    def newGradients(gradients, numPlats):
        """
        creates new gradients with the given starting color and adds them to the list of gradients
        """
        # get the index to start the new gradients from
        fromIndex = gradients[-1].toIndex + 1 if gradients else numPlats

        # get the starting color for the new gradients from the last gradient
        startingColor = Gradient.getCurrentGradient(gradients, fromIndex - 1).targetColor

        for _ in range(0, NEWGRADIENTCOUNT):
            gradient = Gradient(startingColor, gradients, fromIndex)
            gradients.append(gradient)
            # set the starting color for the next gradient to the target color of the current gradient
            startingColor = gradient.targetColor
            fromIndex = gradient.toIndex + 1
        return gradients
    
    @staticmethod
    def getCurrentGradient(gradients, numPlats):
        """
        gets the current gradient for a given color
        """
        # find the appropriate gradient for the current platform count
        for gradient in reversed(gradients):
            if gradient.fromIndex <= numPlats <= gradient.toIndex:
                return gradient
        
        # there should always be a gradient that matches the current platform count
        return gradients[-1] if gradients else None
    
    @staticmethod
    def getCurrentColor(numPlats, gradients):

        gradient = Gradient.getCurrentGradient(gradients, numPlats)
        index = numPlats - gradient.fromIndex

        return gradient.getGradientColor(index)