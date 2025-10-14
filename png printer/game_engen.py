import os
import platform
import time,curses
from PIL import Image as im
from term_image.image import from_file
###  needs work###
# ----------- System sound functions -----------

def play_sound(track_path):
    system_name = platform.system()
    if system_name == 'Windows':
        os.system(f'start /MIN mplay32 /play /close "{track_path}"')  # Windows
    elif system_name == 'Darwin':
        os.system(f'afplay "{track_path}"')  # macOS
    else:
        # Linux/Unix
        os.system(f'aplay "{track_path}"')  # Ensure 'aplay' is installed

def stop_sound():
    # Stopping sound is platform-dependent; for simplicity, skip or implement if needed
    pass
# other functions

def create_composite(objects):
    max_width = 0
    max_height = 0
    images = []

    for filename, x, y in objects:
        img = load_image_with_path(filename)
        images.append((img, x, y))
        max_width = max(max_width, int(x + img.width))
        max_height = max(max_height, int(y + img.height))
    base = im.new('RGBA', (max_width, max_height), (0, 0, 0, 0))
    for img, x, y in images:
        base.paste(img, (int(x), int(y)), img)
    return base

def print_image_in_terminal(image):
    temp_path = 'temp_composite.png'
    image.save(temp_path)
    os.system('clear')
    img = from_file(temp_path)
    img.draw()
    os.remove(temp_path)

def print_objs(objects_to_place):
    composite_image = create_composite(objects_to_place)
    print_image_in_terminal(composite_image)

def load_image_with_path(filename):
    path = os.path.join('png printer/pngs', filename)
    return im.open(path).convert('RGBA')

# ----------- Your classes (Door, Room, Map, Game) -----------

class Door:
    def __init__(self, rotation, x, y, destination, requirement=None):
        self.rotation = rotation
        self.x = x
        self.y = y
        self.destination = destination
        self.requirement = requirement
        self.open = requirement is None

    def is_at_position(self, px, py):
        return int(self.x) == int(px) and int(self.y) == int(py)

    def can_open(self, player):
        if self.requirement is None:
            return True
        return self.requirement in player['items']

class Room:
    def __init__(self, name, blocks=None):
        self.name = name
        self.blocks = blocks if blocks else []
        self.doors = []
        self.entities = []

    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def add_door(self, rotation, x, y, destination, requirement=None):
        self.doors.append(Door(rotation, x, y, destination, requirement))

    def get_door_at(self, x, y):
        for door in self.doors:
            if door.is_at_position(x, y):
                return door
        return None

    def get_blocks(self):
        return self.blocks

    def render(self):
        objs = []
        for (x, y) in self.blocks:
            filename = 'all_side_grass.png'
            objs.append((filename, x * 700, y * 700))
        for e in self.entities:
            objs.append((e['png'], e['x'], e['y']))
        print(f"\n--- {self.name} ---")
        print_objs(objs)

class Map:
    def __init__(self):
        self.visited_rooms = set()

    def mark_visited(self, room_name):
        self.visited_rooms.add(room_name)

    def is_visited(self, room_name):
        return room_name in self.visited_rooms

    def display(self):
        print("\n--- Map ---")
        for room_name in self.visited_rooms:
            print(f"[{room_name}] ", end='')
        print("\n")

class Game:
    def __init__(self):
        self.rooms = {}
        self.current_room = None
        self.map = Map()
        self.player = None

    def add_room(self, room):
        self.rooms[room.name] = room

    def set_current_room(self, room_name):
        self.current_room = self.rooms.get(room_name)
        if self.current_room:
            self.map.mark_visited(room_name)

    def create_player(self, x, y):
        self.player = {
            'x': float(x),
            'y': float(y),
            'width': 700,
            'height': 700,
            'type': 'player',
            'png': 'player.png',
            'items': []
        }
        self.current_room.add_entity(self.player)

    def switch_room(self, room_name, entry_x, entry_y):
        self.current_room.remove_entity(self.player)
        self.set_current_room(room_name)
        self.player['x'] = entry_x
        self.player['y'] = entry_y
        self.current_room.add_entity(self.player)

    def check_for_door_and_transition(self):
        door = self.current_room.get_door_at(self.player['x'], self.player['y'])
        if door:
            if door.can_open(self.player):
                print(f"Opening door to {door.destination}")
                self.switch_room(door.destination, door.x * 700, door.y * 700)
            else:
                print(f"Door requires: {door.requirement}")

    def move_entity(self, entity, target_x, target_y, duration=0.2):
        start_x, start_y = entity['x'], entity['y']
        steps = int(duration * 50)
        for step in range(steps):
            t = (step + 1) / steps
            new_x = start_x + (target_x - start_x) * t
            new_y = start_y + (target_y - start_y) * t
            # Check collisions
            test_entity = {'x': new_x, 'y': new_y, 'width': entity['width'], 'height': entity['height']}
            if check_tile_collision(test_entity, self.current_room) or check_entity_collision(test_entity, self.current_room, exclude_entity=entity):
                break
            entity['x'], entity['y'] = new_x, new_y
            self.current_room.render()
            time.sleep(1/50)

    def run(self):
        import curses
        curses.wrapper(self.game_loop)

    def game_loop(self, stdscr):
        curses.curs_set(0)
        stdscr.nodelay(1)
        stdscr.timeout(50)

        # Initial position
        px, py = 10, 5
        frame_idx = 0
        last_frame_time = time.time()
        frame_delay = 0.2

        # Initialize starting room and music
        self.set_current_room('MainRoom')
        self.create_player(px*700, py*700)
        play_sound('main_room.mp3')  # play initial sound

        while True:
            key = stdscr.getch()

            if key == ord('q'):
                break

            if key == ord('p'):
                # Pausing the game
                stdscr.clear()
                stdscr.addstr(0, 0, "Paused. Press 'p' to resume.")
                stdscr.refresh()
                while True:
                    k = stdscr.getch()
                    if k == ord('p'):
                        break
                    time.sleep(0.1)
                continue

            prev_x, prev_y = px, py

            if key == curses.KEY_UP:
                py -= 1
            elif key == curses.KEY_DOWN:
                py += 1
            elif key == curses.KEY_LEFT:
                px -= 1
            elif key == curses.KEY_RIGHT:
                px += 1

            # Animate sprite
            now = time.time()
            if now - last_frame_time > frame_delay:
                frame_idx = (frame_idx + 1) % len(player_frames)
                last_frame_time = now

            # Clear screen
            os.system('clear')

            # Show info
            stdscr.addstr(0, 0, f"Room: {self.current_room.name}")
            stdscr.addstr(1, 0, "Arrow keys to move, 'q' to quit")
            stdscr.refresh()

            # Room transition
            if px > 50 and self.current_room.name != 'HiddenRoom':
                self.current_room = self.rooms.get('HiddenRoom')
                stop_sound()
                play_sound('hidden_room.mp3')
            elif px < 5 and self.current_room.name != 'MainRoom':
                self.current_room = self.rooms.get('MainRoom')
                stop_sound()
                play_sound('main_room.mp3')

            # Move player
            self.current_room.remove_entity(self.player)
            self.player['x'] = px * 700
            self.player['y'] = py * 700
            self.current_room.add_entity(self.player)

            # Render room
            self.current_room.render()

            # Check door
            self.check_for_door_and_transition()

            # Draw sprite
            objects = [(player_frames[frame_idx], self.player['x'], self.player['y'])]
            print_objs(objects)

            time.sleep(0.05)

# ----------- Setup your game environment -----------

def setup_game():
    game = Game()

    # Create rooms
    main_room = Room('MainRoom', blocks=[(1,1), (2,1), (3,1),(4,1),(4,0),(4,-1)])
    main_room.add_door('left', 0, 7, 'ItemRoom')
    main_room.add_door('up', 10, 0, 'SecretRoom', requirement='missile')

    item_room = Room('ItemRoom', blocks=[(5,5), (6,6), (7,7)])
    item_room.add_door('right', 19, 7, 'MainRoom')

    secret_room = Room('SecretRoom', blocks=[(10,10)])
    secret_room.add_door('down', 10, 0, 'MainRoom', requirement='missile')

    # Add to game
    for r in [main_room, item_room, secret_room]:
        game.add_room(r)

    game.set_current_room('MainRoom')
    game.create_player(2*700, 7*700)

    return game

# Run your game
if __name__ == "__main__":
    game = setup_game()
    game.run()