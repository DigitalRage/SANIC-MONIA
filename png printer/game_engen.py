import os
import pygame
import time

# --- INIT ---
try:
    pygame.mixer.init()
except pygame.error:
    print("Sound init failed; disabling sound.")
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
finally:
    pygame.init()
    try:
        pygame.mixer.init()
    except:
        pass
is_faiding = False

# --- SCREEN ---
screen = pygame.display.set_mode((400, 400))
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
pygame.display.set_caption("Python Metroidvania")

# --- PLAYER IMAGE ---
try:
    player_image = pygame.image.load(r'png printer/pngs/player.png')
    player_image = pygame.transform.scale(player_image, (30, 60))
except pygame.error:
    print("Player image not found; using default.")
    player_image = pygame.Surface((30, 60))
    player_image.fill((255, 0, 0))

# --- SOUND ---
def play_sound(track_path):
    try:
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.play(-1)
    except pygame.error:
        print("Music file not found or sound disabled.")

def stop_sound():
    pygame.mixer.music.stop()

# --- CONSTANTS ---
TILE_SIZE = 30

# --- Enemy class with wall-following logic ---
class Enemy:
    def __init__(self, x, y, width=30, height=30, speed=2):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.direction = 1  # 1 for right, -1 for left

    def move_along_wall(self, walls):
        # Move horizontally
        self.x += self.speed * self.direction
        self.rect.x = self.x

        # Check collision with walls
        collided = False
        for wall in walls:
            if self.rect.colliderect(wall.rect):
                collided = True
                break

        if collided:
            # Reverse direction on wall collision
            self.direction *= -1
            self.x += self.speed * self.direction * 2
            self.rect.x = self.x

    def draw(self, surface, camera_x, camera_y):
        # Draw top red, bottom black
        top_rect = pygame.Rect(self.x - camera_x, self.y - camera_y, self.width, self.height // 2)
        bottom_rect = pygame.Rect(self.x - camera_x, self.y - camera_y + self.height // 2, self.width, self.height // 2)
        pygame.draw.rect(surface, (255, 0, 0), top_rect)
        pygame.draw.rect(surface, (0, 0, 0), bottom_rect)

# --- Game Elements ---
class Wall:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

class Door:
    def __init__(self, x_grid, y_grid, destination, requirement=None):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.destination = destination
        self.requirement = requirement
        self.rect = pygame.Rect(self.x_grid * TILE_SIZE, self.y_grid * TILE_SIZE, TILE_SIZE, TILE_SIZE)

    def can_open(self, player_items):
        if self.requirement is None:
            return True
        return self.requirement in player_items

class Room:
    def __init__(self, name, layout):
        self.name = name
        self.layout = layout
        self.room_width = len(self.layout[0]) * TILE_SIZE
        self.room_height = len(self.layout) * TILE_SIZE
        self.room_surface = pygame.Surface((self.room_width, self.room_height))
        self.walls = []
        self.doors = []
        self.entities = []
        self.door_locations_x = []
        self.door_locations_y = []
        self.enemies = []

    def get_door_location(self, choice):
        if choice == "x":
            return self.door_locations_x
        else:
            return self.door_locations_y

    def load_room(self, doors):
        self.walls = []
        self.enemies = []
        self.doors = doors
        for y, row in enumerate(self.layout):
            for x, tile in enumerate(row):
                if tile == '#':
                    self.walls.append(Wall(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
        # Add enemies for demo
        if self.name == "main room":
            self.enemies.append(Enemy(50, 50))
            self.enemies.append(Enemy(150, 100))

    def add_door(self, door, spawn_x=100, spawn_y=100):
        self.doors.append(door)
        self.door_locations_x.append(spawn_x)
        self.door_locations_y.append(spawn_y)

    def update_enemies(self):
        for enemy in self.enemies:
            enemy.move_along_wall(self.walls)

    def render(self, surface, camera_x, camera_y):
        self.room_surface.fill((0, 0, 0))
        # Walls
        for wall in self.walls:
            pygame.draw.rect(self.room_surface, (0, 255, 0),
                             pygame.Rect(wall.rect.x - camera_x, wall.rect.y - camera_y, TILE_SIZE, TILE_SIZE))
        # Doors
        for door in self.doors:
            pygame.draw.rect(self.room_surface, (255, 255, 0),
                             pygame.Rect(door.rect.x - camera_x, door.rect.y - camera_y, TILE_SIZE, TILE_SIZE))
        # Enemies
        for enemy in self.enemies:
            enemy.draw(self.room_surface, camera_x, camera_y)

        surface.blit(self.room_surface, (0, 0))

    def get_door_at(self, player_rect):
        for door in self.doors:
            if player_rect.colliderect(door.rect):
                return door
        return None

# --- Main Game Class ---
class Game:
    def __init__(self):
        self.rooms = {}
        self.current_room = None
        self.player = {
            "x": 100,
            "y": 100,
            "width": 30,
            "height": 60,
            "image": player_image,
            "items": [],
            "rect": pygame.Rect(100, 100, 30, 60),
            "speed": 5,
            "y_velocity": 0,
            "is_jumping": False,
            "jump_pressed": False,
            "on_ground": False,
        }
        self.gravity = 1
        self.jump_strength = -15
        self.max_fall_speed = 15
        self.running = True
        self.fade_surface = pygame.Surface(screen.get_size())
        self.fade_surface.fill((0, 0, 0))
        self.fade_alpha = 0
        self.fading = False
        self.next_room = None
        self.next_spawn_x = 100
        self.next_spawn_y = 100

    def get_player_rec(self):
        return self.player["rect"]

    def add_room(self, room):
        self.rooms[room.name] = room

    def set_current_room(self, room_name, spawn_x=100, spawn_y=100, previous_room_name=None):
        self.current_room = self.rooms.get(room_name)
        if not self.current_room:
            print(f"Room '{room_name}' not found.")
            return
        self.current_room.load_room(self.current_room.doors)
        self.player['x'] = spawn_x
        self.player['y'] = spawn_y
        self.player['rect'].topleft = (self.player['x'], self.player['y'])

    def move(self, dx):
        self.player['x'] += dx
        self.player['rect'].x = self.player['x']
        for wall in self.current_room.walls:
            if self.player['rect'].colliderect(wall.rect):
                if dx > 0:
                    self.player['rect'].right = wall.rect.left
                elif dx < 0:
                    self.player['rect'].left = wall.rect.right
                self.player['x'] = self.player['rect'].x

    def apply_gravity(self):
        self.player['y_velocity'] += self.gravity
        if self.player['y_velocity'] > self.max_fall_speed:
            self.player['y_velocity'] = self.max_fall_speed
        self.player['y'] += self.player['y_velocity']
        self.player['rect'].y = self.player['y']

        self.player['on_ground'] = False
        for wall in self.current_room.walls:
            if self.player['rect'].colliderect(wall.rect):
                if self.player['y_velocity'] > 0:
                    self.player['rect'].bottom = wall.rect.top
                    self.player['on_ground'] = True
                    self.player['y_velocity'] = 0
                    self.player['is_jumping'] = False
                elif self.player['y_velocity'] < 0:
                    self.player['rect'].top = wall.rect.bottom
                    self.player['y_velocity'] = 0
                self.player['y'] = self.player['rect'].y

    def handle_input(self):
        global is_faiding
        if not is_faiding:
            keys = pygame.key.get_pressed()
            dx = 0
            if keys[pygame.K_LEFT]:
                dx -= self.player['speed']
            if keys[pygame.K_RIGHT]:
                dx += self.player['speed']
            jump_key = keys[pygame.K_UP] or keys[pygame.K_SPACE]
            if jump_key and self.player['on_ground'] and not self.player['jump_pressed']:
                self.player['y_velocity'] = self.jump_strength
                self.player['is_jumping'] = True
                self.player['jump_pressed'] = True
                self.player['on_ground'] = False
            if not jump_key and self.player['is_jumping'] and self.player['y_velocity'] < -5:
                self.player['y_velocity'] = -5
                self.player['is_jumping'] = False
            if not jump_key:
                self.player['jump_pressed'] = False

        self.move(dx)
        if keys[pygame.K_ESCAPE]:
            self.running = False
        if keys[pygame.K_TAB]:
            self.player["x"] = 100
            self.player["y"] = 100

    def check_for_door_and_transition(self):
        door = self.current_room.get_door_at(self.player['rect'])
        if door and door.can_open(self.player['items']):
            index = self.current_room.doors.index(door)
            spawn_x = self.current_room.door_locations_x[index]
            spawn_y = self.current_room.door_locations_y[index]
            self.start_fade(door.destination, spawn_x, spawn_y)

    def start_fade(self, next_room_name, door_spawn_x, door_spawn_y):
        global is_faiding
        self.fading = "fadeout"
        self.next_room = next_room_name
        self.fade_alpha = 0
        self.next_spawn_x = door_spawn_x
        self.next_spawn_y = door_spawn_y

    def update_fade(self):
        global is_faiding
        if not self.fading:
            return
        if self.fading == "fadeout":
            self.fade_alpha += 10
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                previous = self.current_room.name
                self.set_current_room(self.next_room, self.next_spawn_x, self.next_spawn_y, previous_room_name=previous)
                self.fading = "fadein"
        elif self.fading == "fadein":
            self.fade_alpha -= 10
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fading = False
                is_faiding = False

    def run(self):
        clock = pygame.time.Clock()
        try:
            play_sound(r'P:\perl,liam\Chronin7\python metroidvanea\metroidvanea pngs and ohter files\test.mp3')
        except FileNotFoundError:
            print("Music file 'test.mp3' not found.")

        camera_x, camera_y = 0, 0
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.handle_input()
            self.apply_gravity()
            self.check_for_door_and_transition()
            self.update_fade()

            # Update enemies
            if self.current_room:
                self.current_room.update_enemies()

            # Check collision with enemies
            for enemy in self.current_room.enemies:
                if self.player['rect'].colliderect(enemy.rect):
                    print("Player hit by enemy!")

            camera_x = self.player['x'] - SCREEN_WIDTH // 2 + self.player['width'] // 2
            camera_y = self.player['y'] - SCREEN_HEIGHT // 2 + self.player['height'] // 2
            camera_x = max(0, min(camera_x, self.current_room.room_width - SCREEN_WIDTH))
            camera_y = max(0, min(camera_y, self.current_room.room_height - SCREEN_HEIGHT))

            screen.fill((0, 0, 0))
            self.current_room.render(screen, camera_x, camera_y)

            # Draw player
            player_screen_x = self.player['x'] - camera_x
            player_screen_y = self.player['y'] - camera_y
            screen.blit(self.player['image'], (player_screen_x, player_screen_y))

            # Fade overlay
            if self.fading:
                self.fade_surface.set_alpha(self.fade_alpha)
                screen.blit(self.fade_surface, (0, 0))

            pygame.display.flip()
            clock.tick(60)
        pygame.quit()

# --- Setup the game environment ---
def setup_game():
    game = Game()
    main_room_layout = [
        "##############################################################################",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#                                     #                                      #",
        "#       #                             #                                      #",
        "#                                     #                                      #",
        "#               #                     #                                      #",
        "#                                     #                                      #",
        "#                  #                  #                                      #",
        "#       #       #                     #                                      #",
        "#                                     #                                      #",
        "#       #     #                       #                                      #",
        "#                                     #                                      #",
        "#        #                            #                                      #",
        "#         #                           #                                      #",
        "#          #                          #                                      #",
        "#           #                         #                                      #",
        "#            #                        #                                      #",
        "#             #                       #                                      #",
        "#              #                      #                                      #",
        "#              #                      #                                      #",
        "#                 #                   #               ###                    #",
        "#                #                    #               ###                    #",
        "#        ##     #                     #         ##     #                     #",
        "#     #       #                       #       #        #                     #",
        "         #                                   #        # #                     ",
        " d                                                                            ",
        "##############################################################################",
    ]
    main_room = Room("main room", main_room_layout)
    main_room.add_door(Door(1, 43, "item room"), 100, 100)
    main_room.add_door(Door(76, 43, "basic room"), 100, 100)
    game.add_room(main_room)

    item_room_layout = [
        "##############",
        "#            #",
        "#            #",
        "#             ",
        "#           d ",
        "##############",
    ]
    item_room = Room("item room", item_room_layout)
    item_room.add_door(Door(10, 4, "main room"), 100, 100)
    game.add_room(item_room)

    basic_room_layout = [
        "############",
        "#          #",
        "           #",
        " d         #",
        "############"
    ]
    basic_room = Room("basic room", basic_room_layout)
    basic_room.add_door(Door(2, 3, "main room"), 100, 50)
    game.add_room(basic_room)

    game.set_current_room("main room")
    return game

# --- Run the game ---
if __name__ == "__main__":
    game = setup_game()
    game.run()