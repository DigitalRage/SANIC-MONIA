import pygame
import os
import glob
import controller

from TerminalRenderer import TerminalRenderer

renderer = TerminalRenderer()
renderer.patch_pygame_display()
renderer.scale_factor(1)
renderer.enter()


# --- Music ---
controller_on=True
try:
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
    os.chdir(PROJECT_ROOT)
except Exception as e:
    print(f"Error changing directory to project root: {e}")
try:
    pygame.init()
except Exception as e:
    print(f"Error initializing pygame: {e}")
try:
    pygame.mixer.init()
except Exception as e:
    print(f"Error initializing mixer: {e}")
joysticks=[]
try:
    pygame.mixer.music.load("Music cuz why not/Joyful Tone.mp3")  # Replace with your file path
    pygame.mixer.music.play()
except Exception as e:
    print(f"Error loading music: {e}")
try:
    controller.init()
except Exception as e:
    print(f"Error loading music: {e}")
# --- Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(PROJECT_ROOT)
pygame.init()
windowed_size = (800, 600)
screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
pygame.display.set_caption("Tile Grid with Ground Collision")
clock = pygame.time.Clock()
image_cache = {}
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))  # directory of the current script
all_entities = []
def get_files(file_name):
    return os.path.join(file_name)

def get_image(file_name):
    full_path = os.path.join(PROJECT_ROOT, 'Images', file_name)

    if full_path not in image_cache:
        if not os.path.exists(full_path):
            print(f"File not found: {full_path}")
            return pygame.Surface((50, 50), pygame.SRCALPHA)
        try:
            image_cache[full_path] = pygame.image.load(full_path).convert_alpha()
        except Exception as e:
            print(f"Error loading image {full_path}: {e}")
            return pygame.Surface((50, 50), pygame.SRCALPHA)
    return image_cache[full_path]

# Example usage:
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Najjar's Comet ")

# Load images using the caching function
try:
    player_image = get_image("player.png")
except Exception:
    print("player.png not found, using placeholder.")
    player_image = pygame.Surface((50, 50), pygame.SRCALPHA)
    player_image.fill((255, 0, 0))  # Red placeholder

try:
    background_image = get_image("background.jpg")
except Exception:
    print("background.jpg not found, using placeholder.")
    background_image = pygame.Surface((800, 600), pygame.SRCALPHA)
    background_image.fill((0, 0, 255))  # Blue placeholder

# --- Load and scale tile images ---
def load_tile(filename, size, door_destonation=None):
    # Pass the relative path from the working directory to get_image
    path = os.path.join(filename)
    image = get_image(path) # get_image now handles joining with SCRIPT_DIR
    return pygame.transform.scale(image, size)
    # The try/except is now handled inside get_image

def load_ground_any(size, preferred="ground_greye.png"):
    pref_path = os.path.join(preferred)
    if os.path.exists(pref_path):
        return load_tile(preferred, size)

    # Search for any ground_*.png
    candidates = glob.glob(os.path.join('sprites', 'ground_*.png'))
    candidates.sort()
    if candidates:
        try:
            img = pygame.image.load(candidates[0]).convert_alpha()
            return pygame.transform.scale(img, size)
        except Exception as e:
            print(f"Error loading {candidates[0]}: {e}")

    # Fallback placeholder
    surf = pygame.Surface(size, pygame.SRCALPHA)
    surf.fill((120, 80, 40))
    pygame.draw.rect(surf, (80, 50, 20), surf.get_rect(), 2)
    return surf

# The rest of your code remains unchanged...
    
# --- Dynamic tile sizing ---
def get_tile_sizes(screen_size):
    sw, _ = screen_size
    small = int(sw * 0.05)
    large = int(sw * 0.10)
    return (small, small), (large, large)

# --- Tile class with mask ---
class Tile:
    def __init__(self, image, x, y):
        self.image = image
        self.rect = image.get_rect(topleft=(x, y))
        self.mask = pygame.mask.from_surface(image)

    def draw(self, surface, offset):
        # offset is a Vector2 (camera offset). Compute integer screen position.
        pos = (int(self.rect.x + offset.x), int(self.rect.y + offset.y))
        surface.blit(self.image, pos)

    def collides_with(self, other_rect, other_mask, offset):
        # Compute other mask position relative to this tile's mask.
        # Both self.rect are world coords; other_rect is in screen coords, so use offset (camera) to convert.
        # self_screen = (self.rect.x + offset.x, self.rect.y + offset.y)
        # other_screen = (other_rect.x, other_rect.y)
        # relative = (other_screen.x - self_screen.x, other_screen.y - self_screen.y)
        rel_x = int(other_rect.x - (self.rect.x + offset.x))
        rel_y = int(other_rect.y - (self.rect.y + offset.y))
        return self.mask.overlap(other_mask, (rel_x, rel_y)) is not None

# --- Grid overlay ---
def draw_grid(surface, rows, cols, cell_size, offset):
    for r in range(rows + 1):
        pygame.draw.line(surface, (50, 50, 50),
                        (offset.x, offset.y + r * cell_size),
                        (offset.x + cols * cell_size, offset.y + r * cell_size))
    for c in range(cols + 1):
        pygame.draw.line(surface, (50, 50, 50),
                        (offset.x + c * cell_size, offset.y),
                        (offset.x + c * cell_size, offset.y + rows * cell_size))

# --- Helper for large tile placement ---
def is_top_left_of_large_tile(row, col, cell, tile_map):
    # Safely check neighbors when rows may have different lengths.
    above_different = True
    if row > 0:
        if col < len(tile_map[row - 1]):
            above_different = (tile_map[row - 1][col] != cell)
        else:
            above_different = True

    left_different = True
    if col > 0:
        if col - 1 < len(tile_map[row]):
            left_different = (tile_map[row][col - 1] != cell)
        else:
            left_different = True

    return above_different and left_different

# --- Build tile objects from grid ---
def build_tiles(tile_map, small_size):
    tiles = []
    for row in range(len(tile_map)):
        for col in range(len(tile_map[row])):
            cell = tile_map[row][col]
            if cell is None:
                continue
            w, h = cell.get_size()
            x = col * small_size[0]
            y = row * small_size[0]
            if w > small_size[0] or h > small_size[1]:
                if is_top_left_of_large_tile(row, col, cell, tile_map):
                    tiles.append(Tile(cell, x, y))
            else:
                tiles.append(Tile(cell, x, y))
    return tiles

# --- Initial sizes and assets ---
small_size, large_size = get_tile_sizes(windowed_size)
extra_small_size = (small_size[0]//2, small_size[1]//2)
extra_large_size = (large_size[0]*2, large_size[1]*2)
# --- Key tokens so templates can use unquoted identifiers like AA, BA, FG ---
class Key:
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return f"Key({self.name!r})"

AA = Key('AA')
BA = Key('BA')
BB = Key('BB')
FG = Key('FG')
SP = Key('SP')  # spawnpoint
# additional ground tile keys (two-letter tokens starting with F)
FA = Key('FA')  # center.png
FB = Key('FB')  # curve_in_bl.png
FC = Key('FC')  # curve_in_br.png
FD = Key('FD')  # curve_in_tl.png
FE = Key('FE')  # curve_in_tr.png
FF = Key('FF')  # curve_out_bl.png
FH = Key('FH')  # curve_out_br.png (note: original name had a typo 'curve_ou_br')
FI = Key('FI')  # roof.png
FJ = Key('FJ')  # wall_left_1.png
FK = Key('FK')  # wall_left_2.png
FL = Key('FL')  # wall_right_1.png
FM = Key('FM')  # wall_right_2.png
DR = Key('DR')  # door right
DL = Key('DL')  # door left
DU = Key('DU')  # door up
DD = Key('DD')  # door down
PW1 = Key('PW1')  # powerup1
PW2 = Key('PW2')  # powerup2
PW3 = Key('PW3')  # powerup3
PW4 = Key('PW4')  # powerup4
PW5 = Key('PW5')  # powerup5
PW6 = Key('PW6')  # powerup6
PW7 = Key('PW7')  # powerup7
BS1 = Key('BS1')  # boss1
BS2 = Key('BS2')  # boss2
BS3 = Key('BS3')  # boss3
BS4 = Key('BS4')  # boss4
BS5 = Key('BS5')  # boss5
BS6 = Key('BS6')  # boss6
BS7 = Key('BS7')  # boss7
EN1 = Key('EN1')  # enemy1
EN2 = Key('EN2')  # enemy2
EN3 = Key('EN3')  # enemy3
EN4 = Key('EN4')  # enemy4
EN5 = Key('EN5')  # enemy5
EN6 = Key('EN6')  # enemy6
EN7 = Key('EN7')  # enemy7
EN8 = Key('EN8')  # enemy8
EN9 = Key('EN9')  # enemy9
EN10 = Key('EN10')  # enemy10
EN11 = Key('EN11')  # enemy11
EN12 = Key('EN12')  # enemy12
EN13 = Key('EN13')  # enemy13
EN14 = Key('EN14')  # enemy14
EN15 = Key('EN15')  # enemy15
EN16 = Key('EN16')  # enemy16
EN17 = Key('EN17')  # enemy17
EN18 = Key('EN18')  # enemy18
EN19 = Key('EN19')  # enemy19
EN20 = Key('EN20')  # enemy20
EN21 = Key('EN21')  # enemy21
EN22 = Key('EN22')  # enemy22
EN23 = Key('EN23')  # enemy23
EN24 = Key('EN24')  # enemy24
EN25 = Key('EN25')  # enemy25
EN26 = Key('EN26')  # enemy26
EN27 = Key('EN27')  # enemy27
EN28 = Key('EN28')  # enemy28
EN29 = Key('EN29')  # enemy29
EN30 = Key('EN30')  # enemy30
#we may need more than 30 enemies
WT = Key('WT')  # water tile
LT = Key('LT')  # lava tile
WTT = Key('WTT')  # water tile top
LTT = Key('LTT')  # lava tile top
CRR = Key('CRR')  # cristal tile red
CRRL = Key('CRRL')  # cristal tile red large
CRO = Key('CRO')  # cristal tile orange
CROL = Key('CROL')  # cristal tile orange large
CRG = Key('CRG')  # cristal tile green
CRGL = Key('CRGL')  # cristal tile green large
CRT = Key('CRT') # cristal tile teal
CRTL = Key('CRTL') #cristal tile teal large
CRB = Key('CRB')  # cristal tile blue
CRBL = Key('CRBL')  # cristal tile blue large
CRDB = Key('CRDB')  # cristal tile dark blue
CRDBL = Key('CRDBL')  # cristal tile dark blue large
CRPU = Key('CRPU')  # cristal tile purple
CRPUL = Key('CRPUL')  # cristal tile purple large
CRP = Key('CRP') # cristal tile pink
CRPL = Key('CRPL') #cristal tile pink large
CRS = Key('CRS') # cristal tile silver
CRSL = Key('CRSL') #cristal tile silver large
NA = None

# Load surfaces into a mapping so templates that use Key(...) can be resolved.
def load_tile_surfaces(extra_small_size,small_size, large_size,extra_large_size,door_destonation=None):
    # Create spawnpoint placeholder
    spawn_surf = pygame.Surface(small_size, pygame.SRCALPHA)
    spawn_surf.fill((0, 255, 0, 128))  # Semi-transparent green
    pygame.draw.rect(spawn_surf, (0, 255, 0), spawn_surf.get_rect(), 2)
    pygame.draw.circle(spawn_surf, (0, 255, 0), (small_size[0] // 2, small_size[1] // 2), min(small_size) // 4)
    
    return {
        'AA': load_tile("Basic Tile.png", small_size),
        'BA': load_tile("Basic Tile Claw Mark.png", large_size),
        'BB': load_tile("Basic Tile Hole.png", large_size),
        'SP': spawn_surf,  # Add spawnpoint tile
        'FG': load_tile("ground_grey.png", small_size),
    # ground-specific tiles (two-letter F* keys)
        'FA': load_tile("center.png", small_size),
        'FB': load_tile("curve_in_bl.png", small_size),
        'FC': load_tile("curve_in_br.png", small_size),
        'FD': load_tile("curve_in_tl.png", small_size),
        'FE': load_tile("curve_in_tr.png", small_size),
        'FF': load_tile("curve_out_bl.png", small_size),
        'FH': load_tile("curve_out_br.png", small_size),
        'FI': load_tile("roof.png", small_size),
        'FJ': load_tile("wall_left_1.png", small_size),
        'FK': load_tile("wall_left_2.png", small_size),
        'FL': load_tile("wall_right_1.png", small_size),
        'FM': load_tile("wall_right_2.png", small_size),
        'DR': load_tile("door_right.png", large_size,door_destonation),
        'DL': load_tile("door_left.png", large_size,door_destonation),
        'DU': load_tile("door_up.png", large_size,door_destonation),
        'DD': load_tile("door_down.png", large_size,door_destonation),
        'PW1': load_tile("powerup1.png", small_size),
        'PW2': load_tile("powerup2.png", small_size),
        'PW3': load_tile("powerup3.png", small_size),
        'PW4': load_tile("powerup4.png", small_size),
        'PW5': load_tile("powerup5.png", small_size),
        'PW6': load_tile("powerup6.png", small_size),
        'PW7': load_tile("powerup7.png", small_size),
        'BS1': load_tile("boss1.png", extra_large_size),
        'BS2': load_tile("boss2.png", extra_large_size),
        'BS3': load_tile("boss3.png", extra_large_size),
        'BS4': load_tile("boss4.png", extra_large_size),
        'BS5': load_tile("boss5.png", extra_large_size),
        'BS6': load_tile("boss6.png", extra_large_size),
        'BS7': load_tile("boss7.png", extra_large_size),
        'EN1': load_tile("enemy1.png", small_size),
        'EN2': load_tile("enemy2.png", small_size),
        'EN3': load_tile("enemy3.png", small_size),
        'EN4': load_tile("enemy4.png", small_size),
        'EN5': load_tile("enemy5.png", extra_small_size),
        'EN6': load_tile("enemy6.png", extra_large_size),
        'EN7': load_tile("enemy7.png", large_size),
        'EN8': load_tile("enemy8.png", small_size),
        'EN9': load_tile("enemy9.png", small_size),
        'EN10': load_tile("enemy10.png", small_size),
        'EN11': load_tile("enemy11.png", small_size),
        'EN12': load_tile("enemy12.png", small_size),
        'EN13': load_tile("enemy13.png", small_size),
        'EN14': load_tile("enemy14.png", small_size),
        'EN15': load_tile("enemy15.png", small_size),
        'EN16': load_tile("enemy16.png", small_size),
        'EN17': load_tile("enemy17.png", small_size),
        'EN18': load_tile("enemy18.png", small_size),
        'EN19': load_tile("enemy19.png", small_size),
        'EN20': load_tile("enemy20.png", small_size),
        'EN21': load_tile("enemy21.png", small_size),
        'EN22': load_tile("enemy22.png", small_size),
        'EN23': load_tile("enemy23.png", small_size),
        'EN24': load_tile("enemy24.png", small_size),
        'EN25': load_tile("enemy25.png", small_size),
        'EN26': load_tile("enemy26.png", small_size),
        'EN27': load_tile("enemy27.png", small_size),
        'EN28': load_tile("enemy28.png", small_size),
        'EN29': load_tile("enemy29.png", small_size),
        'EN30': load_tile("enemy30.png", small_size),
        'WT': load_tile("water_tile.png", small_size),
        'LT': load_tile("lava_tile.png", small_size),
        'WTT': load_tile("water_tile_top.png", small_size),
        'LTT': load_tile("lava_tile_top.png", small_size),
        
    }

assets = load_tile_surfaces(extra_small_size,small_size, large_size,extra_large_size)

# --- Map templates (single source of truth) ---
# Use short keys in templates; we'll resolve them to loaded surfaces with resolve_map().
background_template1 = [
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, BA, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, NA, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, BB, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, NA, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
]

ground_template1 = [
    [FA, FA, FI, FI, FI, FI, FI, FI, FI, FI, FD, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FA, FD, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FK, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FK, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FK, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FA, FB, NA, NA, NA, FH, FG, FF, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FA, FA, FG, FG, FG, FA, FA, FA, FG, FG, FG, FG, FG, FG, FG, FG, FG, FG, FG, FG],
]

background_template2 = [
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, BA, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, NA, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, BB, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, NA, NA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
    [AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA, AA],
]

ground_template2 = [
    [FA, FA, FI, FI, FI, FI, FI, FI, FI, FI, FD, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FA, FD, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FK, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FK, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FK, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FJ, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FA, FB, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA, NA],
    [FA, FA, FG, FG, FG, FA, FA, FA, FG, FG, FG, FG, FG, FG, FG, FG, FG, FG, FG, FG],
]

# (ground_template1 is the primary ground template variable)

# expose the primary templates under the names used throughout the code
# (some parts of the script reference `background_template` / `ground_template`
#  while the literal declarations were named background_template1 / ground_template1)
background_template = background_template1
ground_template = ground_template1

def resolve_map(template, key_map):
        #Return a new map where keys in the template are replaced by surfaces from key_map.

        #template: 2D list with strings (keys) or None
        #key_map: dict mapping keys to pygame.Surface
    
    out = []
    for row in template:
        out_row = []
        for cell in row:
            # allow templates to contain Key tokens, strings, or already-resolved Surfaces
            if cell is None:
                out_row.append(None)
            elif isinstance(cell, str):
                out_row.append(key_map.get(cell))
            elif hasattr(cell, 'name'):
                # Key-like object
                # Special-case spawnpoint token 'SP': show it while editing (so user can see/place it),
                # but make it invisible during play by resolving to None.
                try:
                    is_editor = bool(editor_mode)
                except NameError:
                    # If editor_mode isn't defined yet, default to False (play behavior)
                    is_editor = False

                if cell.name == 'SP':
                    out_row.append(key_map.get('SP') if is_editor else None)
                else:
                    out_row.append(key_map.get(cell.name))
            else:
                # assume this is already a Surface or similar
                out_row.append(cell)
        out.append(out_row)
    return out

# resolve initial maps using loaded assets
background_map = resolve_map(background_template, assets)
ground_map = resolve_map(ground_template, assets)

background_tiles = build_tiles(background_map, small_size)
ground_tiles = build_tiles(ground_map, small_size)

# --- Multi-room support ---
# Initialize rooms with matching numbered templates
rooms = [
    {
        'background_template': background_template1,
        'ground_template': ground_template1,
        'name': 'Room 1',
    },
    {
        'background_template': background_template2,
        'ground_template': ground_template2,
        'name': 'Room 2',
    }
]

current_room = 0

def rebuild_maps_and_tiles():
    global background_map, ground_map, background_tiles, ground_tiles
    background_map = resolve_map(background_template, assets)
    ground_map = resolve_map(ground_template, assets)
    background_tiles = build_tiles(background_map, small_size)
    ground_tiles = build_tiles(ground_map, small_size)
    # persist current templates into the rooms array so room switching keeps edits
    try:
        rooms[current_room]['background_template'] = background_template
        rooms[current_room]['ground_template'] = ground_template
    except Exception:
        pass

def load_room(idx: int):
    """Switch to room `idx` (wraps)."""
    global current_room, background_template, ground_template
    current_room = idx % len(rooms)
    
    # Load the room templates
    background_template = rooms[current_room]['background_template']
    ground_template = rooms[current_room]['ground_template']
    
    # Make sure to rebuild maps and tiles
    rebuild_maps_and_tiles()
    
    print(f"Loaded Room {current_room + 1}")


# --- Template resize helpers -------------------------------------------------
def normalize_templates():
    """Ensure both background_template and ground_template have the same column counts
    and that each row in a template has a consistent length by padding with NA.
    """
    global background_template, ground_template
    # determine max columns across both templates
    bg_cols = max((len(r) for r in background_template), default=0)
    gd_cols = max((len(r) for r in ground_template), default=0)
    max_cols = max(bg_cols, gd_cols, 1)

    def pad_template(tpl):
        for i in range(len(tpl)):
            if len(tpl[i]) < max_cols:
                tpl[i].extend([NA] * (max_cols - len(tpl[i])))

    pad_template(background_template)
    pad_template(ground_template)


def add_column_left():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    normalize_templates()
    for row in background_template:
        row.insert(0, NA)
    for row in ground_template:
        row.insert(0, NA)
    rebuild_maps_and_tiles()
    print('Added column on left')


def remove_column_left():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    normalize_templates()
    # only remove if more than 1 column
    cols = max(len(background_template[0]) if background_template else 0,
            len(ground_template[0]) if ground_template else 0)
    if cols <= 1:
        print('Cannot remove left column: minimum size reached')
        return
    for row in background_template:
        if row:
            row.pop(0)
    for row in ground_template:
        if row:
            row.pop(0)
    rebuild_maps_and_tiles()
    print('Removed column on left')


def add_column_right():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    normalize_templates()
    for row in background_template:
        row.append(NA)
    for row in ground_template:
        row.append(NA)
    rebuild_maps_and_tiles()
    print('Added column on right')


def remove_column_right():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    normalize_templates()
    cols = max(len(background_template[0]) if background_template else 0,
            len(ground_template[0]) if ground_template else 0)
    if cols <= 1:
        print('Cannot remove right column: minimum size reached')
        return
    for row in background_template:
        if row:
            row.pop()
    for row in ground_template:
        if row:
            row.pop()
    rebuild_maps_and_tiles()
    print('Removed column on right')


def add_row_top():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    normalize_templates()
    cols = max(len(background_template[0]) if background_template else 0,
            len(ground_template[0]) if ground_template else 0)
    new_bg = [NA] * cols
    new_gd = [NA] * cols
    background_template.insert(0, list(new_bg))
    ground_template.insert(0, list(new_gd))
    rebuild_maps_and_tiles()
    print('Added row on top')


def remove_row_top():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    if len(background_template) <= 1 and len(ground_template) <= 1:
        print('Cannot remove top row: minimum size reached')
        return
    if background_template:
        background_template.pop(0)
    if ground_template:
        ground_template.pop(0)
    normalize_templates()
    rebuild_maps_and_tiles()
    print('Removed row on top')


def add_row_bottom():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    cols = max(len(background_template[0]) if background_template else 0,
            len(ground_template[0]) if ground_template else 0)
    new_bg = [NA] * cols
    new_gd = [NA] * cols
    background_template.append(list(new_bg))
    ground_template.append(list(new_gd))
    rebuild_maps_and_tiles()
    print('Added row on bottom')


def remove_row_bottom():
    global background_template, ground_template,preveus_state
    preveus_state={'background_template':background_template,'ground_template':ground_template}
    if len(background_template) <= 1 and len(ground_template) <= 1:
        print('Cannot remove bottom row: minimum size reached')
        return
    if background_template:
        background_template.pop()
    if ground_template:
        ground_template.pop()
    normalize_templates()
    rebuild_maps_and_tiles()
    print('Removed row on bottom')
def control_z_function(preveus_state,current_state):
    global background_template, ground_template
    background_template=preveus_state['background_template']
    
    ground_template=current_state['ground_template']
    rebuild_maps_and_tiles()
    

def next_room():
    load_room(current_room + 1)

def prev_room():
    load_room(current_room - 1)



def save_templates_to_file():
    """Serialize grid_template and ground_template back into this python file.
    This will overwrite the list literals for `grid_template` and `ground_template` in-place.
    A backup of the original file will be written with a .bak suffix.
    """
    import io, time
    path = os.path.abspath(__file__)

    def row_to_code(row):
        parts = []
        for cell in row:
            if cell is None:
                parts.append('NA')
            elif hasattr(cell, 'name'):
                parts.append(cell.name)
            else:
                # Fallback: try to find key name in assets by identity
                found = None
                for k, v in assets.items():
                    if v is cell:
                        found = k
                        break
                parts.append(found or 'NA')
        return '    [' + ', '.join(parts) + '],\n'

    def template_to_block(template):
        s = '[\n'
        for row in template:
            s += row_to_code(row)
        s += ']'
        return s

    grid_code = template_to_block(background_template)
    fg_code = template_to_block(ground_template)

    with open(path, 'r', encoding='utf-8') as f:
        src = f.read()

    def replace_var(src, varname, code_block):
        # find varname = and the following '[' start
        marker = varname + ' ='
        idx = src.find(marker)
        if idx == -1:
            return src
        start = src.find('[', idx)
        if start == -1:
            return src
        i = start
        depth = 0
        end = None
        while i < len(src):
            if src[i] == '[':
                depth += 1
            elif src[i] == ']':
                depth -= 1
                if depth == 0:
                    end = i
                    break
            i += 1
        if end is None:
            return src
        # keep same indentation as original by inserting newline where start was
        new_src = src[:start] + code_block + src[end+1:]
        return new_src

    new_src = replace_var(src, 'background_template', grid_code)
    new_src = replace_var(new_src, 'ground_template', fg_code)

    # write backup then overwrite
    bak_path = path + '.bak'
    with open(bak_path, 'w', encoding='utf-8') as f:
        f.write(src)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_src)


def template_to_names(template):
    """Convert template of Keys/NA into list of token-name lists for JSON serialization."""
    out = []
    for row in template:
        out_row = []
        for cell in row:
            if cell is None:
                out_row.append('NA')
            elif hasattr(cell, 'name'):
                out_row.append(cell.name)
            else:
                # try to find name by identity in assets
                found = None
                for k, v in assets.items():
                    if v is cell:
                        found = k
                        break
                out_row.append(found or 'NA')
        out.append(out_row)
    return out


def names_to_template(names):
    """Convert list-of-name lists back into template using Key tokens or NA."""
    out = []
    for row in names:
        out_row = []
        for name in row:
            if name is None or name == 'NA':
                out_row.append(NA)
            else:
                token = globals().get(name)
                out_row.append(token if token is not None else NA)
        out.append(out_row)
    return out


def save_rooms_to_json(path=None):
    import json
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rooms.json')
    payload = []
    for r in rooms:
        payload.append({
            'name': r.get('name', ''),
            'background': template_to_names(r.get('background_template', [])),
            'ground': template_to_names(r.get('ground_template', [])),
        })
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)


def load_rooms_from_json(path=None):
    import json
    global rooms
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rooms.json')
    if not os.path.exists(path):
        return False
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    new_rooms = []
    for idx, r in enumerate(data):
        bg = names_to_template(r.get('background', []))
        gd = names_to_template(r.get('ground', []))
        new_rooms.append({
            'name': r.get('name', f'Room {idx}'),
            'background_template': bg,
            'ground_template': gd,
        })
    if new_rooms:
        # replace rooms list in-place to preserve reference
        rooms.clear()
        rooms.extend(new_rooms)
        return True
    return False


# --- Player setup ---
# Player is two small tiles tall and one wide
player_size = (small_size[0], small_size[1] * 2)
try:
    player_image = load_tile('test_player.png', player_size)
except Exception:
    # fallback placeholder
    player_image = pygame.Surface(player_size, pygame.SRCALPHA)
    player_image.fill((200, 180, 120))
    pygame.draw.rect(player_image, (120, 90, 60), player_image.get_rect(), 2)

player_rect = player_image.get_rect(topleft=(100, 100))
player_mask = pygame.mask.from_surface(player_image)

# Movement state
vel = pygame.Vector2(0, 0)
speed = 4
gravity = .9
jump_speed = -16
on_ground = False
sensitivity=.3

def resolve_player_collisions(dx, dy):
    """Move player by dx,dy and resolve collisions with ground_tiles using masks.
    This performs AABB checks first for speed, then mask.overlap to confirm pixel collision.
    Returns tuple (landed:boolean) indicating if player is standing on something after vertical move.
    """
    landed = False

    # Horizontal move: move then resolve pixel-perfect using a minimum translation search
    if dx != 0:
        player_rect.x += dx
        safety = 0
        while True:
            overlapped_any = False
            # find first overlapping tile
            for tile in ground_tiles:
                if player_rect.colliderect(tile.rect):
                    orig_offset = (tile.rect.x - player_rect.x, tile.rect.y - player_rect.y)
                    if player_mask.overlap(tile.mask, orig_offset):
                        overlapped_any = True

                        # Attempt a small step-up (auto-step) when on the ground to climb low obstacles
                        stepped = False
                        try:
                            ground_state = on_ground
                        except NameError:
                            ground_state = False
                        if ground_state:
                            max_step = max(1, small_size[1] // 3)
                            for s in range(1, max_step + 1):
                                # try moving player up by s pixels
                                player_rect.y -= s
                                new_offset = (tile.rect.x - player_rect.x, tile.rect.y - player_rect.y)
                                if player_mask.overlap(tile.mask, new_offset) is None:
                                    # make sure stepping up doesn't immediately collide with other tiles
                                    conflict = False
                                    for other in ground_tiles:
                                        if other is tile:
                                            continue
                                        if player_rect.colliderect(other.rect):
                                            other_off = (other.rect.x - player_rect.x, other.rect.y - player_rect.y)
                                            if player_mask.overlap(other.mask, other_off):
                                                conflict = True
                                                break
                                    if not conflict:
                                        # successful step up
                                        stepped = True
                                        landed = True
                                        break
                                # restore and try next
                                player_rect.y += s

                        # compute overlap rect to bound horizontal search
                        overlap_rect = player_rect.clip(tile.rect)
                        max_dx = overlap_rect.width

                        best = None
                        # search horizontal translations (left/right)
                        for n in range(1, max(1, max_dx) + 1):
                            # move left by n -> dx = -n
                            new_offset_left = (orig_offset[0] + n, orig_offset[1])
                            if player_mask.overlap(tile.mask, new_offset_left) is None:
                                cand = (-n, 0)
                                best = cand
                                break
                            # move right by n -> dx = +n
                            new_offset_right = (orig_offset[0] - n, orig_offset[1])
                            if player_mask.overlap(tile.mask, new_offset_right) is None:
                                cand = (n, 0)
                                best = cand
                                break

                        if best is not None:
                            # apply translation and restart checks
                            player_rect.x += best[0]
                        else:
                            # fallback: small step back depending on original dx sign
                            player_rect.x -= 1 if dx > 0 else -1
                        break
            safety += 1
            if not overlapped_any or safety > abs(dx) + 1024:
                break

    # Vertical move: minimum translation search along Y
    if dy != 0:
        player_rect.y += dy
        safety = 0
        while True:
            overlapped_any = False
            for tile in ground_tiles:
                if player_rect.colliderect(tile.rect):
                    orig_offset = (tile.rect.x - player_rect.x, tile.rect.y - player_rect.y)
                    if player_mask.overlap(tile.mask, orig_offset):
                        overlapped_any = True
                        overlap_rect = player_rect.clip(tile.rect)
                        max_dy = overlap_rect.height

                        best = None
                        for n in range(1, max(1, max_dy) + 1):
                            # move up by n -> dy = -n
                            new_offset_up = (orig_offset[0], orig_offset[1] + n)
                            if player_mask.overlap(tile.mask, new_offset_up) is None:
                                best = (0, -n)
                                break
                            # move down by n -> dy = +n
                            new_offset_down = (orig_offset[0], orig_offset[1] - n)
                            if player_mask.overlap(tile.mask, new_offset_down) is None:
                                best = (0, n)
                                break

                        if best is not None:
                            player_rect.y += best[1]
                        else:
                            player_rect.y -= 1 if dy > 0 else -1
                        break
            safety += 1
            if not overlapped_any or safety > abs(dy) + 1024:
                break

        # After vertical resolution, determine landing / head-hit
        if dy > 0:
            player_rect.y += 1
            for tile in ground_tiles:
                if player_rect.colliderect(tile.rect):
                    offset = (tile.rect.x - player_rect.x, tile.rect.y - player_rect.y)
                    if player_mask.overlap(tile.mask, offset):
                        landed = True
                        vel.y = 0
                        break
            player_rect.y -= 1
        elif dy < 0:
            player_rect.y -= 1
            for tile in ground_tiles:
                if player_rect.colliderect(tile.rect):
                    offset = (tile.rect.x - player_rect.x, tile.rect.y - player_rect.y)
                    if player_mask.overlap(tile.mask, offset):
                        vel.y = 0
                        break
            player_rect.y += 1

    return landed

class Entity:
    """
    the class for entetys
    """
    def __init__(self, xpos, ypos, room, typee, file_path, interactions, item_type, atack_pattern, static, colishon_with):
        self.xpos = xpos
        self.ypos = ypos
        self.room = room
        self.typee = typee
        self.image_path = file_path
        self.interactions = interactions
        self.item_type = item_type
        self.atack_pattern = atack_pattern
        self.static = static
        self.colishon_with = colishon_with#dict
        self.alive = True
        try:
            self.image = pygame.image.load(file_path).convert_alpha()
            self.rect = self.image.get_rect(topleft=(self.xpos, self.ypos))
            self.mask = pygame.mask.from_surface(self.image)
        except pygame.error as e:
            print(f"Error loading image at {file_path}: {e}")
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)#Create a dummy surface
            self.rect = self.image.get_rect(topleft=(self.xpos, self.ypos))
            self.mask = pygame.mask.from_surface(self.image)

    def update_position(self, x, y):
        """Helper function to move the entity and its rect."""
        if self.alive: # Only update if the entity is alive
            self.xpos = x
            self.ypos = y
            self.rect.topleft = (x, y)

    def colishon(self, other_entity):
        """
        Checks for pixel-perfect collision with another entity.
        
        :param other_entity: The other Entity object to check collision against.
        :return: True if a collision occurred, False otherwise.
        """
        # Only check collision if both entities are alive
        if not self.alive or not other_entity.alive:
            return False

        # 1. Calculate the offset between the two entities
        offset_x = other_entity.rect.left - self.rect.left
        offset_y = other_entity.rect.top - self.rect.top

        # 2. Use the mask's 'overlap' method
        overlap_point = self.mask.overlap(other_entity.mask, (offset_x, offset_y))

        if overlap_point:
            return True
        else:
            return False
    def on_colishon(self, other_entity, overlap_point,func_to_run):
        """
        Defines the consequences of a collision.
        """
        func_to_run(other_entity,overlap_point)
                
    def kill(self):
        self.alive=False
        del self
        
# --- Main loop ---
camera_offset = pygame.Vector2(0, 0)
scroll_speed = 10
show_grid = True
fullscreen = False
camera_follows = True
running = True
# Editor state
editor_mode = False
editing_ground = False  # if True edit ground_template, else background_template
# order of editable keys (two-letter names) for selection with + / -
key_order = ['AA', 'BA', 'BB', 'SP', 'FG', 'FA', 'FB', 'FC', 'FD', 'FE', 'FF', 'FH', 'FI', 'FJ', 'FK', 'FL', 'FM','DR','DL','DU','DD','PW1','PW2','PW3','PW4','PW5','PW6','PW7','BS1','BS2','BS3','BS4','BS5','BS6','BS7','EN1','EN2','EN3','EN4','EN5','EN6','EN7','EN8','EN9','EN10','EN11','EN12','EN13','EN14','EN15','EN16','EN17','EN18','EN19','EN20','EN21','EN22','EN23','EN24','EN25','EN26','EN27','EN28','EN29','EN30','WT','LT','WTT','LTT','CRR','CRRL','CRO','CROL','CRG','CRGL','CRT','CRTL','CRB','CRBL','CRDB','CRDBL','CRPU','CRPUL','CRP','CRPL','CRS','CRSL']
selected_idx = 0

# map key names to Key tokens so templates can be assigned without quotes
key_token_map = {k: globals().get(k) for k in key_order}
# help visibility
show_help = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                show_grid = not show_grid
            elif event.key == pygame.K_c:
                # toggle camera follow mode
                camera_follows = not camera_follows
            elif event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    info = pygame.display.Info()
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                small_size, large_size ,= get_tile_sizes(screen.get_size())
                extra_small_size = (small_size[0]//2, small_size[1]//2)
                extra_large_size = (large_size[0]*2, large_size[1]*2)
                # reload assets at the new size and rebuild maps
                assets = load_tile_surfaces(extra_small_size,small_size, large_size,extra_large_size)
                background_map = resolve_map(background_template, assets)
                ground_map = resolve_map(ground_template, assets)
                background_tiles = build_tiles(background_map, small_size)
                ground_tiles = build_tiles(ground_map, small_size)
            elif event.key == pygame.K_d:
                # toggle editor mode
                editor_mode = not editor_mode
                # when entering editor, stop camera follow so arrow keys pan
                if editor_mode:
                    prev_camera_follows = camera_follows
                    camera_follows = False
                else:
                    # restore camera follow
                    camera_follows = True
            elif event.key == pygame.K_h:
                show_help = not show_help
            elif event.key == pygame.K_t:
                # toggle editing layer between background_template and ground_template
                editing_ground = not editing_ground
            elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                # next tile
                selected_idx = (selected_idx + 1) % len(key_order)
            elif event.key == pygame.K_MINUS:
                selected_idx = (selected_idx - 1) % len(key_order)
            elif event.key == pygame.K_s and 1==2:
                
                # save rooms/templates to external JSON (rooms.json)
                try:
                    # ensure current templates are persisted into rooms before saving
                    rooms[current_room]['background_template'] = background_template
                    rooms[current_room]['ground_template'] = ground_template
                    save_rooms_to_json()
                    print('Rooms saved to rooms.json')
                except Exception as e:
                    print('Failed to save rooms:', e)
            # Grid resize keys (1-8)
            elif event.key == pygame.K_1:
                # 1 - add column on left
                add_column_left()
            elif event.key == pygame.K_2:
                # 2 - remove column on left
                remove_column_left()
            elif event.key == pygame.K_3:
                # 3 - add column on right
                add_column_right()
            elif event.key == pygame.K_4:
                # 4 - remove column on right
                remove_column_right()
            elif event.key == pygame.K_5:
                # 5 - add row on top
                add_row_top()
            elif event.key == pygame.K_6:
                # 6 - remove row on top
                remove_row_top()
            elif event.key == pygame.K_7:
                # 7 - add row on bottom
                add_row_bottom()
            elif event.key == pygame.K_8:
                # 8 - remove row on bottom
                remove_row_bottom()
            elif event.key == pygame.K_z:
                control_z_function(preveus_state,{'background_template':background_template,'ground_template':ground_template})
            # allow '[' and ']' to navigate rooms; some layouts send a unicode value
            elif (hasattr(event, 'unicode') and event.unicode == ']') or event.key == pygame.K_RIGHTBRACKET:
                # next room
                try:
                    next_room()
                except Exception:
                    pass
            elif (hasattr(event, 'unicode') and event.unicode == '[') or event.key == pygame.K_LEFTBRACKET:
                try:
                    prev_room()
                except Exception:
                    pass
            elif event.key==pygame.K_m:
                if event.key ==  pygame.K_m:
                    player_rect.x=int(input("x cord?"))
                    player_rect.y=int(input("y cord?"))

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            small_size, large_size = get_tile_sizes((event.w, event.h))
            extra_small_size = (small_size[0]//2, small_size[1]//2)
            extra_large_size = (large_size[0]*2, large_size[1]*2)
            # reload assets at the new size and rebuild maps
            assets = load_tile_surfaces(extra_small_size,small_size, large_size,extra_large_size)
            background_map = resolve_map(background_template, assets)
            ground_map = resolve_map(ground_template, assets)
            background_tiles = build_tiles(background_map, small_size)
            ground_tiles = build_tiles(ground_map, small_size)
        elif event.type == pygame.MOUSEBUTTONDOWN and editor_mode:
            # place or erase tiles in the active template
            mx, my = event.pos
            # convert to world coords
            wx = mx - camera_offset.x
            wy = my - camera_offset.y
            col = int(wx // small_size[0])
            row = int(wy // small_size[1])
            # pick the active template
            template = ground_template if editing_ground else background_template
            if 0 <= row < len(template) and 0 <= col < len(template[row]):
                if event.button == 1:
                    # left click: place selected tile token
                    token_name = key_order[selected_idx]
                    token = key_token_map.get(token_name)
                    template[row][col] = token
                elif event.button == 3:
                    # right click: clear
                    template[row][col] = NA
                # after modification rebuild resolved maps and tiles
                background_map = resolve_map(background_template, assets)
                ground_map = resolve_map(ground_template, assets)
                background_tiles = build_tiles(background_map, small_size)
                ground_tiles = build_tiles(ground_map, small_size)
    for entity in all_entities:
        if entity.alive:
            screen.blit(entity.image, entity.rect)
            pass
    all_entities = [entity for entity in all_entities if entity.alive]
    
    # ---- external controller handaling ----
    axiss,butons=controller.get_status()
    # ---- get buton status ----
    try:
        
        buttonA=butons[0][0]
        buttonB=butons[0][1]
        buttonX=butons[0][2]
        buttonY=butons[0][3]
        left_bumper=butons[0][4]
        right_bumper=butons[0][5]
        left_joystickb=butons[0][6]
        right_joystickb=butons[0][7]
        windows_buton=butons[0][8]
        xbuton=butons[0][9] #will not use
        menu_buton=butons[0][10]
        d_pad_up=butons[0][11]
        d_pad_down=butons[0][12]
        d_pad_left=butons[0][13]
        d_pad_right=butons[0][14]
        buton_status={
            "buttonA":buttonA,
            "buttonB":buttonB,
            "buttonX":buttonX,
            "buttonY":buttonY,
            "left_bumper":left_bumper,
            "right_bumper":right_bumper,
            "left_joystick":left_joystickb,
            "right_joystick":right_joystickb,
            "windows_buton":windows_buton,
            "xbuton going to be unused":xbuton,
            "menu_buton":menu_buton,
            "d_pad_up":d_pad_up,
            "d_pad_down":d_pad_down,
            "d_pad_left":d_pad_left,
            "d_pad_right":d_pad_right
        }
        left_joystickx=round(axiss[0][0],2)
        left_joysticky=round(axiss[0][1],2)
        right_joystickx=round(axiss[0][2],2)
        right_joysticky=round(axiss[0][3],2)
        left_trigger=round(axiss[0][4],2)
        left_trigger=round(axiss[0][5],2)
    except Exception as e:
        controller_on=False
    keys = pygame.key.get_pressed()
        # player input (A/D or left/right), jump with W or SPACE or UP
    move_x = 0
    try:
        if abs(left_joystickx)>sensitivity:
            move_x = speed*left_joystickx
        if buton_status['d_pad_right']:
            move_x = speed
        if buton_status['d_pad_left']:
            move_x = -speed
    except:
        controller_on=False
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move_x = -speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move_x = speed
    
    # camera controls
    if editor_mode:
        # in editor mode, arrow keys pan the camera directly
        # keyboard controll
        if keys[pygame.K_LEFT]:
            camera_offset.x += scroll_speed
        if keys[pygame.K_RIGHT]:
            camera_offset.x -= scroll_speed
        if keys[pygame.K_UP]:
            camera_offset.y += scroll_speed
        if keys[pygame.K_DOWN]:
            camera_offset.y -= scroll_speed
    else:
        # camera controls (Shift + arrows) when camera isn't following the player
        if not camera_follows:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                if keys[pygame.K_LEFT]:
                    camera_offset.x += scroll_speed
                if keys[pygame.K_RIGHT]:
                    camera_offset.x -= scroll_speed
                if keys[pygame.K_UP]:
                    camera_offset.y += scroll_speed
                if keys[pygame.K_DOWN]:
                    camera_offset.y -= scroll_speed
        
    # apply horizontal movement and resolve collisions
    resolve_player_collisions(move_x, 0)

    # jump (only when on ground)
    
    if (keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]) and on_ground:
        vel.y = jump_speed
    try:
        if (buton_status["d_pad_up"]or buton_status["buttonA"]) and on_ground:
            vel.y = jump_speed
        if left_joysticky<-sensitivity and on_ground:
            vel.y = jump_speed*-left_joysticky
    except:
        controller_on=False
    # apply gravity
    vel.y += gravity

    # apply vertical movement and resolve collisions
    on_ground = resolve_player_collisions(0, int(vel.y))

    # camera follow: center camera on player (in world coords)
    if camera_follows:
        sw, sh = screen.get_size()
        # center player on screen
        camera_offset.x = (sw // 2) - (player_rect.x + player_rect.width // 2)
        camera_offset.y = (sh // 2) - (player_rect.y + player_rect.height // 2)

    # Editor hover preview
    hover_preview = None
    hover_pos = None
    if editor_mode:
        mx, my = pygame.mouse.get_pos()
        wx = mx - camera_offset.x
        wy = my - camera_offset.y
        col = int(wx // small_size[0])
        row = int(wy // small_size[1])
        template = ground_template if editing_ground else background_template
        if 0 <= row < len(template) and 0 <= col < len(template[row]):
            token_name = key_order[selected_idx]
            surf = assets.get(token_name)
            if surf is not None:
                hover_preview = surf.copy()
                try:
                    hover_preview.set_alpha(160)
                except Exception:
                    pass
                hover_pos = (int(col * small_size[0] + camera_offset.x), int(row * small_size[1] + camera_offset.y))

    screen.fill((30, 30, 30))

    for tile in background_tiles:
        tile.draw(screen, camera_offset)

    # Draw player (apply camera offset) only when not in editor mode
    if not editor_mode:
        screen.blit(player_image, (int(player_rect.x + camera_offset.x), int(player_rect.y + camera_offset.y)))

    # Draw ground tiles on top of the player
    for tile in ground_tiles:
        tile.draw(screen, camera_offset)

    # draw hover preview last so it's on top
    if hover_preview and hover_pos:
        screen.blit(hover_preview, hover_pos)

    # UI: show help and editor status (H toggles visibility)
    font = pygame.font.SysFont(None, 20)
    help_lines = [
        "D - Toggle Editor Mode (enter/exit)",
        "T - Switch Layer (Background / Ground)",
        "+ / - - Change selected tile",
        "Mouse L - Place tile  |  Mouse R - Erase tile",
        "1/2 - Add / Remove column on LEFT",
        "3/4 - Add / Remove column on RIGHT",
        "5/6 - Add / Remove row on TOP",
        "7/8 - Add / Remove row on BOTTOM",
        "SP - Spawnpoint (editor-only; highlights green before placement)",
        "S - Save rooms/templates to rooms.json (persists current room)",
        "C - Toggle camera follow",
        "Arrow keys - Pan camera in Editor / Move player in Play",
        "Shift + Arrows - Pan camera when not following",
        "A/D or ←/→ - Player move  |  W / Space / ↑ - Jump",
        "G - Toggle grid  |  F - Toggle fullscreen",
        "[ / ] - Previous / Next room",
        "m - teleport",
        f"joystics: {axiss}",
        f"buttons: {butons}"
    ]

    line_h = font.get_linesize()
    # Always show the H hint on the very top-left
    hint = f"H - {'Hide' if show_help else 'Show'} Help"
    hint_surf = font.render(hint, True, (240, 240, 120))
    screen.blit(hint_surf, (8, 8))

    # If help is enabled, render the help lines below the H hint
    top_y = 8 + line_h
    if show_help:
        for i, line in enumerate(help_lines):
            surf = font.render(line, True, (200, 200, 200))
            screen.blit(surf, (8, top_y + i * line_h))
        status_y = top_y + len(help_lines) * line_h + 4
    else:
        status_y = top_y + 4

    # draw concise status below help/hint
    status = f"MODE: {'EDITOR' if editor_mode else 'PLAY'}  ROOM: {rooms[current_room]['name']}  LAYER: {'GROUND' if editing_ground else 'GRID'}  SELECT: {key_order[selected_idx]}"
    status_surf = font.render(status, True, (220, 220, 220))
    screen.blit(status_surf, (8, status_y))

    if show_grid:
        cols = max((len(r) for r in background_map), default=0)
        draw_grid(screen, len(background_map), cols, small_size[0], camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
renderer.exit()