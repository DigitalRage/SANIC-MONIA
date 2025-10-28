import pygame
import os
import glob

# --- Setup ---
pygame.init()
windowed_size = (800, 600)
screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
pygame.display.set_caption("Tile Grid with Ground Collision")
clock = pygame.time.Clock()

# --- Load and scale tile images ---
def load_tile(filename, size):
    path = os.path.join('Images', 'sprites', filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return pygame.Surface(size, pygame.SRCALPHA)


def load_ground_any(size, preferred="ground_greye.png"):
    pref_path = os.path.join('Images', 'sprites', preferred)
    if os.path.exists(pref_path):
        return load_tile(preferred, size)

    # Search for any ground_*.png
    candidates = glob.glob(os.path.join('Images', 'sprites', 'ground_*.png'))
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
NA = None

# Load surfaces into a mapping so templates that use Key(...) can be resolved.
def load_tile_surfaces(small_size, large_size):
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
    }

assets = load_tile_surfaces(small_size, large_size)

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
    global background_template, ground_template
    normalize_templates()
    for row in background_template:
        row.insert(0, NA)
    for row in ground_template:
        row.insert(0, NA)
    rebuild_maps_and_tiles()
    print('Added column on left')


def remove_column_left():
    global background_template, ground_template
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
    global background_template, ground_template
    normalize_templates()
    for row in background_template:
        row.append(NA)
    for row in ground_template:
        row.append(NA)
    rebuild_maps_and_tiles()
    print('Added column on right')


def remove_column_right():
    global background_template, ground_template
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
    global background_template, ground_template
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
    global background_template, ground_template
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
    global background_template, ground_template
    normalize_templates()
    cols = max(len(background_template[0]) if background_template else 0,
               len(ground_template[0]) if ground_template else 0)
    new_bg = [NA] * cols
    new_gd = [NA] * cols
    background_template.append(list(new_bg))
    ground_template.append(list(new_gd))
    rebuild_maps_and_tiles()
    print('Added row on bottom')


def remove_row_bottom():
    global background_template, ground_template
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
gravity = 0.6
jump_speed = -11
on_ground = False

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
key_order = ['AA', 'BA', 'BB', 'SP', 'FG', 'FA', 'FB', 'FC', 'FD', 'FE', 'FF', 'FH', 'FI', 'FJ', 'FK', 'FL', 'FM']
selected_idx = 0

# map key names to Key tokens so templates can be assigned without quotes
key_token_map = {k: globals().get(k) for k in key_order}
# help visibility
show_help = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
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
                small_size, large_size = get_tile_sizes(screen.get_size())
                # reload assets at the new size and rebuild maps
                assets = load_tile_surfaces(small_size, large_size)
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
            elif event.key == pygame.K_s:
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

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            small_size, large_size = get_tile_sizes((event.w, event.h))
            # reload assets at the new size and rebuild maps
            assets = load_tile_surfaces(small_size, large_size)
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
                

    keys = pygame.key.get_pressed()
    # camera controls
    if editor_mode:
        # in editor mode, arrow keys pan the camera directly
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

    # player input (A/D or left/right), jump with W or SPACE or UP
    move_x = 0
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        move_x = -speed
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        move_x = speed

    # apply horizontal movement and resolve collisions
    resolve_player_collisions(move_x, 0)

    # jump (only when on ground)
    if (keys[pygame.K_w] or keys[pygame.K_SPACE] or keys[pygame.K_UP]) and on_ground:
        vel.y = jump_speed

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
