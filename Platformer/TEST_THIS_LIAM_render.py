import pygame
import os

# --- Setup ---
pygame.init()
windowed_size = (800, 600)
screen = pygame.display.set_mode(windowed_size, pygame.RESIZABLE)
pygame.display.set_caption("Tile Grid with Foreground Collision")
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
        pos = self.rect.topleft + offset
        surface.blit(self.image, pos)

    def collides_with(self, other_rect, other_mask, offset):
        rel_offset = (self.rect.x - other_rect.x + offset.x, self.rect.y - other_rect.y + offset.y)
        return self.mask.overlap(other_mask, rel_offset)

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
def is_top_left_of_large_tile(row, col, cell, grid_map):
    return (
        (row == 0 or grid_map[row - 1][col] != cell) and
        (col == 0 or grid_map[row][col - 1] != cell)
    )

# --- Build tile objects from grid ---
def build_tiles(grid_map, small_size):
    tiles = []
    for row in range(len(grid_map)):
        for col in range(len(grid_map[0])):
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

# --- Initial sizes and assets ---
small_size, large_size = get_tile_sizes(windowed_size)
AA = load_tile("Basic Tile.png", small_size)
BA = load_tile("Basic Tile Claw Mark.png", large_size)
BB = load_tile("Basic Tile Hole.png", large_size)
FG = load_tile("Foreground Tile Crate.png", small_size)
NA = None

# --- Grid maps ---
grid_map = [
    [AA, AA, AA, AA, AA],
    [AA, BA, NA, AA, AA],
    [AA, NA, NA, AA, AA],
    [AA, AA, AA, BB, NA],
    [AA, AA, AA, NA, NA],
]

foreground_map = [
    [NA, NA, NA, NA, NA],
    [NA, NA, NA, NA, NA],
    [NA, NA, FG, NA, NA],
    [NA, NA, NA, NA, NA],
    [NA, NA, NA, NA, NA],
]

background_tiles = build_tiles(grid_map, small_size)
foreground_tiles = build_tiles(foreground_map, small_size)

# --- Dummy player setup ---
player_image = pygame.Surface(small_size, pygame.SRCALPHA)
pygame.draw.circle(player_image, (255, 255, 0), (small_size[0] // 2, small_size[1] // 2), small_size[0] // 2)
player_rect = player_image.get_rect(topleft=(100, 100))
player_mask = pygame.mask.from_surface(player_image)

# --- Main loop ---
camera_offset = pygame.Vector2(0, 0)
scroll_speed = 10
show_grid = True
fullscreen = False
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
                FG = load_tile("Foreground Tile Crate.png", small_size)
                grid_map = [
                    [AA, AA, AA, AA, AA],
                    [AA, BA, NA, AA, AA],
                    [AA, NA, NA, AA, AA],
                    [AA, AA, AA, BB, NA],
                    [AA, AA, AA, NA, NA],
                ]
                foreground_map = [
                    [NA, NA, NA, NA, NA],
                    [NA, NA, NA, NA, NA],
                    [NA, NA, FG, NA, NA],
                    [NA, NA, NA, NA, NA],
                    [NA, NA, NA, NA, NA],
                ]
                background_tiles = build_tiles(grid_map, small_size)
                foreground_tiles = build_tiles(foreground_map, small_size)

        elif event.type == pygame.VIDEORESIZE:
            screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            small_size, large_size = get_tile_sizes((event.w, event.h))
            AA = load_tile("Basic Tile.png", small_size)
            BA = load_tile("Basic Tile Claw Mark.png", large_size)
            BB = load_tile("Basic Tile Hole.png", large_size)
            FG = load_tile("Foreground Tile Crate.png", small_size)
            grid_map = [
                [AA, AA, AA, AA, AA],
                [AA, BA, NA, AA, AA],
                [AA, NA, NA, AA, AA],
                [AA, AA, AA, BB, NA],
                [AA, AA, AA, NA, NA],
            ]
            foreground_map = [
                [NA, NA, NA, NA, NA],
                [NA, NA, NA, NA, NA],
                [NA, NA, FG, NA, NA],
                [NA, NA, NA, NA, NA],
                [NA, NA, NA, NA, NA],
            ]
            background_tiles = build_tiles(grid_map, small_size)
            foreground_tiles = build_tiles(foreground_map, small_size)

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

    for tile in background_tiles:
        tile.draw(screen, camera_offset)

    for tile in foreground_tiles:
        tile.draw(screen, camera_offset)
        if tile.collides_with(player_rect, player_mask, camera_offset):
            pygame.draw.rect(screen, (255, 0, 0), tile.rect.move(camera_offset), 2)

    screen.blit(player_image, player_rect)

    if show_grid:
        draw_grid(screen, len(grid_map), len(grid_map[0]), small_size[0], camera_offset)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
