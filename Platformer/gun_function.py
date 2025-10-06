import threading
import time
import random
import os
import game_to_png
import sys
import termios
import tty
import threading
import queue
import smtplib

# Event to signal the input thread to stop
stop_event = threading.Event()
# Thread-safe queue for key presses
key_queue = queue.Queue()
# Dictionary to track the state of held keys
key_state = {key: False for key in ["w", "a", "s", "d", " ","*","/","1","2","3","4","5","6","7","8","9","0","f","r","~"]}

def getch():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch

def get_input_thread():
	"""
	Continuously reads keypresses and updates the key state.
	"""
	while not stop_event.is_set():
		try:
			key_input = getch()
			
			# Use lock to prevent race conditions when updating key_state
			# NOTE: Python's queue is thread-safe, so a lock is not strictly needed for this.
			if key_input in key_state or key_input in ("q", '\x03', 'k'):
				key_queue.put(key_input)
			elif key_input == 'q' or key_input == '\x03':  # 'q' or Ctrl+C
				stop_event.set()
				key_queue.put(None)  # Sentinel to unblock the main loop
				return
		except (IOError, termios.error):
			stop_event.set()
			return
			

def start_input_thread():
	"""Sets up and starts the input thread."""
	input_thread1 = threading.Thread(target=get_input_thread, daemon=True)
	input_thread2 = threading.Thread(target=get_input_thread, daemon=True)
	input_thread3 = threading.Thread(target=get_input_thread, daemon=True)
	input_thread1.start()
	input_thread2.start()
	input_thread3.start()
	if input_thread1==None and input_thread2 != None:
		input_thread1=input_thread2
	elif input_thread1==None and input_thread2 == None and input_thread3 != None:
		input_thread1 = input_thread3
	else:
		input_thread1=input_thread1
	return input_thread1

def get_key():
	"""
	Checks the queue for a new keypress and returns it.
	Returns None if no key was pressed.
	"""
	try:
		# Use get_nowait() to check for input without blocking
		return key_queue.get_nowait()
	except queue.Empty:
		return None
# Variables
botton_status=[True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True]
on_ground=True
move_left=True
move_right=True
invincible =False
win=False
debugging = False
vol=0
curant_pos =" "
playerx = 2
playery = 40 # Initial player y-position (adjusted for the ground)
savex = 2
savey = playery
curant_pos_prev = None
move=""
pause=False
#the board
board=[

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
"                                                                         ♣                    █",
"                                                                                              █",
"                                                                                              █",
"                                                                                              █",
"███████████████████████████████████████████████████████████████████████████████████████████████",
"███████████████████████████████████████████████████████████████████████████████████████████████",
"███████████████████████████████████████████████████████████████████████████████████████████████"]
player_char="A"
BOARD_SAVE = list(board)
bullets=[]
BOARD_HEIGHT = len(board)
BOARD_WIDTH = len(board[0])
VIEW_HEIGHT=50
VIEW_WIDTH=95
upgrade=[False]
button_on=["⑴","⑵","⑶","⑷","⑸","⑹","⑺","⑻","⑼","⑽","⑾","⑿","⒀","⒁","⒂","⒃","⒄","⒅","⒆","⒇"]
ground_on=["➊","➋","➌","➍","➎","➏","➐","➑","➒","➓","⓫","⓬","⓭","⓮","⓯","⓰","⓱","⓲","⓳","⓴"]
ground_off=["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫","⑬","⑭","⑮","⑯","⑰","⑱","⑲","⑳"]

def player_aim(direction):
	global player_char
	global upgrade
	if direction=="8" and upgrade[0]==False:
		player_char="E"
	if direction=="9" and upgrade[0]==False:
		player_char="C"
	if direction=="7" and upgrade[0]==False:
		player_char="D"
	if direction=="6" and upgrade[0]==False:
		player_char="A"
	if direction=="4" and upgrade[0]==False:
		player_char="B"
	if direction=="3" and upgrade[0]==False:
		player_char="G"
	if direction=="2" and upgrade[0]==False:
		player_char="I"
	if direction=="1" and upgrade[0]==False:
		player_char="H"
	if direction=="8" and upgrade[0]==True:
		player_char="X"
	if direction=="9" and upgrade[0]==True:
		player_char="V"
	if direction=="7" and upgrade[0]==True:
		player_char="W"
	if direction=="6" and upgrade[0]==True:
		player_char="T"
	if direction=="4" and upgrade[0]==True:
		player_char="U"
	if direction=="3" and upgrade[0]==True:
		player_char="Z"
	if direction=="2" and upgrade[0]==True:
		player_char="b"
	if direction=="1" and upgrade[0]==True:
		player_char="a"
enemies=[]
enemy_location = {}
enemy_dificulty=[]
def check_enemy_atack():
	global board, board_val, enemies, bullets, playerx, playery, invincible
	# Check for bullet-enemy collisions
	new_bullets = []
	for b in bullets:
		hit_enemy = False
		for e in enemies:
			if b["y"] == e["y"] and b["x"] == e["x"]:
				hit_enemy = True
				# Remove enemy from board
				board[e["y"]] = board[e["y"]][:e["x"]] + " " + board[e["y"]][e["x"]+1:]
				enemies.remove(e)
				break
		if not hit_enemy:
			new_bullets.append(b)
	bullets = new_bullets
	
	# Check for enemy-player collisions
	for e in enemies:
		if e["y"] == playery and e["x"] == playerx:
			if not invincible:
				print("You were hit by an enemy!")
				time.sleep(0.5)
				playerx = savex
				playery = savey
				invincible = True

def move_bullet(direction=None):
	global board, board_val, bullets
	# Remove all bullets from board
	for b in bullets:
		y, x = b["y"], b["x"]
		if 0 <= y < BOARD_HEIGHT and 0 <= x < BOARD_WIDTH:
			if board[y][x] == "•":
				board[y] = board[y][:x] + " " + board[y][x+1:]
	# Move bullets
	new_bullets = []
	for b in bullets:
		ny, nx = b["y"] + b["dy"], b["x"] + b["dx"]
		if 0 <= ny < BOARD_HEIGHT and 0 <= nx < BOARD_WIDTH:
			if board_val[ny][nx] != "g" and not check_ground(board_val[ny][nx]):
				board[ny] = board[ny][:nx] + "•" + board[ny][nx+1:]
				new_bullets.append({"y": ny, "x": nx, "dy": b["dy"], "dx": b["dx"]})
	bullets = new_bullets
	board_val = board_eval(board, botton_status)
def move_enemy():
	global board
	global board_val
	global enemies
	global playerx
	global playery
	new_enemies = []
	for e in enemies:
		ey, ex = e["y"], e["x"]
		if 0 <= ey < BOARD_HEIGHT and 0 <= ex < BOARD_WIDTH:
			if board[ey][ex] == "E":
				board[ey] = board[ey][:ex] + " " + board[ey][ex+1:]
		# Simple AI: Move towards the player if on the same row
		if ey == playery:
			if ex < playerx and ex + 1 < BOARD_WIDTH and board_val[ey][ex + 1] != "g" and not check_ground(board_val[ey][ex + 1]):
				ex += 1
			elif ex > playerx and ex - 1 >= 0 and board_val[ey][ex - 1] != "g" and not check_ground(board_val[ey][ex - 1]):
				ex -= 1
		# Add enemy back to board at new position
		if 0 <= ey < BOARD_HEIGHT and 0 <= ex < BOARD_WIDTH:
			if board[ey][ex] == " ":
				board[ey] = board[ey][:ex] + "E" + board[ey][ex+1:]
				new_enemies.append({"y": ey, "x": ex})
enemy_vol=[]
def jump_enemy(enemy_index):
	global board
	global board_val
	global enemies
	global enemy_vol
	if 0 <= enemy_index < len(enemies):
		e = enemies[enemy_index]
		ey, ex = e["y"], e["x"]
		if 0 <= ey < BOARD_HEIGHT and 0 <= ex < BOARD_WIDTH:
			if board[ey][ex] == "E":
				board[ey] = board[ey][:ex] + " " + board[ey][ex+1:]
		# Jump logic
		if ey > 0 and (board_val[ey - 1][ex] != "g" and not check_ground(board_val[ey - 1][ex])):
			ey -= 1  # Move up
			# Simulate gravity
			while ey + 1 < BOARD_HEIGHT and (board_val[ey + 1][ex] != "g" and not check_ground(board_val[ey + 1][ex])):
				ey += 1
		# Add enemy back to board at new position
		if 0 <= ey < BOARD_HEIGHT and 0 <= ex < BOARD_WIDTH:
			if board[ey][ex] == " ":
				board[ey] = board[ey][:ex] + "E" + board[ey][ex+1:]
				enemies[enemy_index] = {"y": ey, "x": ex}
def enemy_logic(dificulty,playerx,playery,enemy_x,enemy_y,enemy_vol):
	global board
	global board_val
	global enemies
	shoot_chance = random.randint(1, 10)
	if dificulty == "easy":
		if shoot_chance > 8:
			aim=logic_for_aiming(playerx,playery,enemy_x,enemy_y)
			shoot(enemy_x, enemy_y, aim)
			return (0, 0)  # No movement when shooting
		else:
			if enemy_x < playerx:
				return (0, 1)  # Move right
			elif enemy_x > playerx:
				return (0, -1)  # Move left
			elif enemy_y < playery:
				jump_enemy(enemys.index({"y": enemy_y, "x": enemy_x}))
	elif dificulty == "medium":
		if shoot_chance > 6:
			aim=logic_for_aiming(playerx,playery,enemy_x,enemy_y)
			shoot(enemy_x, enemy_y, aim)
			return (0, 0)  # No movement when shooting
		else:
			if enemy_x < playerx:
				return (0, 1)  # Move right
			elif enemy_x > playerx:
				return (0, -1)  # Move left
			elif enemy_y < playery:
				jump_enemy(enemys.index({"y": enemy_y, "x": enemy_x}))
def logic_for_aiming(playerx,playery,enemy_x,enemy_y):
	if playerx > enemy_x and playery == enemy_y:
		return "A"  # right
	elif playerx < enemy_x and playery == enemy_y:
		return "B"  # left
	elif playerx > enemy_x and playery < enemy_y:
		return "C"  # up-right
	elif playerx < enemy_x and playery < enemy_y:
		return "D"  # up-left
	elif playerx == enemy_x and playery < enemy_y:
		return "E"  # up
	elif playerx > enemy_x and playery > enemy_y:
		return "F"  # down-right
	elif playerx < enemy_x and playery > enemy_y:
		return "G"  # down-left
	elif playerx == enemy_x and playery > enemy_y:
		return "I"  # down
	else:
		return None  # No valid direction
def shoot(x,y,aim):
	global board
	global board_val
	global upgrade
	if aim==None:
		aim = "6"
	global bullets
	direction_map = {
		"A": (0, 1),   # right
		"B": (0, -1),  # left
		"C": (-1, 1),   #up-right
		"D": (-1, -1),  # up-left
		"E": (-1, 0),  # up
		"F": (1, 1),   # down-right
		"G": (1, 1), # up-left
		"H": (1, -1),  # down-left
		"I": (1, 0),  # down
	}
	if player_char in direction_map:
		dy, dx = direction_map[player_char]
		by, bx = y + dy, x + dx
		if 0 <= by < BOARD_HEIGHT and 0 <= bx < BOARD_WIDTH:
			if board_val[by][bx] != "g" and not check_ground(board_val[by][bx]):
				board[by] = board[by][:bx] + "•" + board[by][bx+1:]
				bullets.append({"y": by, "x": bx, "dy": dy, "dx": dx})
				board_val = board_eval(board, botton_status)
#needs to be worked on
def spawn_enemy(spawn_x, spawn_y):
	global board
	global board_val
	global enemies
	if board[spawn_y][spawn_x] == " ":
		board[spawn_y] = board[spawn_y][:spawn_x] + "E" + board[spawn_y][spawn_x+1:]
		enemy_location = {"y": spawn_y, "x": spawn_x}
		if enemy_location not in enemies:
			enemies.append(enemy_location)
		board_val = board_eval(board, botton_status)
def check_ground(check_cord):
	if check_cord  in ground_on:
		return True
	else:
		return False
### this is where errors happen ###
def spawn_boss(spawn_x, spawn_y,char):
	global board
	global board_val
	global enemies
	if board[spawn_y][spawn_x] == " ":
		board[spawn_y] = board[spawn_y][:spawn_x] + char + board[spawn_y][spawn_x+1:]
		enemy_location = {"y": spawn_y, "x": spawn_x}
		if enemy_location not in enemies:
			enemies.append(enemy_location)
		board_val = board_eval(board, botton_status)
boss_1_sprite_idle=[[
"""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
["""         __        _      """,
"""       _/  \    _(\(o	 """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""  ^      _/   _\ )        """,
"""  \^^--^^ __-^ /(__       """,
"""   ^----^^    "^--v'      """],
["""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
["""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
""" /\ \ \_!  / __!          """,
"""|  | \!   /    \          """,
"""\  \   _/   _\ )          """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
]
boss_1_sprite_atack_single=[[
"""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
["""      __        _         """,
"""     _/  \    _(\(o___    """,
"""    /     \  /  _ /^^^o   """,
"""   _/  !   \/  ! '\vvv    """,
"""  !  !  \ _' ( \____      """,
"""  ! . \ _!\   \===^\)     """,
"""   \ \_!  \ __\           """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
["""         __        _      """,
"""       _/  \    _(\(o___  """,
"""      /     \  /  _/^^^o  """,
"""     _/  !   \/  ! \vvvv' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
["""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
]
boss_atack_spray=[[
"""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
[
"""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' (     /-^  """,
"""    ! . \ _!\   \====-^   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
[
"""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \____    """,
"""    ! . \ _!\   \===^\)   """,
"""     \ \_!  / __!         """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """],
[
"""         __        _      """,
"""       _/  \    _(\(o     """,
"""      /     \  /  _  ^^^o """,
"""     _/  !   \/  ! '!!!v' """,
"""    !  !  \ _' ( \_       """,
"""    ! . \ _!\   \===-^    """,
"""     \ \_!  / __!  \^     """,
"""      \!   /    \         """,
"""(\_      _/   _\ )        """,
""" \ ^^--^^ __-^ /(__       """,
"""  ^^----^^    "^--v'      """]]
boss_2_sprite_idle=[[
"""          v  """,
"""    (__)v | v""",
"""    /\/\\_|_/""",
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  /)))-(  |  """,
""" / /^ ^ \ |  """,
"""/  )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  |  """],
[
"""          v  """,
"""    (__)v | v""",
"""    /\/\\_|_/""",
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  7)))-(  |  """,
""" ( /^ ^ \ |  """,
"""%  )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  |  """],
[
"""          v  """,
"""    (__)v | v""",
"""    /\/\\_|_/""",
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  /)))-(  |  """,
""" / /^ ^ \ |  """,
"""/  )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  |  """],
[
"""          v  """,
"""    (__)v | v""",
"""    /\/\\_|_/""",
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  |)))-(  |  """,
"""  //^ ^ \ |  """,
""" < )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  |  """],]
boss_2_sprite_atack_spray=[[
"""          v  """,
"""    (__)v | v""",
"""    /\/\\_|_/""",
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  /)))-(  |  """,
""" / /^ ^ \ |  """,
"""/  )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  |  """],[
"""		     v  """,
"""        v | v""",
"""    (__)\_|_/""",
"""    /\/\  |  """,
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  /)))-(  |  """,
""" / /^ ^ \ |  """,
"""/  )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  v  """],[
"""          v  """,
"""		   v | v""",
"""        \_|_/  """,
"""    (__)  |  """,
"""    /\/\  |  """,
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  /)))-(  |  """,
""" / /^ ^ \ |  """,
"""/  )^/\^( |  """,
""")_//`__>> v  """,
"""  #   #`     """],[
"""          v  """,
"""    (__)v | v""",
"""    /\/\\_|_/""",
"""   _\__/  |  """,
"""  /  \/`\<`) """,
"""  \ (  |\_/  """,
"""  /)))-(  |  """,
""" / /^ ^ \ |  """,
"""/  )^/\^( |  """,
""")_//`__>> |  """,
"""  #   #`  |  """]]
boss_2_sprite_single_atack=boss_2_sprite_atack_spray
boss_3_sprite=[[
"""    .-.    """,
"""   (0.o)   """,
"""    |=|    """,
"""   __|__   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],[
"""           """,
"""    .-.    """,
"""   (o.0)   """,
"""   _|=|_   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],[
"""    .-.    """,
"""   (0.o)   """,
"""    |=|    """,
"""   __|__   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],[
"""           """,
"""    .-.    """,
"""   (o.0)   """,
"""   _|=|_   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],]
boss_3_sprite_atack_spray=[[
"""    .-.    """,
"""   (0.o)   """,
"""    |=|    """,
"""   __|__   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],[
"""    .-.         """,
"""   (o.0)        """,
"""    |=|         """,
"""   __|__        """,
""" //.=|=.=\\     """,
"""// .=|=.  \\    """,
"""\\ .=|=.  //    """,
""" \\(_=_)  )     """,
"""  (:| |:        """,
"""   || ||        """,
"""   () ()        """,
"""   || ||        """,
"""   || ||        """,
"""  ==' '==       """],[
"""    .-.         """,
"""   (0.o)        """,
"""    |=|     (    """,
"""   __|__   //   """,
""" //.=|=.==//    """,
"""// .=|=.        """,
"""\\ .=|=.        """,
""" \\(_=_)        """,
"""  (:| |:        """,
"""   || ||        """,
"""   () ()        """,
"""   || ||        """,
"""   || ||        """,
"""  ==' '==       """],[
"""    .-.    """,
"""   (o.0)   """,
"""    |=|    """,
"""   __|__   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],]
boss_3_sprite_atack_single=[[
"""    .-.    """,
"""   (0.o)   """,
"""    |=|    """,
"""   __|__   """,
""" //.=|=.\\ """,
"""// .=|=. \\""",
"""\\ .=|=. //""",
""" \\(_=_)// """,
"""  (:| |:)  """,
"""   || ||   """,
"""   () ()   """,
"""   || ||   """,
"""   || ||   """,
"""  ==' '==  """],[
"""          .-.       """,
"""         (o.0)      """,
"""          |=|       """,
"""         __|__      """,
"""       //.=|=//     """,
"""      // .=|//      """,
"""     //  .=#=.      """,
"""    //   ===_)      """,
"""    (   ):| |:      """,
"""         || ||      """,
"""         () ()      """,
"""         || ||      """,
"""         || ||      """,
"""        ==' '==     """],[
"""          .-.       """,
"""         (o.0)      """,
"""          |=|       """,
"""         __|__      """,
"""       //.=|=//     """,
"""      // .=|//      """,
"""     //  .=#=.      """,
"""    //_  ===_)      """,
"""    (|_|):| |:      """,
"""         || ||      """,
"""         () ()      """,
"""         || ||      """,
"""         || ||      """,
"""        ==' '==     """],[
"""          .-.            """,
"""         (o.0)           """,
"""          |=|            """,
"""         __|__           """,
"""         \\|=.\\         """,
"""         .\\=.  \\       """,
"""         .=|===n  ==n    """,
"""         (_=_)           """,
"""         :| |:           """,
"""         || ||           """,
"""         () ()           """,
"""         || ||           """,
"""         || ||           """,
"""        ==' '==          """],]
def spawn_big_projectile(x,y,sprite,direction):
	global board
	for i, line in enumerate(sprite):
		if 0 <= y + i < BOARD_HEIGHT:
			line_to_modify = board[y + i]
			end_index = min(x + len(line), len(line_to_modify))
			new_line = (line_to_modify[:x] + line + line_to_modify[end_index:])[:BOARD_WIDTH]
			board[y + i] = new_line
	while True:
		time.sleep(0.1)
		if direction=="down":
			y+=1
		elif direction=="up":
			y-=1
		elif direction=="left":
			x-=1
		elif direction=="right":
			x+=1
		for i, line in enumerate(sprite):
			if 0 <= y + i < BOARD_HEIGHT:
				line_to_modify = board[y + i]
				new_line = (line_to_modify[:x] + line + line_to_modify[x + len(line):])[:BOARD_WIDTH]
				board[y + i] = new_line
		if y<0 or y>=BOARD_HEIGHT or x<0 or x>=BOARD_WIDTH:
			break
		for i, line in enumerate(sprite):
			if 0 <= y + i < BOARD_HEIGHT:
				line_to_modify = board[y + i]
				new_line = (line_to_modify[:x] + " " * len(line) + line_to_modify[x + len(line):])[:BOARD_WIDTH]
				board[y + i] = new_line
def board_eval(current_board, button_status):
	global enemies
	global enemy_location
	"""Evaluates the board based on button status and returns the value grid."""
	out2 = []
	for y, row in enumerate(current_board):
		out1 = []
		for x, char in enumerate(row):
			if char == "█":
				out1.append("g")
			elif char in ["◀", "▼", "▶", "▲"]:
				out1.append("d")
			elif char == "◉":
				out1.append("s")
			elif char == "⚐":
				out1.append("w")
		out2.append(out1)
	return out2


board_val = board_eval(board, botton_status)

def get_map(inboard):
	"""Converts a list of strings into a list of lists of characters."""
	x = []
	for line in inboard:
		row = list(line)
		x.append(row)
	return x

def get_map_shown(playery, playerx):
	"""Returns a slice of the board centered around the player's position."""
	upper_bound_y = max(0, playery - VIEW_HEIGHT // 2)
	lower_bound_y = upper_bound_y + VIEW_HEIGHT
	if lower_bound_y > BOARD_HEIGHT:
		lower_bound_y = BOARD_HEIGHT
		upper_bound_y = max(0, BOARD_HEIGHT - VIEW_HEIGHT)

	upper_bound_x = max(0, playerx - VIEW_WIDTH // 2)
	lower_bound_x = upper_bound_x + VIEW_WIDTH
	if lower_bound_x > BOARD_WIDTH:
		lower_bound_x = BOARD_WIDTH
		upper_bound_x = max(0, BOARD_WIDTH - VIEW_WIDTH)

	visible_map_str = []
	for y in range(upper_bound_y, lower_bound_y):
		line = board[y][upper_bound_x:lower_bound_x]
		visible_map_str.append(line)
	
	return visible_map_str, upper_bound_x, upper_bound_y


def print_buffer(buffer):
	"""outputs the game board to a png file useing the game_to_png file"""
	for line in buffer:
		print("".join(line))
	if not pause:
		game_to_png.convert_board_char(buffer, 'game_output.png')

def board_game_loop(playerx, playery):
	global player_char
	global debugging
	"""Renders the game board with the player and handles boundary checks."""
	visible_map_str, view_x_start, view_y_start = get_map_shown(playery, playerx)
	buffer = get_map(visible_map_str)
	
	local_playery = playery - view_y_start
	local_playerx = playerx - view_x_start

	# Ensure player position is within the buffer boundaries
	if 0 <= local_playery < len(buffer) and 0 <= local_playerx < len(buffer[local_playery]):
		buffer[local_playery][local_playerx] = player_char
email_sent=False
email_count=0
reccored=False
cooldown=0
if debugging:
	print(f"""botton_status:{botton_status}
on_ground:{on_ground}
move_left:{move_left}
move_right:{move_right}
invincible:{invincible}
win:{win}
debugging:{debugging}
vol:{vol}
curant_pos:{curant_pos}
playerx:{playerx}
playery:{playery}
savex:{savex}
savey:{savey}
curant_pos_prev:{curant_pos_prev}
move:{move}
pause:{pause}
recording?:{reccored}
email sent:{email_sent}
email count:{email_count}""")
debug_log=[]
tic=0
cooldown=0
# Main game loop
while True:
	tic+=1
	try:
		input_thread = start_input_thread()
		print("Program started. Press WASD. Press Ctrl+C to exit.")
		
		curant_pos_prev = None
		
		while not stop_event.is_set():
			move = get_key()
			
			current_board = list(BOARD_SAVE) # Reset the board to the original state
			# --- handle debugging ---
			
			if move =="*":
				debugging=not debugging
				print(f"debugging {debugging}")

			# --- Handle Jump and Vertical Movement ---
			if move == "f" and debugging:
				vol+=.5
			if move == "w" and on_ground:
				vol = .5
				
			# Apply gravity
			if vol > -2:
				vol -= .125

			# Check for a collision on the next Y position
			if vol != 0:
				step_direction = -1 if vol > 0 else 1
				
				for i in range(int(abs(vol * 2)) + 1): # A bit more granular check
					next_y = playery + step_direction * (i / 2)
					if 0 <= next_y < BOARD_HEIGHT:
						if board_val[int(next_y)][playerx] == "g" or check_ground(board_val[int(next_y)][playerx]):
							vol = 0
							break
			next_y = playery
			if vol > 0:
				next_y = max(0, playery - 1)
			elif vol < 0:
				next_y = min(BOARD_HEIGHT - 1, playery + 1)

			# --- Handle Horizontal Movement ---
			next_x = playerx
			if move == "k":
				print("you died")
				playerx = savex
				playery = savey
			if move == "5" and cooldown==0:
				cooldown=5
				# Use the current aim direction based on player_char
				shoot(playerx, playery, player_char)
				shoot(playerx,playery,player_aim)
			
			if cooldown>0:
				cooldown-=1
			if move == "a" and move_left:
				next_x = max(0, playerx - 1)
			if move in ["1","2","3","4","5","6","7","8","9","0"]:
				player_aim(move)
			if move == "d" and move_right:
				next_x = min(BOARD_WIDTH - 1, playerx + 1)
			if board_val[playery][next_x] != "g" and not check_ground(board_val[playery][next_x]):
				next_x = min(BOARD_WIDTH - 1, playerx + 1)
			if board_val[playery][next_x] != "g" or not check_ground(board_val[playery][next_x]):
				if board_val[next_y][next_x]!="g":
					playery=next_y
					playerx = next_x
				elif board_val[next_y][playerx]!="g":
					playery=next_y
				elif board_val[playery][next_x]!="g":
					playerx=next_x

			# --- Update Collision Flags ---
			# Check if the player is on the ground
			on_ground = (playery + 1 < BOARD_HEIGHT and board_val[playery + 1][playerx] == "g") or check_ground(board_val[playery+1][playerx])

			if playerx > 0:
				move_left = board_val[playery][playerx - 1] != "g" and not check_ground(board_val[playery][playerx-1])
			else:
				move_left = False

			if playerx < BOARD_WIDTH - 1:
				move_right = board_val[playery][playerx + 1] != "g" and not check_ground(board_val[playery][playerx+1])
			else:
				move_right = False

			
			# --- Render the Game Frame ---
			board_game_loop(playerx, playery)
			
			# --- Check for Game Events ---
			move_bullet()
			move_enemy()
			check_enemy_atack()
			curant_pos = board_val[playery][playerx]
			if curant_pos.startswith("B") and curant_pos != curant_pos_prev:
				count = int(curant_pos[1:])
				botton_status[count] = not botton_status[count]
				board_val = board_eval(current_board, botton_status)
				if botton_status[count]:
					text_status="on"
				else:
					text_status="off"
				print(f"button {count+1} {text_status}")
				time.sleep(.5)
			curant_pos_prev = curant_pos
			
			if curant_pos == "d" and invincible==False:
				print("You died!")
				time.sleep(0.5)
				playerx = savex
				playery = savey
				vol = 0
			if curant_pos == "s":
				savex = playerx
				savey = playery
			if curant_pos == "w":
				win = True
				break
			time.sleep(0.075)
				
	except KeyboardInterrupt:
		print("Ctrl+C detected. Shutting down...")
		quit()
	finally:
		stop_event.set()
		if 'input_thread' in locals() and input_thread.is_alive():
			input_thread.join(timeout=1)
	if win:
		break
print("you win")