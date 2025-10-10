#sudocode yay
from PIL import Image
import subprocess

from PIL import Image, ImageDraw

def print_to_png():
    #needs editing
    """
    Renders the game state to a PNG file using Pillow.
    This creates a visual representation of the tilemap, player, and enemies.
    """
    # Calculate image dimensions based on your map and tile size
    img_width = MAP_WIDTH * tile_size
    img_height = MAP_HEIGHT * tile_size
    
    # Create a new blank image with a white background
    img = Image.new('RGB', (img_width, img_height), 'white')
    draw = ImageDraw.Draw(img)

    # --- Draw the tilemap ---
    for y in range(MAP_HEIGHT):
        for x in range(MAP_WIDTH):
            tile_type = tile_map[y][x]
            tile_x = x * tile_size
            tile_y = y * tile_size
            
            # Draw different colored squares for different tile types
            if tile_type == 1:  # Solid block
                draw.rectangle([(tile_x, tile_y), (tile_x + tile_size, tile_y + tile_size)], fill='black')
            elif tile_type == 2:  # Start area (or other special tile)
                draw.rectangle([(tile_x, tile_y), (tile_x + tile_size, tile_y + tile_size)], fill='lightblue')

    # --- Draw the player ---
    player_rect = (
        player_data['x'],
        player_data['y'],
        player_data['x'] + player_data['width'],
        player_data['y'] + player_data['height']
    )
    draw.rectangle(player_rect, fill='blue')

    # --- Draw the enemies ---
    for enemy in enemies:
        enemy_rect = (
            enemy['x'],
            enemy['y'],
            enemy['x'] + enemy['width'],
            enemy['y'] + enemy['height']
        )
        draw.rectangle(enemy_rect, fill='red')

    # --- Save the image to a file ---
    # Create a simple filename based on the current time or a frame counter
    filename = f"game_frame_{random.randint(1000, 9999)}.png"
    img.save(filename, 'PNG')
    print(f"Saved frame to {filename}")

def collision(rect1, rect2):
    if (rect1['x'] < rect2['x'] + rect2['width'] and
        rect1['x'] + rect1['width'] > rect2['x'] and
        rect1['y'] < rect2['y'] + rect2['height'] and
        rect1['y'] + rect1['height'] > rect2['y']):
        return True
    else:
        return False
def main_game_loop():
    #not done
    pass
def enemy_game_loop():
    #not done
    pass
def player_game_loop():
    #not done
    pass
def entity_game_loop():
    #not done
    pass