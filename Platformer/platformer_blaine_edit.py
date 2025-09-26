import threading
import time
import os
import queue
import readchar
from the_board import board  # Make sure this file exists and defines `board`

# Input handling setup
stop_event = threading.Event()
key_queue = queue.Queue()
key_state = {key: False for key in ["w", "a", "s", "d", " ", "*", "/", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "f"]}

def getch():
    return readchar.readkey()

def get_input_thread():
    while not stop_event.is_set():
        try:
            key_input = getch()
            if key_input in key_state or key_input in ("q", '\x03', 'k'):
                key_queue.put(key_input)
            elif key_input == 'q' or key_input == '\x03':
                stop_event.set()
                key_queue.put(None)
                return
        except Exception:
            stop_event.set()
            return

def start_input_thread():
    input_thread = threading.Thread(target=get_input_thread, daemon=True)
    input_thread.start()
    return input_thread

def get_key():
    try:
        return key_queue.get_nowait()
    except queue.Empty:
        return None

# Game constants
button_on = ["⑴","⑵","⑶","⑷","⑸","⑹","⑺","⑻","⑼","⑽","⑾","⑿","⒀","⒁","⒂","⒃","⒄","⒅","⒆","⒇"]
ground_on = ["➊","➋","➌","➍","➎","➏","➐","➑","➒","➓","⓫","⓬","⓭","⓮","⓯","⓰","⓱","⓲","⓳","⓴"]
BOARD_HEIGHT = len(board)
BOARD_WIDTH = len(board[0])
VIEW_HEIGHT = 50
VIEW_WIDTH = 95

# Game state
botton_status = [True] * 20
on_ground = True
move_left = True
move_right = True
invincible = False
win = False
debugging = False
vol = 0
playerx = 2
playery = 4863
savex = 2
savey = playery
curant_pos = " "
curant_pos_prev = None
move = ""

def check_ground(char):
    return char in ground_on

def board_eval(current_board, button_status):
    out2 = []
    for row in current_board:
        out1 = []
        for char in row:
            if char == "█":
                out1.append("g")
            elif char in ["◀", "▼", "▶", "▲"]:
                out1.append("d")
            elif char == "◉":
                out1.append("s")
            elif char == "⚐":
                out1.append("w")
            elif char in button_on:
                count = button_on.index(char)
                out1.append(f"B{count}")
            else:
                is_ground = False
                for count, g_on_char in enumerate(ground_on):
                    if char == g_on_char and button_status[count]:
                        out1.append("g")
                        is_ground = True
                        break
                if not is_ground:
                    out1.append(" ")
        out2.append(out1)
    return out2

def get_map(inboard):
    return [list(line) for line in inboard]

def get_map_shown(playery, playerx):
    upper_y = max(0, playery - VIEW_HEIGHT // 2)
    lower_y = min(BOARD_HEIGHT, upper_y + VIEW_HEIGHT)
    upper_x = max(0, playerx - VIEW_WIDTH // 2)
    lower_x = min(BOARD_WIDTH, upper_x + VIEW_WIDTH)
    visible_map = [board[y][upper_x:lower_x] for y in range(upper_y, lower_y)]
    return visible_map, upper_x, upper_y

def print_buffer(buffer):
    os.system('cls' if os.name == 'nt' else 'clear')
    for line in buffer:
        print("".join(line))

def board_game_loop(playerx, playery):
    visible_map, view_x, view_y = get_map_shown(playery, playerx)
    buffer = get_map(visible_map)
    local_y = playery - view_y
    local_x = playerx - view_x
    if 0 <= local_y < len(buffer) and 0 <= local_x < len(buffer[local_y]):
        buffer[local_y][local_x] = "🯅"
    print_buffer(buffer)
    if debugging:
        print(f"Debug Info:\nplayerx={playerx}, playery={playery}, vol={vol}, on_ground={on_ground}")

def game_loop():
    global playerx, playery, vol, on_ground, move_left, move_right, win, curant_pos, curant_pos_prev, debugging, savex, savey
    input_thread = start_input_thread()
    print("Game started. Use WASD. Ctrl+C to quit.")

    while not stop_event.is_set():
        move = get_key()
        current_board = board[:]
        board_val = board_eval(current_board, botton_status)
        next_y = playery

        # Jump and gravity
        if move == "f" and debugging:
            vol += 0.5
        if (move == " " or move == "w") and on_ground:
            vol = 0.5
        if vol > -2:
            vol -= 0.125

        if vol != 0:
            step = -1 if vol > 0 else 1
            for _ in range(int(abs(vol * 2)) + 1):
                candidate_y = next_y + step
                if candidate_y < 0 or candidate_y >= BOARD_HEIGHT or board_val[candidate_y][playerx] == "g" or check_ground(board_val[candidate_y][playerx]):
                    vol = 0
                    on_ground = step > 0
                    break
                next_y = candidate_y

        # Horizontal movement
        next_x = playerx
        if move == "a" and move_left:
            next_x -= 1
        elif move == "d" and move_right:
            next_x += 1
        next_x = max(0, min(BOARD_WIDTH - 1, next_x))

        if board_val[next_y][next_x] != "g" and not check_ground(board_val[next_y][next_x]):
            playerx, playery = next_x, next_y

        # Update flags
        on_ground = playery + 1 < BOARD_HEIGHT and (board_val[playery + 1][playerx] == "g" or check_ground(board_val[playery + 1][playerx]))
        move_left = playerx > 0 and (board_val[playery][playerx - 1] != "g" or check_ground(board_val[playery][playerx - 1]))
        move_right = playerx < BOARD_WIDTH - 1 and (board_val[playery][playerx + 1] != "g" or check_ground(board_val[playery][playerx + 1]))

        # Render
        board_game_loop(playerx, playery)

        # Events
        curant_pos = board_val[playery][playerx]
        if curant_pos.startswith("B") and curant_pos != curant_pos_prev:
            count = int(curant_pos[1:])
            botton_status[count] = not botton_status[count]
            print(f"Button {count + 1} {'on' if botton_status[count] else 'off'}")
            time.sleep(0.5)
        curant_pos_prev = curant_pos

        if curant_pos == "d" and not invincible:
            print("You died!")
            time.sleep(0.5)
            playerx, playery = savex, savey
            vol = 0
        if curant_pos == "s":
            savex, savey = playerx, playery
        if curant_pos == "w":
            win = True
            break
        if move == "*":
            debugging = not debugging
        if move == "k":
            print("You died (manual reset).")
            playerx, playery = savex, savey
            vol = 0

        time.sleep(0.075)

try:
    game_loop()
except KeyboardInterrupt:
    print("Ctrl+C detected. Exiting...")
finally:
    stop_event.set()
    print("Game over.")