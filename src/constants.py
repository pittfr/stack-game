from utils.system_utils import getCurrentMonitorFramerate, count_sounds_in_directory

# constants
WINDOW_WIDTH = 650
WINDOW_HEIGHT = 1000

FRAMERATE = getCurrentMonitorFramerate()  # get the monitor's refresh rate

DECIMALPLACES = 3  # number of decimal places to round to

SPHEIGHT = 5  # starting platform height
PHEIGHT = 1.5  # platform height
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

NUM_NORMAL_STACK_SFX = count_sounds_in_directory("assets/SFX/normalStack")  # number of normal stacking sound effects
NUM_PERFECT_STACK_SFX = count_sounds_in_directory("assets/SFX/perfectStack")  # number of perfect stacking sound effects
NUM_EXPAND_SFX = count_sounds_in_directory("assets/SFX/expandPlatform")  # number of expand sound effects
NUM_PAUSE_GAME_SFX = count_sounds_in_directory("assets/SFX/pauseGame")  # number of pause game sound effects
NUM_RESUME_GAME_SFX = count_sounds_in_directory("assets/SFX/resumeGame")  # number of resume game sound effects
NUM_BUTTON_CLICK_SFX = count_sounds_in_directory("assets/SFX/buttonClick")  # number of button click sound effects

# fonts
LIGHT_FONT = "assets/fonts/Cresta-Light.ttf"
REGULAR_FONT = "assets/fonts/Cresta-Regular.ttf"
SCORE_FONT = "assets/fonts/Arial-Black.ttf"
HAIRLINE_FONT = "assets/fonts/Cresta-Hairline.ttf"