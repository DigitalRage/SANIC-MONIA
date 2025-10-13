from PIL import Image
import time,threading,queue,random,re,os,copy,calendar,png_to_terminal
# Constants
TILE_SIZE = 20

# --- Room Class ---
class Room:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Use a sparse dictionary for tiles: {(x, y): tile_type}
        self.tiles = {}
        self.entities = []
        self.create_borders()

    def create_borders(self):
        # Fill borders with tiles (tile_type = 1)
        for x in range(self.width):
            self.set_tile(x, 0, 1)
            self.set_tile(x, self.height - 1, 1)
        for y in range(self.height):
            self.set_tile(0, y, 1)
            self.set_tile(self.width - 1, y, 1)

    def get_tile(self, x, y):
        return self.tiles.get((x, y), 0)  # 0 = empty

    def set_tile(self, x, y, tile_type):
        self.tiles[(x, y)] = tile_type

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def get_entities_near(self, x, y, radius):
        nearby = []
        for e in self.entities:
            dist = abs(e['x'] - x) + abs(e['y'] - y)
            if dist <= radius:
                nearby.append(e)
        return nearby

# --- Entity Management ---
def create_entity(x, y, width, height, entity_type):
    return {'x': x, 'y': y, 'width': width, 'height': height, 'type': entity_type}

# --- Detect what entity or tile is touched ---
def detect_touching(entity, room):
    # Check tile under entity's bottom center
    x_center = entity['x'] + entity['width'] / 2
    y_bottom = entity['y'] + entity['height']
    tile_x = int(x_center / TILE_SIZE)
    tile_y = int(y_bottom / TILE_SIZE)

    if 0 <= tile_x < room.width and 0 <= tile_y < room.height:
        tile_type = room.get_tile(tile_x, tile_y)
        if tile_type == 1:
            print(f"{entity['type']} touches a tile at ({tile_x}, {tile_y})")
        else:
            print(f"{entity['type']} is not touching any tile at ({tile_x}, {tile_y})")
    else:
        print(f"{entity['type']} is outside the room bounds.")

    # Check collision with other entities
    for e in room.entities:
        if e != entity:
            if (entity['x'] < e['x'] + e['width'] and
                entity['x'] + entity['width'] > e['x'] and
                entity['y'] < e['y'] + e['height'] and
                entity['y'] + entity['height'] > e['y']):
                print(f"{entity['type']} touches {e['type']} at ({e['x']}, {e['y']})")

# --- Move entity with simple collision check ---
def move_entity(entity, target_x, target_y, room):
    # Move in small steps for smoothness
    steps = 10
    dx = (target_x - entity['x']) / steps
    dy = (target_y - entity['y']) / steps
    for _ in range(steps):
        new_x = entity['x'] + dx
        new_y = entity['y'] + dy
        if not check_tile_collision(new_x, new_y, entity, room) and not check_entity_collision(new_x, new_y, entity, room):
            entity['x'] = new_x
            entity['y'] = new_y
        else:
            break
        time.sleep(0.02)

def check_tile_collision(x, y, entity, room):
    # Check the tile at the entity's position
    tile_x = int(x / TILE_SIZE)
    tile_y = int(y / TILE_SIZE)
    if 0 <= tile_x < room.width and 0 <= tile_y < room.height:
        if room.get_tile(tile_x, tile_y) == 1:
            return True
    return False

def check_entity_collision(x, y, entity, room):
    # Check collision with other entities
    for e in room.entities:
        if e != entity:
            if (x < e['x'] + e['width'] and
                x + entity['width'] > e['x'] and
                y < e['y'] + e['height'] and
                y + entity['height'] > e['y']):
                return True
    return False

# --- Rendering in console ---
def render(room, camera_x=0, camera_y=0, view_width=200, view_height=200):
    start_x = int(camera_x / TILE_SIZE)
    start_y = int(camera_y / TILE_SIZE)
    end_x = int((camera_x + view_width) / TILE_SIZE)
    end_y = int((camera_y + view_height) / TILE_SIZE)
    print("\n--- Room View ---")
    for y in range(start_y, min(end_y + 1, room.height)):
        row = ''
        for x in range(start_x, min(end_x + 1, room.width)):
            # Check for entities
            entity_char = None
            for e in room.entities:
                e_x_tile = int(e['x'] / TILE_SIZE)
                e_y_tile = int(e['y'] / TILE_SIZE)
                if e_x_tile == x and e_y_tile == y:
                    if e['type'] == 'player':
                        entity_char = 'P'
                    elif e['type'] == 'spike':
                        entity_char = 'S'
                    else:
                        entity_char = 'E'
            if entity_char:
                row += entity_char
            elif room.get_tile(x, y) == 1:
                row += '#'
            else:
                row += ' '
        print(row)

# --- Example Usage ---
def main():
    # Create a room of arbitrary size
    room_width = 30  # change for testing bigger rooms
    room_height = 15
    room = Room(room_width, room_height)

    # Add entities
    player = create_entity(2 * TILE_SIZE, 2 * TILE_SIZE, TILE_SIZE, TILE_SIZE, 'player')
    spike = create_entity(5 * TILE_SIZE, 5 * TILE_SIZE, TILE_SIZE, TILE_SIZE, 'spike')
    room.add_entity(player)
    room.add_entity(spike)

    # Main loop (simulate movement)
    for step in range(20):
        # Example: move player right
        target_x = player['x'] + 5
        target_y = player['y']
        move_entity(player, target_x, target_y, room)
        render(room, camera_x=0, camera_y=0, view_width=200, view_height=200)
        detect_touching(player, room)
        time.sleep(0.2)

if __name__ == "__main__":
    main()