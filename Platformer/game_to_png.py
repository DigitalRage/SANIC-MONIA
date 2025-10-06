import random
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.colors as mcolors
import matplotlib.cm as cm
import io
import base64
import textwrap
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.preprocessing import StandardScaler
import os
import math
class color:
   PURPLE = '\033[95m'
   CYAN = '\033[96m'
   DARKCYAN = '\033[36m'
   BLUE = '\033[94m'
   GREEN = '\033[92m'
   YELLOW = '\033[93m'
   RED = '\033[91m'
   BOLD = '\033[1m'
   UNDERLINE = '\033[4m'
   END = '\033[0m'
def get_color(char):
	compare_chars=["🟥","🟪","🟦","🟩","🟨","🟧"]
	colors = ["red", "purple", "blue", "green", "yellow", "orange"]
	if char in compare_chars:
		return colors[compare_chars.index(char)]
class goround_tiles:
	grass = """🟩🟩🟩🟩
🟩🟩🟩🟩
🟩🟩🟩🟩
🟩🟩🟩🟩"""
	water= """🟦🟦🟦🟦
 🟦🟦🟦🟦
 🟦🟦🟦🟦
 🟦🟦🟦🟦"""
	spike = """    
 ⬜⬜ 
 ⬜⬜ 
⬜⬜⬜⬜"""
	empty = """    
    
    
    """
	button = """    
    
 🟥🟥 
⬛⬛⬛⬛"""

class sprites:
	player_up_faceing_left = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_up_faceing_right = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_down_facing_left = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_down_facing_right = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_left = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_right = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_up_left ="""🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_up_right = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_down_left = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	player_down_right = """🟥🟥🟥🟥
	🟥🟦🟦🟥
	🟥🟦🟦🟥
	🟥🟥🟥🟥"""
	sprite_idle = """🟩🟩🟩🟩
	🟩🟦🟦🟩
	🟩🟦🟦🟩
	🟩🟩🟩🟩"""

def char_to_sprite(char,xlocation,ylocation,size,path=None):
	if char == "UL":
		sprite = sprites.player_up_left
	elif char == "UR":
		sprite = sprites.player_up_right
	elif char == "DL":
		sprite = sprites.player_down_left
	elif char == "DR":
		sprite = sprites.player_down_right
	elif char == "UFL":
		sprite = sprites.player_up_faceing_left
	elif char == "UFR":
		sprite = sprites.player_up_faceing_right
	elif char == "DFL":
		sprite = sprites.player_down_facing_left
	elif char == "DFR":
		sprite = sprites.player_down_facing_right
	elif char == "L":
		sprite = sprites.player_left
	elif char == "R":
		sprite = sprites.player_right
	else:
		sprite = sprites.sprite_idle
	sprite = sprite.split("\n")
	sprite = [line.strip() for line in sprite]
	sprite_height = len(sprite)
	sprite_width = len(sprite[0])
	image = Image.new("RGBA", (sprite_width * size, sprite_height * size), (0, 0, 0, 0))
	draw = ImageDraw.Draw(image)
	for y, line in enumerate(sprite):
		for x, char in enumerate(line):
			color = get_color(char)
			if color:
				draw.rectangle([x * size, y * size, (x + 1) * size, (y + 1) * size], fill=color)
	if path:
		image.save(path)
	return image
def board_to_image(board,cell_size,path=None):
	board_height = len(board)
	board_width = len(board[0])
	image = Image.new("RGBA", (board_width * cell_size, board_height * cell_size), (0, 0, 0, 0))
	draw = ImageDraw.Draw(image)
	for y, line in enumerate(board):
		for x, char in enumerate(line):
			tile = convert_board_char(char)
			tile = tile.split("\n")
			tile = [line.strip() for line in tile]
			for ty, tline in enumerate(tile):
				for tx, tchar in enumerate(tline):
					color = get_color(tchar)
					if color:
						draw.rectangle([x * cell_size + tx * (cell_size // 4), y * cell_size + ty * (cell_size // 4), x * cell_size + (tx + 1) * (cell_size // 4), y * cell_size + (ty + 1) * (cell_size // 4)], fill=color)
	if path:
		image.save(path)
	return image
def monster_to_sprite(monster,xlocation,ylocation,size,path=None):
	sprite = monster["sprite"]
	sprite = sprite.split("\n")
	sprite = [line.strip() for line in sprite]
	sprite_height = len(sprite)
	sprite_width = len(sprite[0])
	image = Image.new("RGBA", (sprite_width * size, sprite_height * size), (0, 0, 0, 0))
	draw = ImageDraw.Draw(image)
	for y, line in enumerate(sprite):
		for x, char in enumerate(line):
			color = get_color(char)
			if color:
				draw.rectangle([x * size, y * size, (x + 1) * size, (y + 1) * size], fill=color)
	if path:
		image.save(path)
	return image
def combine_images(images,layout,order_of_layyers=['forground','player','monsters','ground','backround'],path=None):
	if layout:
		width = layout['width']
		height = layout['height']
	else:
		width = max([img['x'] + img['image'].width for img in images])
		height = max([img['y'] + img['image'].height for img in images])
	final_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
	sorted_images = sorted(images, key=lambda x: order_of_layyers.index(x['layer']) if x['layer'] in order_of_layyers else len(order_of_layyers))
	for img in sorted_images:
		final_image.paste(img['image'], (img['x'], img['y']), img['image'])
	if path:
		final_image.save(path)
	return final_image
#testing
char_to_sprite("UL",0,0,50,"test_sprite.png")
board = [
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"███████████████████████████████████████████████████████████████████████████████████████████████",
"███████████████████████████████████████████████████████████████████████████████████████████████",
"███████████████████████████████████████████████████████████████████████████████████████████████"]
def convert_board_char(char):
	if char == " ":
		return goround_tiles.empty
	elif char == "█":
		return goround_tiles.grass
	elif char == "~":
		return goround_tiles.water
	elif char in ["◀", "▼", "▶", "▲"]:
		return goround_tiles.spike
board_to_image(board,50,"test_board.png")
monster = {
	"name": "Goblin",
	"sprite": """🟩🟩🟩🟩
🟩🟩🟩🟩
🟩🟩🟩🟩
🟩🟩🟩🟩"""
}
monster_to_sprite(monster,0,0,50,"test_monster.png")
images = [
	{"image": board_to_image(board,50), "x": 0, "y": 0, "layer": "ground"},
	{"image": char_to_sprite("UL",0,0,50), "x": 100, "y": 100, "layer": "player"},
	{"image": monster_to_sprite(monster,0,0,50), "x": 200, "y": 200, "layer": "monsters"}]
combine_images(images,layout=None,path="test_combined.png")