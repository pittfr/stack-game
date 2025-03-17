# animations

def ease_in_out(t): # easing function for the animations (t is the time variable)
        """
        easing function for the animation
        
        t: time variable
        returns eased time value
        """
        return 1 - (1 - t)**3

#colors

def lightenColor(rgb, factor=1.2):
    """
    lightens the given RGB color by a specified factor
    
    rgb: tuple of (r, g, b) values
    factor: lightening factor (should be > 1.0)
    returns a tuple of lightened (r, g, b) values
    """
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)

def darkenColor(rgb, factor=0.8):
    """
    darkens the given RGB color by a specified factor
    
    rgb: tuple of (r, g, b) values
    factor: darkening factor (should be < 1.0)
    returns a tuple of darkened (r, g, b) values
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