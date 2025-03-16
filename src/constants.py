from utils.system_utils import getCurrentMonitorFramerate

# constants
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 1000

FRAMERATE = getCurrentMonitorFramerate()  # get the monitor's refresh rate

DECIMALPLACES = 3  # number of decimal places to round to

SPHEIGHT = 5  # starting platform height
PHEIGHT = 2  # platform height
NSPLATS = 3  # number of starting platforms
SBASEWIDTH = 12.5  # starting base's width
SBASEDEPTH = SBASEWIDTH  # starting base's height
MAXBASESIDE = SBASEWIDTH  # maximum base side length
PLATCENTEROFFSET = 25  # platform center offset
MAXPERFECTOFFSETPERCENTAGE = 0.12  # maximum offset for a perfect placement
MINVALIDSIDE = 0.15  # minimum valid side length for a platform

PERFECT_STACKS_TO_EXPAND = 8 # number of perfect stacks to expand the platform
EXPANDAMOUNT = 2.5  # amount to expand the platform by
EXPAND_MARGIN = 1.5  # margin for expanding the platform

DEFAULTALIGNINDEX = 0  # default alignment index

COLORTHRESHOLD = 30  # color distance threshold for the gradients
BACKGROUNDLIGHTENING = 1.4  # background lightening factor
BACKGROUNDDESATURATION = 0.4  # background desaturation factor
MINCVALUE, MAXCVALUE = 25, 175  # MINIMUM AND MAXIMUM COLOR VALUES
MINNSTEPS, MAXNSTEPS = 7, 10  # MINIMUM AND MAXIMUM NUMBER OF STEPS FOR THE GRADIENT
NEWGRADIENTCOUNT = 2  # number of new gradients to create at a time

BACKGROUND_ROW_GROUP_SIZE = 5  # define the number of rows to group together
BACKGROUND_ANIMATION_CHANCE = .5  # chance of a background animation
MIN_DISTANCE, MAX_DISTANCE = 1, 3  # minimum and maximum distance between indexes of colors of the background gradient

STARTVEL = 26.5  # starting platform velocity
VELINCREMENT = 0.20  # velocity increment

ISO_MULTIPLIER = 25

NUM_NORMAL_STACK_SFX = 2  # number of normal stacking sound effects
NUM_PERFECT_STACK_SFX = 20  # number of perfect stacking sound effects
NUM_EXPAND_SFX = 2  # number of expand sound effects

ARIAL_BLACK_PATH = "assets/fonts/Arial-Black.ttf"  # font path