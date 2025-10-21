import pygame
import os

# --- Setup ---
pygame.init()
windowed_size = (800, 600)
screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
pygame.display.set_caption("Scrollable Tile Grid")
clock = pygame.time.Clock()

# --- Load and scale tile images ---
def load_tile(filename, size):
    path = os.path.join('Images', 'sprites', filename)
    try:
        image = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(image, size)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return pygame.Surface(size)

# --- Dynamic tile sizing (square based on width) ---
def get_tile_sizes(screen_size):
    sw, _ = screen_size
    small = int(sw * 0.05)
    large = int(sw * 0.10)
    return (small, small), (large, large)

# --- Grid overlay ---
def draw_grid(surface, rows, cols, cell_size, offset):
    for r in range(rows + 1):
        pygame.draw.line(surface, (50, 50, 50),
                         (offset[0], offset[1] + r * cell_size),
                         (offset[0] + cols * cell_size, offset[1] + r * cell_size))
    for c in range(cols + 1):
        pygame.draw.line(surface, (50, 50, 50),
                         (offset[0] + c * cell_size, offset[1]),
                         (offset[0] + c * cell_size, offset[1] + rows * cell_size))

# --- Tile class ---
class Tile:
    def __init__(self, image, x, y):
        self.image = image
        self.base_pos = pygame.Vector2(x, y)

    def draw(self, surface, offset):
        pos = self.base_pos + offset
        surface.blit(self.image, pos)

# --- Helper to check top-left of large tile ---
def is_top_left_of_large_tile(row, col, cell, grid_map):
    return (
        (row == 0 or grid_map[row - 1][col] != cell) and
        (col == 0 or grid_map[row][col - 1] != cell)
    )

# --- Build tile objects from grid ---
def build_tiles(grid_map, small_size):
    tiles = []
    rows = len(grid_map)
    cols = len(grid_map[0])
    for row in range(rows):
        for col in range(cols):
            cell = grid_map[row][col]
            if cell is None:
                continue
            w, h = cell.get_size()
            x = col * small_size[0]
            y = row * small_size[0]
            if w > small_size[0] or h > small_size[1]:
                if is_top_left_of_large_tile(row, col, cell, grid_map):
                    tiles.append(Tile(cell, x, y))
            else:
                tiles.append(Tile(cell, x, y))
    return tiles

# --- Initial tile sizes and assets ---
small_size, large_size = get_tile_sizes(windowed_size)
AA = load_tile("Basic Tile.png", small_size)
BA = load_tile("Basic Tile Claw Mark.png", large_size)
BB = load_tile("Basic Tile Hole.png", large_size)
NA = None  # Reserved space

# --- Grid map (preserved two-letter format) ---
grid_map = [
    [AA, AA, AA, AA, AA],
    [AA, BA, NA, AA, AA],
    [AA, NA, NA, AA, AA],
    [AA, AA, AA, BB, NA],
    [AA, AA, AA, NA, NA],
]

tiles = build_tiles(grid_map, small_size)

# --- Main loop ---
show_grid = True
fullscreen = False
camera_offset = pygame.Vector2(0, 0)
scroll_speed = 10
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_g:
                show_grid = not show_grid
            elif event.key == pygame.K_f:
                fullscreen = not fullscreen
                if fullscreen:
                    info = pygame.display.Info()
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                else:
                    screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
                small_size, large_size = get_tile_sizes(screen.get_size())
                AA = load_tile("Basic Tile.png", small_size)
                BA = load_tile("Basic Tile Claw Mark.png", large_size)
                BB = load_tile("Basic Tile Hole.png", large_size)
                grid_map = [
                    [AA, AA, AA, AA, AA],
                    [AA, BA, NA, AA, AA],
                    [AA, NA, NA, AA, AA],
                    [AA, AA, AA, BB, NA],
                    [AA, AA, AA, NA, NA],
                ]
                tiles = build_tiles(grid_map, small_size)
        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            small_size, large_size = get_tile_sizes((event.w, event.h))
            AA = load_tile("Basic Tile.png", small_size)
            BA = load_tile("Basic Tile Claw Mark.png", large_size)
            BB = load_tile("Basic Tile Hole.png", large_size)
            grid_map = [
                [AA, AA, AA, AA, AA],
                [AA, BA, NA, AA, AA],
                [AA, NA, NA, AA, AA],
                [AA, AA, AA, BB, NA],
                [AA, AA, AA, NA, NA],
            ]
            tiles = build_tiles(grid_map, small_size)

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        camera_offset.x += scroll_speed
    if keys[pygame.K_RIGHT]:
        camera_offset.x -= scroll_speed
    if keys[pygame.K_UP]:
        camera_offset.y += scroll_speed
    if keys[pygame.K_DOWN]:
        camera_offset.y -= scroll_speed

    screen.fill((30, 30, 30))

    for tile in tiles:
        tile.draw(screen, camera_offset)

    if show_grid:
        draw_grid(screen, len(grid_map), len(grid_map[0]), small_size[0], camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
