import os
import time
from PIL import Image as im
from term_image.image import from_file

# Constants
GRID_SIZE = 700
PNG_FOLDER = 'png printer/pngs'

# Load images
def load_image_with_path(filename):
	path = os.path.join(PNG_FOLDER, filename)
	return im.open(path).convert('RGBA')

# Tile types
tile_types = {
	'floor': 'all_side_grass.png',
	'wall': 'all_side_grass.png',
	'decor': 'all_side_grass.png'
}

# Entity images
PNG = {
	'enemy': 'enemy.png',
	'player': 'player.png',
	'spike': 'spike.png',
	'item': 'item.png'
}

# ------------------ Helper functions ------------------

def create_composite(objects):
	max_width = 0
	max_height = 0
	images = []

	# Load images and determine size
	for filename, x, y in objects:
		img = load_image_with_path(filename)
		images.append((img, x, y))
		max_width = max(max_width, int(x + img.width))
		max_height = max(max_height, int(y + img.height))
	
	# Create a transparent base image with exact size
	base = im.new('RGBA', (max_width, max_height), (0, 0, 0, 0))
	
	for img, x, y in images:
		# Ensure paste position is integers
		paste_x = int(x)
		paste_y = int(y)
		# Paste with alpha mask for transparency
		base.paste(img, (paste_x, paste_y), img)
	
	return base


def print_image_in_terminal(image):
	temp_path = 'temp_composite.png'
	image.save(temp_path)
	img = from_file(temp_path)
	img.draw()
	os.remove(temp_path)

def print_objs(objects_to_place):
	composite_image = create_composite(objects_to_place)
	print_image_in_terminal(composite_image)

# ------------------ Entity creation ------------------

def create_entity(x, y, width, height, entity_type, png_filename):
	return {
		'x': float(x),
		'y': float(y),
		'width': width,
		'height': height,
		'type': entity_type,
		'png': png_filename
	}

# ------------------ Room and Door classes ------------------

class Door:
	def __init__(self, rotation, x, y, destination, requirement=None):
		self.rotation = rotation  # 'up', 'down', 'left', 'right'
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
		self.blocks = blocks if blocks else []  # List of (x, y) as integers
		self.doors = []  # List of Door objects
		self.entities = []

	def add_entity(self, entity):
		self.entities.append(entity)

	def remove_entity(self, entity):
		if entity in self.entities:
			self.entities.remove(entity)

	def add_door(self, rotation, x, y, destination, requirement=None):
		door = Door(rotation, x, y, destination, requirement)
		self.doors.append(door)

	def get_door_at(self, x, y):
		for door in self.doors:
			if door.is_at_position(x, y):
				return door
		return None

	def get_blocks(self):
		return self.blocks

	def render(self):
		objs = []
		# Draw blocks
		for (x, y) in self.blocks:
			filename = tile_types['wall']
			objs.append((filename, x * GRID_SIZE, y * GRID_SIZE))
		# Draw entities
		for e in self.entities:
			objs.append((e['png'], e['x'], e['y']))
		print(f"\n--- {self.name} ---")
		print_objs(objs)

# ------------------ Map and Player ------------------

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

# ------------------ Main Game Logic ------------------

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
		self.player = create_entity(x, y, GRID_SIZE, GRID_SIZE, 'player', PNG['player'])
		self.current_room.add_entity(self.player)

	def move_entity(self, entity, target_x, target_y, duration=1.0):
		start_x, start_y = entity['x'], entity['y']
		steps = int(duration * 50)
		for step in range(steps):
			t = (step + 1) / steps
			new_x = start_x + (target_x - start_x) * t
			new_y = start_y + (target_y - start_y) * t
			test_entity = {'x': new_x, 'y': new_y, 'width': entity['width'], 'height': entity['height']}
			if check_tile_collision(test_entity, self.current_room) or check_entity_collision(test_entity, self.current_room, exclude_entity=entity):
				break
			entity['x'], entity['y'] = new_x, new_y
			self.current_room.render()
			time.sleep(1/50)

	def switch_room(self, room_name, entry_x, entry_y):
		self.current_room.remove_entity(self.player)
		self.set_current_room(room_name)
		self.player['x'] = entry_x
		self.player['y'] = entry_y
		self.current_room.add_entity(self.player)
		self.current_room.render()

	def check_for_door_and_transition(self):
		door = self.current_room.get_door_at(self.player['x'], self.player['y'])
		if door:
			if door.can_open(self.player):
				print(f"Opening door to {door.destination}")
				self.switch_room(door.destination, door.x, door.y)
			else:
				print(f"Door requires: {door.requirement}")

	def run(self):
		# Example game loop with simple controls
		import sys
		while True:
			self.current_room.render()
			self.map.display()
			print(f"Health: {self.player['health']}/{self.player['max_health']}")
			print("Enter command: w/a/s/d to move, q to quit")
			cmd = input().lower()
			if cmd == 'q':
				break
			elif cmd == 'w':
				new_x = self.player['x']
				new_y = self.player['y'] - GRID_SIZE
			elif cmd == 's':
				new_x = self.player['x']
				new_y = self.player['y'] + GRID_SIZE
			elif cmd == 'a':
				new_x = self.player['x'] - GRID_SIZE
				new_y = self.player['y']
			elif cmd == 'd':
				new_x = self.player['x'] + GRID_SIZE
				new_y = self.player['y']
			else:
				continue

			# Move smoothly
			self.move_entity(self.player, new_x, new_y, duration=0.2)
			# Check for door
			self.check_for_door_and_transition()
			# Example: simulate damage
			# self.player['health'] -= 5
			# if self.player['health'] <= 0:
			#     print("Game Over!")
			#     break

# ------------------ Helper collision functions ------------------

def check_tile_collision(entity, room):
	left = int(entity['x'] / GRID_SIZE)
	right = int((entity['x'] + entity['width']) / GRID_SIZE)
	top = int(entity['y'] / GRID_SIZE)
	bottom = int((entity['y'] + entity['height']) / GRID_SIZE)
	for (x, y) in room.get_blocks():
		if (x >= left and x <= right) and (y >= top and y <= bottom):
			rect = {'x': x * GRID_SIZE, 'y': y * GRID_SIZE, 'width': GRID_SIZE, 'height': GRID_SIZE}
			if detect_collision(entity, rect):
				return True
	return False

def check_entity_collision(entity, room, exclude_entity=None):
	for e in room.entities:
		if e != exclude_entity:
			if detect_collision(entity, e):
				return True
	return False

def detect_collision(entityA, entityB):
	ax1, ay1 = entityA['x'], entityA['y']
	ax2, ay2 = ax1 + entityA['width'], ay1 + entityA['height']
	bx1, by1 = entityB['x'], entityB['y']
	bx2, by2 = bx1 + entityB['width'], by1 + entityB['height']
	if ax2 >= bx1 and ax1 <= bx2 and ay2 >= by1 and ay1 <= by2:
		if (ax2 == bx1 or ax1 == bx2) and (ay1 < by2 and ay2 > by1):
			return True
		if (ay2 == by1 or ay1 == by2) and (ax1 < bx2 and ax2 > bx1):
			return True
	return False

# ------------------ Setup game data ------------------

def setup_game():
	game = Game()

	# Create rooms
	main_room = Room('MainRoom', blocks=[(1,1), (2,2), (3,3)])
	item_room = Room('ItemRoom', blocks=[(5,5), (6,6), (7,7)])

	# Add doors with facing directions and requirements
	main_room.add_door('left', 0, 7, 'ItemRoom', requirement=None)
	item_room.add_door('right', 19, 7, 'MainRoom', requirement=None)

	# Example locked door requiring missile
	secret_room = Room('SecretRoom', blocks=[(10,10)])
	secret_room.add_door('down', 10, 0, 'MainRoom', requirement='missile')
	main_room.add_door('up', 10, 0, 'SecretRoom', requirement='missile')

	# Add some items (simulate pickups)
	# For simplicity, just add 'missile' in items list
	# You can expand with item pickups mechanics

	# Add rooms to game
	game.add_room(main_room)
	game.add_room(item_room)
	game.add_room(secret_room)

	game.set_current_room('MainRoom')

	# Create player
	game.create_player(2 * GRID_SIZE, 7 * GRID_SIZE)

	return game

# ------------------ Run the game ------------------

if __name__ == "__main__":
	game = setup_game()
	game.run()